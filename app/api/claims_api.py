from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
import io
from PIL import Image
import numpy as np
from typing import List, Optional
from pydantic import BaseModel

# Add the parent directory to system path
sys.path.append(str(Path(__file__).parent.parent))

from core.fraud_detector import FraudDetector
from core.damage_detector import DamageDetector

app = FastAPI(title="Claims Intelligence API")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML models
fraud_detector = FraudDetector()
damage_detector = DamageDetector()

class ClaimAnalysisRequest(BaseModel):
    amount: float
    claimType: str
    policeReport: bool
    vehiclePrice: Optional[float] = None
    vehicleAge: Optional[int] = None
    policyDuration: Optional[int] = None
    previousClaims: Optional[int] = 0
    timeToReport: Optional[int] = 0

@app.post("/api/analyze")
async def analyze_claim(
    claim: ClaimAnalysisRequest,
    files: List[UploadFile] = File(None)
):
    """Analyze a claim using ML models"""
    
    # Process claim data for fraud detection
    claim_data = {
        'ClaimAmount': claim.amount,
        'VehiclePrice': claim.vehiclePrice or claim.amount * 4,  # Estimate if not provided
        'VehicleAge': claim.vehicleAge or 3,  # Default values
        'PolicyDuration': claim.policyDuration or 365,
        'previous_claims_count': claim.previousClaims,
        'time_to_report': claim.timeToReport,
        'claim_time': '2025-10-12',  # Current date
        'required_documents': {
            'Police Report': claim.policeReport,
            'Medical Report': False,  # Could be added to frontend later
            'Witness Statement': False,
            'Photos': bool(files)
        }
    }
    
    # Run fraud detection
    fraud_result = fraud_detector.detect_fraud(claim_data)
    
    # Process damage assessment if images provided
    damage_results = []
    if files:
        for file in files:
            content = await file.read()
            image = Image.open(io.BytesIO(content))
            result = damage_detector.detect_damage(image)
            damage_results.append(result)
    
    # Calculate metrics
    risk_score = calculate_risk_score(fraud_result, damage_results, claim)
    severity = calculate_severity(damage_results, claim.amount)
    cost_estimate = calculate_cost_estimate(damage_results, claim.amount, severity)
    recommended_actions = generate_recommendations(
        risk_score=risk_score,
        fraud_probability=fraud_result['fraud_probability'] * 100,
        severity=severity,
        police_report=claim.policeReport,
        damage_results=damage_results
    )
    
    return {
        "riskScore": risk_score,
        "fraudProbability": round(fraud_result['fraud_probability'] * 100, 1),
        "damageSeverity": severity,
        "costEstimate": round(cost_estimate, 2),
        "recommendedActions": recommended_actions
    }

def calculate_risk_score(fraud_result, damage_results, claim) -> int:
    """Calculate overall risk score (0-100)"""
    # Base risk from fraud probability
    fraud_risk = fraud_result['fraud_probability'] * 100
    
    # Risk factors from claim type
    type_risk = {
        "Collision": 35,
        "Theft": 55,
        "Natural Disaster": 25,
        "Vandalism": 45,
        "Other": 30
    }.get(claim.claimType, 30)
    
    # Risk from damage assessment
    damage_risk = 0
    if damage_results:
        severity_scores = [r['total_severity'] * 100 for r in damage_results]
        damage_risk = sum(severity_scores) / len(severity_scores)
    
    # Combine risks with weights
    total_risk = (
        fraud_risk * 0.4 +
        type_risk * 0.3 +
        damage_risk * 0.3
    )
    
    # Apply modifiers
    if claim.policeReport:
        total_risk -= 10
    if claim.previousClaims > 2:
        total_risk += 15
    
    return round(min(max(total_risk, 0), 100))

def calculate_severity(damage_results, claim_amount) -> str:
    """Determine damage severity level"""
    if not damage_results:
        # Base on claim amount if no images
        if claim_amount > 8000:
            return "Severe"
        elif claim_amount > 2500:
            return "Moderate"
        return "Minor"
    
    # Calculate average severity from damage detection
    total_severity = 0
    damage_count = 0
    for result in damage_results:
        for damage in result['damages']:
            total_severity += damage['severity']
            damage_count += 1
    
    if damage_count == 0:
        return "Minor"
    
    avg_severity = total_severity / damage_count
    if avg_severity > 0.7:
        return "Severe"
    elif avg_severity > 0.4:
        return "Moderate"
    return "Minor"

def calculate_cost_estimate(damage_results, claim_amount, severity) -> float:
    """Estimate repair costs"""
    if not damage_results:
        # Adjust claimed amount based on severity if no images
        return claim_amount * {
            "Severe": 1.05,
            "Moderate": 0.95,
            "Minor": 0.85
        }[severity]
    
    # Sum up estimated costs from damage detection
    total_cost = sum(r['estimated_cost'] for r in damage_results)
    
    # Blend with claimed amount
    return (total_cost + claim_amount) / 2

def generate_recommendations(
    risk_score: float,
    fraud_probability: float,
    severity: str,
    police_report: bool,
    damage_results: list
) -> List[str]:
    """Generate action recommendations based on analysis"""
    actions = []
    
    if not police_report:
        actions.append("Request official police report documentation.")
        
    if fraud_probability >= 60:
        actions.append("Escalate to fraud investigation team.")
        actions.append("Request additional documentation and proof.")
    
    if risk_score >= 70:
        actions.append("Trigger enhanced underwriting review.")
        actions.append("Schedule detailed claim investigation.")
    
    if severity == "Severe":
        actions.append("Schedule in-person adjuster inspection.")
        if damage_results:
            damages_found = sum(len(r['damages']) for r in damage_results)
            if damages_found >= 3:
                actions.append("Request structural integrity assessment.")
    elif severity == "Moderate":
        actions.append("Proceed with remote adjuster assessment.")
        if not damage_results:
            actions.append("Request additional damage documentation.")
    else:  # Minor
        actions.append("Process for expedited assessment.")
    
    if fraud_probability < 30 and risk_score < 40 and police_report:
        actions.append("Fast-track approval recommended.")
    
    return actions