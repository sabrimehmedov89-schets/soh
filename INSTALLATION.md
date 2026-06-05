# EV SOH Platform - Installation Guide

## Prerequisites

- Docker & Docker Compose (v1.29+)
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 14+ (for local development)
- Git

## Quick Start with Docker Compose

### 1. Clone Repository

```bash
git clone https://github.com/sabrimehmedov89-schets/soh.git
cd soh
```

### 2. Environment Configuration

Copy example environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Update `backend/.env`:

```env
# Database
DATABASE_URL=postgresql://ev_user:ev_password@postgres:5432/ev_soh_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# S3 (Optional - for PDF storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=your-bucket
```

Update `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=EV SOH Platform
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Load sample data (optional)
docker-compose exec backend python -m app.scripts.load_sample_data
```

### 5. Access Applications

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432 (user: ev_user, password: ev_password)

## Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Configure database
export DATABASE_URL="postgresql://localhost:5432/ev_soh_db"

# Run migrations
alembic upgrade head

# Start development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Database Setup

### PostgreSQL Installation

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### Create Database

```bash
sudo -u postgres psql

CREATE USER ev_user WITH PASSWORD 'ev_password';
CREATE DATABASE ev_soh_db OWNER ev_user;
ALTER ROLE ev_user SET client_encoding TO 'utf8';
ALTER ROLE ev_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ev_user SET default_transaction_deferrable TO on;
ALTER ROLE ev_user SET default_time_zone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ev_soh_db TO ev_user;
\q
```

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

## Production Deployment

### Prerequisites
- Server with Ubuntu 22.04 LTS
- 4GB+ RAM
- 20GB+ storage
- SSL certificate

### Deployment Steps

1. **Build Docker Images**
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Configure Production Environment**
   - Update `.env` with production values
   - Set `ENVIRONMENT=production`
   - Use strong `SECRET_KEY`
   - Configure HTTPS

3. **Deploy Services**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Setup Monitoring**
   - Configure health checks
   - Setup log aggregation
   - Monitor resource usage

5. **Backup Strategy**
   - Daily database backups
   - S3/Cloud storage for backups
   - Test restore procedures

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Verify PostgreSQL is running
psql -U ev_user -d ev_soh_db -h localhost

# Check database URL
echo $DATABASE_URL
```

### Migration Issues

```bash
# Check migration status
alembic current
alembic history

# Rollback migration
alembic downgrade -1
```

### Docker Issues

```bash
# Rebuild images
docker-compose up -d --build

# View logs
docker-compose logs -f service_name

# Clean up
docker-compose down -v
docker system prune -a
```

## Support

For issues, check:
1. Docker logs: `docker-compose logs`
2. Application logs in `/var/log/`
3. Database logs in PostgreSQL
4. GitHub Issues
