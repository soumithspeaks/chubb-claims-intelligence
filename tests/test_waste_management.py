"""
Tests for waste management API endpoints
"""

import pytest
from decimal import Decimal


def test_waste_classifier_initialization():
    """Test waste classifier can be initialized"""
    from app.core.waste_classifier import WasteClassifier
    
    classifier = WasteClassifier()
    assert classifier is not None
    assert len(classifier.waste_categories) > 0


def test_waste_classification():
    """Test waste classification returns expected format"""
    from app.core.waste_classifier import WasteClassifier
    
    classifier = WasteClassifier()
    result = classifier.classify_images(["/path/to/image.jpg"])
    
    assert 'category' in result
    assert 'subcategory' in result
    assert 'confidence' in result
    assert 'estimated_weight_kg' in result
    assert 'estimated_payment' in result
    
    # Check confidence is between 0 and 1
    assert 0 <= result['confidence'] <= 1


def test_payment_calculation():
    """Test payment calculation for different waste types"""
    from app.core.waste_classifier import WasteClassifier
    
    classifier = WasteClassifier()
    
    # Test plastic payment
    payment = classifier.calculate_payment("Plastic", "PET", 2.5)
    assert isinstance(payment, Decimal)
    assert payment > 0
    
    # Test paper payment
    payment = classifier.calculate_payment("Paper", "CARDBOARD", 5.0)
    assert isinstance(payment, Decimal)
    assert payment > 0


def test_get_all_categories():
    """Test retrieving all waste categories"""
    from app.core.waste_classifier import WasteClassifier
    
    classifier = WasteClassifier()
    categories = classifier.get_all_categories()
    
    assert isinstance(categories, list)
    assert len(categories) >= 8  # We defined 8 categories
    
    # Check structure of first category
    if categories:
        cat = categories[0]
        assert 'id' in cat
        assert 'name' in cat
        assert 'subcategories' in cat


def test_environmental_impact_calculation():
    """Test environmental impact calculation"""
    from app.core.waste_classifier import WasteClassifier
    
    classifier = WasteClassifier()
    
    waste_records = [
        {"category": "Plastic", "weight_kg": 5.0},
        {"category": "Paper", "weight_kg": 10.0},
        {"category": "Metal", "weight_kg": 3.0}
    ]
    
    impact = classifier.calculate_environmental_impact(waste_records)
    
    assert 'total_waste_kg' in impact
    assert 'co2_saved_kg' in impact
    assert 'trees_saved' in impact
    assert 'energy_saved_kwh' in impact
    
    assert impact['total_waste_kg'] == 18.0


def test_agent_matcher_initialization():
    """Test agent matcher can be initialized"""
    from app.core.matching_algorithm import AgentMatcher
    
    matcher = AgentMatcher()
    assert matcher is not None
    assert matcher.max_distance_km > 0


def test_distance_calculation():
    """Test Haversine distance calculation"""
    from app.core.matching_algorithm import AgentMatcher
    
    matcher = AgentMatcher()
    
    # Test distance between two known locations
    # San Francisco to Los Angeles (approx 559 km)
    sf = (37.7749, -122.4194)
    la = (34.0522, -118.2437)
    
    distance = matcher._calculate_distance(sf, la)
    
    assert isinstance(distance, float)
    assert 500 < distance < 600  # Approximate range


def test_find_best_agent():
    """Test finding best agent for pickup"""
    from app.core.matching_algorithm import AgentMatcher
    
    matcher = AgentMatcher()
    
    pickup_location = (37.7749, -122.4194)
    
    agents = [
        {
            'id': 1,
            'name': 'Agent A',
            'current_latitude': 37.7849,
            'current_longitude': -122.4094,
            'rating': 4.8,
            'total_ratings': 100,
            'current_active_pickups': 1,
            'total_requests_received': 200,
            'total_requests_accepted': 180
        },
        {
            'id': 2,
            'name': 'Agent B',
            'current_latitude': 37.7649,
            'current_longitude': -122.4294,
            'rating': 4.5,
            'total_ratings': 50,
            'current_active_pickups': 3,
            'total_requests_received': 100,
            'total_requests_accepted': 80
        }
    ]
    
    result = matcher.find_best_agent(
        pickup_location,
        agents,
        {'waste_category': 'Plastic'}
    )
    
    assert result is not None
    assert 'agent' in result
    assert 'score' in result
    assert 'distance_km' in result
    assert 'estimated_arrival_minutes' in result


def test_earnings_calculation():
    """Test agent earnings calculation"""
    from app.core.matching_algorithm import AgentMatcher
    
    matcher = AgentMatcher()
    
    earnings = matcher.calculate_estimated_earnings(Decimal('25.00'), 0.20)
    
    assert 'gross_payment' in earnings
    assert 'commission' in earnings
    assert 'agent_earnings' in earnings
    assert 'commission_rate' in earnings
    
    assert earnings['gross_payment'] == 25.00
    assert earnings['commission'] == 5.00
    assert earnings['agent_earnings'] == 20.00


def test_pydantic_models():
    """Test Pydantic models can be instantiated"""
    from app.models.waste_management import (
        UserCreate, AgentCreate, WasteCategory,
        PickupRequestCreate
    )
    
    # Test UserCreate
    user = UserCreate(
        email="test@example.com",
        phone="1234567890",
        full_name="Test User",
        password="password123"
    )
    assert user.email == "test@example.com"
    
    # Test WasteCategory enum
    assert WasteCategory.PLASTIC == "Plastic"
    assert WasteCategory.PAPER == "Paper"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
