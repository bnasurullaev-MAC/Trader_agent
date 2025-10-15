from __future__ import annotations
import os
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    """Configuration settings for the knowledge base system."""
    
    # Qdrant connection settings
    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    collection: str = os.getenv("QDRANT_COLLECTION", "kb_vectors")

    # Embedding model settings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    batch_size: int = int(os.getenv("BATCH_SIZE", "64"))

    # Knowledge base settings
    kb_root: str = os.getenv("KB_ROOT", "./KB")
    max_chunk_words: int = int(os.getenv("MAX_CHUNK_WORDS", "1000"))
    chunk_overlap_words: int = int(os.getenv("CHUNK_OVERLAP_WORDS", "200"))

    # Query settings
    top_k: int = int(os.getenv("TOP_K", "5"))

    def __post_init__(self) -> None:
        """Validate configuration settings after initialization."""
        self._validate_settings()

    def _validate_settings(self) -> None:
        """Validate configuration settings and warn about potential issues."""
        # Validate port range
        if not (1 <= self.qdrant_port <= 65535):
            warnings.warn(f"Qdrant port {self.qdrant_port} is outside valid range (1-65535)")
        
        # Validate batch size
        if self.batch_size <= 0:
            warnings.warn(f"Batch size {self.batch_size} should be positive")
        elif self.batch_size > 1000:
            warnings.warn(f"Large batch size {self.batch_size} may cause memory issues")
        
        # Validate chunk settings
        if self.max_chunk_words <= 0:
            warnings.warn(f"Max chunk words {self.max_chunk_words} should be positive")
        
        if self.chunk_overlap_words < 0:
            warnings.warn(f"Chunk overlap words {self.chunk_overlap_words} should be non-negative")
        
        if self.chunk_overlap_words >= self.max_chunk_words:
            warnings.warn(f"Chunk overlap {self.chunk_overlap_words} should be less than max chunk size {self.max_chunk_words}")
        
        # Validate top_k
        if self.top_k <= 0:
            warnings.warn(f"Top K {self.top_k} should be positive")
        
        # Check if KB root exists
        kb_path = Path(self.kb_root)
        if not kb_path.exists():
            warnings.warn(f"Knowledge base root path does not exist: {self.kb_root}")
        
        # Validate collection name
        if not self.collection or not self.collection.replace("_", "").replace("-", "").isalnum():
            warnings.warn(f"Collection name '{self.collection}' may not be valid for Qdrant")

SETTINGS = Settings()
