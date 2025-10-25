# API Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: Configure your deployment URL

## Quick Start

### Running the Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the FastAPI server:
```bash
cd app/api
python waste_management_api.py
```

Or use uvicorn directly:
```bash
uvicorn app.api.waste_management_api:app --reload --host 0.0.0.0 --port 8000
```

3. Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Running the Frontend

1. Install Node.js dependencies:
```bash
cd chubb-claims-intelligence
npm install --legacy-peer-deps
```

2. Start the development server:
```bash
npm run dev
```

3. Open browser: http://localhost:3000

### Running Tests

```bash
pytest tests/test_waste_management.py -v
```

## API Endpoints

### Health & Status

#### `GET /`
Root endpoint showing API status.

**Response:**
```json
{
  "message": "Waste Management Platform API",
  "version": "1.0.0",
  "status": "operational"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-25T16:30:00.000Z"
}
```

### Waste Classification

#### `POST /api/classify`
Classify waste from uploaded images using AI.

**Request Body:**
```json
{
  "image_urls": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ]
}
```

**Response:**
```json
{
  "category": "Plastic",
  "subcategory": "PET",
  "confidence": 0.94,
  "estimated_weight_kg": 2.5,
  "estimated_payment": 1.25
}
```

#### `GET /api/waste-types`
Get all waste categories and subcategories with pricing.

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Plastic",
      "subcategories": [
        {
          "code": "PET",
          "name": "Polyethylene Terephthalate",
          "price_per_kg": 0.50
        }
      ],
      "color_code": "#FFA726",
      "icon": "♻️"
    }
  ]
}
```

### User Management

#### `POST /api/users/register`
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "phone": "1234567890",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "phone": "1234567890",
  "full_name": "John Doe",
  "wallet_balance": 0.00,
  "total_waste_recycled": 0.00,
  "carbon_footprint_saved": 0.00,
  "created_at": "2025-10-25T16:30:00.000Z",
  "is_active": true
}
```

#### `POST /api/users/login`
User login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "mock_token_1",
  "token_type": "bearer",
  "user_id": 1,
  "role": "user"
}
```

#### `GET /api/users/{user_id}`
Get user profile.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "wallet_balance": 127.50,
  "total_waste_recycled": 45.2,
  "carbon_footprint_saved": 113.0
}
```

#### `GET /api/users/{user_id}/dashboard`
Get user dashboard with statistics.

**Response:**
```json
{
  "wallet_balance": 127.50,
  "total_waste_recycled": 45.2,
  "carbon_footprint_saved": 113.0,
  "total_pickups": 23,
  "pending_pickups": 1,
  "completed_pickups": 22,
  "total_earnings": 127.50,
  "recent_pickups": []
}
```

### Agent Management

#### `POST /api/agents/register`
Register a new agent.

**Request Body:**
```json
{
  "email": "agent@example.com",
  "phone": "1234567890",
  "full_name": "Jane Smith",
  "vehicle_type": "van",
  "vehicle_number": "ABC123",
  "license_number": "DL123456",
  "password": "securepassword123"
}
```

#### `PATCH /api/agents/{agent_id}/availability`
Toggle agent online/offline status.

**Request Body:**
```json
{
  "is_online": true
}
```

#### `PATCH /api/agents/{agent_id}/location`
Update agent's current location.

