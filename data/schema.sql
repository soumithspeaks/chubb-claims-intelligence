"""
Database schema for waste management platform
This file defines the SQL schema for PostgreSQL database
"""

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    profile_image_url VARCHAR(500),
    wallet_balance DECIMAL(10, 2) DEFAULT 0.00,
    total_waste_recycled DECIMAL(10, 2) DEFAULT 0.00,
    carbon_footprint_saved DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE
);

-- User addresses
CREATE TABLE IF NOT EXISTS user_addresses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    label VARCHAR(50),  -- 'Home', 'Work', 'Other'
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    profile_image_url VARCHAR(500),
    vehicle_type VARCHAR(50),  -- 'bike', 'van', 'truck'
    vehicle_number VARCHAR(50),
    license_number VARCHAR(50),
    wallet_balance DECIMAL(10, 2) DEFAULT 0.00,
    total_earnings DECIMAL(10, 2) DEFAULT 0.00,
    total_pickups_completed INTEGER DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    total_ratings INTEGER DEFAULT 0,
    is_online BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    last_location_update TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Godowns (collection centers)
CREATE TABLE IF NOT EXISTS godowns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    capacity_kg DECIMAL(10, 2) NOT NULL,
    current_load_kg DECIMAL(10, 2) DEFAULT 0.00,
    operating_hours VARCHAR(100),  -- e.g., "08:00-18:00"
    contact_phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pickup requests
CREATE TABLE IF NOT EXISTS pickup_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
    godown_id INTEGER REFERENCES godowns(id) ON DELETE SET NULL,
    
    -- Status: pending, agent_assigned, agent_en_route, agent_arrived, 
    --         in_progress, completed, cancelled
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    -- Waste details
    waste_category VARCHAR(50) NOT NULL,
    waste_subcategory VARCHAR(50),
    estimated_weight_kg DECIMAL(10, 2),
    actual_weight_kg DECIMAL(10, 2),
    classification_confidence DECIMAL(5, 4),  -- AI confidence score
    
    -- Location
    pickup_address VARCHAR(500) NOT NULL,
    pickup_latitude DECIMAL(10, 8) NOT NULL,
    pickup_longitude DECIMAL(11, 8) NOT NULL,
    
    -- Scheduling
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_for TIMESTAMP,
    is_immediate BOOLEAN DEFAULT TRUE,
    
    -- Payment
    estimated_payment DECIMAL(10, 2),
    actual_payment DECIMAL(10, 2),
    
    -- Verification
    otp_code VARCHAR(6),
    qr_code VARCHAR(100),
    
    -- Tracking
    agent_accepted_at TIMESTAMP,
    agent_arrived_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason VARCHAR(500),
    
    -- Images
    waste_images_urls TEXT[],  -- Array of image URLs
    
    -- Ratings
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    user_feedback TEXT,
    agent_rating INTEGER CHECK (agent_rating BETWEEN 1 AND 5),
    agent_feedback TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
    pickup_request_id INTEGER REFERENCES pickup_requests(id) ON DELETE SET NULL,
    
    transaction_type VARCHAR(50) NOT NULL,  -- 'pickup_payment', 'withdrawal', 'deposit', 'commission'
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    
    -- Payment details
    payment_method VARCHAR(50),  -- 'wallet', 'bank_transfer', 'upi'
    payment_reference VARCHAR(100),
    payment_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'completed', 'failed'
    
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent availability schedule
CREATE TABLE IF NOT EXISTS agent_schedules (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),  -- 0 = Sunday
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recycling units
CREATE TABLE IF NOT EXISTS recycling_units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    specialization TEXT[],  -- Array of waste types they handle
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Godown pickups by recycling units
CREATE TABLE IF NOT EXISTS recycling_collections (
    id SERIAL PRIMARY KEY,
    recycling_unit_id INTEGER REFERENCES recycling_units(id) ON DELETE SET NULL,
    godown_id INTEGER REFERENCES godowns(id) ON DELETE SET NULL,
    
    waste_category VARCHAR(50) NOT NULL,
    weight_kg DECIMAL(10, 2) NOT NULL,
    collection_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',  -- 'scheduled', 'completed', 'cancelled'
    
    vehicle_number VARCHAR(50),
    driver_name VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    
    notification_type VARCHAR(50) NOT NULL,  -- 'pickup_request', 'agent_assigned', 'pickup_completed', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    
    related_pickup_id INTEGER REFERENCES pickup_requests(id) ON DELETE SET NULL,
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User achievements/badges
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    achievement_type VARCHAR(50) NOT NULL,  -- 'first_pickup', 'eco_warrior', 'metal_master', etc.
    achievement_name VARCHAR(255) NOT NULL,
    achievement_description TEXT,
    icon_url VARCHAR(500),
    
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_agents_location ON agents(current_latitude, current_longitude);
CREATE INDEX IF NOT EXISTS idx_agents_online ON agents(is_online, is_active);
CREATE INDEX IF NOT EXISTS idx_pickup_requests_status ON pickup_requests(status);
CREATE INDEX IF NOT EXISTS idx_pickup_requests_user ON pickup_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_pickup_requests_agent ON pickup_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_pickup_requests_location ON pickup_requests(pickup_latitude, pickup_longitude);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_agent ON transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_agent ON notifications(agent_id, is_read);
