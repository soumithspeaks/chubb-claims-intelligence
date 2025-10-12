import numpy as np
import pandas as pd
import joblib
from pathlib import Path

class FraudDetector:
    def __init__(self, model_dir=None):
        """
        Initialize the fraud detector with a LightGBM model
        
        Args:
            model_dir (str, optional): Path to directory containing model files
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent.parent / 'models' / 'fraud_detector'
        else:
            model_dir = Path(model_dir)
            
        # Load model and preprocessing components
        self.model = joblib.load(model_dir / 'model.joblib')
        self.label_encoders = joblib.load(model_dir / 'label_encoders.joblib')
        self.optimal_threshold = joblib.load(model_dir / 'optimal_threshold.joblib')
        
        # Define fraud indicators
        self.fraud_indicators = {
            'temporal': [
                'unusual_time',
                'weekend_claim',
                'holiday_claim',
                'new_policy_claim'
            ],
            'financial': [
                'high_claim_amount',
                'multiple_claims_history',
                'inconsistent_damage_cost',
                'high_claim_ratio'
            ],
            'behavioral': [
                'incomplete_documentation',
                'inconsistent_statements',
                'delayed_reporting'
            ],
            'historical': [
                'previous_fraud_attempts',
                'multiple_claims_same_period',
                'recent_policy_changes'
            ]
        }
    
    def preprocess_claim_data(self, claim_data):
        """
        Preprocess claim data for fraud detection
        
        Args:
            claim_data (dict): Claim information including numerical and categorical features
            
        Returns:
            pd.DataFrame: Processed features ready for model prediction
        """
        # Convert to DataFrame for easier processing
        df = pd.DataFrame([claim_data])
        
        # Encode categorical variables
        for col, encoder in self.label_encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[col].astype(str))
        
        # Feature engineering
        if 'VehicleAge' in df.columns:
            df['VehicleAgeSquared'] = df['VehicleAge'] ** 2
        
        if 'ClaimAmount' in df.columns and 'VehiclePrice' in df.columns:
            df['ClaimAmountRatio'] = df['ClaimAmount'] / df['VehiclePrice']
        
        if 'PolicyDuration' in df.columns:
            df['PolicyDurationMonths'] = df['PolicyDuration'] / 30
            df['IsNewPolicy'] = (df['PolicyDuration'] < 90).astype(int)
        
        if 'VehicleAge' in df.columns and 'ClaimAmount' in df.columns:
            df['AgeAmount_Interaction'] = df['VehicleAge'] * df['ClaimAmount']
        
        return df
    
    def detect_fraud(self, claim_data):
        """
        Detect potential fraud in a claim
        
        Args:
            claim_data (dict): Claim information
            
        Returns:
            dict: Fraud detection results with confidence scores and explanations
        """
        # Preprocess claim data
        processed_data = self.preprocess_claim_data(claim_data)
        
        # Get model predictions
        fraud_probability = float(self.model.predict_proba(processed_data)[:, 1][0])
        is_fraud = fraud_probability >= self.optimal_threshold
        
        # Analyze specific fraud indicators
        indicators = self.analyze_fraud_indicators(claim_data, processed_data)
        
        # Calculate risk factors
        risk_factors = self.calculate_risk_factors(claim_data, indicators, processed_data)
        
        # Generate detailed analysis
        analysis = self.generate_fraud_analysis(
            fraud_probability,
            is_fraud,
            indicators,
            risk_factors
        )
        
        return {
            'is_fraud': bool(is_fraud),
            'fraud_probability': fraud_probability,
            'risk_level': self.get_risk_level(fraud_probability),
            'indicators': indicators,
            'risk_factors': risk_factors,
            'analysis': analysis
        }
    
    def analyze_fraud_indicators(self, claim_data, processed_data):
        """
        Analyze specific fraud indicators in the claim
        
        Args:
            claim_data (dict): Original claim information
            processed_data (pd.DataFrame): Processed feature data
            
        Returns:
            dict: Detected fraud indicators by category
        """
        indicators = {category: [] for category in self.fraud_indicators.keys()}
        
        # Temporal indicators
        claim_time = pd.to_datetime(claim_data.get('claim_time'))
        if claim_time:
            if claim_time.hour < 6 or claim_time.hour > 22:
                indicators['temporal'].append('unusual_time')
            if claim_time.dayofweek >= 5:
                indicators['temporal'].append('weekend_claim')
        
        if processed_data.get('IsNewPolicy', [0])[0] == 1:
            indicators['temporal'].append('new_policy_claim')
        
        # Financial indicators
        if processed_data.get('ClaimAmountRatio', [0])[0] > 0.7:
            indicators['financial'].append('high_claim_ratio')
        if claim_data.get('previous_claims_count', 0) > 3:
            indicators['financial'].append('multiple_claims_history')
        
        # Behavioral indicators
        if not all(claim_data.get('required_documents', {}).values()):
            indicators['behavioral'].append('incomplete_documentation')
        if claim_data.get('time_to_report', 0) > 7:
            indicators['behavioral'].append('delayed_reporting')
        
        # Historical indicators
        if claim_data.get('previous_suspicious_claims', 0) > 0:
            indicators['historical'].append('previous_fraud_attempts')
        
        return indicators
    
    def calculate_risk_factors(self, claim_data, indicators, processed_data):
        """
        Calculate risk factors based on claim data and detected indicators
        
        Args:
            claim_data (dict): Original claim information
            indicators (dict): Detected fraud indicators
            processed_data (pd.DataFrame): Processed feature data
            
        Returns:
            dict: Risk factors with scores
        """
        risk_factors = {
            'temporal_risk': 0,
            'financial_risk': 0,
            'behavioral_risk': 0,
            'historical_risk': 0
        }
        
        # Calculate risk scores for each category
        for category in indicators:
            detected_count = len(indicators[category])
            total_indicators = len(self.fraud_indicators[category])
            risk_score = (detected_count / total_indicators) * 10
            
            # Adjust financial risk based on claim amount ratio
            if category == 'financial' and 'ClaimAmountRatio' in processed_data:
                ratio = float(processed_data['ClaimAmountRatio'])
                risk_score *= (1 + ratio)
            
            risk_factors[f'{category}_risk'] = round(risk_score, 2)
        
        return risk_factors
    
    def get_risk_level(self, fraud_probability):
        """
        Determine risk level based on fraud probability
        
        Args:
            fraud_probability (float): Model's fraud probability
            
        Returns:
            str: Risk level category
        """
        if fraud_probability < self.optimal_threshold * 0.5:
            return 'low'
        elif fraud_probability < self.optimal_threshold:
            return 'moderate'
        elif fraud_probability < self.optimal_threshold * 1.5:
            return 'high'
        else:
            return 'critical'
    
    def generate_fraud_analysis(self, fraud_probability, is_fraud, indicators, risk_factors):
        """
        Generate detailed analysis of fraud detection results
        
        Args:
            fraud_probability (float): Model's fraud probability
            is_fraud (bool): Final fraud determination
            indicators (dict): Detected fraud indicators
            risk_factors (dict): Calculated risk factors
            
        Returns:
            dict: Detailed analysis including summary and recommendations
        """
        risk_level = self.get_risk_level(fraud_probability)
        
        # Generate summary
        summary = (
            f"Claim assessed as {'fraudulent' if is_fraud else 'legitimate'} "
            f"with {risk_level} risk level ({fraud_probability:.2%} probability)"
        )
        
        # Compile key findings
        findings = []
        for category, detected in indicators.items():
            if detected:
                findings.append(f"{category.title()}: {', '.join(detected)}")
        
        # Generate recommendations
        recommendations = []
        
        if is_fraud:
            recommendations.extend([
                "Initiate detailed fraud investigation",
                "Request additional documentation and evidence",
                "Schedule in-person assessment",
                "Review claim history in detail"
            ])
        
        if risk_level in ['high', 'critical']:
            recommendations.extend([
                "Escalate to senior claims adjuster",
                "Consider third-party verification"
            ])
        
        for category, detected in indicators.items():
            if category == 'behavioral' and 'incomplete_documentation' in detected:
                recommendations.append("Follow up on missing documents")
            elif category == 'financial' and 'high_claim_ratio' in detected:
                recommendations.append("Request detailed cost breakdown")
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }