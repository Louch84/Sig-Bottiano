
"""
Vector Memory System
Hybrid: SQLite + Simple embeddings for fast retrieval
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

class VectorMemory:
    """
    Enhanced memory with vector similarity search.
    Falls back to keyword search if vectors unavailable.
    """
    
    def __init__(self, db_path: str = "memory/vector_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite with vector capabilities"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                embedding BLOB,  -- Simple numpy array
                metadata TEXT,    -- JSON
                timestamp TEXT,
                category TEXT,    -- user, system, lesson
                importance REAL   -- 0-1 score
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
        conn.commit()
        conn.close()
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Simple word-frequency embedding.
        Not as good as OpenAI but works locally.
        """
        # Normalize
        text = text.lower()
        words = text.split()
        
        # Create simple bag-of-words vector (256 dim)
        vector = np.zeros(256)
        for word in words:
            # Hash word to index
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % 256
            vector[idx] += 1
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector.astype(np.float32)
    
    def _similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity"""
        return float(np.dot(a, b))
    
    def store(self, content: str, category: str = "general", 
              importance: float = 0.5, metadata: dict = None):
        """Store memory with embedding"""
        
        embedding = self._simple_embedding(content)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO memories (content, embedding, metadata, timestamp, category, importance) VALUES (?, ?, ?, ?, ?, ?)",
            (
                content,
                embedding.tobytes(),
                json.dumps(metadata or {}),
                datetime.now().isoformat(),
                category,
                importance
            )
        )
        conn.commit()
        conn.close()
    
    def search(self, query: str, category: Optional[str] = None, 
               top_k: int = 5) -> List[Dict]:
        """Semantic search with vector similarity"""
        
        query_vec = self._simple_embedding(query)
        
        conn = sqlite3.connect(self.db_path)
        
        # Build query
        if category:
            cursor = conn.execute(
                "SELECT content, embedding, metadata, timestamp, importance FROM memories WHERE category = ?",
                (category,)
            )
        else:
            cursor = conn.execute(
                "SELECT content, embedding, metadata, timestamp, importance FROM memories"
            )
        
        results = []
        for row in cursor:
            content, emb_bytes, meta_json, timestamp, importance = row
            
            if emb_bytes:
                stored_vec = np.frombuffer(emb_bytes, dtype=np.float32)
                similarity = self._similarity(query_vec, stored_vec)
            else:
                # Fallback to keyword matching
                similarity = self._keyword_similarity(query, content)
            
            results.append({
                'content': content,
                'similarity': similarity,
                'metadata': json.loads(meta_json),
                'timestamp': timestamp,
                'importance': importance
            })
        
        conn.close()
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def _keyword_similarity(self, query: str, content: str) -> float:
        """Fallback keyword matching"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0
        
        overlap = len(query_words & content_words)
        return overlap / len(query_words)

# Usage
memory = VectorMemory()
