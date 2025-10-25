"""
Waste Management Platform API
FastAPI application for waste collection and recycling
"""

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import uvicorn
import json
from datetime import datetime
from pathlib import Path

# Import models and services
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.waste_management import (
    UserCreate, UserResponse, UserLogin,
    AgentCreate, AgentResponse, AgentLocationUpdate, AgentAvailabilityUpdate,
    WasteClassificationRequest, WasteClassificationResult,
    PickupRequestCreate, PickupRequestResponse, PickupStatusUpdate, PickupRating,
    AddressCreate, AddressResponse,
    TransactionResponse, NotificationResponse,
    UserDashboard, AgentDashboard, EnvironmentalImpact,
    Token, WasteCategory
)
from core.waste_classifier import WasteClassifier
from core.matching_algorithm import AgentMatcher

# Initialize FastAPI app
app = FastAPI(
    title="Waste Management Platform API",
    description="Enterprise waste management platform with AI classification and agent matching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
waste_classifier = WasteClassifier()
agent_matcher = AgentMatcher()

# In-memory storage for MVP (replace with database in production)
users_db = {}
agents_db = {}
pickups_db = {}
addresses_db = {}
transactions_db = {}
notifications_db = {}

# Counters for IDs
user_id_counter = 1
agent_id_counter = 1
pickup_id_counter = 1
address_id_counter = 1
transaction_id_counter = 1
notification_id_counter = 1


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Waste Management Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ==================== Waste Classification Endpoints ====================

@app.post("/api/classify", response_model=WasteClassificationResult, tags=["Classification"])
async def classify_waste(request: WasteClassificationRequest):
    """
    Classify waste from uploaded images using AI
    
    - **image_urls**: List of 1-5 image URLs or paths
    
    Returns classification result with confidence score and estimated payment
    """
    try:
        result = waste_classifier.classify_images(request.image_urls)
        
        return WasteClassificationResult(
            category=WasteCategory(result['category']),
            subcategory=result.get('subcategory'),
            confidence=result['confidence'],
            estimated_weight_kg=result.get('estimated_weight_kg'),
            estimated_payment=result.get('estimated_payment')
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@app.get("/api/waste-types", tags=["Classification"])
async def get_waste_types():
    """
    Get all waste categories and subcategories with pricing
    """
    categories = waste_classifier.get_all_categories()
    return {"categories": categories}


@app.get("/api/waste-types/{category}", tags=["Classification"])
async def get_waste_category_info(category: str):
    """
    Get detailed information about a specific waste category
    """
    info = waste_classifier.get_waste_info(category)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waste category '{category}' not found"
        )
    return info


# ==================== User Endpoints ====================

@app.post("/api/users/register", response_model=UserResponse, tags=["Users"])
async def register_user(user: UserCreate):
    """
    Register a new user
    """
    global user_id_counter
    
    # Check if user already exists
    if any(u['email'] == user.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user (in production, hash the password)
    user_id = user_id_counter
    user_id_counter += 1
    
    user_data = {
        'id': user_id,
        'email': user.email,
        'phone': user.phone,
        'full_name': user.full_name,
        'profile_image_url': None,
        'wallet_balance': 0.00,
        'total_waste_recycled': 0.00,
        'carbon_footprint_saved': 0.00,
        'created_at': datetime.utcnow(),
        'is_active': True,
        'email_verified': False,
        'phone_verified': False
    }
    
    users_db[user_id] = user_data
    
    return UserResponse(**user_data)


@app.post("/api/users/login", response_model=Token, tags=["Users"])
async def login_user(credentials: UserLogin):
    """
    User login
    """
    # Simple authentication (in production, use proper password hashing and JWT)
    user = next(
        (u for u in users_db.values() if u['email'] == credentials.email),
        None
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return Token(
        access_token=f"mock_token_{user['id']}",
        user_id=user['id'],
        role="user"
    )


@app.get("/api/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user_profile(user_id: int):
    """
    Get user profile
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**users_db[user_id])


@app.get("/api/users/{user_id}/dashboard", response_model=UserDashboard, tags=["Users"])
async def get_user_dashboard(user_id: int):
    """
    Get user dashboard with statistics and recent pickups
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = users_db[user_id]
    user_pickups = [p for p in pickups_db.values() if p.get('user_id') == user_id]
    
    recent_pickups = sorted(
        user_pickups,
        key=lambda x: x['created_at'],
        reverse=True
    )[:5]
    
    return UserDashboard(
        wallet_balance=user['wallet_balance'],
        total_waste_recycled=user['total_waste_recycled'],
        carbon_footprint_saved=user['carbon_footprint_saved'],
        total_pickups=len(user_pickups),
        pending_pickups=len([p for p in user_pickups if p['status'] == 'pending']),
        completed_pickups=len([p for p in user_pickups if p['status'] == 'completed']),
        total_earnings=user['wallet_balance'],
        recent_pickups=[PickupRequestResponse(**p) for p in recent_pickups]
    )


# ==================== Agent Endpoints ====================

@app.post("/api/agents/register", response_model=AgentResponse, tags=["Agents"])
async def register_agent(agent: AgentCreate):
    """
    Register a new agent
    """
    global agent_id_counter
    
    # Check if agent already exists
    if any(a['email'] == agent.email for a in agents_db.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    agent_id = agent_id_counter
    agent_id_counter += 1
    
    agent_data = {
        'id': agent_id,
        'email': agent.email,
        'phone': agent.phone,
        'full_name': agent.full_name,
        'vehicle_type': agent.vehicle_type,
        'vehicle_number': agent.vehicle_number,
        'license_number': agent.license_number,
        'profile_image_url': None,
        'wallet_balance': 0.00,
        'total_earnings': 0.00,
        'total_pickups_completed': 0,
        'rating': 0.00,
        'total_ratings': 0,
        'is_online': False,
        'is_verified': False,
        'is_active': True,
        'current_latitude': None,
        'current_longitude': None,
        'last_location_update': None,
        'created_at': datetime.utcnow()
    }
    
    agents_db[agent_id] = agent_data
    
    return AgentResponse(**agent_data)


@app.patch("/api/agents/{agent_id}/availability", tags=["Agents"])
async def update_agent_availability(agent_id: int, update: AgentAvailabilityUpdate):
    """
    Toggle agent online/offline status
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agents_db[agent_id]['is_online'] = update.is_online
    
    return {"message": "Availability updated", "is_online": update.is_online}


@app.patch("/api/agents/{agent_id}/location", tags=["Agents"])
async def update_agent_location(agent_id: int, location: AgentLocationUpdate):
    """
    Update agent's current location
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agents_db[agent_id]['current_latitude'] = location.latitude
    agents_db[agent_id]['current_longitude'] = location.longitude
    agents_db[agent_id]['last_location_update'] = datetime.utcnow()
    
    return {"message": "Location updated"}


@app.get("/api/agents/{agent_id}/dashboard", response_model=AgentDashboard, tags=["Agents"])
async def get_agent_dashboard(agent_id: int):
    """
    Get agent dashboard with earnings and statistics
    """
    if agent_id not in agents_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent = agents_db[agent_id]
    agent_pickups = [p for p in pickups_db.values() if p.get('agent_id') == agent_id]
    
    today = datetime.utcnow().date()
    today_pickups = [
        p for p in agent_pickups 
        if p.get('completed_at') and p['completed_at'].date() == today
    ]
    
    return AgentDashboard(
        wallet_balance=agent['wallet_balance'],
        total_earnings=agent['total_earnings'],
        total_pickups_completed=agent['total_pickups_completed'],
        rating=agent['rating'],
        total_ratings=agent['total_ratings'],
        today_earnings=sum(p.get('actual_payment', 0) * 0.8 for p in today_pickups),
        today_pickups=len(today_pickups),
        pending_requests=len([p for p in agent_pickups if p['status'] == 'agent_assigned']),
        active_pickup=None
    )


# ==================== Pickup Request Endpoints ====================

@app.post("/api/pickups/request", response_model=PickupRequestResponse, tags=["Pickups"])
async def create_pickup_request(pickup: PickupRequestCreate, user_id: int):
    """
    Create a new pickup request
    """
    global pickup_id_counter
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate estimated payment
    estimated_payment = waste_classifier.calculate_payment(
        pickup.waste_category.value,
        pickup.waste_subcategory or "MIXED",
        float(pickup.estimated_weight_kg or 1.0)
    )
    
    # Generate OTP
    import random
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    pickup_id = pickup_id_counter
    pickup_id_counter += 1
    
    pickup_data = {
        'id': pickup_id,
        'user_id': user_id,
        'agent_id': None,
        'godown_id': None,
        'status': 'pending',
        'waste_category': pickup.waste_category,
        'waste_subcategory': pickup.waste_subcategory,
        'estimated_weight_kg': pickup.estimated_weight_kg,
        'actual_weight_kg': None,
        'pickup_address': pickup.pickup_address,
        'pickup_latitude': pickup.pickup_latitude,
        'pickup_longitude': pickup.pickup_longitude,
        'scheduled_for': pickup.scheduled_for,
        'is_immediate': pickup.is_immediate,
        'estimated_payment': estimated_payment,
        'actual_payment': None,
        'otp_code': otp,
        'requested_at': datetime.utcnow(),
        'agent_accepted_at': None,
        'agent_arrived_at': None,
        'completed_at': None,
        'cancelled_at': None,
        'cancellation_reason': None,
        'user_rating': None,
        'user_feedback': None,
        'agent_rating': None,
        'agent_feedback': None,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    pickups_db[pickup_id] = pickup_data
    
    # Find and assign agent (simplified for MVP)
    if pickup.is_immediate:
        online_agents = [a for a in agents_db.values() if a['is_online']]
        if online_agents:
            best_agent = agent_matcher.find_best_agent(
                (pickup.pickup_latitude, pickup.pickup_longitude),
                online_agents,
                {'waste_category': pickup.waste_category}
            )
            
            if best_agent:
                pickup_data['agent_id'] = best_agent['agent']['id']
                pickup_data['status'] = 'agent_assigned'
                pickup_data['agent_accepted_at'] = datetime.utcnow()
    
    return PickupRequestResponse(**pickup_data)


@app.get("/api/pickups/{pickup_id}", response_model=PickupRequestResponse, tags=["Pickups"])
async def get_pickup(pickup_id: int):
    """
    Get pickup request details
    """
    if pickup_id not in pickups_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )
    
    return PickupRequestResponse(**pickups_db[pickup_id])


@app.patch("/api/pickups/{pickup_id}/status", tags=["Pickups"])
async def update_pickup_status(pickup_id: int, update: PickupStatusUpdate):
    """
    Update pickup status (agent actions)
    """
    if pickup_id not in pickups_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )
    
    pickup = pickups_db[pickup_id]
    pickup['status'] = update.status
    pickup['updated_at'] = datetime.utcnow()
    
    if update.actual_weight_kg:
        pickup['actual_weight_kg'] = update.actual_weight_kg
        # Recalculate payment
        pickup['actual_payment'] = waste_classifier.calculate_payment(
            pickup['waste_category'].value,
            pickup['waste_subcategory'] or "MIXED",
            float(update.actual_weight_kg)
        )
    
    if update.status.value == 'completed':
        pickup['completed_at'] = datetime.utcnow()
        
        # Update user stats
        user = users_db[pickup['user_id']]
        user['wallet_balance'] = float(user['wallet_balance']) + float(pickup['actual_payment'] or 0)
        user['total_waste_recycled'] = float(user['total_waste_recycled']) + float(pickup['actual_weight_kg'] or 0)
        
        # Update agent stats
        if pickup['agent_id']:
            agent = agents_db[pickup['agent_id']]
            earnings = float(pickup['actual_payment'] or 0) * 0.8  # 80% to agent
            agent['wallet_balance'] = float(agent['wallet_balance']) + earnings
            agent['total_earnings'] = float(agent['total_earnings']) + earnings
            agent['total_pickups_completed'] += 1
    
    return {"message": "Status updated", "pickup": pickup}


@app.post("/api/pickups/{pickup_id}/rate", tags=["Pickups"])
async def rate_pickup(pickup_id: int, rating: PickupRating, user_id: int):
    """
    Rate a completed pickup
    """
    if pickup_id not in pickups_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pickup not found"
        )
    
    pickup = pickups_db[pickup_id]
    
    if pickup['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    pickup['user_rating'] = rating.rating
    pickup['user_feedback'] = rating.feedback
    
    # Update agent rating
    if pickup['agent_id']:
        agent = agents_db[pickup['agent_id']]
        total_ratings = agent['total_ratings']
        current_rating = float(agent['rating'])
        
        new_rating = ((current_rating * total_ratings) + rating.rating) / (total_ratings + 1)
        agent['rating'] = round(new_rating, 2)
        agent['total_ratings'] += 1
    
    return {"message": "Rating submitted"}


# ==================== Environmental Impact Endpoint ====================

@app.get("/api/impact/{user_id}", response_model=EnvironmentalImpact, tags=["Analytics"])
async def get_environmental_impact(user_id: int):
    """
    Calculate user's environmental impact
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_pickups = [
        p for p in pickups_db.values() 
        if p['user_id'] == user_id and p['status'] == 'completed'
    ]
    
    waste_records = [
        {
            'category': p['waste_category'].value,
            'weight_kg': float(p['actual_weight_kg'] or 0)
        }
        for p in user_pickups
    ]
    
    impact = waste_classifier.calculate_environmental_impact(waste_records)
    
    return EnvironmentalImpact(**impact)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
