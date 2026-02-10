# SIGAIA - Documentación Técnica Completa

**Sistema de Gestión Académica Integral con Inteligencia Artificial**

> Última actualización: Febrero 2026

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Requisitos del Sistema](#4-requisitos-del-sistema)
5. [Módulos Funcionales](#5-módulos-funcionales)
6. [Modelo de Datos](#6-modelo-de-datos)
7. [Diseño de API](#7-diseño-de-api)
8. [Estructura del Proyecto](#8-estructura-del-proyecto)
9. [Guía de Instalación](#9-guía-de-instalación)
10. [Guía de Desarrollo](#10-guía-de-desarrollo)
11. [Testing y Calidad](#11-testing-y-calidad)
12. [Despliegue](#12-despliegue)

---

## 1. Resumen Ejecutivo

### 1.1 Descripción General

SIGAIA es un sistema web modular diseñado para centralizar procesos académicos universitarios, integrando capacidades de **Inteligencia Artificial** para:

- **Recomendaciones inteligentes** de materias basadas en historial académico
- **Detección de riesgo académico** con alertas tempranas
- **Búsqueda semántica** de documentos usando embeddings

### 1.2 Contexto del Proyecto

| Aspecto | Detalle |
|---------|---------|
| **Usuarios objetivo** | Universidad mediana (5,000-15,000 alumnos) |
| **Equipo de desarrollo** | 1-3 desarrolladores |
| **Timeline MVP** | 4-6 meses |
| **Arquitectura** | Monolito modular (preparado para microservicios) |
| **Despliegue** | Docker en cualquier proveedor cloud |

### 1.3 Usuarios del Sistema

| Rol | Descripción |
|-----|-------------|
| **Alumno** | Consulta historial, planea materias, ve riesgo, busca material, aplica a prácticas |
| **Profesor** | Dashboard de riesgo de grupos, sube material, evalúa prácticas |
| **Coordinador Académico** | Gestión global de riesgo, reportes, aprobaciones |
| **Administrador de Recursos** | Gestiona catálogo de recursos, reservas, sanciones |
| **Gestor de Prácticas** | Valida empresas, asigna alumnos, libera residencias |
| **Administrador del Sistema** | Gestión total de usuarios, roles, configuración |

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Contexto (C4 - Nivel 1)

```mermaid
graph TB
    subgraph Usuarios
        A[Alumno]
        P[Profesor]
        C[Coordinador]
        AR[Admin Recursos]
        GP[Gestor Prácticas]
        AS[Admin Sistema]
    end
    
    S["SIGAIA<br/>Sistema de Gestión Académica"]
    
    A --> S
    P --> S
    C --> S
    AR --> S
    GP --> S
    AS --> S
    
    S --> E["Email Service<br/>SMTP/SendGrid"]
    S --> ST["Storage<br/>S3/MinIO"]
```

### 2.2 Diagrama de Contenedores (C4 - Nivel 2)

```mermaid
graph TB
    subgraph Frontend
        SPA["React SPA<br/>TailwindCSS"]
    end
    
    subgraph Backend
        API["FastAPI<br/>REST API"]
        ML["ML Service<br/>scikit-learn"]
        EMB["Embedding Service<br/>sentence-transformers"]
    end
    
    subgraph Data
        PG[("PostgreSQL<br/>+ pgvector")]
        REDIS[("Redis<br/>Cache/Sessions")]
    end
    
    subgraph External
        SMTP[Email Service]
        S3[Object Storage]
    end
    
    SPA --> API
    API --> PG
    API --> REDIS
    API --> ML
    API --> EMB
    API --> SMTP
    API --> S3
    ML --> PG
    EMB --> PG
```

### 2.3 Arquitectura en Capas (Backend)

```
┌─────────────────────────────────────────────────────────────┐
│                     ROUTERS (API Layer)                     │
│  auth.py │ users.py │ subjects.py │ risk.py │ search.py    │
├─────────────────────────────────────────────────────────────┤
│                    SERVICES (Business Logic)                │
│  AuthService │ UserService │ PlanningService │ RiskService  │
├─────────────────────────────────────────────────────────────┤
│                   REPOSITORIES (Data Access)                │
│  UserRepo │ SubjectRepo │ EnrollmentRepo │ DocumentRepo     │
├─────────────────────────────────────────────────────────────┤
│                     MODELS (ORM/Domain)                     │
│  User │ Subject │ Group │ Enrollment │ Document │ Resource  │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE                           │
│  Database │ Cache │ Storage │ Email │ ML Pipeline           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Stack Tecnológico

### 3.1 Backend

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| **Framework** | FastAPI | ≥0.109.0 | Async, tipado, ideal para IA, autodocs |
| **Lenguaje** | Python | 3.11+ | Ecosistema ML maduro |
| **ORM** | SQLAlchemy | 2.0+ | Async support, tipado |
| **Migraciones** | Alembic | ≥1.13.1 | Estándar con SQLAlchemy |
| **Validación** | Pydantic | ≥2.5.3 | Schemas tipados |
| **Auth** | python-jose | ≥3.3.0 | JWT tokens |
| **Passwords** | passlib[bcrypt] | ≥1.7.4 | Hash seguro |

### 3.2 Machine Learning

| Componente | Tecnología | Versión | Uso |
|------------|------------|---------|-----|
| **ML** | scikit-learn | ≥1.4.0 | Modelos clasificación/recomendación |
| **NLP** | sentence-transformers | ≥2.3.1 | Embeddings de texto |
| **Data** | pandas | ≥2.1.4 | Procesamiento de datos |
| **Vectores** | pgvector | ≥0.2.4 | Búsqueda vectorial en PostgreSQL |

### 3.3 Frontend

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| **Framework** | React | ^18.3.1 | Ecosistema maduro |
| **Lenguaje** | TypeScript | ~5.6.2 | Tipado estático |
| **Styling** | TailwindCSS | ^3.4.17 | Utility-first, responsive |
| **State** | Zustand | ^5.0.2 | Ligero, simple |
| **Data Fetching** | React Query | ^5.62.11 | Cache, refetch automático |
| **HTTP** | Axios | ^1.7.9 | Cliente HTTP |
| **Router** | react-router-dom | ^7.1.1 | Navegación SPA |
| **Build** | Vite | ^6.0.5 | Build rápido, HMR |
| **Icons** | lucide-react | ^0.468.0 | Iconos modernos |

### 3.4 Infraestructura

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Base de datos** | PostgreSQL + pgvector | 16 |
| **Cache/Sessions** | Redis | 7 |
| **Contenedores** | Docker + docker-compose | Latest |
| **Storage (dev)** | MinIO | Latest |
| **Storage (prod)** | AWS S3 o compatible | - |
| **Email (dev)** | MailHog | Latest |
| **Email (prod)** | SMTP/SendGrid | - |

### 3.5 Herramientas de Desarrollo

| Categoría | Herramienta |
|-----------|-------------|
| **Linting Python** | ruff (reemplaza flake8, isort, black) |
| **Linting TS** | ESLint + Prettier |
| **Tests Backend** | pytest + pytest-asyncio + httpx |
| **Tests Frontend** | Vitest + React Testing Library |
| **Type Check** | mypy (Python) / TypeScript |
| **CI/CD** | GitHub Actions |

---

## 4. Requisitos del Sistema

### 4.1 Requisitos Funcionales

#### Módulo Núcleo (Core)

| ID | Requisito | Prioridad |
|----|-----------|-----------| 
| RF-CORE-001 | Registro de usuarios con correo institucional | Alta |
| RF-CORE-002 | Autenticación JWT con expiración configurable | Alta |
| RF-CORE-003 | Roles: Alumno, Profesor, Coordinador, Admin Recursos, Gestor Prácticas, Admin Sistema | Alta |
| RF-CORE-004 | Perfil de usuario con nombre, matrícula, carrera, foto | Alta |
| RF-CORE-005 | Auditoría de login/logout, cambios de rol, modificaciones críticas | Media |
| RF-CORE-006 | Recuperación de contraseña por correo | Media |
| RF-CORE-007 | CRUD completo de usuarios para administrador | Alta |

#### Módulo Planeación de Materias

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-PLAN-001 | Historial académico: materias, calificaciones, créditos | Alta |
| RF-PLAN-002 | Catálogo de materias con prerrequisitos y créditos | Alta |
| RF-PLAN-003 | Grupos disponibles con horario, profesor, cupo | Alta |
| RF-PLAN-004 | Detección de choques de horario | Alta |
| RF-PLAN-005 | Simulación de inscripción ("carritos") | Media |
| RF-PLAN-006 | Recomendación por prerrequisitos cumplidos | Alta |
| RF-PLAN-007 | **[IA]** Recomendación de carga óptima según historial | Media |
| RF-PLAN-008 | **[IA]** Explicación del razonamiento de recomendaciones | Media |

#### Módulo Riesgo Académico

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-RISK-001 | Índice de riesgo por alumno (0-100) | Alta |
| RF-RISK-002 | Factores: asistencia, calificaciones, entregas, reprobaciones | Alta |
| RF-RISK-003 | Clasificación: Bajo (0-30), Medio (31-60), Alto (61-100) | Alta |
| RF-RISK-004 | Dashboard para profesores por grupo | Alta |
| RF-RISK-005 | Dashboard de coordinador con gráficas comparativas | Media |
| RF-RISK-006 | Vista de riesgo personal del alumno | Media |
| RF-RISK-007 | **[IA]** Factores principales del riesgo explicados | Media |

#### Módulo Búsqueda Semántica

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-SEARCH-001 | Upload de documentos PDF, PPT, DOC hasta 50MB | Alta |
| RF-SEARCH-002 | Indexación automática de contenido | Alta |
| RF-SEARCH-003 | Búsqueda con lenguaje natural | Alta |
| RF-SEARCH-004 | Filtros por materia, profesor, tipo | Media |
| RF-SEARCH-005 | Snippets relevantes en resultados | Media |
| RF-SEARCH-006 | Ordenamiento por relevancia semántica | Alta |

#### Módulo Prácticas/Residencias

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-PRAC-001 | Registro de empresas y publicación de plazas | Alta |
| RF-PRAC-002 | Plazas con descripción, requisitos, duración | Alta |
| RF-PRAC-003 | Búsqueda y filtro de plazas | Alta |
| RF-PRAC-004 | Aplicación con CV y documentos | Alta |
| RF-PRAC-005 | Aprobación/rechazo de aplicaciones | Alta |
| RF-PRAC-006 | Seguimiento: reportes, evaluación, liberación | Media |
| RF-PRAC-007 | Generación de PDFs oficiales | Media |
| RF-PRAC-008 | Validación de requisitos del alumno | Media |

#### Módulo Reservas de Recursos

| ID | Requisito | Prioridad |
|----|-----------|-----------|
| RF-RES-001 | Catálogo de salas, laboratorios, equipos | Alta |
| RF-RES-002 | Calendario visual de disponibilidad | Alta |
| RF-RES-003 | Creación de reservas por fecha/hora | Alta |
| RF-RES-004 | Validación de conflictos | Alta |
| RF-RES-005 | Reglas configurables de reserva | Media |
| RF-RES-006 | Notificaciones por email | Media |
| RF-RES-007 | Sistema de sanciones | Baja |

### 4.2 Requisitos No Funcionales

| ID | Categoría | Requisito |
|----|-----------|-----------|
| RNF-001 | Performance | Tiempo de respuesta <500ms para CRUD |
| RNF-002 | Performance | Búsqueda semántica <2s para 100k documentos |
| RNF-003 | Escalabilidad | 500 usuarios concurrentes en MVP |
| RNF-004 | Seguridad | Passwords con bcrypt (cost=12) |
| RNF-005 | Seguridad | HTTPS obligatorio en producción |
| RNF-006 | Seguridad | Rate limiting: 100 req/min por usuario |
| RNF-007 | Disponibilidad | Uptime objetivo: 99.5% |
| RNF-008 | Usabilidad | Diseño responsive (móvil, tablet, desktop) |
| RNF-009 | Mantenibilidad | Cobertura de tests >70% código crítico |
| RNF-010 | Portabilidad | Despliegue via Docker en cualquier cloud |

---

## 5. Módulos Funcionales

### 5.1 Módulo Núcleo (Core)

**Propósito:** Autenticación, autorización y gestión de usuarios.

**Componentes:**
- Registro y login con JWT
- Gestión de roles y permisos
- Perfiles de usuario
- Auditoría de acciones

**Estado:** ✅ Implementado

### 5.2 Módulo Planeación de Materias

**Propósito:** Gestión académica y simulación de inscripciones.

**Componentes:**
- Catálogo de materias
- Historial académico
- Grupos y horarios
- Detección de conflictos
- Recomendaciones con IA

**Estado:** ✅ Implementado (básico)

### 5.3 Módulo Riesgo Académico

**Propósito:** Detección temprana de alumnos en riesgo.

**Componentes:**
- Cálculo de índice de riesgo
- Dashboards por rol
- Alertas y sugerencias
- Modelo ML explicable

**Estado:** ✅ Implementado (básico)

### 5.4 Módulo Búsqueda Semántica

**Propósito:** Búsqueda inteligente de material académico.

**Componentes:**
- Upload de documentos
- Indexación con embeddings
- Búsqueda vectorial
- Filtros y snippets

**Estado:** ⏳ Planificado (Sprint 5)

### 5.5 Módulo Prácticas/Residencias

**Propósito:** Gestión del proceso de prácticas profesionales.

**Componentes:**
- Portal de empresas (CRUD, verificación)
- Catálogo de posiciones (modalidad, requisitos, capacidad)
- Aplicaciones de alumnos (workflow de aprobación)
- Prácticas activas (supervisores, reportes mensuales)
- Generación de reportes

**Estado:** ✅ Implementado

### 5.6 Módulo Reservas de Recursos

**Propósito:** Gestión de espacios y equipos reservables.

**Componentes:**
- Catálogo de recursos (salas, laboratorios, auditorios, equipos)
- Calendario de disponibilidad por recurso
- Sistema de reservas con detección de conflictos
- Check-in/check-out de reservaciones
- Sistema de reglas y sanciones
- Workflow de aprobación (configurable por recurso)

**Estado:** ✅ Implementado

---

## 6. Modelo de Datos

### 6.1 Diagrama Entidad-Relación

```mermaid
erDiagram
    User ||--o{ UserRole : has
    User ||--|| Profile : has
    User ||--o{ Enrollment : makes
    User ||--o{ AuditLog : generates
    User ||--o{ Reservation : makes
    User ||--o{ InternshipApplication : submits
    
    Role ||--o{ UserRole : assigned
    
    Subject ||--o{ Group : has
    Subject ||--o{ SubjectPrerequisite : requires
    Subject ||--o{ Enrollment : enrolled
    
    Group ||--o{ Schedule : has
    Group ||--|{ User : taught_by
    
    Document ||--o{ DocumentEmbedding : has
    Document }|--|| User : uploaded_by
    Document }|--o| Subject : belongs_to
    
    Resource ||--o{ Reservation : reserved
    
    Company ||--o{ InternshipPosition : offers
    InternshipPosition ||--o{ InternshipApplication : receives
    InternshipApplication ||--o{ InternshipReport : has
```

### 6.2 Tablas Principales

#### Core
```sql
users (id, email, password_hash, is_active, created_at, updated_at)
roles (id, name, description)
user_roles (user_id, role_id)
profiles (user_id, first_name, last_name, student_id, department, photo_url)
audit_logs (id, user_id, action, entity_type, entity_id, details_json, created_at)
```

#### Planeación
```sql
subjects (id, code, name, credits, description, department)
subject_prerequisites (subject_id, prerequisite_id)
academic_periods (id, name, start_date, end_date, is_current)
groups (id, subject_id, period_id, professor_id, capacity, enrolled_count)
schedules (id, group_id, day_of_week, start_time, end_time, classroom)
enrollments (id, user_id, group_id, status, grade, created_at)
```

#### Riesgo Académico
```sql
attendance_records (id, user_id, group_id, date, status)
partial_grades (id, user_id, group_id, partial_number, grade, weight)
risk_scores (id, user_id, period_id, score, classification, factors_json)
```

#### Búsqueda Semántica
```sql
documents (id, title, file_path, file_type, subject_id, uploaded_by)
document_chunks (id, document_id, chunk_index, content, embedding vector(384))
```

#### Prácticas/Residencias
```sql
companies (id, name, rfc, contact_email, contact_phone, address, description, website, logo_url, is_verified, is_active, created_at, updated_at)
internship_positions (id, company_id, title, description, requirements, benefits, duration_months, modality, location, min_gpa, min_credits, capacity, filled_count, is_active, created_at, updated_at)
internship_applications (id, user_id, position_id, status, cv_path, cover_letter, additional_documents, applied_at, reviewed_at, reviewer_id, reviewer_notes)
internships (id, application_id, start_date, expected_end_date, actual_end_date, status, supervisor_name, supervisor_email, supervisor_phone, total_hours, final_grade, completion_certificate_path, created_at, updated_at)
internship_reports (id, internship_id, month_number, report_date, file_path, hours_worked, activities_summary, achievements, challenges, supervisor_comments, supervisor_grade, status, submitted_at, reviewed_at, created_at, updated_at)
```

#### Reservas de Recursos
```sql
resources (id, name, code, description, resource_type, location, building, floor, capacity, features, status, is_active, image_url, min_reservation_minutes, max_reservation_minutes, advance_booking_days, requires_approval, responsible_user_id, created_at, updated_at)
reservations (id, resource_id, user_id, start_time, end_time, title, description, attendees_count, status, approved_by_id, approved_at, rejection_reason, checked_in_at, checked_out_at, is_recurring, recurrence_pattern, parent_reservation_id, notes, created_at, updated_at)
reservation_rules (id, resource_id, rule_type, name, description, day_of_week, start_time, end_time, start_date, end_date, max_reservations_per_day, max_reservations_per_week, max_hours_per_day, max_hours_per_week, priority, is_active, created_at, updated_at)
user_sanctions (id, user_id, reservation_id, sanction_type, reason, description, start_date, end_date, applied_by_id, is_resolved, resolved_at, resolved_by_id, resolution_notes, created_at)
```

---

## 7. Diseño de API

### 7.1 Autenticación

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Registro de usuario |
| POST | `/api/v1/auth/login` | Login, retorna JWT |
| POST | `/api/v1/auth/refresh` | Refresh token |
| POST | `/api/v1/auth/logout` | Invalidar refresh token |
| POST | `/api/v1/auth/forgot-password` | Solicitar reset |
| POST | `/api/v1/auth/reset-password` | Confirmar reset |

### 7.2 Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/users/me` | Perfil del usuario actual |
| PUT | `/api/v1/users/me` | Actualizar perfil propio |
| GET | `/api/v1/users` | Listar usuarios (admin) |
| GET | `/api/v1/users/{id}` | Detalle de usuario |
| PUT | `/api/v1/users/{id}` | Actualizar usuario (admin) |
| DELETE | `/api/v1/users/{id}` | Desactivar usuario |

### 7.3 Planeación

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/subjects` | Catálogo de materias |
| GET | `/api/v1/subjects/{id}/groups` | Grupos de una materia |
| GET | `/api/v1/academic-history` | Historial del alumno |
| GET | `/api/v1/planning/recommendations` | **[IA]** Materias recomendadas |
| POST | `/api/v1/planning/simulate` | Simular inscripción |
| GET | `/api/v1/planning/schedule-conflicts` | Detectar choques |

### 7.4 Riesgo Académico

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/risk/my-score` | Riesgo del alumno actual |
| GET | `/api/v1/risk/group/{group_id}` | Riesgo por grupo (profesor) |
| GET | `/api/v1/risk/department/{dept_id}` | Dashboard coordinador |
| GET | `/api/v1/risk/factors/{user_id}` | **[IA]** Factores de riesgo |

### 7.5 Prácticas/Residencias - Empresas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/companies` | Listar empresas |
| POST | `/api/v1/companies` | Registrar empresa |
| GET | `/api/v1/companies/{id}` | Detalle de empresa |
| PUT | `/api/v1/companies/{id}` | Actualizar empresa |
| PUT | `/api/v1/companies/{id}/verify` | Verificar empresa (admin) |

### 7.6 Prácticas/Residencias - Posiciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/internships/positions` | Listar posiciones |
| POST | `/api/v1/internships/positions` | Crear posición |
| GET | `/api/v1/internships/positions/{id}` | Detalle de posición |
| PUT | `/api/v1/internships/positions/{id}` | Actualizar posición |
| DELETE | `/api/v1/internships/positions/{id}` | Eliminar posición |

### 7.7 Prácticas/Residencias - Aplicaciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/internships/apply` | Aplicar a posición |
| GET | `/api/v1/internships/my-applications` | Mis aplicaciones |
| GET | `/api/v1/internships/applications` | Todas las aplicaciones (admin) |
| GET | `/api/v1/internships/applications/{id}` | Detalle de aplicación |
| PUT | `/api/v1/internships/applications/{id}/approve` | Aprobar aplicación |
| PUT | `/api/v1/internships/applications/{id}/reject` | Rechazar aplicación |
| DELETE | `/api/v1/internships/applications/{id}` | Cancelar aplicación |

### 7.8 Prácticas/Residencias - Prácticas Activas

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/internships/active` | Mi práctica activa |
| GET | `/api/v1/internships/my-internships` | Mis prácticas (historial) |
| GET | `/api/v1/internships` | Todas las prácticas (admin) |
| POST | `/api/v1/internships` | Crear práctica (desde aplicación aprobada) |
| GET | `/api/v1/internships/{id}` | Detalle de práctica |
| PUT | `/api/v1/internships/{id}/complete` | Completar práctica |

### 7.9 Prácticas/Residencias - Reportes Mensuales

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/internships/{id}/reports` | Listar reportes |
| POST | `/api/v1/internships/{id}/reports` | Crear reporte mensual |
| PUT | `/api/v1/internships/{id}/reports/{rid}/submit` | Enviar reporte |
| PUT | `/api/v1/internships/{id}/reports/{rid}/review` | Revisar reporte (supervisor) |

### 7.10 Reservas - Recursos

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/v1/resources` | Listar recursos con filtros |
| POST | `/api/v1/resources` | Crear recurso |
| GET | `/api/v1/resources/{id}` | Detalle de recurso |
| PUT | `/api/v1/resources/{id}` | Actualizar recurso |
| DELETE | `/api/v1/resources/{id}` | Eliminar recurso |
| GET | `/api/v1/resources/buildings` | Listar edificios (para filtros) |
| PUT | `/api/v1/resources/{id}/status` | Cambiar estado del recurso |

### 7.11 Reservas - Reservaciones

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/v1/reservations` | Crear reservación |
| GET | `/api/v1/reservations/my-reservations` | Mis reservaciones |
| GET | `/api/v1/reservations/calendar/{resource_id}` | Calendario de recurso |
| GET | `/api/v1/reservations/{id}` | Detalle de reservación |
| PUT | `/api/v1/reservations/{id}` | Actualizar reservación |
| DELETE | `/api/v1/reservations/{id}` | Cancelar reservación |
| POST | `/api/v1/reservations/{id}/approve` | Aprobar reservación |
| POST | `/api/v1/reservations/{id}/reject` | Rechazar reservación |
| POST | `/api/v1/reservations/{id}/check-in` | Check-in |
| POST | `/api/v1/reservations/{id}/check-out` | Check-out |

---

## 8. Estructura del Proyecto

### 8.1 Backend

```
backend/
├── alembic/                    # Migraciones de BD
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings (pydantic-settings)
│   ├── dependencies.py         # Inyección de dependencias
│   │
│   ├── core/                   # Módulo Núcleo
│   │   ├── models/             # User, Profile, Role, AuditLog
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # AuthService, UserService
│   │   └── routers/            # auth.py, users.py
│   │
│   ├── planning/               # Módulo Planeación
│   │   ├── models/             # Subject, Group, Enrollment
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── routers/            # subjects.py, groups.py, enrollments.py
│   │   └── ml/                 # Modelos ML recomendaciones
│   │
│   ├── risk/                   # Módulo Riesgo Académico
│   │   ├── models/             # RiskScore, AttendanceRecord
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/           # RiskService, RiskCalculator
│   │   └── routers/            # risk_router.py
│   │
│   ├── internships/            # Módulo Prácticas ✅ NUEVO
│   │   ├── models/             # Company, Position, Application, Internship, Report
│   │   ├── schemas/            # CRUD y validación
│   │   ├── repositories/       # CompanyRepo, PositionRepo, etc.
│   │   ├── services/           # Lógica de negocio y workflows
│   │   └── routers/            # companies.py, positions.py, applications.py, internships.py
│   │
│   └── shared/                 # Utilidades compartidas
│       ├── database.py
│       ├── security.py
│       └── pagination.py
│
├── tests/
│   ├── conftest.py             # Fixtures compartidos
│   ├── core/                   # Tests del módulo core
│   └── internships/            # Tests del módulo internships ✅ NUEVO
│       ├── test_companies.py
│       ├── test_positions.py
│       ├── test_applications.py
│       └── test_internships.py
│
├── Dockerfile
├── pyproject.toml
└── .env.example
```

### 8.2 Frontend

```
frontend/
├── src/
│   ├── main.tsx                # Entry point
│   ├── App.tsx                 # Root component + routing
│   ├── index.css               # TailwindCSS imports
│   │
│   ├── api/                    # Clientes API
│   │   ├── client.ts           # Axios instance
│   │   ├── auth.ts             # Autenticación
│   │   ├── planning.ts         # Planeación académica
│   │   ├── risk.ts             # Riesgo académico
│   │   └── internships.ts      # Prácticas ✅ NUEVO
│   │
│   ├── components/             # Componentes reutilizables
│   │   ├── ui/                 # Button, Input, Modal, Card, Badge
│   │   ├── layout/             # Navbar, Sidebar, Layout
│   │   └── shared/             # LoadingSpinner, etc.
│   │
│   ├── features/               # Módulos por feature
│   │   ├── auth/               # LoginPage, RegisterPage
│   │   ├── dashboard/          # DashboardPage
│   │   ├── planning/           # PlanningPage, HistoryPage
│   │   ├── risk/               # RiskPage
│   │   ├── profile/            # ProfilePage
│   │   └── internships/        # ✅ NUEVO
│   │       ├── InternshipsPage.tsx      # Catálogo de posiciones
│   │       ├── MyApplicationsPage.tsx   # Mis solicitudes
│   │       └── ActiveInternshipPage.tsx # Práctica activa
│   │
│   └── store/                  # Estado global (Zustand)
│       └── authStore.ts
│
├── Dockerfile
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

---

## 9. Guía de Instalación

### 9.1 Prerrequisitos

- **Docker** y **Docker Compose** (recomendado)
- **Node.js 20+** (desarrollo frontend)
- **Python 3.11+** (desarrollo backend)
- **PostgreSQL 16** (si no usa Docker)
- **Redis 7** (si no usa Docker)

### 9.2 Instalación con Docker (Recomendado)

```bash
# Clonar repositorio
git clone <repo-url>
cd Project_W

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

**URLs de acceso:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 9.3 Instalación Local (Desarrollo)

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -e ".[dev]"

# Copiar variables de entorno
cp .env.example .env
# Editar .env con configuración local

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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

### 9.4 Variables de Entorno

#### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sigaia_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_ENV=development
DEBUG=true
```

#### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 10. Guía de Desarrollo

### 10.1 Convenciones de Código

#### Python (Backend)
- **Linter:** ruff
- **Formato:** 100 caracteres por línea
- **Imports:** ordenados por ruff (isort)
- **Tipado:** mypy strict mode

#### TypeScript (Frontend)
- **Linter:** ESLint
- **Formato:** Prettier
- **Tipado:** strict mode

### 10.2 Estrategia de Ramas

```
main          ──────────────────────► (producción)
                 ↑         ↑
develop       ───┴─────────┴────────► (integración)
                 ↑    ↑    ↑
feature/*     ───┴────┴────┘          (desarrollo)
hotfix/*      ──────────────────────► (parches urgentes)
```

### 10.3 Versionado Semántico

```
MAJOR.MINOR.PATCH
  │     │     └── Corrección de bugs
  │     └──────── Nuevas funcionalidades (retrocompatibles)
  └────────────── Cambios breaking
```

### 10.4 Formato de Commits

```
<tipo>(<alcance>): <descripción>

Tipos: feat, fix, docs, style, refactor, test, chore
```

---

## 11. Testing y Calidad

### 11.1 Backend

```bash
cd backend

# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=app --cov-report=term-missing

# Solo un módulo
pytest tests/core/ -v
```

### 11.2 Frontend

```bash
cd frontend

# Ejecutar tests
npm test

# Con UI
npm run test:ui

# Con cobertura
npm run test:coverage
```

### 11.3 Linting

```bash
# Backend
cd backend
ruff check .
ruff format .
mypy app/

# Frontend
cd frontend
npm run lint
```

---

## 12. Despliegue

### 12.1 Docker Compose (Producción)

```bash
# Build de imágenes
docker-compose -f docker-compose.yml build

# Iniciar servicios
docker-compose up -d

# Ver estado
docker-compose ps
```

### 12.2 Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **db** | 5432 | PostgreSQL con pgvector |
| **redis** | 6379 | Cache y sesiones |
| **backend** | 8000 | FastAPI API |
| **frontend** | 5173 | React SPA |
| **minio** | 9000/9001 | Object storage (perfil: storage) |
| **mailhog** | 8025 | Email testing (perfil: email) |

### 12.3 Healthchecks

Los servicios principales incluyen healthchecks:

```bash
# Verificar salud
docker-compose exec db pg_isready -U sigaia -d sigaia_db
docker-compose exec redis redis-cli ping
curl http://localhost:8000/health
```

---

## Apéndices

### A. Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [pgvector](https://github.com/pgvector/pgvector)

### B. Changelog

Ver archivo [CHANGELOG.md](../CHANGELOG.md) para historial de cambios.

### C. Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.

---

**Documento generado automáticamente - SIGAIA Team © 2026**
