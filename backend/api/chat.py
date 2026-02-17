"""
Chat Router - API endpoints for chat session management.

Endpoints:
- POST /chats - Create a new chat session
- GET /chats - List all chat sessions
- GET /chats/{chat_id} - Get chat details
- POST /chats/{chat_id}/message - Send a message
- DELETE /chats/{chat_id} - Delete a chat session
"""

import random
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Body

from ai import (
    ChatManager,
    build_patient_prompt,
    PATIENT_PROFILES,
    PathologyEnum,
    list_pathologies,
    sanitize_response,
    get_sanitizer,
)
from api.schemas import (
    CreateChatRequest,
    CreateChatResponse,
    SendMessageRequest,
    SendMessageResponse,
    ChatDetailResponse,
    ChatListResponse,
    ChatSummary,
    PathologyListResponse,
    PathologyInfo,
    Message,
    ErrorResponse,
)
from api.exceptions import (
    ChatNotFoundError,
    InvalidPathologyError,
    GenerationError,
)
from api.dependencies import get_engine, get_chat_manager, EngineType


# Create router with prefix and tags for OpenAPI
router = APIRouter(
    prefix="/chats",
    tags=["Chat"],
    responses={
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    }
)


# ============================================
# Dependency Type Aliases
# ============================================

EngineDep = Annotated[EngineType, Depends(get_engine)]
ChatManagerDep = Annotated[ChatManager, Depends(get_chat_manager)]


# ============================================
# Endpoints
# ============================================

@router.post(
    "",
    response_model=CreateChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
    description="Creates a new patient simulation chat. Optionally specify a pathology, or one will be chosen randomly.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid pathology"},
    }
)
async def create_chat(
    chat_manager: ChatManagerDep,
    request: Optional[CreateChatRequest] = Body(None)
) -> CreateChatResponse:
    """
    Create a new chat session with a simulated patient.

    If no pathology is specified, one is chosen randomly from the available options.
    """
    # Handle None request (no body provided)
    if request is None:
        request = CreateChatRequest()

    # Select pathology
    if request.pathology:
        pathology = request.pathology.lower()
        if pathology not in PATIENT_PROFILES:
            raise InvalidPathologyError(
                pathology=pathology,
                valid_options=list_pathologies()
            )
    else:
        # Random selection
        pathology = random.choice(list(PathologyEnum)).value

    # Get profile and build prompt
    profile = PATIENT_PROFILES[pathology]
    system_prompt = build_patient_prompt(
        pathology_label=profile["label"],
        profile=profile
    )

    # Create chat session
    chat_id = chat_manager.create_chat(
        system_prompt=system_prompt,
        pathology=pathology
    )

    session = chat_manager.get_session(chat_id)

    return CreateChatResponse(
        chat_id=chat_id,
        pathology=pathology,
        created_at=session.created_at.isoformat()
    )


@router.get(
    "",
    response_model=ChatListResponse,
    summary="List all chat sessions",
    description="Returns a list of all active chat sessions with their metadata."
)
async def list_chats(
    chat_manager: ChatManagerDep
) -> ChatListResponse:
    """List all active chat sessions."""
    chats = chat_manager.list_chats()
    return ChatListResponse(
        chats=[ChatSummary(**chat) for chat in chats],
        total=len(chats)
    )


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
    summary="Get chat details",
    description="Returns the full details of a chat session including all messages.",
    responses={
        404: {"model": ErrorResponse, "description": "Chat not found"},
    }
)
async def get_chat(
    chat_id: str,
    chat_manager: ChatManagerDep
) -> ChatDetailResponse:
    """Get full details of a specific chat session."""
    session = chat_manager.get_session(chat_id)
    if session is None:
        raise ChatNotFoundError(chat_id)

    return ChatDetailResponse(
        chat_id=session.chat_id,
        pathology=session.pathology,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        message_count=len(session.messages),
        messages=[Message(role=m["role"], content=m["content"]) for m in session.messages]
    )


@router.post(
    "/{chat_id}/message",
    response_model=SendMessageResponse,
    summary="Send a message to the patient",
    description="Send a message to the simulated patient and receive their response.",
    responses={
        404: {"model": ErrorResponse, "description": "Chat not found"},
        500: {"model": ErrorResponse, "description": "Generation failed"},
    }
)
async def send_message(
    chat_id: str,
    request: SendMessageRequest,
    engine: EngineDep,
    chat_manager: ChatManagerDep
) -> SendMessageResponse:
    """
    Send a message to the simulated patient.

    The patient will respond based on their assigned pathology and symptoms.
    Responses are sanitized for safety before being returned.
    """
    # Verify chat exists
    session = chat_manager.get_session(chat_id)
    if session is None:
        raise ChatNotFoundError(chat_id)

    # Check conversation length
    sanitizer = get_sanitizer()
    length_warning = sanitizer.check_conversation_length(len(session.messages))

    # Add user message
    chat_manager.add_user_message(chat_id, request.message)

    try:
        # Generate response
        messages = chat_manager.get_messages(chat_id)
        raw_reply = engine.generate(
            messages=messages,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature
        )

        # Sanitize response for safety
        sanitized_reply = sanitize_response(raw_reply)

        # Add assistant response (sanitized version)
        chat_manager.add_assistant_message(chat_id, sanitized_reply)

        response = SendMessageResponse(
            reply=sanitized_reply,
            chat_id=chat_id,
            message_count=len(chat_manager.get_messages(chat_id))
        )

        # Add warning header if conversation is getting long
        # (handled in middleware or logged, response stays clean)

        return response
    except Exception as e:
        # Remove the user message if generation failed
        # (to maintain conversation consistency)
        if session.messages and session.messages[-1].get("role") == "user":
            session.messages.pop()
        raise GenerationError(f"Failed to generate response: {str(e)}")


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
    description="Permanently deletes a chat session and all its messages.",
    responses={
        404: {"model": ErrorResponse, "description": "Chat not found"},
    }
)
async def delete_chat(
    chat_id: str,
    chat_manager: ChatManagerDep
) -> None:
    """Delete a chat session."""
    if not chat_manager.delete_chat(chat_id):
        raise ChatNotFoundError(chat_id)


@router.post(
    "/{chat_id}/reset",
    response_model=CreateChatResponse,
    summary="Reset a chat session",
    description="Clears conversation history while keeping the same pathology and session ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Chat not found"},
    }
)
async def reset_chat(
    chat_id: str,
    chat_manager: ChatManagerDep
) -> CreateChatResponse:
    """
    Reset a chat session to start fresh.

    This keeps the same chat_id and pathology but clears all messages.
    Useful when the conversation has gone off track or reached its limit.
    """
    session = chat_manager.get_session(chat_id)
    if session is None:
        raise ChatNotFoundError(chat_id)

    chat_manager.reset_chat(chat_id)

    return CreateChatResponse(
        chat_id=chat_id,
        pathology=session.pathology,
        created_at=session.created_at.isoformat()
    )


# ============================================
# Pathology Information Endpoint
# ============================================

@router.get(
    "/pathologies/list",
    response_model=PathologyListResponse,
    summary="List available pathologies",
    description="Returns a list of all pathologies that can be simulated."
)
async def list_available_pathologies() -> PathologyListResponse:
    """List all available pathologies for simulation."""
    pathologies = [
        PathologyInfo(
            key=key,
            label=profile["label"],
            chief_complaint=profile["chief_complaint"]
        )
        for key, profile in PATIENT_PROFILES.items()
    ]
    return PathologyListResponse(
        pathologies=pathologies,
        total=len(pathologies)
    )

