# Medical AI Chatbot

An AI-powered dental patient simulation system for medical training and education.

## 📋 Overview

This application simulates realistic dental patient interactions, allowing medical students and professionals to practice diagnostic questioning in a safe, controlled environment. The AI patient responds based on predefined pathologies while maintaining realistic conversational behavior.

## 🎥 Demo Video

👉 https://github.com/MihaiAdomnitei/ChatBot/blob/main/Demo.mp4

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 Streamlit Web UI                         │    │
│  │  - Chat Interface    - Session Management                │    │
│  │  - Pathology Select  - Settings Control                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
│  │   API Layer    │  │  AI Module     │  │   Schemas      │     │
│  │  - /chats      │  │  - Engine      │  │  - Request     │     │
│  │  - /health     │  │  - Manager     │  │  - Response    │     │
│  │  - /pathologies│  │  - Safety      │  │  - Validation  │     │
│  └────────────────┘  └────────────────┘  └────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Model Inference
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI INFERENCE LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Fine-tuned LLM (Phi-3.5-mini)              │    │
│  │  - Base Model + LoRA Adapter                            │    │
│  │  - Controlled Generation Parameters                      │    │
│  │  - Output Sanitization                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- CUDA-compatible GPU (recommended) or CPU
- 8GB+ RAM (16GB+ recommended for GPU inference)

### Installation

1. **Clone the repository**
   ```bash
   cd ai-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

4. **Start the backend**
   ```bash
   cd backend
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

5. **Start the frontend** (new terminal)
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

6. **Open the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
ai-chatbot/
├── backend/
│   ├── app.py                 # FastAPI application entry point
│   ├── requirements.txt       # Backend dependencies
│   ├── pytest.ini            # Test configuration
│   ├── api/
│   │   ├── __init__.py       # API module exports
│   │   ├── chat.py           # Chat endpoints
│   │   ├── health.py         # Health check endpoints
│   │   ├── schemas.py        # Pydantic models
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── dependencies.py   # Dependency injection
│   ├── ai/
│   │   ├── __init__.py       # AI module exports
│   │   ├── patient_engine.py # LLM inference engine
│   │   ├── chat_manager.py   # Session management
│   │   ├── prompt_builder.py # Prompt construction
│   │   ├── patient_profiles.py # Pathology definitions
│   │   ├── pathology_enum.py # Pathology enumeration
│   │   ├── config.py         # Generation configuration
│   │   ├── safety.py         # Output sanitization
│   │   └── model_repo/       # Model files
│   └── tests/
│       ├── test_api.py       # API tests
│       └── test_ai.py        # AI component tests
└── frontend/
    ├── streamlit_app.py      # Streamlit UI
    └── requirements.txt      # Frontend dependencies
```

## 🔧 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with API info |
| `GET` | `/health` | Health check |
| `GET` | `/health/ready` | Readiness probe |
| `GET` | `/health/live` | Liveness probe |
| `POST` | `/chats` | Create new chat session |
| `GET` | `/chats` | List all sessions |
| `GET` | `/chats/{id}` | Get session details |
| `POST` | `/chats/{id}/message` | Send message |
| `POST` | `/chats/{id}/reset` | Reset session |
| `DELETE` | `/chats/{id}` | Delete session |
| `GET` | `/chats/pathologies/list` | List pathologies |

### Example Usage

```python
import requests

# Create a chat session
response = requests.post("http://localhost:8000/chats", json={"pathology": "dental_caries"})
chat_id = response.json()["chat_id"]

# Send a message
response = requests.post(
    f"http://localhost:8000/chats/{chat_id}/message",
    json={"message": "Where does it hurt?"}
)
print(response.json()["reply"])
```

## 🦷 Supported Pathologies

| Pathology | Description |
|-----------|-------------|
| `dental_caries` | Simple caries without pulpal involvement |
| `periodontal_abscess` | Localized gum infection |
| `pulpal_necrosis` | Dead tooth pulp (post acute pulpitis) |
| `chronic_apical_periodontitis` | Chronic apical infection |
| `acute_apical_periodontitis` | Acute apical infection |
| `pericoronitis` | Wisdom tooth inflammation |
| `reversible_pulpitis` | Mild pulp inflammation |
| `acute_total_pulpitis` | Severe pulp inflammation |

## 🔒 Safety Features

- **Output Sanitization**: Removes potentially unsafe content
- **Diagnosis Protection**: Prevents AI from revealing diagnoses
- **Character Consistency**: Detects when AI breaks character
- **Response Validation**: Checks for quality and appropriateness
- **Generation Controls**: Temperature and token limits

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest
```

Run with coverage:

```bash
pytest --cov=backend --cov-report=html
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOAD_MODEL_ON_STARTUP` | `true` | Load AI model on startup |
| `USE_GPU` | `true` | Use GPU for inference |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins |

### Generation Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `max_new_tokens` | 10-500 | 100 | Max response length |
| `temperature` | 0.0-1.5 | 0.4 | Creativity level |
| `top_p` | 0.0-1.0 | 0.9 | Nucleus sampling |
| `repetition_penalty` | 1.0-2.0 | 1.1 | Repetition penalty |

## 📊 Academic Use

This project is designed for academic purposes, particularly suitable for:

- **Bachelor's Thesis**: Complete implementation with documentation
- **Medical Education**: Training diagnostic questioning skills
- **AI Research**: Fine-tuning and prompt engineering examples

### Suggested Thesis Topics

1. "AI-Assisted Medical Training: A Patient Simulation Approach"
2. "Safety Constraints in Medical AI Chatbots"
3. "Fine-tuning Large Language Models for Domain-Specific Applications"

## 🚧 Future Extensions

- [ ] User authentication and roles
- [ ] Persistent database storage (PostgreSQL)
- [ ] Django admin integration
- [ ] Kubernetes deployment
- [ ] Multi-language support
- [ ] Performance analytics
- [ ] Scoring/evaluation system

## 📜 License

MIT License - See LICENSE file for details.

## ⚠️ Disclaimer

This is a **training tool only**. It should not be used for actual medical diagnosis. The simulated patient responses are for educational purposes and do not constitute medical advice.

