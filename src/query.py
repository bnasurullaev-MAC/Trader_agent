from __future__ import annotations
import argparse
import logging
import sys
from typing import Any, Dict, List, Optional

from .config import SETTINGS
from .embeddings import EmbeddingModel
from .index_qdrant import connect, search

logger = logging.getLogger(__name__)

class QueryResult:
    """Represents a single query result with metadata."""
    
    def __init__(self, score: float, payload: Dict[str, Any], result_id: Optional[str] = None):
        self.score = score
        self.payload = payload or {}
        self.result_id = result_id
        
    @property
    def text(self) -> str:
        """Get the text content of the result."""
        return self.payload.get("text", "").strip()
    
    @property
    def source(self) -> str:
        """Get the source of the result."""
        return self.payload.get("source", "unknown")
    
    @property
    def class_id(self) -> str:
        """Get the class ID of the result."""
        return self.payload.get("class_id", "unknown")
    
    @property
    def word_count(self) -> int:
        """Get the word count of the text."""
        return self.payload.get("word_count", len(self.text.split()))
    
    @property
    def chunk_index(self) -> Optional[int]:
        """Get the chunk index."""
        return self.payload.get("chunk_index")

def pretty_print(results: List[QueryResult], max_text_length: int = 260) -> None:
    """
    Print query results in a formatted way.
    
    Args:
        results: List of QueryResult objects
        max_text_length: Maximum length of text to display
    """
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        # Format text
        text = result.text.replace("\n", " ")
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        # Format metadata
        metadata_parts = [
            f"score={result.score:.4f}",
            f"class={result.class_id}",
            f"source={result.source}"
        ]
        
        if result.chunk_index is not None:
            metadata_parts.append(f"chunk={result.chunk_index}")
        
        if result.word_count > 0:
            metadata_parts.append(f"words={result.word_count}")
        
        metadata_str = " | ".join(metadata_parts)
        
        print(f"[{i}] {metadata_str}")
        print(f"    {text}\n")

def run_query(
    question: str, 
    *, 
    top_k: int, 
    filters: Optional[Dict[str, Any]] = None,
    collection: Optional[str] = None
) -> List[QueryResult]:
    """
    Run a semantic search query against the knowledge base.
    
    Args:
        question: Query question or text
        top_k: Number of results to return
        filters: Optional filters to apply
        collection: Optional collection name (defaults to SETTINGS.collection)
        
    Returns:
        List of QueryResult objects
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If query execution fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    
    try:
        logger.info(f"Running query: '{question}' with top_k={top_k}")
        if filters:
            logger.info(f"Applying filters: {filters}")
        
        # Initialize embedding model
        embed = EmbeddingModel(SETTINGS.embedding_model)
        
        # Connect to Qdrant
        client = connect(SETTINGS.qdrant_host, SETTINGS.qdrant_port, SETTINGS.qdrant_api_key)
        
        # Generate query vector
        query_vector = embed.encode([question])[0].tolist()
        
        # Use provided collection or default
        target_collection = collection or SETTINGS.collection
        
        # Perform search
        raw_results = search(client, target_collection, query_vector, top_k, filters)
        
        # Convert to QueryResult objects
        results = []
        for raw_result in raw_results:
            result = QueryResult(
                score=raw_result.score,
                payload=raw_result.payload,
                result_id=getattr(raw_result, 'id', None)
            )
            results.append(result)
        
        logger.info(f"Query returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise RuntimeError(f"Query execution failed: {e}") from e

def run_query_with_stats(
    question: str, 
    *, 
    top_k: int, 
    filters: Optional[Dict[str, Any]] = None,
    collection: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a query and return results with statistics.
    
    Args:
        question: Query question or text
        top_k: Number of results to return
        filters: Optional filters to apply
        collection: Optional collection name
        
    Returns:
        Dictionary containing results and statistics
    """
    import time
    
    start_time = time.time()
    
    try:
        results = run_query(question, top_k=top_k, filters=filters, collection=collection)
        
        # Calculate statistics
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            min_score = min(r.score for r in results)
            max_score = max(r.score for r in results)
            
            # Count by source
            source_counts = {}
            class_counts = {}
            for result in results:
                source_counts[result.source] = source_counts.get(result.source, 0) + 1
                class_counts[result.class_id] = class_counts.get(result.class_id, 0) + 1
        else:
            avg_score = min_score = max_score = 0.0
            source_counts = {}
            class_counts = {}
        
        query_time = time.time() - start_time
        
        return {
            "status": "success",
            "results": results,
            "statistics": {
                "total_results": len(results),
                "query_time_seconds": query_time,
                "avg_score": avg_score,
                "min_score": min_score,
                "max_score": max_score,
                "source_counts": source_counts,
                "class_counts": class_counts
            }
        }
        
    except Exception as e:
        query_time = time.time() - start_time
        return {
            "status": "error",
            "error": str(e),
            "query_time_seconds": query_time,
            "results": []
        }

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Query the knowledge base using semantic search")
    parser.add_argument("--question", type=str, required=True,
                       help="Question or query text to search for")
    parser.add_argument("--top-k", type=int, default=SETTINGS.top_k,
                       help="Number of results to return")
    parser.add_argument("--class-id", type=str, default=None,
                       help="Filter results by class folder name")
    parser.add_argument("--collection", type=str, default=None,
                       help="Qdrant collection name (defaults to settings)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--stats", action="store_true",
                       help="Show query statistics")
    parser.add_argument("--max-text-length", type=int, default=260,
                       help="Maximum length of result text to display")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Build filters
        filters = None
        if args.class_id:
            filters = {"class_id": args.class_id}
        
        if args.stats:
            # Run with statistics
            result = run_query_with_stats(
                args.question, 
                top_k=args.top_k, 
                filters=filters,
                collection=args.collection
            )
            
            if result["status"] == "success":
                stats = result["statistics"]
                print(f"\n[STATS] Query Statistics:")
                print(f"   Query time: {stats['query_time_seconds']:.3f}s")
                print(f"   Total results: {stats['total_results']}")
                print(f"   Score range: {stats['min_score']:.4f} - {stats['max_score']:.4f}")
                print(f"   Average score: {stats['avg_score']:.4f}")
                
                if stats['source_counts']:
                    print(f"   Results by source: {stats['source_counts']}")
                if stats['class_counts']:
                    print(f"   Results by class: {stats['class_counts']}")
                
                pretty_print(result["results"], max_text_length=args.max_text_length)
            else:
                print(f"\n[ERROR] Query failed: {result['error']}")
                sys.exit(1)
        else:
            # Run simple query
            results = run_query(
                args.question, 
                top_k=args.top_k, 
                filters=filters,
                collection=args.collection
            )
            pretty_print(results, max_text_length=args.max_text_length)
            
    except Exception as e:
        print(f"\n[ERROR] Query failed: {e}")
        sys.exit(1)
