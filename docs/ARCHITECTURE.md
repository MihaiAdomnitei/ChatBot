# Technical Documentation

## System Architecture

### Overview

The Medical AI Chatbot is a three-tier application designed for dental patient simulation:

1. **Presentation Layer** (Frontend) - Streamlit-based web interface
2. **Application Layer** (Backend) - FastAPI REST API
3. **AI Layer** - Fine-tuned LLM with LoRA adapter

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                      │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                     Web Browser                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT FRONTEND                               │
│                                                                          │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │
│   │   APIClient    │  │ SessionState   │  │  UI Components │           │
│   │   - HTTP calls │  │ - chat_id      │  │  - Sidebar     │           │
│   │   - Error      │  │ - messages     │  │  - Chat        │           │
│   │     handling   │  │ - settings     │  │  - Footer      │           │
│   └────────────────┘  └────────────────┘  └────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ REST API (JSON)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND                                 │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         API LAYER                                │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│   │   │ chat.py  │  │health.py │  │schemas.py│  │exceptions│       │   │
│   │   └──────────┘  └──────────┘  └──────────┘  └──────────┘       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    │ Dependency Injection                │
│                                    ▼                                     │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         AI MODULE                                │   │
│   │   ┌────────────┐  ┌────────────┐  ┌────────────┐               │   │
│   │   │ Engine     │  │ Manager    │  │ Safety     │               │   │
│   │   │ - generate │  │ - sessions │  │ - sanitize │               │   │
│   │   │ - model    │  │ - messages │  │ - validate │               │   │
│   │   └────────────┘  └────────────┘  └────────────┘               │   │
│   │   ┌────────────┐  ┌────────────┐  ┌────────────┐               │   │
│   │   │ Prompts    │  │ Profiles   │  │ Config     │               │   │
│   │   │ - build    │  │ - symptoms │  │ - params   │               │   │
│   │   │ - safety   │  │ - history  │  │ - presets  │               │   │
│   │   └────────────┘  └────────────┘  └────────────┘               │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Inference
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AI INFERENCE                                    │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Phi-3.5-mini-instruct                         │   │
│   │                    + LoRA Adapter                                │   │
│   │                    (Fine-tuned for patient simulation)           │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                           GPU/CPU                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Sequence Diagrams

### Chat Session Creation

```
┌────────┐          ┌──────────┐          ┌──────────┐          ┌─────────┐
│ Client │          │ Frontend │          │ Backend  │          │   AI    │
└───┬────┘          └────┬─────┘          └────┬─────┘          └────┬────┘
    │                    │                     │                     │
    │  Select Pathology  │                     │                     │
    │───────────────────>│                     │                     │
    │                    │                     │                     │
    │                    │  POST /chats        │                     │
    │                    │────────────────────>│                     │
    │                    │                     │                     │
    │                    │                     │  Build System Prompt│
    │                    │                     │────────────────────>│
    │                    │                     │                     │
    │                    │                     │  Create Session     │
    │                    │                     │<────────────────────│
    │                    │                     │                     │
    │                    │  201 Created        │                     │
    │                    │  {chat_id, ...}     │                     │
    │                    │<────────────────────│                     │
    │                    │                     │                     │
    │  Display Chat UI   │                     │                     │
    │<───────────────────│                     │                     │
    │                    │                     │                     │
```

### Message Exchange

```
┌────────┐          ┌──────────┐          ┌──────────┐          ┌─────────┐
│ Client │          │ Frontend │          │ Backend  │          │   AI    │
└───┬────┘          └────┬─────┘          └────┬─────┘          └────┬────┘
    │                    │                     │                     │
    │  Type Message      │                     │                     │
    │───────────────────>│                     │                     │
    │                    │                     │                     │
    │                    │ POST /chats/{id}/   │                     │
    │                    │      message        │                     │
    │                    │────────────────────>│                     │
    │                    │                     │                     │
    │                    │                     │  Add User Message   │
    │                    │                     │──────────┐          │
    │                    │                     │<─────────┘          │
    │                    │                     │                     │
    │                    │                     │  Generate Response  │
    │                    │                     │────────────────────>│
    │                    │                     │                     │
    │                    │                     │  Raw Response       │
    │                    │                     │<────────────────────│
    │                    │                     │                     │
    │                    │                     │  Sanitize Response  │
    │                    │                     │──────────┐          │
    │                    │                     │<─────────┘          │
    │                    │                     │                     │
    │                    │  200 OK             │                     │
    │                    │  {reply, ...}       │                     │
    │                    │<────────────────────│                     │
    │                    │                     │                     │
    │  Display Response  │                     │                     │
    │<───────────────────│                     │                     │
    │                    │                     │                     │
```

---

## Data Flow

### Request/Response Flow

```
Request:
  Client → Streamlit → FastAPI → ChatManager → Engine → LLM

Response:
  LLM → Engine → Sanitizer → ChatManager → FastAPI → Streamlit → Client
```

