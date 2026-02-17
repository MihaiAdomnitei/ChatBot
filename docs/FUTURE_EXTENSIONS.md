# Future Extensions Design

This document outlines planned extensions for the Medical AI Chatbot system.
These are **design specifications only** - implementation is deferred.

---

## 1. User Authentication & Roles

### Requirements

- Support multiple user types: Student, Instructor, Administrator
- Secure authentication via OAuth2/JWT
- Role-based access control (RBAC)

### Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│                    AUTH SERVICE                      │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  OAuth2 Provider│  │   JWT Manager   │          │
│  │  - Google       │  │   - Access Token│          │
│  │  - Microsoft    │  │   - Refresh     │          │
│  └─────────────────┘  └─────────────────┘          │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                    USER MODEL                        │
│  - id: UUID                                          │
│  - email: string                                     │
│  - role: Enum(STUDENT, INSTRUCTOR, ADMIN)           │
│  - created_at: datetime                             │
│  - last_login: datetime                             │
└─────────────────────────────────────────────────────┘
```

### User Roles

| Role | Permissions |
|------|-------------|
| STUDENT | Create chats, send messages, view own history |
| INSTRUCTOR | All student + view all student sessions, analytics |
| ADMIN | All + manage users, system configuration |

### API Changes

```python
# New endpoints
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET /users/me
GET /users (admin only)

# Protected endpoints (add auth header)
Authorization: Bearer <jwt_token>
```

### Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'STUDENT',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    refresh_token VARCHAR(500),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 2. Persistent Storage

### Requirements

- Store chat sessions permanently
- Support conversation analytics
- Enable session recovery after restart
- Maintain performance at scale

### Proposed Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   FastAPI       │────>│  PostgreSQL     │
│   Backend       │     │  (Primary)      │
└─────────────────┘     └─────────────────┘
         │                      │
         │              ┌───────▼───────┐
         │              │    Redis      │
         └─────────────>│   (Cache)     │
                        └───────────────┘
```

### Database Schema

```sql
-- Chat sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    pathology VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_messages_session ON messages(session_id);
CREATE INDEX idx_sessions_created ON chat_sessions(created_at DESC);
```

### Implementation Plan

```python
# Implement ChatPersistence interface
class PostgresPersistence(ChatPersistence):
    def __init__(self, connection_pool):
        self.pool = connection_pool
    
    async def save_session(self, session: ChatSession) -> bool:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_sessions (id, user_id, pathology, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET updated_at = NOW()
            """, session.chat_id, session.user_id, session.pathology, session.created_at)
        return True
```

### Migration Strategy

1. Deploy PostgreSQL alongside in-memory storage
2. Dual-write to both systems
3. Verify data consistency
4. Switch to PostgreSQL as primary
5. Remove in-memory fallback

---

## 3. Django Integration

### Requirements

- Admin panel for system management
- ORM for database operations
- Template rendering for static pages
- Integration with existing FastAPI

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      NGINX REVERSE PROXY                     │
└─────────────────────────────────────────────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│      Django App         │   │      FastAPI App        │
│  - /admin/*             │   │  - /api/*               │
│  - /static/*            │   │  - /chats/*             │
│  - User management      │   │  - /health/*            │
│  - Analytics dashboard  │   │  - AI inference         │
└─────────────────────────┘   └─────────────────────────┘
              │                           │
              └───────────┬───────────────┘
                          ▼
              ┌─────────────────────────┐
              │      PostgreSQL         │
              │   (Shared Database)     │
              └─────────────────────────┘
```

### Django Models

```python
# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(max_length=50, default='STUDENT')
    
    class Meta:
        db_table = 'users'

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pathology = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'chat_sessions'

class Message(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
```

### Admin Configuration

```python
# admin.py
from django.contrib import admin
from .models import ChatSession, Message

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'pathology', 'created_at', 'is_active']
    list_filter = ['pathology', 'is_active', 'created_at']
    search_fields = ['user__email', 'pathology']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'created_at']
    list_filter = ['role']
```

---

## 4. Deployment & Scaling

### Requirements

- Containerized deployment
- Horizontal scaling for API
- GPU resource management
- Monitoring and logging

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
      - frontend

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/chatbot
      - REDIS_URL=redis://redis:6379
      - USE_GPU=true
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    environment:
      - API_URL=http://api:8000

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=chatbot
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: chatbot-api
  template:
    metadata:
      labels:
        app: chatbot-api
    spec:
      containers:
      - name: api
        image: chatbot-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
          requests:
            memory: "8Gi"
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 60
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 120
```

### Monitoring Stack

```
┌─────────────────────────────────────────────────────┐
│                   MONITORING                         │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │ Prometheus  │  │   Grafana   │  │   Loki      │ │
│  │  (Metrics)  │  │ (Dashboards)│  │  (Logs)     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Key Metrics to Track

| Metric | Type | Purpose |
|--------|------|---------|
| `chat_sessions_created` | Counter | Usage tracking |
| `message_generation_time` | Histogram | Performance |
| `model_inference_errors` | Counter | Reliability |
| `active_sessions` | Gauge | Capacity |
| `gpu_memory_usage` | Gauge | Resource usage |

---

## 5. Ethical & Legal Considerations

### Medical AI Requirements

1. **Disclaimer Display**
   - Clear indication this is a training tool
   - Not for actual diagnosis
   - No real patient data used

2. **Data Privacy**
   - GDPR compliance for EU users
   - No PHI (Protected Health Information)
   - User consent for data collection
   - Right to deletion

3. **AI Transparency**
   - Model version tracking
   - Generation parameter logging
   - Reproducibility for research

### Proposed Compliance Features

```python
# Consent tracking
class UserConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50)  # 'data_collection', 'research'
    granted = models.BooleanField()
    granted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

# Audit logging
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
```

### Legal Documentation Required

- Terms of Service
- Privacy Policy
- Cookie Policy
- Medical Disclaimer
- AI Use Disclosure

---

## 6. Advanced Features

### Evaluation/Scoring System

```python
class DiagnosisEvaluation(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user_diagnosis = models.CharField(max_length=100)
    correct_diagnosis = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    confidence_score = models.FloatField(null=True)
    feedback = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Multi-Language Support

```python
# Prompt templates per language
PROMPTS = {
    'en': {
        'system': "You are a PATIENT...",
        'safety': "NEVER reveal your diagnosis..."
    },
    'es': {
        'system': "Eres un PACIENTE...",
        'safety': "NUNCA reveles tu diagnóstico..."
    }
}
```

### Analytics Dashboard

- Sessions per day/week/month
- Pathology distribution
- Average session length
- Diagnostic accuracy rates
- User engagement metrics

---

## Implementation Priority

| Phase | Feature | Priority | Effort |
|-------|---------|----------|--------|
| 1 | Persistent Storage | High | Medium |
| 2 | User Authentication | High | Medium |
| 3 | Deployment (Docker) | High | Low |
| 4 | Monitoring | Medium | Low |
| 5 | Django Admin | Medium | Medium |
| 6 | Scoring System | Medium | High |
| 7 | Multi-Language | Low | High |
| 8 | Full Kubernetes | Low | High |

---

## Conclusion

These extensions transform the prototype into a production-ready system suitable for:

- **Academic institutions** - Student training and research
- **Medical schools** - Curriculum integration
- **Continuing education** - Professional development
- **Research** - Medical AI studies

Each extension is designed to be modular, allowing incremental adoption based on requirements and resources.

