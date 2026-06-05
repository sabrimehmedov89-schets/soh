# EV SOH Platform - Electric Vehicle Battery State of Health Diagnostics

A production-ready multi-tenant SaaS platform for Electric Vehicle Battery State of Health (SOH) diagnostics and certification.

## Features

### Core Capabilities
- **Multi-tenant Architecture**: Secure customer isolation with role-based access control
- **Battery SOH Monitoring**: Real-time State of Health, State of Charge, and cycle count tracking
- **Comprehensive Diagnostics**: Temperature monitoring, internal resistance analysis, cell balancing detection
- **Alert System**: Automated alerts for critical battery conditions
- **PDF Reports**: Battery Health Certificates with QR verification codes
- **Data Integration**: OBD-II, CAN Bus, CSV Import, and REST API support
- **Dashboard Analytics**: Historical trends, fleet statistics, and critical alerts

### User Roles
1. **Platform Admin** - System-wide management and analytics
2. **Dealer** - Customer and fleet management
3. **Fleet Manager** - Vehicle and battery monitoring
4. **Read-Only User** - Dashboard access without modifications

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with TypeScript
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT + Refresh Tokens
- **Charts**: Plotly
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger/OpenAPI

## Project Structure

```
ev-soh-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── routes/
│   │   ├── utils/
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .gitignore
└── INSTALLATION.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Installation

See [INSTALLATION.md](./INSTALLATION.md) for detailed setup instructions.

```bash
# Clone repository
git clone https://github.com/yourusername/ev-soh-platform.git
cd ev-soh-platform

# Start services
docker-compose up -d

# Access applications
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

## API Documentation

API documentation is available at `http://localhost:8000/docs` (Swagger UI).

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

**Vehicles**
- `GET /api/v1/vehicles` - List vehicles
- `POST /api/v1/vehicles` - Create vehicle
- `GET /api/v1/vehicles/{id}` - Get vehicle details
- `PUT /api/v1/vehicles/{id}` - Update vehicle

**Battery Management**
- `GET /api/v1/batteries/{vehicle_id}` - Get battery info
- `POST /api/v1/measurements` - Record measurement
- `GET /api/v1/soh/{vehicle_id}` - Get SOH data

**Reports & Alerts**
- `GET /api/v1/reports/{vehicle_id}` - Get reports
- `POST /api/v1/reports/{vehicle_id}/generate` - Generate PDF report
- `GET /api/v1/alerts` - List alerts

## Database Schema

Key tables:
- `customers` - Tenant information
- `users` - User accounts with roles
- `vehicles` - EV details (VIN, brand, model, year)
- `battery_packs` - Battery specifications
- `measurements` - Raw measurement data
- `soh_records` - Calculated SOH values
- `alerts` - System alerts
- `reports` - Generated reports
- `audit_logs` - System audit trail

## Security Features

- JWT-based authentication with refresh tokens
- Multi-tenant data isolation
- Role-based access control (RBAC)
- Rate limiting on API endpoints
- Input validation and sanitization
- HTTPS in production
- Audit logging for compliance
- Password hashing with bcrypt

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Deployment

See deployment guides in the respective service directories for production deployment instructions.

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please use the GitHub Issues page.
