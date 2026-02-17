"""
ChatManager - In-memory conversation session management.

This module handles:
- Creating new chat sessions with system prompts
- Storing and retrieving message history
- Adding user and assistant messages
- Conversation reset and cleanup
- Session statistics and boundaries
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod


# ============================================
# Configuration Constants
# ============================================

# Maximum messages before suggesting a reset
MAX_CONVERSATION_LENGTH = 100

# Session expiration time (in hours)
SESSION_EXPIRATION_HOURS = 24


class ChatSession:
    """
    Represents a single chat session with its metadata and messages.

    Attributes:
        chat_id: Unique session identifier
        pathology: The pathology being simulated
        created_at: Session creation timestamp
        updated_at: Last activity timestamp
        messages: List of message dictionaries
    """

    def __init__(self, chat_id: str, system_prompt: str, pathology: str):
        self.chat_id = chat_id
        self.pathology = pathology
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self._system_prompt = system_prompt  # Store for reset
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session."""
        self.messages.append({"role": role, "content": content})
        self.updated_at = datetime.now(timezone.utc)

    def reset(self) -> None:
        """
        Reset the conversation while keeping the session.

        Clears all messages except the system prompt.
        """
        self.messages = [{"role": "system", "content": self._system_prompt}]
        self.updated_at = datetime.now(timezone.utc)

    def get_user_messages(self) -> List[Dict[str, str]]:
        """Get only user messages."""
        return [m for m in self.messages if m["role"] == "user"]

    def get_assistant_messages(self) -> List[Dict[str, str]]:
        """Get only assistant messages."""
        return [m for m in self.messages if m["role"] == "assistant"]

    def get_conversation_pairs(self) -> List[Dict[str, str]]:
        """
        Get conversation as user-assistant pairs.

        Returns:
            List of dicts with 'user' and 'assistant' keys
        """
        pairs = []
        user_msg = None
        for msg in self.messages:
            if msg["role"] == "user":
                user_msg = msg["content"]
            elif msg["role"] == "assistant" and user_msg:
                pairs.append({"user": user_msg, "assistant": msg["content"]})
                user_msg = None
        return pairs

    def is_expired(self, hours: int = SESSION_EXPIRATION_HOURS) -> bool:
        """Check if session has expired."""
        expiration_time = self.updated_at + timedelta(hours=hours)
        return datetime.now(timezone.utc) > expiration_time

    def is_at_limit(self, max_messages: int = MAX_CONVERSATION_LENGTH) -> bool:
        """Check if conversation has reached the message limit."""
        return len(self.messages) >= max_messages

    def get_statistics(self) -> Dict:
        """Get conversation statistics."""
        user_msgs = self.get_user_messages()
        assistant_msgs = self.get_assistant_messages()

        return {
            "total_messages": len(self.messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "avg_user_length": sum(len(m["content"]) for m in user_msgs) / max(len(user_msgs), 1),
            "avg_assistant_length": sum(len(m["content"]) for m in assistant_msgs) / max(len(assistant_msgs), 1),
            "duration_minutes": (self.updated_at - self.created_at).total_seconds() / 60,
            "is_at_limit": self.is_at_limit(),
        }

    def to_dict(self) -> Dict:
        """Convert session to dictionary representation."""
        return {
            "chat_id": self.chat_id,
            "pathology": self.pathology,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages),
            "messages": self.messages,
            "statistics": self.get_statistics()
        }


