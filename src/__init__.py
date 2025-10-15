"""
Knowledge Base Vector Search System

A Python package for ingesting, indexing, and querying knowledge bases using
semantic vector search with Qdrant and sentence transformers.

Main components:
- config: Configuration management with validation
- embeddings: Text embedding generation using SentenceTransformers
- chunkers: Text chunking and Excel processing utilities
- utils: General utility functions for file handling and data processing
- index_qdrant: Qdrant vector database operations
- ingest: Knowledge base ingestion pipeline
- query: Semantic search query interface

Example usage:
    from src import ingest, query
    
    # Ingest knowledge base
    stats = ingest.ingest("./KB", "my_collection")
    
    # Query the knowledge base
    results = query.run_query("What is machine learning?", top_k=5)
    query.pretty_print(results)
"""

__version__ = "1.0.0"
__author__ = "Knowledge Base System"
__description__ = "Semantic vector search system for knowledge bases"

# Import main classes and functions for easy access
from .config import SETTINGS, Settings
from .embeddings import EmbeddingModel
from .chunkers import Chunk, chunk_text, excel_to_text_summaries
from .utils import (
    read_text, list_classes, sha1, save_json, load_json, 
    batched, ensure_directory, get_file_size
)
from .index_qdrant import (
    connect, recreate_collection, upsert_points, search,
    get_collection_info, delete_collection
)
from .advanced_ingest import ingest_advanced
from .query import QueryResult, run_query, run_query_with_stats, pretty_print

__all__ = [
    # Configuration
    "SETTINGS",
    "Settings",
    
    # Core classes
    "EmbeddingModel",
    "Chunk",
    "QueryResult",
    
    # Utility functions
    "read_text",
    "list_classes", 
    "sha1",
    "save_json",
    "load_json",
    "batched",
    "ensure_directory",
    "get_file_size",
    
    # Text processing
    "chunk_text",
    "excel_to_text_summaries",
    
    # Vector database operations
    "connect",
    "recreate_collection",
    "upsert_points",
    "search",
    "get_collection_info",
    "delete_collection",
    
    # Main pipeline functions
    "ingest_advanced",
    "run_query",
    "run_query_with_stats",
    "pretty_print",
]
