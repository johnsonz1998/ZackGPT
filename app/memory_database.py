import json
import numpy as np
import faiss
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from openai import OpenAI

import config
from app.debug_logger import debug_log, debug_info, debug_error, debug_warning

@dataclass
class MemoryScore:
    semantic_similarity: float
    tag_match_score: float
    importance_score: float
    recency_score: float
    total_score: float

class MemoryDatabase:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.memories: List[Dict[str, Any]] = []
        self.index = None
        self.embedding_dim = 1536  # Dimension for text-embedding-3-small
        
        # Scoring weights
        self.weights = {
            "semantic": 0.4,
            "tags": 0.2,
            "importance": 0.2,
            "recency": 0.2
        }
        
    def load_memories(self) -> None:
        """Load memories from JSON files and build the FAISS index."""
        try:
            memory_dir = Path("memories")
            if not memory_dir.exists():
                debug_warning("Memory directory not found", str(memory_dir))
                return
                
            self.memories = []
            for file in memory_dir.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        memory = json.load(f)
                        if "embedding" in memory:
                            self.memories.append(memory)
                except Exception as e:
                    debug_error(f"Error loading memory file {file}", e)
                    
            if not self.memories:
                debug_warning("No memories found with embeddings")
                return
                
            # Build FAISS index
            embeddings = np.array([m["embedding"] for m in self.memories])
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index.add(embeddings.astype('float32'))
            
            debug_success("Memory database initialized", {
                "num_memories": len(self.memories),
                "index_size": self.index.ntotal
            })
            
        except Exception as e:
            debug_error("Failed to initialize memory database", e)
            
    def calculate_scores(self, query: str, memory: Dict[str, Any]) -> MemoryScore:
        """Calculate various scores for a memory based on the query."""
        try:
            # Get query embedding
            query_embedding = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            ).data[0].embedding
            
            # Semantic similarity (cosine similarity)
            memory_embedding = np.array(memory["embedding"])
            semantic_sim = np.dot(query_embedding, memory_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(memory_embedding)
            )
            
            # Tag matching
            query_tags = set(tag.lower() for tag in query.split())
            memory_tags = set(tag.lower() for tag in memory.get("tags", []))
            tag_match = len(query_tags & memory_tags) / max(len(query_tags), 1)
            
            # Importance scoring
            importance_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
            importance_score = importance_map.get(memory.get("importance", "medium"), 0.6)
            
            # Recency scoring (exponential decay over 30 days)
            memory_date = datetime.fromisoformat(memory.get("timestamp", datetime.now().isoformat()))
            days_old = (datetime.now() - memory_date).days
            recency_score = np.exp(-days_old / 30)  # Decay over 30 days
            
            # Calculate total weighted score
            total_score = (
                self.weights["semantic"] * semantic_sim +
                self.weights["tags"] * tag_match +
                self.weights["importance"] * importance_score +
                self.weights["recency"] * recency_score
            )
            
            return MemoryScore(
                semantic_similarity=semantic_sim,
                tag_match_score=tag_match,
                importance_score=importance_score,
                recency_score=recency_score,
                total_score=total_score
            )
            
        except Exception as e:
            debug_error("Error calculating memory scores", e)
            return MemoryScore(0, 0, 0, 0, 0)
            
    def query(self, query: str, threshold: float = 0.6, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query memories using the combined scoring system."""
        if not self.index or not self.memories:
            debug_warning("Memory database not initialized")
            return []
            
        try:
            # Get query embedding
            query_embedding = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            ).data[0].embedding
            
            # Get initial candidates using FAISS
            D, I = self.index.search(
                np.array([query_embedding]).astype('float32'),
                min(top_k * 2, len(self.memories))
            )
            
            # Score and filter candidates
            scored_memories = []
            for idx in I[0]:
                memory = self.memories[idx]
                scores = self.calculate_scores(query, memory)
                
                if scores.total_score >= threshold:
                    scored_memories.append({
                        "memory": memory,
                        "scores": scores
                    })
                    
            # Sort by total score and take top_k
            scored_memories.sort(key=lambda x: x["scores"].total_score, reverse=True)
            results = scored_memories[:top_k]
            
            debug_info("Memory query results", {
                "query": query,
                "num_results": len(results),
                "threshold": threshold
            })
            
            return results
            
        except Exception as e:
            debug_error("Error querying memories", e)
            return []
            
    def get_memory_context(self, query: str, threshold: float = 0.6, top_k: int = 5) -> str:
        """Get formatted context from relevant memories."""
        results = self.query(query, threshold, top_k)
        
        if not results:
            return ""
            
        context_parts = []
        for result in results:
            memory = result["memory"]
            scores = result["scores"]
            
            context_parts.append(
                f"Memory: {memory['question']}\n"
                f"Answer: {memory['answer']}\n"
                f"Tags: {', '.join(memory.get('tags', []))}\n"
                f"Importance: {memory.get('importance', 'medium')}\n"
                f"Relevance: {scores.total_score:.2f}\n"
            )
            
        return "\n".join(context_parts) 