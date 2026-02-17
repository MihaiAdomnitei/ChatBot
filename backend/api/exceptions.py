"""
API Exceptions - Custom exception classes and handlers.

This module provides:
- Domain-specific exception classes
- Centralized exception handlers for FastAPI
- Consistent error response formatting
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any


# ============================================
# Custom Exception Classes
# ============================================

class APIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details or {}
        super().__init__(message)


class ModelNotLoadedError(APIException):
    """Raised when the AI model is not yet loaded."""

    def __init__(self, message: str = "AI model is not loaded yet. Please try again later."):
        super().__init__(
            code="MODEL_NOT_LOADED",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class ChatNotFoundError(APIException):
    """Raised when a chat session is not found."""

    def __init__(self, chat_id: str):
        super().__init__(
            code="CHAT_NOT_FOUND",
            message=f"Chat session '{chat_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            field="chat_id"
        )


class InvalidPathologyError(APIException):
    """Raised when an invalid pathology is specified."""

    def __init__(self, pathology: str, valid_options: list[str]):
        super().__init__(
            code="INVALID_PATHOLOGY",
            message=f"'{pathology}' is not a valid pathology",
            status_code=status.HTTP_400_BAD_REQUEST,
            field="pathology",
            details={"valid_options": valid_options}
        )


class GenerationError(APIException):
    """Raised when AI generation fails."""

    def __init__(self, message: str = "Failed to generate response"):
        super().__init__(
            code="GENERATION_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RateLimitError(APIException):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after}
        )


# ============================================
# Exception Handlers
# ============================================

async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions with consistent formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "field": exc.field,
                **exc.details
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with a generic error response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


# ============================================
# Handler Registration
# ============================================

def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(ModelNotLoadedError, api_exception_handler)
    app.add_exception_handler(ChatNotFoundError, api_exception_handler)
    app.add_exception_handler(InvalidPathologyError, api_exception_handler)
    app.add_exception_handler(GenerationError, api_exception_handler)
    app.add_exception_handler(RateLimitError, api_exception_handler)
    # Optionally catch all unhandled exceptions (uncomment for production)
    # app.add_exception_handler(Exception, generic_exception_handler)

