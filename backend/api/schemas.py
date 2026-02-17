"""
API Schemas - Pydantic models for request/response validation.

These schemas provide:
- Input validation with detailed error messages
- Automatic OpenAPI documentation
- Type safety throughout the API layer
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ============================================
# Enums for API
# ============================================

class MessageRole(str, Enum):
    """Valid message roles in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# ============================================
# Chat Message Schemas
# ============================================

class Message(BaseModel):
    """A single message in a conversation."""
    role: MessageRole = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The message content", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "I have a toothache that started yesterday."
            }
        }


# ============================================
# Chat Request/Response Schemas
# ============================================

class CreateChatRequest(BaseModel):
    """Request body for creating a new chat session."""
    pathology: Optional[str] = Field(
        default=None,
        description="Specific pathology to simulate. If not provided, one is chosen randomly.",
        examples=["dental_caries", "periodontal_abscess"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pathology": "dental_caries"
            }
        }


class CreateChatResponse(BaseModel):
    """Response body after creating a new chat session."""
    chat_id: str = Field(..., description="Unique identifier for the chat session")
    pathology: str = Field(..., description="The pathology being simulated")
    created_at: str = Field(..., description="ISO timestamp of creation")

    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                "pathology": "dental_caries",
                "created_at": "2025-01-10T12:00:00"
            }
        }


class SendMessageRequest(BaseModel):
    """Request body for sending a message to the patient."""
    message: str = Field(
        ...,
        description="The user's message to the patient",
        min_length=1,
        max_length=2000
    )
    max_new_tokens: int = Field(
        default=100,
        description="Maximum tokens in the response",
        ge=10,
        le=500
    )
    temperature: float = Field(
        default=0.4,
        description="Sampling temperature (lower = more deterministic)",
        ge=0.0,
        le=2.0
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Can you describe where exactly the pain is located?",
                "max_new_tokens": 100,
                "temperature": 0.4
            }
        }


class SendMessageResponse(BaseModel):
    """Response body containing the patient's reply."""
    reply: str = Field(..., description="The simulated patient's response")
    chat_id: str = Field(..., description="The chat session ID")
    message_count: int = Field(..., description="Total messages in the conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "reply": "The pain is mostly in my lower right side, near the back teeth.",
                "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                "message_count": 4
            }
        }


class ChatDetailResponse(BaseModel):
    """Full details of a chat session including all messages."""
    chat_id: str = Field(..., description="Unique identifier for the chat session")
    pathology: str = Field(..., description="The pathology being simulated")
    created_at: str = Field(..., description="ISO timestamp of creation")
    updated_at: str = Field(..., description="ISO timestamp of last update")
    message_count: int = Field(..., description="Total number of messages")
    messages: List[Message] = Field(..., description="All messages in the conversation")


class ChatSummary(BaseModel):
    """Summary of a chat session (for listing)."""
    chat_id: str = Field(..., description="Unique identifier for the chat session")
    pathology: str = Field(..., description="The pathology being simulated")
    created_at: str = Field(..., description="ISO timestamp of creation")
    message_count: int = Field(..., description="Total number of messages")


class ChatListResponse(BaseModel):
    """Response containing a list of chat sessions."""
    chats: List[ChatSummary] = Field(..., description="List of chat session summaries")
    total: int = Field(..., description="Total number of chat sessions")


# ============================================
# Health Check Schemas
# ============================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall API status")
    model_loaded: bool = Field(..., description="Whether the AI model is loaded")
    version: str = Field(..., description="API version")
    uptime_seconds: Optional[float] = Field(None, description="Server uptime in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "version": "1.0.0",
                "uptime_seconds": 3600.5
            }
        }


# ============================================
# Pathology Schemas
# ============================================

class PathologyInfo(BaseModel):
    """Information about a pathology."""
    key: str = Field(..., description="Pathology key identifier")
    label: str = Field(..., description="Human-readable name")
    chief_complaint: str = Field(..., description="Main complaint description")


class PathologyListResponse(BaseModel):
    """List of available pathologies."""
    pathologies: List[PathologyInfo] = Field(..., description="Available pathologies")
    total: int = Field(..., description="Total number of pathologies")


# ============================================
# Error Schemas
# ============================================

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error, if applicable")


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: ErrorDetail = Field(..., description="Error details")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "CHAT_NOT_FOUND",
                    "message": "Chat session with the specified ID was not found",
                    "field": "chat_id"
                },
                "request_id": "req_abc123"
            }
        }

