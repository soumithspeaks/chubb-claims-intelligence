"""
Data models for waste management platform
Using Pydantic for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    ADMIN = "admin"


class PickupStatus(str, Enum):
    PENDING = "pending"
    AGENT_ASSIGNED = "agent_assigned"
    AGENT_EN_ROUTE = "agent_en_route"
    AGENT_ARRIVED = "agent_arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WasteCategory(str, Enum):
    PLASTIC = "Plastic"
    PAPER = "Paper"
    METAL = "Metal"
    GLASS = "Glass"
    EWASTE = "E-waste"
    ORGANIC = "Organic"
    HAZARDOUS = "Hazardous"
    TEXTILES = "Textiles"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    id: int
    profile_image_url: Optional[str] = None
    wallet_balance: Decimal = Field(default=0.00, decimal_places=2)
    total_waste_recycled: Decimal = Field(default=0.00, decimal_places=2)
    carbon_footprint_saved: Decimal = Field(default=0.00, decimal_places=2)
    created_at: datetime
    is_active: bool = True
    email_verified: bool = False
    phone_verified: bool = False

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Address Models
class AddressBase(BaseModel):
    label: str = Field(..., max_length=50)  # 'Home', 'Work', 'Other'
    address_line1: str = Field(..., max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    country: str = Field(..., max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AddressCreate(AddressBase):
    is_default: bool = False


class AddressResponse(AddressBase):
    id: int
    user_id: int
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Agent Models
class AgentBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=255)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    vehicle_number: Optional[str] = Field(None, max_length=50)
    license_number: Optional[str] = Field(None, max_length=50)


class AgentCreate(AgentBase):
    password: str = Field(..., min_length=8, max_length=100)


class AgentResponse(AgentBase):
    id: int
    profile_image_url: Optional[str] = None
    wallet_balance: Decimal = Field(default=0.00, decimal_places=2)
    total_earnings: Decimal = Field(default=0.00, decimal_places=2)
    total_pickups_completed: int = 0
    rating: Decimal = Field(default=0.00, decimal_places=2)
    total_ratings: int = 0
    is_online: bool = False
    is_verified: bool = False
    is_active: bool = True
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    last_location_update: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AgentLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AgentAvailabilityUpdate(BaseModel):
    is_online: bool


# Waste Classification Models
class WasteClassificationRequest(BaseModel):
    image_urls: List[str] = Field(..., min_items=1, max_items=5)


class WasteClassificationResult(BaseModel):
    category: WasteCategory
    subcategory: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    estimated_weight_kg: Optional[Decimal] = None
    estimated_payment: Optional[Decimal] = None


# Pickup Request Models
class PickupRequestBase(BaseModel):
    waste_category: WasteCategory
    waste_subcategory: Optional[str] = None
    estimated_weight_kg: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    pickup_address: str = Field(..., max_length=500)
    pickup_latitude: float = Field(..., ge=-90, le=90)
    pickup_longitude: float = Field(..., ge=-180, le=180)
    scheduled_for: Optional[datetime] = None
    is_immediate: bool = True


class PickupRequestCreate(PickupRequestBase):
    waste_images_urls: List[str] = Field(default=[], max_items=5)
    classification_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class PickupRequestResponse(PickupRequestBase):
    id: int
    user_id: int
    agent_id: Optional[int] = None
    godown_id: Optional[int] = None
    status: PickupStatus
    actual_weight_kg: Optional[Decimal] = None
    estimated_payment: Optional[Decimal] = None
    actual_payment: Optional[Decimal] = None
    otp_code: Optional[str] = None
    requested_at: datetime
    agent_accepted_at: Optional[datetime] = None
    agent_arrived_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = None
    agent_rating: Optional[int] = Field(None, ge=1, le=5)
    agent_feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PickupStatusUpdate(BaseModel):
    status: PickupStatus
    actual_weight_kg: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    notes: Optional[str] = None


class PickupRating(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=500)


# Transaction Models
class TransactionType(str, Enum):
    PICKUP_PAYMENT = "pickup_payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    COMMISSION = "commission"


class TransactionResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    pickup_request_id: Optional[int] = None
    transaction_type: TransactionType
    amount: Decimal = Field(..., decimal_places=2)
    balance_before: Decimal = Field(..., decimal_places=2)
    balance_after: Decimal = Field(..., decimal_places=2)
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_status: str = "pending"
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Notification Models
class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    related_pickup_id: Optional[int] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard/Analytics Models
class UserDashboard(BaseModel):
    wallet_balance: Decimal
    total_waste_recycled: Decimal
    carbon_footprint_saved: Decimal
    total_pickups: int
    pending_pickups: int
    completed_pickups: int
    total_earnings: Decimal
    recent_pickups: List[PickupRequestResponse]


class AgentDashboard(BaseModel):
    wallet_balance: Decimal
    total_earnings: Decimal
    total_pickups_completed: int
    rating: Decimal
    total_ratings: int
    today_earnings: Decimal
    today_pickups: int
    pending_requests: int
    active_pickup: Optional[PickupRequestResponse] = None


# Environmental Impact Models
class EnvironmentalImpact(BaseModel):
    total_waste_kg: Decimal
    co2_saved_kg: Decimal
    trees_saved: Decimal
    energy_saved_kwh: Decimal
    water_saved_liters: Decimal


# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: UserRole


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
