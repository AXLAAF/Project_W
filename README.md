# SIGAIA - Sistema de Gestión Académica Integral con IA

Sistema web modular para centralizar procesos académicos universitarios con capacidades de Inteligencia Artificial.

## 🚀 Características

- **Núcleo**: Autenticación JWT, gestión de usuarios y roles, auditoría
- **Planeación de Materias**: Catálogo, historial, simulación, recomendaciones con IA
- **Riesgo Académico**: Índice de riesgo, dashboards, alertas tempranas
- **Búsqueda Semántica**: Embeddings y búsqueda vectorial de documentos
- **Prácticas Profesionales**: Flujo completo de gestión empresa-alumno
- **Reservas de Recursos**: Calendario, validación de conflictos, notificaciones

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Frontend | React 18 + TypeScript + TailwindCSS |
| Backend | Python 3.11 + FastAPI + SQLAlchemy 2.0 |
| Base de datos | PostgreSQL 16 + pgvector |
| Cache | Redis |
| ML | scikit-learn + sentence-transformers |
| Contenedores | Docker + docker-compose |

## 📋 Requisitos

- Docker y Docker Compose
- Node.js 20+ (para desarrollo frontend)
- Python 3.11+ (para desarrollo backend)

## 🏃 Inicio Rápido

### Con Docker (recomendado)

```bash
# Clonar repositorio
git clone <repo-url>
cd Project_W

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

Acceder a:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Desarrollo Local

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -e ".[dev]"

# Copiar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Copiar variables de entorno
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

## 📁 Estructura del Proyecto

```
Project_W/
├── backend/
│   ├── app/
│   │   ├── core/          # Módulo núcleo (auth, users)
│   │   ├── planning/      # Planeación de materias
│   │   ├── risk/          # Riesgo académico
│   │   ├── search/        # Búsqueda semántica
│   │   ├── internships/   # Prácticas profesionales
│   │   ├── reservations/  # Reservas de recursos
│   │   └── shared/        # Utilidades compartidas
│   ├── alembic/           # Migraciones de BD
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/           # Clientes API
│   │   ├── components/    # Componentes reutilizables
│   │   ├── features/      # Módulos por funcionalidad
│   │   └── store/         # Estado global (Zustand)
│   └── tests/
└── docker-compose.yml
```

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test
```

## 📝 Licencia

MIT

## 👥 Equipo

SIGAIA Team
