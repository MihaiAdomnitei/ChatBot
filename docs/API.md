# API Documentation

Complete reference for the Medical AI Chatbot REST API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. Future versions will implement OAuth2.

---

## Endpoints

### Root

#### GET /

Returns basic API information.

**Response** `200 OK`

```json
{
  "name": "Medical AI Chatbot API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### Health Checks

#### GET /health

Comprehensive health check including model status.

**Response** `200 OK`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

**Status Values**:
- `healthy` - All systems operational
- `degraded` - API running but model not loaded

---

#### GET /health/ready

Kubernetes-style readiness probe.

**Response** `200 OK`

```json
{
  "status": "ready",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

**Status Values**:
- `ready` - Ready to serve requests
- `not_ready` - Not ready (model loading)

---

#### GET /health/live

Kubernetes-style liveness probe.

**Response** `200 OK`

```json
{
  "status": "alive",
  "model_loaded": true,
  "version": "1.0.0",
  "uptime_seconds": 3600.5
}
```

---

### Chat Sessions

#### POST /chats

Create a new chat session with a simulated patient.

**Request Body** (optional)

```json
{
  "pathology": "dental_caries"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pathology` | string | No | Pathology key. If omitted, random selection. |

**Response** `201 Created`

```json
{
  "chat_id": "550e8400-e29b-41d4-a716-446655440000",
  "pathology": "dental_caries",
  "created_at": "2025-01-10T12:00:00"
}
```

**Errors**

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_PATHOLOGY` | Specified pathology doesn't exist |

---

#### GET /chats

List all active chat sessions.

**Response** `200 OK`

```json
{
  "chats": [
    {
      "chat_id": "550e8400-e29b-41d4-a716-446655440000",
      "pathology": "dental_caries",
      "created_at": "2025-01-10T12:00:00",
      "message_count": 5
    }
  ],
  "total": 1
}
```

---

#### GET /chats/{chat_id}

Get full details of a chat session including all messages.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_id` | string | Unique chat session identifier |

**Response** `200 OK`

```json
{
  "chat_id": "550e8400-e29b-41d4-a716-446655440000",
  "pathology": "dental_caries",
  "created_at": "2025-01-10T12:00:00",
  "updated_at": "2025-01-10T12:05:00",
  "message_count": 5,
  "messages": [
    {
      "role": "system",
      "content": "You are a patient..."
    },
    {
      "role": "user",
      "content": "Where does it hurt?"
    },
    {
      "role": "assistant",
      "content": "I have a sharp pain in my lower right tooth."
    }
  ]
}
```

**Errors**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `CHAT_NOT_FOUND` | Chat session doesn't exist |

---

#### POST /chats/{chat_id}/message

Send a message to the simulated patient and receive their response.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_id` | string | Unique chat session identifier |

**Request Body**

```json
{
  "message": "Can you describe the pain?",
  "max_new_tokens": 100,
  "temperature": 0.4
}
```

| Field | Type | Required | Default | Range | Description |
|-------|------|----------|---------|-------|-------------|
| `message` | string | Yes | - | 1-2000 chars | Your message to the patient |
| `max_new_tokens` | integer | No | 100 | 10-500 | Max response length in tokens |
| `temperature` | float | No | 0.4 | 0.0-2.0 | Sampling temperature |

**Response** `200 OK`

```json
{
  "reply": "The pain is sharp and throbbing. It started about three days ago.",
  "chat_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_count": 4
}
```

**Errors**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `CHAT_NOT_FOUND` | Chat session doesn't exist |
| 500 | `GENERATION_ERROR` | AI generation failed |
| 503 | `MODEL_NOT_LOADED` | AI model not ready |

---

#### POST /chats/{chat_id}/reset

Reset a chat session, clearing messages but keeping the session.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_id` | string | Unique chat session identifier |

**Response** `200 OK`

```json
{
  "chat_id": "550e8400-e29b-41d4-a716-446655440000",
  "pathology": "dental_caries",
  "created_at": "2025-01-10T12:00:00"
}
```

**Errors**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `CHAT_NOT_FOUND` | Chat session doesn't exist |

---

#### DELETE /chats/{chat_id}

Permanently delete a chat session.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `chat_id` | string | Unique chat session identifier |

**Response** `204 No Content`

**Errors**

| Status | Code | Description |
|--------|------|-------------|
| 404 | `CHAT_NOT_FOUND` | Chat session doesn't exist |

---

### Pathologies

#### GET /chats/pathologies/list

List all available pathologies for simulation.

**Response** `200 OK`

```json
{
  "pathologies": [
    {
      "key": "dental_caries",
      "label": "Simple Caries / No Pulpal Involvement",
      "chief_complaint": "Tooth discomfort only when exposed to cold..."
    },
    {
      "key": "periodontal_abscess",
      "label": "Periodontal Abscess",
      "chief_complaint": "Pain near a tooth, initially thought to be tooth pain."
    }
  ],
  "total": 8
}
```

---

## Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "field": "field_name"
  },
  "request_id": "optional_tracking_id"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `MODEL_NOT_LOADED` | 503 | AI model is not loaded |
| `CHAT_NOT_FOUND` | 404 | Chat session not found |
| `INVALID_PATHOLOGY` | 400 | Invalid pathology specified |
| `GENERATION_ERROR` | 500 | AI generation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Rate Limiting

Currently not enforced. Future implementation will use:

- **Limit**: 60 requests per minute
- **Header**: `X-RateLimit-Remaining`
- **Response**: 429 with `retry_after` in body

---

## Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Create session
response = requests.post(f"{BASE_URL}/chats", json={"pathology": "dental_caries"})
chat_id = response.json()["chat_id"]

# Send message
response = requests.post(
    f"{BASE_URL}/chats/{chat_id}/message",
    json={"message": "Where is the pain located?"}
)
print(response.json()["reply"])

# Reset session
requests.post(f"{BASE_URL}/chats/{chat_id}/reset")

# Delete session
requests.delete(f"{BASE_URL}/chats/{chat_id}")
```

### cURL

```bash
# Create session
curl -X POST http://localhost:8000/chats \
  -H "Content-Type: application/json" \
  -d '{"pathology": "dental_caries"}'

# Send message
curl -X POST http://localhost:8000/chats/{chat_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Describe your symptoms"}'

# Health check
curl http://localhost:8000/health
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';

// Create session
const createResponse = await fetch(`${BASE_URL}/chats`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ pathology: 'dental_caries' })
});
const { chat_id } = await createResponse.json();

// Send message
const messageResponse = await fetch(`${BASE_URL}/chats/${chat_id}/message`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Where does it hurt?' })
});
const { reply } = await messageResponse.json();
console.log(reply);
```

---

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **JSON Schema**: http://localhost:8000/openapi.json

