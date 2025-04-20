# Development Guide

## Setup Development Environment

1. Install Python 3.9+
2. Install Docker and Docker Compose
3. Clone the repository
4. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in each service directory with:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Running Services

### Using Docker (Recommended)

Start all services:
```bash
docker-compose up -d
```

Stop all services:
```bash
docker-compose down
```

### Using Python (Development)

Run individual services:
```bash
cd services/user-service
uvicorn app.main:app --reload --port 8001
```

## Database Setup

Initialize the database:
```bash
python init_db.py
```

## Testing

Run all tests:
```bash
python test_services.py
```

## API Documentation

Each service provides Swagger UI documentation at the `/docs` endpoint:

- User Service: http://localhost:8001/docs
- Table Service: http://localhost:8002/docs
- Menu Service: http://localhost:8003/docs
- Order Service: http://localhost:8004/docs
- Kitchen Service: http://localhost:8005/docs
- Payment Service: http://localhost:8006/docs

## Code Structure

```
restaurant-api/
├── docs/                   # Documentation
├── services/              # Microservices
│   ├── user-service/     
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── table-service/
│   ├── menu-service/
│   ├── order-service/
│   ├── kitchen-service/
│   └── payment-service/
├── docker-compose.yml    # Docker configuration
├── requirements.txt      # Global dependencies
└── init_db.py           # Database initialization
```

## Best Practices

1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Write docstrings

2. **API Design**
   - Use RESTful principles
   - Version your APIs
   - Provide clear error messages

3. **Testing**
   - Write unit tests
   - Test API endpoints
   - Test error cases

4. **Security**
   - Validate input data
   - Use authentication
   - Handle errors gracefully

5. **Documentation**
   - Keep API docs updated
   - Document environment setup
   - Include example requests
