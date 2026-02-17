"""
API Dependencies - Dependency injection for FastAPI endpoints.

This module provides:
- Access to shared resources (engine, chat manager)
- Request-scoped dependencies
- Configuration injection
"""

from typing import Optional, Union, Any
from fastapi import Depends, Request

from ai import PatientChatEngine, ChatManager
from ai.mock_engine import MockPatientEngine
from ai.huggingface_engine import HuggingFaceEngine
from ai.huggingface_endpoint_engine import HuggingFaceEndpointEngine
from api.exceptions import ModelNotLoadedError


# Type alias for any engine (real, mock, or Hugging Face API/Endpoint)
EngineType = Union[PatientChatEngine, MockPatientEngine, HuggingFaceEngine, HuggingFaceEndpointEngine]


# ============================================
# Global State (set during app startup)
# ============================================

_engine: Optional[EngineType] = None
_chat_manager: Optional[ChatManager] = None


def set_engine(engine: EngineType) -> None:
    """Set the global engine instance during startup."""
    global _engine
    _engine = engine


def set_chat_manager(manager: ChatManager) -> None:
    """Set the global chat manager instance during startup."""
    global _chat_manager
    _chat_manager = manager


# ============================================
# Dependency Functions
# ============================================

def get_engine() -> EngineType:
    """
    Dependency that provides the AI engine.

    Raises:
        ModelNotLoadedError: If the engine is not initialized

    Returns:
        The PatientChatEngine or MockPatientEngine instance
    """
    if _engine is None:
        raise ModelNotLoadedError()
    return _engine


def get_chat_manager() -> ChatManager:
    """
    Dependency that provides the chat manager.

    Returns:
        The ChatManager instance
    """
    if _chat_manager is None:
        # Create default instance if not set
        return ChatManager.get_instance()
    return _chat_manager


def get_engine_optional() -> Optional[EngineType]:
    """
    Dependency that provides the AI engine without raising an error.

    Returns:
        The PatientChatEngine/MockPatientEngine instance or None if not loaded
    """
    return _engine


# ============================================
# Request Context Dependencies
# ============================================

async def get_request_id(request: Request) -> Optional[str]:
    """
    Extract request ID from headers for tracking.

    Returns:
        Request ID if provided in X-Request-ID header
    """
    return request.headers.get("X-Request-ID")


# ============================================
# Type Aliases for Dependency Injection
# ============================================

EngineDep = Depends(get_engine)
ChatManagerDep = Depends(get_chat_manager)
EngineOptionalDep = Depends(get_engine_optional)

