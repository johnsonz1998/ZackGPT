"""
ZackGPT Database Manager - SQLite-based persistence for threads, messages, and memories
"""
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import threading
from contextlib import contextmanager
import numpy as np
from openai import OpenAI

from .logger import debug_success, debug_error, debug_info, debug_warning


class ZackGPTDatabase:
    """Comprehensive SQLite database for ZackGPT persistence."""
    
    def __init__(self, db_path: str = "data/zackgpt.db"):
        self.db_path_str = db_path
        if db_path != ":memory:":
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(exist_ok=True)
        else:
            self.db_path = db_path  # Keep as string for in-memory
        self.lock = threading.Lock()
        
        # Initialize OpenAI for embeddings
        self.openai_client = OpenAI()
        self.embedding_model = "text-embedding-3-small"
        
        self._init_database()
        debug_success("ZackGPT Database initialized", {"path": str(self.db_path)})
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with proper locking."""
        with self.lock:
            # Use the string path directly for in-memory, Path object for files
            db_path = self.db_path if isinstance(self.db_path, str) else str(self.db_path)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def _init_database(self):
        """Initialize all database tables."""
        with self.get_connection() as conn:
            # Threads table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT  -- JSON field for additional data
                )
            """)
            
            # Messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,  -- JSON field for additional data
                    FOREIGN KEY (thread_id) REFERENCES threads (id) ON DELETE CASCADE
                )
            """)
            
            # Memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    agent TEXT DEFAULT 'core_assistant',
                    importance TEXT DEFAULT 'medium',
                    tags TEXT,  -- JSON array of tags
                    embedding TEXT,  -- JSON array of embedding values
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT  -- JSON field for additional data
                )
            """)
            
            # User preferences/settings table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Session data table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,  -- JSON field
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_timestamp ON memories(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_agent ON memories(agent)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_threads_updated ON threads(updated_at)")
            
            conn.commit()
    
    # =============================
    #        THREAD OPERATIONS
    # =============================
    
    def create_thread(self, title: str, thread_id: str = None) -> Dict[str, Any]:
        """Create a new conversation thread."""
        if not thread_id:
            thread_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO threads (id, title, created_at, updated_at, message_count)
                VALUES (?, ?, ?, ?, 0)
            """, (thread_id, title, datetime.now(), datetime.now()))
            conn.commit()
        
        debug_success("Created thread", {"id": thread_id, "title": title})
        return self.get_thread(thread_id)
    
    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific thread by ID."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT id, title, created_at, updated_at, message_count, metadata
                FROM threads WHERE id = ?
            """, (thread_id,)).fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "title": row["title"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "message_count": row["message_count"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
        return None
    
    def get_all_threads(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all threads, ordered by updated_at desc."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT id, title, created_at, updated_at, message_count, metadata
                FROM threads 
                ORDER BY updated_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
            
            return [{
                "id": row["id"],
                "title": row["title"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "message_count": row["message_count"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            } for row in rows]
    
    def update_thread(self, thread_id: str, **updates) -> bool:
        """Update thread properties."""
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ["title", "metadata"]:
                set_clauses.append(f"{key} = ?")
                values.append(json.dumps(value) if key == "metadata" else value)
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = ?")
        values.append(datetime.now())
        values.append(thread_id)
        
        with self.get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE threads SET {', '.join(set_clauses)}
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        with self.get_connection() as conn:
            # Delete messages first (though CASCADE should handle this)
            conn.execute("DELETE FROM messages WHERE thread_id = ?", (thread_id,))
            
            # Delete the thread
            cursor = conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
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
        
        with self.get_connection() as conn:
            # Insert the message
            conn.execute("""
                INSERT INTO messages (id, thread_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message_id, thread_id, role, content, 
                datetime.now(), 
                json.dumps(metadata) if metadata else None
            ))
            
            # Update thread message count and updated_at
            conn.execute("""
                UPDATE threads SET 
                    message_count = (SELECT COUNT(*) FROM messages WHERE thread_id = ?),
                    updated_at = ?
                WHERE id = ?
            """, (thread_id, datetime.now(), thread_id))
            
            conn.commit()
        
        debug_info("Added message", {"thread_id": thread_id, "role": role})
        return self.get_message(message_id)
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific message by ID."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT id, thread_id, role, content, timestamp, metadata
                FROM messages WHERE id = ?
            """, (message_id,)).fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "thread_id": row["thread_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                }
        return None
    
    def get_thread_messages(self, thread_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all messages in a thread."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT id, thread_id, role, content, timestamp, metadata
                FROM messages 
                WHERE thread_id = ? 
                ORDER BY timestamp ASC 
                LIMIT ? OFFSET ?
            """, (thread_id, limit, offset)).fetchall()
            
            return [{
                "id": row["id"],
                "thread_id": row["thread_id"],
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            } for row in rows]
    
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
            
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO memories (id, question, answer, agent, importance, tags, embedding, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id, question, answer, agent, importance,
                    json.dumps(tags or []),
                    json.dumps(embedding),
                    datetime.now()
                ))
                conn.commit()
            
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
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT id, question, answer, agent, importance, tags, timestamp, metadata
                FROM memories WHERE id = ?
            """, (memory_id,)).fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "agent": row["agent"],
                    "importance": row["importance"],
                    "tags": json.loads(row["tags"]) if row["tags"] else [],
                    "timestamp": row["timestamp"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
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
            
            # Build WHERE clause for filters
            where_conditions = []
            params = []
            
            if agent:
                where_conditions.append("agent = ?")
                params.append(agent)
            
            if importance:
                where_conditions.append("importance = ?")
                params.append(importance)
            
            where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
            
            with self.get_connection() as conn:
                rows = conn.execute(f"""
                    SELECT id, question, answer, agent, importance, tags, embedding, timestamp, metadata
                    FROM memories 
                    {where_clause}
                    ORDER BY timestamp DESC
                """, params).fetchall()
                
                # Calculate similarities and filter
                results = []
                for row in rows:
                    embedding = json.loads(row["embedding"]) if row["embedding"] else []
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    
                    if similarity >= similarity_threshold:
                        memory = {
                            "id": row["id"],
                            "question": row["question"],
                            "answer": row["answer"],
                            "agent": row["agent"],
                            "importance": row["importance"],
                            "tags": json.loads(row["tags"]) if row["tags"] else [],
                            "timestamp": row["timestamp"],
                            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                            "similarity": similarity
                        }
                        
                        # Filter by tags if specified
                        if tags:
                            memory_tags = memory["tags"]
                            if not any(tag in memory_tags for tag in tags):
                                continue
                        
                        results.append(memory)
                
                # Sort by similarity and return top results
                results.sort(key=lambda x: x["similarity"], reverse=True)
                return results[:limit]
                
        except Exception as e:
            debug_error("Failed to query memories", e)
            return []
    
    def update_memory(self, memory_id: str, **updates) -> bool:
        """Update a memory."""
        try:
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ["question", "answer", "agent", "importance", "tags", "metadata"]:
                    set_clauses.append(f"{key} = ?")
                    if key in ["tags", "metadata"]:
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
            
            if not set_clauses:
                return False
            
            # If question or answer changed, regenerate embedding
            if "question" in updates or "answer" in updates:
                memory = self.get_memory(memory_id)
                if memory:
                    new_question = updates.get("question", memory["question"])
                    new_answer = updates.get("answer", memory["answer"])
                    new_embedding = self._generate_embedding(f"{new_question} {new_answer}")
                    if new_embedding:
                        set_clauses.append("embedding = ?")
                        values.append(json.dumps(new_embedding))
            
            values.append(memory_id)
            
            with self.get_connection() as conn:
                cursor = conn.execute(f"""
                    UPDATE memories SET {', '.join(set_clauses)}
                    WHERE id = ?
                """, values)
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            debug_error("Failed to update memory", e)
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                debug_info("Deleted memory", {"id": memory_id})
            return deleted
    
    # =============================
    #        SETTINGS OPERATIONS
    # =============================
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a user setting."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(value), datetime.now()))
            conn.commit()
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a user setting."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT value FROM user_settings WHERE key = ?
            """, (key,)).fetchone()
            
            if row:
                return json.loads(row["value"])
            return default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all user settings."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT key, value FROM user_settings
            """).fetchall()
            
            return {row["key"]: json.loads(row["value"]) for row in rows}
    
    # =============================
    #        STATISTICS
    # =============================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {}
            
            # Thread stats
            thread_stats = conn.execute("""
                SELECT COUNT(*) as total, 
                       SUM(message_count) as total_messages,
                       MAX(updated_at) as last_activity
                FROM threads
            """).fetchone()
            
            stats["threads"] = {
                "total": thread_stats["total"],
                "total_messages": thread_stats["total_messages"] or 0,
                "last_activity": thread_stats["last_activity"]
            }
            
            # Memory stats
            memory_stats = conn.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN importance = 'high' THEN 1 END) as high_importance,
                       COUNT(CASE WHEN importance = 'medium' THEN 1 END) as medium_importance,
                       COUNT(CASE WHEN importance = 'low' THEN 1 END) as low_importance
                FROM memories
            """).fetchone()
            
            stats["memories"] = {
                "total": memory_stats["total"],
                "by_importance": {
                    "high": memory_stats["high_importance"],
                    "medium": memory_stats["medium_importance"],
                    "low": memory_stats["low_importance"]
                }
            }
            
            # Database size
            db_size = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()").fetchone()
            stats["database"] = {
                "size_bytes": db_size["size"],
                "size_mb": round(db_size["size"] / (1024 * 1024), 2)
            }
            
            return stats
    
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data (optional maintenance)."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            # Clean old sessions
            cursor = conn.execute("""
                DELETE FROM sessions WHERE expires_at < ? OR created_at < ?
            """, (datetime.now(), cutoff_date))
            sessions_deleted = cursor.rowcount
            
            conn.commit()
            
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