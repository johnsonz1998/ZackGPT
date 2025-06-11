"""
ZackGPT Thread Manager - Database-backed persistent thread and message management
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

from .database import get_database
from .logger import debug_success, debug_error, debug_info


class Thread(BaseModel):
    """Thread model for API responses."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    message_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatMessage(BaseModel):
    """Chat message model for API responses."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PersistentThreadManager:
    """Database-backed thread and message manager."""
    
    def __init__(self):
        self.db = get_database()
        debug_success("Thread manager initialized with database persistence")
    
    # =============================
    #        THREAD OPERATIONS
    # =============================
    
    def create_thread(self, title: str) -> Thread:
        """Create a new conversation thread."""
        thread_data = self.db.create_thread(title)
        debug_success(f"Created thread: {thread_data['title']}", {"thread_id": thread_data['id']})
        
        return Thread(
            id=thread_data['id'],
            title=thread_data['title'],
            created_at=thread_data['created_at'],
            updated_at=thread_data['updated_at'],
            message_count=thread_data['message_count'],
            metadata=thread_data['metadata']
        )
    
    def get_thread(self, thread_id: str) -> Optional[Thread]:
        """Get a specific thread by ID."""
        thread_data = self.db.get_thread(thread_id)
        if not thread_data:
            return None
        
        return Thread(
            id=thread_data['id'],
            title=thread_data['title'],
            created_at=thread_data['created_at'],
            updated_at=thread_data['updated_at'],
            message_count=thread_data['message_count'],
            metadata=thread_data['metadata']
        )
    
    def get_all_threads(self, limit: int = 100, offset: int = 0) -> List[Thread]:
        """Get all threads, ordered by updated_at desc."""
        threads_data = self.db.get_all_threads(limit, offset)
        
        return [Thread(
            id=thread['id'],
            title=thread['title'],
            created_at=thread['created_at'],
            updated_at=thread['updated_at'],
            message_count=thread['message_count'],
            metadata=thread['metadata']
        ) for thread in threads_data]
    
    def update_thread(self, thread_id: str, **updates) -> bool:
        """Update thread properties (title, metadata)."""
        return self.db.update_thread(thread_id, **updates)
    
    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        return self.db.delete_thread(thread_id)
    
    # =============================
    #        MESSAGE OPERATIONS
    # =============================
    
    def add_message(self, thread_id: str, role: str, content: str, 
                   message_id: str = None, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Add a message to a thread."""
        message_data = self.db.add_message(
            thread_id=thread_id,
            role=role,
            content=content,
            message_id=message_id,
            metadata=metadata
        )
        
        return ChatMessage(
            id=message_data['id'],
            thread_id=message_data['thread_id'],
            role=message_data['role'],
            content=message_data['content'],
            timestamp=message_data['timestamp'],
            metadata=message_data['metadata']
        )
    
    def get_message(self, message_id: str) -> Optional[ChatMessage]:
        """Get a specific message by ID."""
        message_data = self.db.get_message(message_id)
        if not message_data:
            return None
        
        return ChatMessage(
            id=message_data['id'],
            thread_id=message_data['thread_id'],
            role=message_data['role'],
            content=message_data['content'],
            timestamp=message_data['timestamp'],
            metadata=message_data['metadata']
        )
    
    def get_messages(self, thread_id: str, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """Get all messages in a thread."""
        messages_data = self.db.get_thread_messages(thread_id, limit, offset)
        
        return [ChatMessage(
            id=msg['id'],
            thread_id=msg['thread_id'],
            role=msg['role'],
            content=msg['content'],
            timestamp=msg['timestamp'],
            metadata=msg['metadata']
        ) for msg in messages_data]
    
    # =============================
    #        CONVENIENCE METHODS
    # =============================
    
    def add_user_message(self, thread_id: str, content: str, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Convenience method to add a user message."""
        return self.add_message(thread_id, "user", content, metadata=metadata)
    
    def add_assistant_message(self, thread_id: str, content: str, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Convenience method to add an assistant message."""
        return self.add_message(thread_id, "assistant", content, metadata=metadata)
    
    def get_conversation_history(self, thread_id: str, limit: int = 50) -> List[Dict[str, str]]:
        """Get conversation history in OpenAI format."""
        messages = self.get_messages(thread_id, limit=limit)
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def get_thread_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of thread with recent activity."""
        thread = self.get_thread(thread_id)
        if not thread:
            return None
        
        recent_messages = self.get_messages(thread_id, limit=5)
        last_message = recent_messages[-1] if recent_messages else None
        
        return {
            "thread": thread.dict(),
            "last_message": last_message.dict() if last_message else None,
            "recent_message_count": len(recent_messages)
        }
    
    # =============================
    #        STATISTICS
    # =============================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get thread and message statistics."""
        return self.db.get_stats()
    
    def search_messages(self, query: str, thread_id: str = None, limit: int = 20) -> List[ChatMessage]:
        """Search messages by content (simple text search)."""
        # For now, implement a simple search. Could be enhanced with full-text search later
        if thread_id:
            all_messages = self.get_messages(thread_id, limit=1000)  # Get more for search
        else:
            # Would need to implement a cross-thread search in database
            debug_info("Cross-thread search not yet implemented")
            return []
        
        # Simple case-insensitive substring search
        query_lower = query.lower()
        matching_messages = [
            msg for msg in all_messages 
            if query_lower in msg.content.lower()
        ]
        
        return matching_messages[:limit] 