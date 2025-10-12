from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
from pathlib import Path
import sys
from PIL import Image
import io
import json

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))

from core.fraud_detector import FraudDetector
from core.damage_detector import DamageDetector

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models
fraud_detector = FraudDetector()
damage_detector = DamageDetector()

@app.post("/api/analyze-claim")
async def analyze_claim(
    files: List[UploadFile] = File(None),
    claim_data: str = Form(...)
):
    try:
        # Parse claim data
        claim_info = json.loads(claim_data)
        
        # Process claim for fraud detection
        claim_info_processed = {
            'ClaimAmount': float(claim_info.get('amount', 0)),
            'VehiclePrice': float(claim_info.get('vehiclePrice', 0)),
            'VehicleAge': int(claim_info.get('vehicleAge', 3)),
            'PolicyDuration': int(claim_info.get('policyDuration', 365)),
            'previous_claims_count': int(claim_info.get('previousClaims', 0)),
            'time_to_report': int(claim_info.get('timeToReport', 1)),
            'claim_time': claim_info.get('claimDate', '2025-10-12'),
            'required_documents': {
                'Police Report': claim_info.get('policeReport', False),
                'Medical Report': False,
                'Witness Statement': False,
                'Photos': bool(files)
            }
        }
        
        # Get fraud detection results
        fraud_result = fraud_detector.detect_fraud(claim_info_processed)
        
        # Process images for damage detection
        damage_results = []
        if files:
            for file in files:
                content = await file.read()
                image = Image.open(io.BytesIO(content))
                result = damage_detector.detect_damage(image)
                damage_results.append(result)
        
        # Calculate final metrics
        risk_score = calculate_risk_score(fraud_result, damage_results, claim_info)
        estimated_cost = calculate_cost_estimate(damage_results, claim_info_processed['ClaimAmount'])
        damage_severity = calculate_severity(damage_results, estimated_cost)
        
        # Generate recommendations
        recommendations = generate_recommendations(
            fraud_result=fraud_result,
            damage_results=damage_results,
            risk_score=risk_score,
            claim_info=claim_info
        )
        
        return {
            "riskScore": risk_score,
            "fraudProbability": round(fraud_result['fraud_probability'] * 100, 1),
            "damageSeverity": damage_severity,
            "costEstimate": round(estimated_cost, 2),
            "recommendations": recommendations,
            "details": {
                "fraudAnalysis": fraud_result['analysis'],
                "damageAnalysis": [
                    {
                        "damages": result['damages'],
                        "confidence": result['max_confidence'],
                        "severity": result['total_severity']
                    }
                    for result in damage_results
                ] if damage_results else []
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

def calculate_risk_score(fraud_result, damage_results, claim_info) -> int:
    """Calculate overall risk score (0-100)"""
    # Base risk from fraud probability
    fraud_risk = fraud_result['fraud_probability'] * 100
    
    # Risk based on claim type
    type_risk = {
        "Collision": 35,
        "Theft": 55,
        "Natural Disaster": 25,
        "Vandalism": 45,
        "Other": 30
    }.get(claim_info.get('claimType', 'Other'), 30)
    
    # Risk from damage assessment
    damage_risk = 0
    if damage_results:
        severity_scores = [r['total_severity'] * 100 for r in damage_results]
        damage_risk = sum(severity_scores) / len(severity_scores)
    
    # Weighted combination
    total_risk = (
        fraud_risk * 0.4 +  # Fraud detection weight
        type_risk * 0.3 +   # Claim type weight
        damage_risk * 0.3    # Damage assessment weight
    )
    
    # Apply modifiers
    if claim_info.get('policeReport'):
        total_risk -= 10
    if int(claim_info.get('previousClaims', 0)) > 2:
        total_risk += 15
        
    return round(min(max(total_risk, 0), 100))

def calculate_severity(damage_results, estimated_cost) -> str:
    """Determine damage severity level"""
    if not damage_results:
        if estimated_cost > 8000:
            return "Severe"
        elif estimated_cost > 2500:
            return "Moderate"
        return "Minor"
    
    # Calculate from damage detection results
    max_severity = 0
    for result in damage_results:
        for damage in result['damages']:
            max_severity = max(max_severity, damage['severity'])
    
    if max_severity > 0.7:
        return "Severe"
    elif max_severity > 0.4:
        return "Moderate"
    return "Minor"

def calculate_cost_estimate(damage_results, claim_amount) -> float:
    """Calculate estimated repair costs"""
    if not damage_results:
        return claim_amount
    
    # Get cost estimates from damage detection
    total_damage_cost = sum(result['estimated_cost'] for result in damage_results)
    
    # Blend with claimed amount (weighted average)
    return (total_damage_cost * 0.7 + claim_amount * 0.3)

def generate_recommendations(fraud_result, damage_results, risk_score, claim_info) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    # Fraud-related recommendations
    fraud_prob = fraud_result['fraud_probability'] * 100
    if fraud_prob > 70:
        recommendations.extend([
            "🚨 High fraud risk - Immediate investigation required",
            "📋 Request additional documentation and proof",
            "👥 Schedule in-person interview with claimant"
        ])
    elif fraud_prob > 40:
        recommendations.extend([
            "⚠️ Moderate fraud risk - Enhanced verification needed",
            "📝 Verify documentation authenticity",
            "🔍 Cross-reference claim history"
        ])
    
    # Police report recommendations
    if not claim_info.get('policeReport'):
        recommendations.append("👮 Request official police report")
    
    # Damage assessment recommendations
    if damage_results:
        damage_count = sum(len(result['damages']) for result in damage_results)
        if damage_count > 3:
            recommendations.extend([
                "🚗 Schedule comprehensive vehicle inspection",
                "⚡ Request structural integrity assessment"
            ])
    else:
        recommendations.append("📸 Request additional damage photographs")
    
    # Cost-related recommendations
    if risk_score > 60:
        recommendations.extend([
            "💰 Review cost estimates in detail",
            "📊 Compare with similar claims in database"
        ])
    
    # Process optimization recommendations
    if risk_score < 30 and fraud_prob < 25:
        recommendations.append("✅ Consider for fast-track processing")
    
    return recommendations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)