### Session State Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                        SESSION LIFECYCLE                            │
│                                                                     │
│   CREATE          ACTIVE              RESET             DELETE      │
│     │               │                   │                 │         │
│     ▼               ▼                   ▼                 ▼         │
│  ┌─────┐        ┌─────┐            ┌─────┐          ┌─────┐        │
│  │ New │───────>│ Chat│───────────>│Reset│─────────>│ Del │        │
│  │     │        │     │            │     │          │     │        │
│  └─────┘        └─────┘            └─────┘          └─────┘        │
│                    │                   │                            │
│                    │  messages[]       │  messages = [system]       │
│                    │  updated_at       │  updated_at = now          │
│                    │                   │                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## Technology Justification

### Backend: FastAPI

**Chosen over**: Flask, Django

**Reasons**:
1. **Native async support** - Critical for non-blocking AI inference
2. **Automatic OpenAPI docs** - Reduces documentation effort
3. **Type hints & validation** - Pydantic integration reduces bugs
4. **Performance** - Among the fastest Python web frameworks
5. **Modern Python** - Leverages Python 3.10+ features

### Frontend: Streamlit

**Chosen over**: React, Vue, Flask templates

**Reasons**:
1. **Rapid prototyping** - Python-only, no JS required
2. **Built-in components** - Chat, sliders, forms out of box
3. **Session state** - Native state management
4. **Academic focus** - Easier for thesis demonstrations
5. **Extensible** - Can migrate to React later

### AI: Phi-3.5-mini + LoRA

**Chosen over**: GPT-4, Llama 2, Full fine-tuning

**Reasons**:
1. **Size efficiency** - 3.8B parameters, fits on consumer GPU
2. **LoRA efficiency** - Only ~0.1% of parameters trained
3. **Local deployment** - No API costs, full control
4. **Medical safety** - Can enforce strict constraints
5. **Reproducibility** - Consistent behavior for thesis

### Session Storage: In-Memory

**Chosen over**: Redis, PostgreSQL, SQLite

**Reasons**:
1. **Simplicity** - No external dependencies
2. **Speed** - Fastest possible access
3. **Prototype stage** - Can add persistence later
4. **Interface ready** - `ChatPersistence` ABC defined

---

## Error Handling Strategy

### Exception Hierarchy

```
Exception
└── APIException (base)
    ├── ModelNotLoadedError (503)
    ├── ChatNotFoundError (404)
    ├── InvalidPathologyError (400)
    ├── GenerationError (500)
    └── RateLimitError (429)
```

### Error Response Format

```json
{
  "error": {
    "code": "CHAT_NOT_FOUND",
    "message": "Chat session 'abc123' was not found",
    "field": "chat_id"
  },
  "request_id": "req_xyz789"
}
```

---

## Security Considerations

### Medical AI Safety

1. **Prompt injection protection** - System prompt is isolated
2. **Output sanitization** - Blocked phrases removed
3. **Diagnosis protection** - AI instructed to never reveal
4. **Character consistency** - Detects AI breaking role
5. **Response validation** - Quality and safety checks

### Application Security

1. **CORS configuration** - Restricted origins in production
2. **Input validation** - Pydantic schema enforcement
3. **Rate limiting** - Prepared (RateLimitError defined)
4. **No sensitive data** - No real patient information

---

## Performance Considerations

### Model Loading

- **Single load** at startup (lifespan manager)
- **Singleton pattern** for engine access
- **GPU memory** - Model kept in VRAM

### Generation Optimization

- **FP16 inference** - Half-precision for speed
- **Controlled token limits** - Max 500 tokens
- **Temperature control** - Lower = faster convergence

### Memory Management

- **Session cleanup** - Expired sessions removed
- **Conversation limits** - 100 message maximum
- **Response truncation** - 1000 character limit

---

## Deployment Considerations

### Development

```bash
# Backend
uvicorn backend.app:app --reload --port 8000

# Frontend
streamlit run frontend/streamlit_app.py
```

### Production

```bash
# Backend with Gunicorn
gunicorn backend.app:app -w 1 -k uvicorn.workers.UvicornWorker

# Frontend
streamlit run frontend/streamlit_app.py --server.port 8501
```

### Docker (Future)

```dockerfile
# Example Dockerfile structure
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0"]
```

---

## Future Extension Points

### Database Integration

```python
# Implement ChatPersistence interface
class PostgresPersistence(ChatPersistence):
    def save_session(self, session: ChatSession) -> bool:
        # SQLAlchemy implementation
        pass
```

### Authentication

```python
# Add OAuth2 dependency
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### Microservices Split

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Gateway   │────>│  Chat API   │────>│  AI Service │
│   (Nginx)   │     │  (FastAPI)  │     │  (gRPC)     │
└─────────────┘     └─────────────┘     └─────────────┘
```

