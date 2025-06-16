"""
ZackGPT Database Manager - MongoDB-based persistence for all data
"""
import json
import uuid
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import threading
import numpy as np
from openai import OpenAI
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from bson import ObjectId

from .logger import debug_success, debug_error, debug_info, debug_warning


class ZackGPTDatabase:
    """Comprehensive MongoDB database for ZackGPT persistence."""
    
    def __init__(self, mongo_uri: str = None):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongo_uri)
        self.db: Database = self.client.zackgpt
        self.lock = threading.Lock()
        
        # Collections
        self.threads: Collection = self.db.threads
        self.messages: Collection = self.db.messages
        self.memories: Collection = self.db.memories
        self.user_settings: Collection = self.db.user_settings
        self.sessions: Collection = self.db.sessions
        
        # Initialize OpenAI for embeddings
        self.openai_client = OpenAI()
        self.embedding_model = "text-embedding-3-small"
        
        self._setup_indexes()
        debug_success("ZackGPT MongoDB Database initialized", {"uri": self.mongo_uri})
    
    def _setup_indexes(self):
        """Create necessary indexes for efficient querying."""
        try:
            # Threads indexes
            self.threads.create_index([("updated_at", DESCENDING)])
            self.threads.create_index([("created_at", DESCENDING)])
            
            # Messages indexes
            self.messages.create_index([("thread_id", ASCENDING)])
            self.messages.create_index([("timestamp", ASCENDING)])
            self.messages.create_index([("thread_id", ASCENDING), ("timestamp", ASCENDING)])
            
            # Memories indexes
            self.memories.create_index([("question", "text"), ("answer", "text")])
            self.memories.create_index([("timestamp", DESCENDING)])
            self.memories.create_index([("importance", ASCENDING)])
            self.memories.create_index([("tags", ASCENDING)])
            self.memories.create_index([("agent", ASCENDING)])
            
            # Settings indexes
            self.user_settings.create_index([("key", ASCENDING)], unique=True)
            
            # Sessions indexes
            self.sessions.create_index([("expires_at", ASCENDING)])
            self.sessions.create_index([("created_at", DESCENDING)])
            
            debug_success("Created MongoDB indexes")
        except Exception as e:
            debug_error("Failed to create indexes", e)
    
    # =============================
    #        THREAD OPERATIONS
    # =============================
    
    def create_thread(self, title: str, thread_id: str = None) -> Dict[str, Any]:
        """Create a new conversation thread."""
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        thread_doc = {
            "_id": thread_id,
            "title": title,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0,
            "metadata": {}
        }
        
        self.threads.insert_one(thread_doc)
        debug_success("Created thread", {"id": thread_id, "title": title})
        return self.get_thread(thread_id)
    
    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific thread by ID."""
        thread = self.threads.find_one({"_id": thread_id})
        if thread:
            return {
                "id": thread["_id"],
                "title": thread["title"],
                "created_at": thread["created_at"],
                "updated_at": thread["updated_at"],
                "message_count": thread["message_count"],
                "metadata": thread.get("metadata", {})
            }
        return None
    
    def get_all_threads(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all threads, ordered by updated_at desc."""
        threads = self.threads.find().sort("updated_at", DESCENDING).skip(offset).limit(limit)
        
        return [{
            "id": thread["_id"],
            "title": thread["title"],
            "created_at": thread["created_at"],
            "updated_at": thread["updated_at"],
            "message_count": thread["message_count"],
            "metadata": thread.get("metadata", {})
        } for thread in threads]
    
    def update_thread(self, thread_id: str, **updates) -> bool:
        """Update thread properties."""
        update_data = {}
        
        for key, value in updates.items():
            if key in ["title", "metadata"]:
                update_data[key] = value
        
        if not update_data:
            return False
        
        update_data["updated_at"] = datetime.now()
        
        result = self.threads.update_one(
            {"_id": thread_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        # Delete messages first
        self.messages.delete_many({"thread_id": thread_id})
        
        # Delete the thread
        result = self.threads.delete_one({"_id": thread_id})
        
        deleted = result.deleted_count > 0
        if deleted:
            debug_info("Deleted thread", {"id": thread_id})
        return deleted
    
    # =============================
    #        MESSAGE OPERATIONS
    # =============================
    
    def add_message(self, thread_id: str, role: str, content: str, 
                   message_id: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Add a message to a thread."""
        if not message_id:
            message_id = str(uuid.uuid4())
        
        message_doc = {
            "_id": message_id,
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        
        self.messages.insert_one(message_doc)
        
        # Update thread message count and updated_at
        message_count = self.messages.count_documents({"thread_id": thread_id})
        self.threads.update_one(
            {"_id": thread_id},
            {
                "$set": {
                    "message_count": message_count,
                    "updated_at": datetime.now()
                }
            }
        )
        
        debug_info("Added message", {"thread_id": thread_id, "role": role})
        return self.get_message(message_id)
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message by ID."""
        message = self.messages.find_one({"_id": message_id})
        if message:
            return {
                "id": message["_id"],
                "thread_id": message["thread_id"],
                "role": message["role"],
                "content": message["content"],
                "timestamp": message["timestamp"],
                "metadata": message.get("metadata", {})
            }
        return None
    
    def get_thread_messages(self, thread_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all messages in a thread."""
        messages = self.messages.find(
            {"thread_id": thread_id}
        ).sort("timestamp", ASCENDING).skip(offset).limit(limit)
        
        return [{
            "id": message["_id"],
            "thread_id": message["thread_id"],
            "role": message["role"],
            "content": message["content"],
            "timestamp": message["timestamp"],
            "metadata": message.get("metadata", {})
        } for message in messages]
    
    # =============================
    #        MEMORY OPERATIONS
    # =============================
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI's API."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            debug_error("Failed to generate embedding", e)
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def save_memory(self, question: str, answer: str, agent: str = "core_assistant",
                   importance: str = "medium", tags: List[str] = None,
                   similarity_threshold: float = 0.95) -> Optional[str]:
        """Save a memory with deduplication."""
        try:
            # Generate embedding
            combined_text = f"{question} {answer}"
            embedding = self._generate_embedding(combined_text)
            
            if not embedding:
                debug_error("Failed to generate embedding for memory")
                return None
            
            # Check for similar memories to avoid duplicates
            recent_memories = self.query_memories_by_similarity(
                combined_text, limit=10, similarity_threshold=similarity_threshold
            )
            
            if recent_memories:
                debug_info("Skipped saving memory due to high similarity", {
                    "similarity": recent_memories[0]["similarity"],
                    "existing_question": recent_memories[0]["question"]
                })
                return None
            
            memory_id = str(uuid.uuid4())
            
            memory_doc = {
                "_id": memory_id,
                "question": question,
                "answer": answer,
                "agent": agent,
                "importance": importance,
                "tags": tags or [],
                "embedding": embedding,
                "timestamp": datetime.now(),
                "metadata": {}
            }
            
            self.memories.insert_one(memory_doc)
            
            debug_success("Saved memory", {
                "id": memory_id,
                "question": question[:50] + "...",
                "importance": importance
            })
            return memory_id
            
        except Exception as e:
            debug_error("Failed to save memory", e)
            return None
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID."""
        memory = self.memories.find_one({"_id": memory_id})
        if memory:
            return {
                "id": memory["_id"],
                "question": memory["question"],
                "answer": memory["answer"],
                "agent": memory["agent"],
                "importance": memory["importance"],
                "tags": memory.get("tags", []),
                "timestamp": memory["timestamp"],
                "metadata": memory.get("metadata", {})
            }
        return None
    
    def query_memories(self, query: str, limit: int = 5, agent: str = None,
                      importance: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Query memories by text similarity."""
        return self.query_memories_by_similarity(query, limit, agent, importance, tags, 0.3)
    
    def query_memories_by_similarity(self, query: str, limit: int = 5, 
                                   agent: str = None, importance: str = None, 
                                   tags: List[str] = None,
                                   similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Query memories by semantic similarity."""
        try:
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # Build filter
            filter_query = {}
            if agent:
                filter_query["agent"] = agent
            if importance:
                filter_query["importance"] = importance
            if tags:
                filter_query["tags"] = {"$in": tags}
            
            # Get all matching memories
            memories = list(self.memories.find(filter_query).sort("timestamp", DESCENDING))
            
            # Calculate similarities and filter
            results = []
            for memory in memories:
                embedding = memory.get("embedding", [])
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                if similarity >= similarity_threshold:
                    memory_result = {
                        "id": memory["_id"],
                        "question": memory["question"],
                        "answer": memory["answer"],
                        "agent": memory["agent"],
                        "importance": memory["importance"],
                        "tags": memory.get("tags", []),
                        "timestamp": memory["timestamp"],
                        "metadata": memory.get("metadata", {}),
                        "similarity": similarity
                    }
                    results.append(memory_result)
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:limit]
                
        except Exception as e:
            debug_error("Failed to query memories", e)
            return []
    
    def update_memory(self, memory_id: str, **updates) -> bool:
        """Update a memory."""
        try:
            update_data = {}
            
            for key, value in updates.items():
                if key in ["question", "answer", "agent", "importance", "tags", "metadata"]:
                    update_data[key] = value
            
            if not update_data:
                return False
            
            # If question or answer changed, regenerate embedding
            if "question" in updates or "answer" in updates:
                memory = self.get_memory(memory_id)
                if memory:
                    new_question = updates.get("question", memory["question"])
                    new_answer = updates.get("answer", memory["answer"])
                    new_embedding = self._generate_embedding(f"{new_question} {new_answer}")
                    if new_embedding:
                        update_data["embedding"] = new_embedding
            
            result = self.memories.update_one(
                {"_id": memory_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                debug_info("Updated memory", {"id": memory_id})
                return True
            return False
            
        except Exception as e:
            debug_error("Failed to update memory", e)
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        result = self.memories.delete_one({"_id": memory_id})
        
        deleted = result.deleted_count > 0
        if deleted:
            debug_info("Deleted memory", {"id": memory_id})
        return deleted
    
    # =============================
    #        SETTINGS OPERATIONS
    # =============================
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a user setting."""
        self.user_settings.update_one(
            {"key": key},
            {
                "$set": {
                    "key": key,
                    "value": value,
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a user setting."""
        setting = self.user_settings.find_one({"key": key})
        if setting:
            return setting["value"]
        return default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings."""
        settings = self.user_settings.find()
        return {setting["key"]: setting["value"] for setting in settings}
    
    # =============================
    #        SESSION OPERATIONS
    # =============================
    
    def set_session(self, session_id: str, data: Dict, expires_at: datetime = None) -> None:
        """Set session data."""
        if not expires_at:
            expires_at = datetime.now() + timedelta(hours=24)
        
        self.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "session_id": session_id,
                    "data": data,
                    "expires_at": expires_at,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        session = self.sessions.find_one({
            "session_id": session_id,
            "expires_at": {"$gt": datetime.now()}
        })
        return session["data"] if session else None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        result = self.sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    # =============================
    #        UTILITY OPERATIONS
    # =============================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        return {
            "threads": self.threads.count_documents({}),
            "messages": self.messages.count_documents({}),
            "memories": self.memories.count_documents({}),
            "settings": self.user_settings.count_documents({}),
            "sessions": self.sessions.count_documents({}),
            "memory_stats": {
                "by_importance": {
                    "high": self.memories.count_documents({"importance": "high"}),
                    "medium": self.memories.count_documents({"importance": "medium"}),
                    "low": self.memories.count_documents({"importance": "low"})
                }
            }
        }
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data (optional maintenance)."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean old sessions
        result = self.sessions.delete_many({
            "$or": [
                {"expires_at": {"$lt": datetime.now()}},
                {"created_at": {"$lt": cutoff_date}}
            ]
        })
        sessions_deleted = result.deleted_count
        
        return {
            "sessions_deleted": sessions_deleted,
            "cutoff_date": cutoff_date.isoformat()
        }


# Global database instance
db = None

def get_database() -> ZackGPTDatabase:
    """Get the global database instance."""
    global db
    if db is None:
        db = ZackGPTDatabase()
    return db 