class ChatManager:
    """
    Manages multiple chat sessions in memory.

    This implementation stores sessions in a dictionary for fast lookup.
    Future versions may implement persistence via database.

    Attributes:
        sessions: Dictionary mapping chat_id to ChatSession
    """

    _instance: Optional['ChatManager'] = None

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}

    def create_chat(self, system_prompt: str, pathology: str) -> str:
        """
        Create a new chat session.

        Args:
            system_prompt: The system prompt defining the AI's behavior
            pathology: The pathology type for this session

        Returns:
            The unique chat_id for the new session
        """
        chat_id = str(uuid.uuid4())
        self.sessions[chat_id] = ChatSession(
            chat_id=chat_id,
            system_prompt=system_prompt,
            pathology=pathology
        )
        return chat_id

    def get_session(self, chat_id: str) -> Optional[ChatSession]:
        """
        Get a chat session by ID.

        Args:
            chat_id: The unique identifier for the chat

        Returns:
            ChatSession if found, None otherwise
        """
        return self.sessions.get(chat_id)

    def get_messages(self, chat_id: str) -> Optional[List[Dict[str, str]]]:
        """
        Get all messages for a chat session.

        Args:
            chat_id: The unique identifier for the chat

        Returns:
            List of message dictionaries if found, None otherwise
        """
        session = self.sessions.get(chat_id)
        if session:
            return session.messages
        return None

    def add_user_message(self, chat_id: str, message: str) -> bool:
        """
        Add a user message to a chat session.

        Args:
            chat_id: The unique identifier for the chat
            message: The user's message content

        Returns:
            True if successful, False if chat not found
        """
        session = self.sessions.get(chat_id)
        if session:
            session.add_message("user", message)
            return True
        return False

    def add_assistant_message(self, chat_id: str, message: str) -> bool:
        """
        Add an assistant message to a chat session.

        Args:
            chat_id: The unique identifier for the chat
            message: The assistant's message content

        Returns:
            True if successful, False if chat not found
        """
        session = self.sessions.get(chat_id)
        if session:
            session.add_message("assistant", message)
            return True
        return False

    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat session.

        Args:
            chat_id: The unique identifier for the chat

        Returns:
            True if deleted, False if not found
        """
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            return True
        return False

    def list_chats(self) -> List[Dict]:
        """
        List all active chat sessions (metadata only).

        Returns:
            List of chat session summaries
        """
        return [
            {
                "chat_id": session.chat_id,
                "pathology": session.pathology,
                "created_at": session.created_at.isoformat(),
                "message_count": len(session.messages)
            }
            for session in self.sessions.values()
        ]

    def reset_chat(self, chat_id: str) -> bool:
        """
        Reset a chat session, clearing messages but keeping the session.

        Args:
            chat_id: The unique identifier for the chat

        Returns:
            True if reset successful, False if chat not found
        """
        session = self.sessions.get(chat_id)
        if session:
            session.reset()
            return True
        return False

    def cleanup_expired(self, hours: int = SESSION_EXPIRATION_HOURS) -> int:
        """
        Remove all expired sessions.

        Args:
            hours: Number of hours after which sessions expire

        Returns:
            Number of sessions removed
        """
        expired = [
            chat_id for chat_id, session in self.sessions.items()
            if session.is_expired(hours)
        ]
        for chat_id in expired:
            del self.sessions[chat_id]
        return len(expired)

    def get_global_statistics(self) -> Dict:
        """
        Get global statistics across all sessions.

        Returns:
            Dictionary with aggregate statistics
        """
        if not self.sessions:
            return {
                "total_sessions": 0,
                "total_messages": 0,
                "pathology_distribution": {},
                "avg_messages_per_session": 0,
            }

        total_messages = sum(len(s.messages) for s in self.sessions.values())
        pathology_counts: Dict[str, int] = {}
        for session in self.sessions.values():
            pathology_counts[session.pathology] = pathology_counts.get(session.pathology, 0) + 1

        return {
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "pathology_distribution": pathology_counts,
            "avg_messages_per_session": total_messages / len(self.sessions),
        }

    @classmethod
    def get_instance(cls) -> 'ChatManager':
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = ChatManager()
        return cls._instance

    @classmethod
    def set_instance(cls, instance: 'ChatManager') -> None:
        """Set the singleton instance."""
        cls._instance = instance


# ============================================
# Persistence Interface (for future implementation)
# ============================================

class ChatPersistence(ABC):
    """
    Abstract base class for chat persistence.

    Implement this interface to add database storage for chat sessions.
    This prepares the system for future persistence without requiring
    immediate database implementation.
    """

    @abstractmethod
    def save_session(self, session: ChatSession) -> bool:
        """Save a chat session to persistent storage."""
        pass

    @abstractmethod
    def load_session(self, chat_id: str) -> Optional[ChatSession]:
        """Load a chat session from persistent storage."""
        pass

    @abstractmethod
    def delete_session(self, chat_id: str) -> bool:
        """Delete a chat session from persistent storage."""
        pass

    @abstractmethod
    def list_sessions(self, limit: int = 100) -> List[Dict]:
        """List chat sessions from persistent storage."""
        pass


class InMemoryPersistence(ChatPersistence):
    """
    In-memory implementation of ChatPersistence.

    This is the default implementation that stores sessions in memory.
    Useful for development and testing.
    """

    def __init__(self, chat_manager: ChatManager):
        self._manager = chat_manager

    def save_session(self, session: ChatSession) -> bool:
        """Save session to memory (no-op as sessions are already in memory)."""
        return True

    def load_session(self, chat_id: str) -> Optional[ChatSession]:
        """Load session from memory."""
        return self._manager.get_session(chat_id)

    def delete_session(self, chat_id: str) -> bool:
        """Delete session from memory."""
        return self._manager.delete_chat(chat_id)

    def list_sessions(self, limit: int = 100) -> List[Dict]:
        """List sessions from memory."""
        return self._manager.list_chats()[:limit]


