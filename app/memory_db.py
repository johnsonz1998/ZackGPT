from typing import List, Dict, Optional, Any
from datetime import datetime
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
import numpy as np
from openai import OpenAI
from .debug_logger import debug_log, debug_error, debug_info, debug_success

class MemoryDatabase:
    def __init__(self, mongo_uri: str = None):
        """Initialize MongoDB connection and setup collections."""
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongo_uri)
        self.db: Database = self.client.zackgpt
        self.memories: Collection = self.db.memories
        self.embeddings: Collection = self.db.embeddings
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI()
        self.embedding_model = "text-embedding-3-small"
        
        # Create indexes
        self._setup_indexes()
        
    def _setup_indexes(self):
        """Create necessary indexes for efficient querying."""
        try:
            # Text index for semantic search
            self.memories.create_index([("question", "text"), ("answer", "text")])
            
            # Index for timestamp-based queries
            self.memories.create_index([("timestamp", DESCENDING)])
            
            # Index for importance-based queries
            self.memories.create_index([("importance", ASCENDING)])
            
            # Index for tag-based queries
            self.memories.create_index([("tags", ASCENDING)])
            
            # Index for agent-based queries
            self.memories.create_index([("agent", ASCENDING)])
            
            debug_success("Created MongoDB indexes")
        except Exception as e:
            debug_error("Failed to create indexes", e)
            
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
            
    def save_memory(self, question: str, answer: str, agent: str = "core_assistant", 
                   importance: str = "medium", tags: List[str] = None) -> str:
        """Save a new memory to MongoDB."""
        try:
            # Generate embeddings
            question_embedding = self._generate_embedding(question)
            answer_embedding = self._generate_embedding(answer)
            
            # Create memory document
            memory_doc = {
                "timestamp": datetime.utcnow(),
                "question": question,
                "answer": answer,
                "agent": agent,
                "importance": importance,
                "tags": tags or [],
                "question_embedding": question_embedding,
                "answer_embedding": answer_embedding
            }
            
            # Insert into MongoDB
            result = self.memories.insert_one(memory_doc)
            memory_id = str(result.inserted_id)
            
            debug_success("Saved memory to MongoDB", {
                "id": memory_id,
                "question": question[:50] + "...",
                "importance": importance
            })
            
            return memory_id
            
        except Exception as e:
            debug_error("Failed to save memory", e)
            return None
            
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Retrieve a specific memory by ID."""
        try:
            memory = self.memories.find_one({"_id": memory_id})
            if memory:
                memory["_id"] = str(memory["_id"])  # Convert ObjectId to string
            return memory
        except Exception as e:
            debug_error("Failed to get memory", e)
            return None
            
    def query_memories(self, query: str, limit: int = 5, 
                      min_importance: str = None,
                      tags: List[str] = None,
                      start_date: datetime = None,
                      end_date: datetime = None) -> List[Dict]:
        """Query memories using semantic similarity and filters."""
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build filter
            filter_query = {}
            if min_importance:
                filter_query["importance"] = {"$gte": min_importance}
            if tags:
                filter_query["tags"] = {"$in": tags}
            if start_date:
                filter_query["timestamp"] = {"$gte": start_date}
            if end_date:
                filter_query["timestamp"] = {"$lte": end_date}
                
            # Find similar memories using vector similarity
            pipeline = [
                {"$match": filter_query},
                {"$addFields": {
                    "question_similarity": {
                        "$function": {
                            "body": """
                            function(question_embedding, query_embedding) {
                                let dotProduct = 0;
                                let normA = 0;
                                let normB = 0;
                                for (let i = 0; i < question_embedding.length; i++) {
                                    dotProduct += question_embedding[i] * query_embedding[i];
                                    normA += question_embedding[i] * question_embedding[i];
                                    normB += query_embedding[i] * query_embedding[i];
                                }
                                return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
                            }
                            """,
                            "args": ["$question_embedding", query_embedding],
                            "lang": "js"
                        }
                    }
                }},
                {"$sort": {"question_similarity": -1}},
                {"$limit": limit}
            ]
            
            results = list(self.memories.aggregate(pipeline))
            
            # Convert ObjectIds to strings
            for result in results:
                result["_id"] = str(result["_id"])
                
            debug_success("Queried memories", {
                "query": query[:50] + "...",
                "results": len(results)
            })
            
            return results
            
        except Exception as e:
            debug_error("Failed to query memories", e)
            return []
            
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory."""
        try:
            # If question or answer is updated, regenerate embeddings
            if "question" in updates:
                updates["question_embedding"] = self._generate_embedding(updates["question"])
            if "answer" in updates:
                updates["answer_embedding"] = self._generate_embedding(updates["answer"])
                
            result = self.memories.update_one(
                {"_id": memory_id},
                {"$set": updates}
            )
            
            success = result.modified_count > 0
            if success:
                debug_success("Updated memory", {"id": memory_id})
            else:
                debug_info("No changes made to memory", {"id": memory_id})
                
            return success
            
        except Exception as e:
            debug_error("Failed to update memory", e)
            return False
            
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        try:
            result = self.memories.delete_one({"_id": memory_id})
            success = result.deleted_count > 0
            
            if success:
                debug_success("Deleted memory", {"id": memory_id})
            else:
                debug_info("Memory not found", {"id": memory_id})
                
            return success
            
        except Exception as e:
            debug_error("Failed to delete memory", e)
            return False
            
    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories."""
        try:
            stats = {
                "total_memories": self.memories.count_documents({}),
                "by_importance": {
                    "high": self.memories.count_documents({"importance": "high"}),
                    "medium": self.memories.count_documents({"importance": "medium"}),
                    "low": self.memories.count_documents({"importance": "low"})
                },
                "by_agent": {},
                "by_tag": {}
            }
            
            # Get counts by agent
            agent_counts = self.memories.aggregate([
                {"$group": {"_id": "$agent", "count": {"$sum": 1}}}
            ])
            for agent in agent_counts:
                stats["by_agent"][agent["_id"]] = agent["count"]
                
            # Get counts by tag
            tag_counts = self.memories.aggregate([
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}}
            ])
            for tag in tag_counts:
                stats["by_tag"][tag["_id"]] = tag["count"]
                
            return stats
            
        except Exception as e:
            debug_error("Failed to get memory stats", e)
            return {} 