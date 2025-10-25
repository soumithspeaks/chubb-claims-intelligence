# Setup and Installation Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** (Node.js 20 recommended)
- **npm 10+** or **pnpm**
- **Git**
- **PostgreSQL 14+** (optional, for production database)

## Quick Setup (Development)

### 1. Clone the Repository

```bash
git clone https://github.com/soumithspeaks/chubb-claims-intelligence.git
cd chubb-claims-intelligence
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional dependencies for email validation
pip install email-validator

# Install testing dependencies (optional)
pip install pytest pytest-cov
```

#### Run Backend Server

```bash
# Method 1: Direct Python execution
cd app/api
python waste_management_api.py

# Method 2: Using uvicorn
uvicorn app.api.waste_management_api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd chubb-claims-intelligence

# Using npm (with legacy peer deps for compatibility)
npm install --legacy-peer-deps

# Or using pnpm
pnpm install
```

#### Run Development Server

```bash
npm run dev
# or
pnpm dev
```

The frontend will be available at:
- **Application**: http://localhost:3000

### 4. Verify Installation

#### Test Backend

```bash
# Run tests
pytest tests/test_waste_management.py -v

# Test API health
curl http://localhost:8000/health
```

#### Test Frontend

Open your browser and navigate to:
- Main page: http://localhost:3000
- User app: http://localhost:3000/user
- Agent app: http://localhost:3000/agent

## Production Setup

### Database Setup

1. **Install PostgreSQL**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

2. **Create Database**

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE waste_management;
CREATE USER waste_admin WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE waste_management TO waste_admin;
\q

# Run schema
psql -U waste_admin -d waste_management -f data/schema.sql
```

3. **Update Database Connection**

Create `.env` file in project root:

```env
DATABASE_URL=postgresql://waste_admin:your_secure_password@localhost:5432/waste_management
SECRET_KEY=generate-a-secure-random-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Environment Configuration

Create `.env` file with production settings:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/waste_management

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
MAPBOX_ACCESS_TOKEN=your-mapbox-token

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password

# Payment Gateway
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# AWS S3 (for image storage)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=waste-management-images
AWS_REGION=us-east-1

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Build for Production

#### Backend

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn app.api.waste_management_api:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Frontend

```bash
cd chubb-claims-intelligence

# Build for production
npm run build

# Start production server
npm start

# Or use PM2 for process management
npm install -g pm2
pm2 start npm --name "waste-frontend" -- start
```

## Docker Deployment

### Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: waste_management
      POSTGRES_USER: waste_admin
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./data/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://waste_admin:secure_password@postgres:5432/waste_management
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build:
      context: ./chubb-claims-intelligence
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Create `Dockerfile.backend`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

EXPOSE 8000

CMD ["gunicorn", "app.api.waste_management_api:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Deploy with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment

1. **EC2 for Backend**
   - Launch Ubuntu Server instance
   - Install Python, PostgreSQL
   - Deploy using systemd or PM2

2. **RDS for Database**
   - Create PostgreSQL RDS instance
   - Update DATABASE_URL

3. **S3 for Image Storage**
   - Create S3 bucket
   - Configure CORS
   - Update AWS credentials

4. **Elastic Beanstalk (Alternative)**
   - Package application
   - Deploy using EB CLI

### Google Cloud Platform

1. **Cloud Run for Backend**
   - Containerize application
   - Deploy to Cloud Run
   - Configure Cloud SQL

2. **Cloud Storage for Images**
   - Create storage bucket
   - Configure access

### Heroku Deployment

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create waste-management-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

## Monitoring and Logging

### Setup Logging

```python
# Add to backend (production)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('waste_management.log'),
        logging.StreamHandler()
    ]
)
```

### Setup Monitoring

```bash
# Install monitoring tools
pip install prometheus-client sentry-sdk

# Install APM
npm install @sentry/nextjs
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process
   # Linux/Mac:
   lsof -ti:8000 | xargs kill -9
   # Windows:
   netstat -ano | findstr :8000
   taskkill /PID <pid> /F
   ```

2. **Database Connection Failed**
   - Check PostgreSQL is running
   - Verify credentials
   - Check firewall settings

3. **Frontend Build Errors**
   ```bash
   # Clear cache
   rm -rf .next node_modules package-lock.json
   npm install --legacy-peer-deps
   npm run build
   ```

4. **Module Not Found (Python)**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

### Performance Optimization

1. **Backend Caching**
   - Install Redis
   - Implement caching for waste categories
   - Cache agent locations

2. **Frontend Optimization**
   - Enable Next.js image optimization
   - Implement code splitting
   - Use CDN for static assets

3. **Database Optimization**
   - Add indexes (already in schema.sql)
   - Use connection pooling
   - Implement query caching

## Development Tips

1. **Hot Reload**
   - Backend: Use `--reload` flag with uvicorn
   - Frontend: Automatic with `npm run dev`

2. **Debugging**
   - Backend: Use Python debugger (pdb)
   - Frontend: Use React DevTools

3. **Code Quality**
   ```bash
   # Python linting
   pip install black flake8
   black app/
   flake8 app/

   # JavaScript/TypeScript linting
   npm run lint
   ```

## Next Steps

1. Review [API_DOCS.md](./API_DOCS.md) for API endpoints
2. Check [README.md](./README.md) for feature overview
3. Explore the code in `app/` and `chubb-claims-intelligence/`
4. Run tests: `pytest tests/ -v`
5. Build your first feature!

## Support

Need help? Contact:
- GitHub Issues: https://github.com/soumithspeaks/chubb-claims-intelligence/issues
- Email: support@wastemanagement.platform
