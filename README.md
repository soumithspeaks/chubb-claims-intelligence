# Enterprise Waste Management Platform

A comprehensive, AI-powered waste management ecosystem connecting users with waste collection agents, featuring intelligent waste classification, real-time tracking, and incentivized recycling programs.

## 🌟 Features

- **AI-Powered Waste Classification**
  - Deep learning-based waste type identification (8+ categories)
  - Multi-image upload support with confidence scoring
  - Real-time classification with visual feedback
  - Support for organic, plastic, paper, metal, glass, e-waste, and hazardous materials

- **Smart Pickup Management**
  - Uber-style instant pickup requests
  - Intelligent agent matching algorithm
  - Real-time location tracking
  - Scheduled and recurring pickups
  - OTP/QR code verification system

- **Dual Mobile Applications**
  - User App: Waste disposal with payment incentives
  - Agent App: Pickup management and earnings tracking
  - Real-time communication between users and agents
  - Interactive map integration

- **Incentivized Recycling**
  - Dynamic pricing based on waste type and weight
  - Digital wallet system
  - Payment processing and automated payouts
  - Gamification with achievements and rewards

- **Analytics & Environmental Impact**
  - Total waste recycled tracking
  - Carbon footprint reduction metrics
  - Recycling unit coordination
  - Performance analytics for agents and users

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for web interface)
- Git
- PostgreSQL or MongoDB (for production)

### Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/soumithspeaks/chubb-claims-intelligence.git
   cd chubb-claims-intelligence
   ```

2. Set up backend services:
   ```bash
   pip install -r requirements.txt
   python -m app.api.main
   ```

3. Set up frontend (User/Agent portal):
   ```bash
   cd chubb-claims-intelligence
   npm install
   npm run dev
   ```

### Development Setup

For backend development:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Test specific modules:
```bash
pytest tests/test_waste_classifier.py
pytest tests/test_api.py
```

## 🚀 API Documentation

Once the server is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints:

**User Operations:**
- `POST /api/users/register` - User registration
- `POST /api/users/login` - Authentication
- `GET /api/users/profile` - Get user profile
- `GET /api/users/wallet` - Wallet balance

**Waste Classification:**
- `POST /api/classify` - Upload and classify waste images
- `GET /api/waste-types` - List all waste categories

**Pickup Requests:**
- `POST /api/pickups/request` - Create pickup request
- `GET /api/pickups/{id}` - Get pickup details
- `GET /api/pickups/history` - User pickup history
- `PATCH /api/pickups/{id}/cancel` - Cancel pickup

**Agent Operations:**
- `POST /api/agents/register` - Agent registration
- `PATCH /api/agents/availability` - Toggle online/offline
- `GET /api/agents/requests` - View available requests
- `POST /api/agents/accept/{id}` - Accept pickup request
- `PATCH /api/agents/complete/{id}` - Complete pickup

**Real-time:**
- `WS /ws/tracking/{pickup_id}` - Live location tracking
- `WS /ws/notifications/{user_id}` - Push notifications

## 🌍 Environmental Impact

The platform tracks and reports:
- Total waste diverted from landfills
- CO2 emissions prevented
- Water saved through recycling
- Energy conservation metrics
- Trees equivalent saved

## 📱 Mobile App Features

### User App:
- 📸 Camera-based waste classification
- 📍 GPS location & address management
- 💰 Wallet & earnings tracking
- 🗺️ Real-time agent tracking
- 📊 Environmental impact dashboard
- 🏆 Gamification & rewards

### Agent App:
- 📍 Live location sharing
- 📱 Incoming request notifications
- 🧭 Route optimization
- ✅ Pickup verification (OTP/QR)
- 💵 Earnings tracker
- ⭐ Performance metrics

## 📦 Project Structure

```
├── app/
│   ├── api/
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── waste_management_api.py    # Waste management endpoints
│   │   └── auth.py                    # Authentication & authorization
│   ├── core/
│   │   ├── waste_classifier.py        # AI waste classification model
│   │   ├── matching_algorithm.py      # Agent matching logic
│   │   ├── payment_processor.py       # Payment calculations
│   │   └── geolocation.py            # Location services
│   ├── models/
│   │   ├── user.py                    # User data models
│   │   ├── agent.py                   # Agent data models
│   │   ├── pickup.py                  # Pickup request models
│   │   └── waste_type.py              # Waste classification models
│   └── services/
│       ├── notification.py            # Push notifications
│       └── realtime.py                # WebSocket for live tracking
├── chubb-claims-intelligence/         # Next.js frontend
│   ├── app/
│   │   ├── user/                      # User app pages
│   │   ├── agent/                     # Agent app pages
│   │   └── api/                       # Frontend API routes
│   └── components/
│       ├── waste-classifier/          # Waste upload & classification UI
│       ├── map/                       # Map components
│       └── pickup/                    # Pickup request components
├── data/
│   └── waste_types.json               # Waste category definitions
├── models/
│   └── waste_classifier/              # Trained ML models
├── tests/
│   ├── test_api.py
│   └── test_classifier.py
└── README.md
```

## 🛠 Technologies Used

**Backend:**
- **Framework**: FastAPI (REST API + WebSocket)
- **ML/AI**: PyTorch, TensorFlow Lite, MobileNet
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache**: Redis
- **Authentication**: JWT, OAuth2

**Frontend:**
- **Framework**: Next.js 15, React 19
- **UI Components**: Radix UI, shadcn/ui
- **Styling**: Tailwind CSS
- **Maps**: Google Maps API / Mapbox
- **Real-time**: Socket.io client

**Mobile (Future):**
- React Native / Flutter for native apps
- TensorFlow Lite for on-device classification

**Infrastructure:**
- **Deployment**: Docker, Kubernetes
- **Cloud**: AWS/GCP/Azure
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana

## 🎯 System Architecture

### Core Components:

1. **Waste Classification Engine**
   - Pre-trained CNN models (MobileNetV3, EfficientNet)
   - 8+ waste categories with 90%+ accuracy
   - Real-time inference under 200ms

2. **Agent Matching Algorithm**
   - Proximity-based matching
   - Load balancing across agents
   - Fair distribution with performance weighting
   - ETA calculation with traffic data

3. **Payment System**
   - Dynamic pricing per waste type
   - Wallet management
   - Transaction processing
   - Automated agent payouts

4. **Real-time Tracking**
   - WebSocket connections
   - Live location updates
   - Push notifications
   - In-app messaging

## 📊 Waste Categories & Pricing

| Category | Subcategories | Price per kg | Examples |
|----------|---------------|--------------|----------|
| Plastic | PET, HDPE, PVC, LDPE, PP, PS | $0.20-0.50 | Bottles, containers, bags |
| Paper | Cardboard, newspaper, office paper | $0.10-0.30 | Boxes, documents, magazines |
| Metal | Aluminum, steel, copper | $0.80-2.00 | Cans, wires, appliances |
| Glass | Clear, colored, broken | $0.05-0.15 | Bottles, jars, windows |
| E-waste | Electronics, batteries, bulbs | $1.00-5.00 | Phones, computers, TVs |
| Organic | Food waste, garden waste | $0.02-0.05 | Compostable materials |

## 🔐 Security & Compliance

- End-to-end encryption for sensitive data
- PCI-DSS compliance for payment processing
- GDPR/CCPA compliance for user data
- Agent background verification
- Multi-factor authentication
- Rate limiting and DDoS protection

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- TensorFlow and PyTorch communities
- Open-source waste classification datasets
- Environmental organizations promoting recycling
- All contributors to sustainable waste management

## 📞 Support

For support and questions:
- Create an issue in this repository
- Contact: support@wastemanagement.platform
- Documentation: [docs.wastemanagement.platform](https://docs.wastemanagement.platform)

---

**Building a sustainable future, one pickup at a time.** ♻️🌍
