import torch
import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sklearn.preprocessing import StandardScaler
import pandas as pd
from pathlib import Path

class FraudDetector:
    def __init__(self, model_path=None):
        """
        Initialize the fraud detector with a transformer-based model
        
        Args:
            model_path (str, optional): Path to a pre-trained model
        """
        if model_path and Path(model_path).exists():
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        else:
            # Initialize with pre-trained RoBERTa
            self.model = AutoModelForSequenceClassification.from_pretrained(
                'roberta-base',
                num_labels=2
            )
            self.tokenizer = AutoTokenizer.from_pretrained('roberta-base')
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Initialize feature scaler for numerical features
        self.scaler = StandardScaler()
        
        # Define fraud indicators
        self.fraud_indicators = {
            'temporal': [
                'unusual_time',
                'weekend_claim',
                'holiday_claim'
            ],
            'financial': [
                'high_claim_amount',
                'multiple_claims_history',
                'inconsistent_damage_cost'
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
            claim_data (dict): Claim information including text and numerical features
            
        Returns:
            tuple: Processed text features and numerical features
        """
        # Extract text features
        text_features = [
            claim_data.get('claim_description', ''),
            claim_data.get('incident_report', ''),
            claim_data.get('additional_notes', '')
        ]
        combined_text = ' '.join(filter(None, text_features))
        
        # Process numerical features
        numerical_features = [
            claim_data.get('claim_amount', 0),
            claim_data.get('time_to_report', 0),
            claim_data.get('previous_claims_count', 0),
            claim_data.get('policy_age_days', 0)
        ]
        
        return combined_text, np.array(numerical_features).reshape(1, -1)
    
    def detect_fraud(self, claim_data):
        """
        Detect potential fraud in a claim
        
        Args:
            claim_data (dict): Claim information including text and numerical features
            
        Returns:
            dict: Fraud detection results with confidence scores and explanations
        """
        # Preprocess claim data
        text, numerical_features = self.preprocess_claim_data(claim_data)
        
        # Tokenize text
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            return_tensors='pt'
        ).to(self.device)
        
        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            fraud_probability = float(probs[0][1].cpu().numpy())
        
        # Analyze specific fraud indicators
        indicators = self.analyze_fraud_indicators(claim_data)
        
        # Calculate risk factors
        risk_factors = self.calculate_risk_factors(claim_data, indicators)
        
        # Generate detailed analysis
        analysis = self.generate_fraud_analysis(
            fraud_probability,
            indicators,
            risk_factors
        )
        
        return {
            'fraud_probability': fraud_probability,
            'risk_level': self.get_risk_level(fraud_probability),
            'indicators': indicators,
            'risk_factors': risk_factors,
            'analysis': analysis
        }
    
    def analyze_fraud_indicators(self, claim_data):
        """
        Analyze specific fraud indicators in the claim
        
        Args:
            claim_data (dict): Claim information
            
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
        
        # Financial indicators
        if claim_data.get('claim_amount', 0) > claim_data.get('average_claim_amount', 0) * 1.5:
            indicators['financial'].append('high_claim_amount')
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
    
    def calculate_risk_factors(self, claim_data, indicators):
        """
        Calculate risk factors based on claim data and detected indicators
        
        Args:
            claim_data (dict): Claim information
            indicators (dict): Detected fraud indicators
            
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
            risk_factors[f'{category}_risk'] = round(risk_score, 2)
        
        return risk_factors
    
    def generate_fraud_analysis(self, fraud_probability, indicators, risk_factors):
        """
        Generate detailed analysis of fraud detection results
        
        Args:
            fraud_probability (float): Model's fraud probability
            indicators (dict): Detected fraud indicators
            risk_factors (dict): Calculated risk factors
            
        Returns:
            dict: Detailed analysis including summary and recommendations
        """
        # Generate summary
        risk_level = self.get_risk_level(fraud_probability)
        summary = f"Claim assessed with {risk_level} risk level ({fraud_probability:.2%} probability)"
        
        # Compile key findings
        findings = []
        for category, detected in indicators.items():
            if detected:
                findings.append(f"{category.title()}: {', '.join(detected)}")
        
        # Generate recommendations
        recommendations = self.generate_recommendations(risk_level, indicators)
        
        return {
            'summary': summary,
            'findings': findings,
            'recommendations': recommendations
        }
    
    def get_risk_level(self, fraud_probability):
        """
        Determine risk level based on fraud probability
        
        Args:
            fraud_probability (float): Model's fraud probability
            
        Returns:
            str: Risk level category
        """
        if fraud_probability < 0.2:
            return 'low'
        elif fraud_probability < 0.4:
            return 'moderate'
        elif fraud_probability < 0.7:
            return 'high'
        else:
            return 'critical'
    
    def generate_recommendations(self, risk_level, indicators):
        """
        Generate recommendations based on risk level and indicators
        
        Args:
            risk_level (str): Determined risk level
            indicators (dict): Detected fraud indicators
            
        Returns:
            list: List of recommendations
        """
        recommendations = []
        
        if risk_level in ['high', 'critical']:
            recommendations.append("Conduct detailed investigation")
            recommendations.append("Request additional documentation")
            recommendations.append("Schedule in-person assessment")
        
        if 'incomplete_documentation' in indicators.get('behavioral', []):
            recommendations.append("Follow up on missing documents")
        
        if 'delayed_reporting' in indicators.get('behavioral', []):
            recommendations.append("Investigate reason for delayed reporting")
        
        if 'multiple_claims_history' in indicators.get('financial', []):
            recommendations.append("Review claims history in detail")
        
        return recommendations