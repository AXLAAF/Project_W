# Guía de Despliegue - SIGAIA

## Requisitos

- Docker y Docker Compose
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (para frontend)
- Python 3.11+

## Configuración de Entorno

### Variables de Entorno (Backend)

```env
# Aplicación
APP_NAME=SIGAIA
APP_ENV=production
DEBUG=false
SECRET_KEY=<tu-clave-secreta>

# Base de datos
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sigaia

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=<tu-jwt-secret>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=https://sigaia.universidad.edu
```

### Variables de Entorno (Frontend)

```env
VITE_API_URL=https://api.sigaia.universidad.edu/api/v1
```

## Despliegue con Docker

### 1. Construir imágenes

```bash
# Backend
cd backend
docker build -t sigaia-api:latest .

# Frontend
cd frontend
docker build -t sigaia-web:latest .
```

### 2. Iniciar servicios

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Ejecutar migraciones

```bash
docker exec sigaia-api alembic upgrade head
```

## Despliegue Manual

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend
npm install
npm run build
# Servir con nginx o similar
```

## Health Checks

- **Backend**: `GET /health`
- **Base de datos**: Verificar conexión PostgreSQL
- **Redis**: Verificar conexión Redis

## Monitoreo

### Logs

```bash
# Ver logs del API
docker logs -f sigaia-api

# Ver logs de base de datos
docker logs -f sigaia-db
```

### Métricas

El endpoint `/health` retorna:
```json
{
  "status": "healthy",
  "service": "SIGAIA"
}
```

## Backup

### Base de datos

```bash
pg_dump -h localhost -U user sigaia > backup_$(date +%Y%m%d).sql
```

### Restaurar

```bash
psql -h localhost -U user sigaia < backup_20260206.sql
```

## Troubleshooting

| Problema | Solución |
|----------|----------|
| Error de conexión DB | Verificar DATABASE_URL y estado de PostgreSQL |
| JWT inválido | Regenerar JWT_SECRET_KEY y limpiar cache |
| CORS bloqueado | Agregar dominio a CORS_ORIGINS |
| 502 Bad Gateway | Verificar que uvicorn está corriendo |

---

*Documentación de despliegue SIGAIA v1.0*
