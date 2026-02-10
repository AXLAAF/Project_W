# SIGAIA Backend

Backend API for the SIGAIA Academic Management System.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL + pgvector
- Redis

## Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run server
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit http://localhost:8000/docs for Swagger UI.
