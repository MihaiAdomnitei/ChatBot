"""
Medical AI Chatbot - FastAPI Application

Main application entry point that:
- Initializes the FastAPI app with metadata
- Registers routers and exception handlers
- Loads the AI model on startup
- Provides CORS configuration for frontend integration
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import PatientChatEngine, ChatManager
from ai.mock_engine import get_mock_engine
from ai.huggingface_engine import get_huggingface_engine
from ai.huggingface_endpoint_engine import get_huggingface_endpoint_engine
from api.chat import router as chat_router
from api.health import router as health_router, set_startup_time
from api.dependencies import set_engine, set_chat_manager
from api.exceptions import register_exception_handlers


# ============================================
# Configuration
# ============================================

# CORS origins allowed to access the API
# In production, this should be restricted to specific domains
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Model loading configuration
LOAD_MODEL_ON_STARTUP = os.getenv("LOAD_MODEL_ON_STARTUP", "true").lower() == "true"
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"
USE_HUGGINGFACE = os.getenv("USE_HUGGINGFACE", "false").lower() == "true"
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "microsoft/Phi-3.5-mini-instruct")
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")  # Optional: dedicated endpoint URL


# ============================================
# Lifespan Management
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Load AI model, initialize managers
    - Shutdown: Cleanup resources
    """
    # === STARTUP ===
    print("🚀 Starting Medical AI Chatbot API...")
    set_startup_time()

    # Initialize chat manager (singleton)
    chat_manager = ChatManager()
    ChatManager.set_instance(chat_manager)
    set_chat_manager(chat_manager)
    print("✅ Chat manager initialized")

    # Load AI model (optional, can be deferred)
    if USE_HUGGINGFACE:
        # Use Hugging Face Inference API or Dedicated Endpoint
        try:
            if HF_ENDPOINT_URL:
                # Use dedicated Inference Endpoint (faster, requires deployment)
                engine = get_huggingface_endpoint_engine(endpoint_url=HF_ENDPOINT_URL)
                set_engine(engine)
                print("✅ Hugging Face Inference Endpoint initialized")
            else:
                # Use free Inference API (slower, no deployment needed)
                engine = get_huggingface_engine(model_id=HF_MODEL_ID)
                set_engine(engine)
                print("✅ Hugging Face Inference API initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize Hugging Face: {e}")
            print("   Falling back to mock engine for testing.")
            mock_engine = get_mock_engine()
            set_engine(mock_engine)
            print("✅ Mock engine activated")
    elif LOAD_MODEL_ON_STARTUP:
        # Load local model
        try:
            device_map = "auto" if USE_GPU else None
            engine = PatientChatEngine(device_map=device_map)
            PatientChatEngine.set_instance(engine)
            set_engine(engine)
            print("✅ AI model loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load AI model: {e}")
            print("   Falling back to mock engine for testing.")
            mock_engine = get_mock_engine()
            set_engine(mock_engine)
            print("✅ Mock engine activated")
    else:
        print("ℹ️ Model loading disabled - using mock engine for testing")
        mock_engine = get_mock_engine()
        set_engine(mock_engine)
        print("✅ Mock engine activated")

    print("✅ API is ready to serve requests")

    yield  # Application runs here

    # === SHUTDOWN ===
    print("🛑 Shutting down Medical AI Chatbot API...")
    # Cleanup resources if needed
    print("✅ Shutdown complete")


# ============================================
# Application Factory
# ============================================

def create_app() -> FastAPI:
    """
    Application factory function.

    Creates and configures the FastAPI application with:
    - Metadata for OpenAPI documentation
    - CORS middleware
    - Route handlers
    - Exception handlers

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Medical AI Chatbot API",
        description="""
## Overview
AI-powered medical chatbot that simulates patient interactions for dental diagnosis training.

## Features
- **Patient Simulation**: Realistic patient responses based on dental pathologies
- **Session Management**: Create, manage, and delete chat sessions
- **Health Monitoring**: Comprehensive health check endpoints

## Usage
1. Create a chat session with `POST /chats`
2. Send messages with `POST /chats/{chat_id}/message`
3. View conversation with `GET /chats/{chat_id}`

## Safety Note
This is a training tool and should not be used for actual medical diagnosis.
        """,
        version="1.0.0",
        contact={
            "name": "AI Chatbot Team",
            "email": "support@example.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Register routers
    app.include_router(chat_router)
    app.include_router(health_router)

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Medical AI Chatbot API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }

    return app


# Create the application instance
app = create_app()


# ============================================
# Development Server
# ============================================

if __name__ == "__main__":
    import uvicorn

    # Development server configuration
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

