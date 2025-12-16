# Enterprise Video Intelligence & Safety Monitoring Platform

A production-grade video intelligence platform for industrial clients that ingests CCTV/video streams, detects safety and security events using Ultralytics YOLO11, and generates alerts, dashboards, and scheduled reports.

## Features

- **Video Ingestion**: RTSP/HTTP streams and file uploads
- **AI-Powered Detection**: YOLO11-based object detection, tracking, and event detection
- **Configurable Events**: 100+ event types (PPE violations, safety incidents, security events)
- **Real-Time Alerts**: Multi-channel notifications (Email, Webhook, In-App)
- **Enterprise Security**: JWT authentication, RBAC, audit logging
- **Scalable Architecture**: Distributed GPU workers, horizontal scaling
- **Event-Clip Storage**: Privacy-first design (stores only event clips, not full videos)

## Architecture

See [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) for detailed system architecture and design decisions.

## Tech Stack

### Frontend
- React 18+ with TypeScript
- Tailwind CSS
- ShadCN UI
- Framer Motion
- Recharts

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Pydantic

### ML/Inference
- PyTorch
- Ultralytics YOLO11
- OpenCV
- CUDA

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- CUDA-capable GPU (for workers)
- Windows 10/11 or Linux

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/adnanulhasanseecs/workplace-monitoring.git
cd workplace-monitoring
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
```

4. **Frontend Setup**
```bash
cd frontend
npm install
```

5. **Start Services**

Start PostgreSQL and Redis, then:

```bash
# Terminal 1: API Server
cd backend/app
uvicorn main:app --reload

# Terminal 2: Worker (requires GPU)
cd backend/worker
python main.py

# Terminal 3: Frontend
cd frontend
npm run dev
```

## Development

### Project Structure

```
workflow-monitoring/
├── frontend/          # React frontend
├── backend/
│   ├── app/          # FastAPI application
│   ├── worker/       # GPU inference runtime
│   ├── gateway/      # API Gateway
│   ├── domain/       # Business logic
│   ├── models/       # DB models & schemas
│   └── ...
├── config/           # Configuration files
└── infrastructure/   # Docker, deployment configs
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Configuration

- Event definitions: `config/events/*.yaml`
- System config: `.env`
- Database migrations: `backend/alembic/`

## Deployment

See `infrastructure/` for Docker and deployment configurations.

## Security

- All secrets via environment variables
- JWT-based authentication
- RBAC (Admin, Supervisor, Viewer)
- Audit logging for compliance
- Encryption at rest for event clips

## License

Proprietary - Enterprise License

## Support

For issues and questions, please contact the development team.

