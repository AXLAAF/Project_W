"""
Enhanced API metadata and OpenAPI configuration for SIGAIA.
"""
from typing import Dict, Any

# API Tags metadata for OpenAPI documentation
TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Autenticación y autorización de usuarios. Registro, login y gestión de sesiones.",
    },
    {
        "name": "users",
        "description": "Gestión de perfiles de usuario y configuración de cuenta.",
    },
    {
        "name": "Planning",
        "description": "Planificación académica. Gestión de materias, grupos y inscripciones.",
    },
    {
        "name": "Risk",
        "description": "Evaluación de riesgo académico usando modelos de Inteligencia Artificial.",
    },
    {
        "name": "Companies",
        "description": "Gestión de empresas para prácticas profesionales.",
    },
    {
        "name": "Positions",
        "description": "Plazas de prácticas profesionales ofrecidas por empresas.",
    },
    {
        "name": "Applications",
        "description": "Solicitudes de estudiantes a plazas de prácticas.",
    },
    {
        "name": "Internships",
        "description": "Prácticas profesionales activas y reportes mensuales.",
    },
    {
        "name": "Resources",
        "description": "Catálogo de recursos reservables: salas, laboratorios, equipos.",
    },
    {
        "name": "Reservations",
        "description": "Reservación de recursos con detección de conflictos y check-in/out.",
    },
    {
        "name": "health",
        "description": "Endpoints de estado del sistema y health checks.",
    },
]


def get_openapi_config() -> Dict[str, Any]:
    """Get OpenAPI configuration for the application."""
    return {
        "title": "SIGAIA API",
        "description": """
## Sistema de Gestión Académica Integral con IA

SIGAIA es una plataforma integral para la gestión académica universitaria que incluye:

### Módulos Disponibles

- **Autenticación**: Registro, login y gestión de sesiones
- **Planificación Académica**: Materias, grupos e inscripciones
- **Riesgo Académico**: Evaluación con IA del riesgo de deserción
- **Prácticas Profesionales**: Empresas, plazas y seguimiento
- **Reservación de Recursos**: Salas, laboratorios y equipos

### Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación. 

1. Obtén un token mediante `/api/v1/auth/login`
2. Incluye el token en el header: `Authorization: Bearer <token>`

### Límites de Uso

- Rate limiting: 100 requests/minuto por usuario
- Máximo payload: 10MB

### Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 201 | Recurso creado |
| 400 | Error de validación |
| 401 | No autenticado |
| 403 | No autorizado |
| 404 | No encontrado |
| 409 | Conflicto (ej. reservación) |
| 500 | Error interno |
        """,
        "version": "1.0.0",
        "contact": {
            "name": "Equipo SIGAIA",
            "email": "soporte@sigaia.edu.mx",
        },
        "license_info": {
            "name": "Uso Educativo",
        },
        "openapi_tags": TAGS_METADATA,
    }


# API version prefix
API_V1_PREFIX = "/api/v1"

# Security scheme for OpenAPI
SECURITY_SCHEMES = {
    "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Ingresa tu token JWT",
    }
}