**Request Body:**
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194
}
```

#### `GET /api/agents/{agent_id}/dashboard`
Get agent dashboard with earnings and statistics.

**Response:**
```json
{
  "wallet_balance": 342.50,
  "total_earnings": 342.50,
  "total_pickups_completed": 157,
  "rating": 4.8,
  "total_ratings": 145,
  "today_earnings": 85.20,
  "today_pickups": 12,
  "pending_requests": 3
}
```

### Pickup Requests

#### `POST /api/pickups/request`
Create a new pickup request.

**Query Parameters:**
- `user_id` (required): User ID creating the request

**Request Body:**
```json
{
  "waste_category": "Plastic",
  "waste_subcategory": "PET",
  "estimated_weight_kg": 2.5,
  "pickup_address": "123 Main St, City, State 12345",
  "pickup_latitude": 37.7749,
  "pickup_longitude": -122.4194,
  "is_immediate": true,
  "waste_images_urls": [
    "https://example.com/image1.jpg"
  ],
  "classification_confidence": 0.94
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "agent_id": null,
  "status": "pending",
  "waste_category": "Plastic",
  "estimated_weight_kg": 2.5,
  "estimated_payment": 1.25,
  "otp_code": "123456",
  "requested_at": "2025-10-25T16:30:00.000Z"
}
```

#### `GET /api/pickups/{pickup_id}`
Get pickup request details.

#### `PATCH /api/pickups/{pickup_id}/status`
Update pickup status (agent actions).

**Request Body:**
```json
{
  "status": "completed",
  "actual_weight_kg": 2.8,
  "notes": "Pickup completed successfully"
}
```

#### `POST /api/pickups/{pickup_id}/rate`
Rate a completed pickup.

**Query Parameters:**
- `user_id` (required): User ID submitting the rating

**Request Body:**
```json
{
  "rating": 5,
  "feedback": "Great service! Quick and professional."
}
```

### Analytics

#### `GET /api/impact/{user_id}`
Calculate user's environmental impact.

**Response:**
```json
{
  "total_waste_kg": 45.2,
  "co2_saved_kg": 113.0,
  "trees_saved": 0.77,
  "energy_saved_kwh": 180.8,
  "water_saved_liters": 2260.0
}
```

## Data Models

### Waste Categories
- **Plastic**: PET, HDPE, PVC, LDPE, PP, PS (${content}0.20-$0.50/kg)
- **Paper**: Cardboard, Newspaper, Office ($0.10-$0.30/kg)
- **Metal**: Aluminum, Steel, Copper ($0.80-$5.00/kg)
- **Glass**: Clear, Colored, Broken ($0.05-$0.15/kg)
- **E-waste**: Phones, Computers, Batteries ($1.00-$5.00/kg)
- **Organic**: Food waste, Garden waste ($0.02-$0.05/kg)
- **Hazardous**: Chemicals, Paint, Medical (Special handling)
- **Textiles**: Clothing, Fabric, Shoes ($0.10-$0.20/kg)

### Pickup Status Flow
1. `pending` - Pickup request created
2. `agent_assigned` - Agent accepted the request
3. `agent_en_route` - Agent is traveling to location
4. `agent_arrived` - Agent has arrived at pickup location
5. `in_progress` - Pickup is being collected
6. `completed` - Pickup completed successfully
7. `cancelled` - Pickup was cancelled

## Error Handling

All API endpoints return standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid input)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a `detail` field with the error message:

```json
{
  "detail": "User not found"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production:
- User endpoints: 100 requests/minute
- Agent endpoints: 200 requests/minute
- Classification endpoint: 50 requests/minute

## Authentication

Currently using mock authentication. In production, implement:
- JWT tokens
- OAuth2 with Password Flow
- Token expiration (24 hours)
- Refresh tokens

## WebSocket Support (Coming Soon)

Real-time features will use WebSocket connections:
- `WS /ws/tracking/{pickup_id}` - Live location tracking
- `WS /ws/notifications/{user_id}` - Push notifications

## Database

Current implementation uses in-memory storage. For production:

1. Install PostgreSQL
2. Create database using `data/schema.sql`
3. Update connection string in the API
4. Use SQLAlchemy ORM for database operations

```bash
psql -U postgres -d waste_management -f data/schema.sql
```

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:pass@localhost/waste_management
SECRET_KEY=your-secret-key-here
GOOGLE_MAPS_API_KEY=your-maps-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-password
```

## Production Deployment

### Backend (FastAPI)
```bash
gunicorn app.api.waste_management_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)
```bash
npm run build
npm start
```

### Docker
```bash
docker-compose up -d
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/soumithspeaks/chubb-claims-intelligence/issues
- Email: support@wastemanagement.platform
- Documentation: README.md
