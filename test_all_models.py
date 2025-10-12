import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
from app.core.fraud_detector import FraudDetector
from app.core.damage_detector import DamageDetector

@pytest.fixture
def fraud_detector():
    return FraudDetector()

@pytest.fixture
def damage_detector():
    return DamageDetector()

class TestFraudDetector:
    def test_fraud_detection_low_risk(self, fraud_detector):
        claim_data = {
            'ClaimAmount': 1000,
            'VehiclePrice': 20000,
            'VehicleAge': 2,
            'PolicyDuration': 365,
            'previous_claims_count': 0,
            'time_to_report': 1,
            'claim_time': '2023-10-12',
            'required_documents': {
                'Police Report': True,
                'Medical Report': True,
                'Witness Statement': True,
                'Photos': True
            }
        }
        
        result = fraud_detector.detect_fraud(claim_data)
        
        assert isinstance(result, dict)
        assert 'is_fraud' in result
        assert 'fraud_probability' in result
        assert result['risk_level'] == 'low'
        
    def test_fraud_detection_high_risk(self, fraud_detector):
        claim_data = {
            'ClaimAmount': 19000,
            'VehiclePrice': 20000,
            'VehicleAge': 10,
            'PolicyDuration': 30,
            'previous_claims_count': 5,
            'time_to_report': 15,
            'claim_time': '2023-10-12',
            'required_documents': {
                'Police Report': False,
                'Medical Report': False,
                'Witness Statement': False,
                'Photos': True
            }
        }
        
        result = fraud_detector.detect_fraud(claim_data)
        
        assert isinstance(result, dict)
        assert 'is_fraud' in result
        assert 'fraud_probability' in result
        assert result['risk_level'] in ['high', 'critical']
        
    def test_preprocess_claim_data(self, fraud_detector):
        claim_data = {
            'ClaimAmount': 1000,
            'VehiclePrice': 20000,
            'VehicleAge': 2,
            'PolicyDuration': 365
        }
        
        processed_data = fraud_detector.preprocess_claim_data(claim_data)
        
        assert isinstance(processed_data, pd.DataFrame)
        assert 'VehicleAgeSquared' in processed_data.columns
        assert 'ClaimAmountRatio' in processed_data.columns
        assert 'PolicyDurationMonths' in processed_data.columns

class TestDamageDetector:
    def test_damage_detection_no_damage(self, damage_detector):
        # Create a blank image
        image = Image.new('RGB', (640, 480), color='white')
        
        result = damage_detector.detect_damage(image)
        
        assert isinstance(result, dict)
        assert 'damages_detected' in result
        assert not result['damages_detected']
        assert result['estimated_cost'] == 0
        
    def test_preprocess_image(self, damage_detector):
        # Test with different image formats
        image_rgb = Image.new('RGB', (640, 480), color='white')
        image_rgba = Image.new('RGBA', (640, 480), color='white')
        image_l = Image.new('L', (640, 480), color='white')
        
        processed_rgb = damage_detector.preprocess_image(image_rgb)
        processed_rgba = damage_detector.preprocess_image(image_rgba)
        processed_l = damage_detector.preprocess_image(image_l)
        
        assert isinstance(processed_rgb, np.ndarray)
        assert isinstance(processed_rgba, np.ndarray)
        assert isinstance(processed_l, np.ndarray)
        assert processed_rgb.shape[-1] == 3  # Should be RGB
        assert processed_rgba.shape[-1] == 3  # Should be converted to RGB
        assert processed_l.shape[-1] == 3  # Should be converted to RGB
        
    def test_calculate_severity(self, damage_detector):
        # Test different confidence and area combinations
        severity1 = damage_detector.calculate_severity(0.9, 0.1)
        severity2 = damage_detector.calculate_severity(0.5, 0.5)
        severity3 = damage_detector.calculate_severity(0.1, 0.9)
        
        assert 0 <= severity1 <= 1
        assert 0 <= severity2 <= 1
        assert 0 <= severity3 <= 1
        
    def test_estimate_repair_cost(self, damage_detector):
        # Test with no damages
        assert damage_detector.estimate_repair_cost([]) == 0
        
        # Test with sample damages
        damages = [
            {
                'type': 'scratch',
                'confidence': 0.9,
                'severity': 0.3,
                'bbox': [0, 0, 100, 100]
            },
            {
                'type': 'dent',
                'confidence': 0.8,
                'severity': 0.6,
                'bbox': [200, 200, 300, 300]
            }
        ]
        
        cost = damage_detector.estimate_repair_cost(damages)
        assert isinstance(cost, float)
        assert cost >= 100  # Minimum cost should be $100

if __name__ == '__main__':
    pytest.main([__file__])
