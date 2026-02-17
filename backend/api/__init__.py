"""
API Module - FastAPI routers and utilities.

This module exposes:
- chat_router: Chat session management endpoints
- health_router: Health check endpoints
- Exception classes and handlers
- Schema models for request/response validation
"""

from api.chat import router as chat_router
from api.health import router as health_router
from api.exceptions import (
    APIException,
    ChatNotFoundError,
    InvalidPathologyError,
    GenerationError,
    ModelNotLoadedError,
    RateLimitError,
    register_exception_handlers,
)
from api.dependencies import (
    get_engine,
    get_chat_manager,
    get_engine_optional,
    set_engine,
    set_chat_manager,
)
from api.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    SendMessageRequest,
    SendMessageResponse,
    ChatDetailResponse,
    ChatListResponse,
    ChatSummary,
    HealthResponse,
    PathologyListResponse,
    PathologyInfo,
    Message,
    MessageRole,
    ErrorResponse,
    ErrorDetail,
)

__all__ = [
    # Routers
    "chat_router",
    "health_router",
    # Exceptions
    "APIException",
    "ChatNotFoundError",
    "InvalidPathologyError",
    "GenerationError",
    "ModelNotLoadedError",
    "RateLimitError",
    "register_exception_handlers",
    # Dependencies
    "get_engine",
    "get_chat_manager",
    "get_engine_optional",
    "set_engine",
    "set_chat_manager",
    # Schemas
    "CreateChatRequest",
    "CreateChatResponse",
    "SendMessageRequest",
    "SendMessageResponse",
    "ChatDetailResponse",
    "ChatListResponse",
    "ChatSummary",
    "HealthResponse",
    "PathologyListResponse",
    "PathologyInfo",
    "Message",
    "MessageRole",
    "ErrorResponse",
    "ErrorDetail",
]
