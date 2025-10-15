"""
RAG (Retrieval-Augmented Generation) query module with Gemini AI integration.

This module provides enhanced query capabilities that combine semantic search
with AI-generated responses using Google's Gemini API.
"""

from __future__ import annotations
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Suppress gRPC warnings
os.environ.setdefault("GRPC_VERBOSITY", "NONE")

from .config import SETTINGS
from .query import QueryResult, run_query
from .gemini_client import create_gemini_client, GeminiClient

logger = logging.getLogger(__name__)


class RAGQueryResult:
    """
    Enhanced query result with Gemini-generated response.
    
    Contains the generated response, context chunks used, and metadata
    about the generation process.
    """
    
    def __init__(
        self, 
        question: str, 
        response: str, 
        context_chunks: List[QueryResult],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Initialize RAG query result.
        
        Args:
            question: Original user question
            response: Generated response from Gemini
            context_chunks: Chunks used as context
            metadata: Generation metadata
        """
        self.question = question
        self.response = response
        self.context_chunks = context_chunks
        self.metadata = metadata
    
    @property
    def success(self) -> bool:
        """Check if the query was successful."""
        return self.metadata.get("success", False)
    
    @property
    def sources(self) -> List[Dict[str, Any]]:
        """Get source information from metadata."""
        return self.metadata.get("sources", [])
    
    @property
    def model_used(self) -> str:
        """Get the model used for generation."""
        return self.metadata.get("model", "unknown")
    
    def print_response(self, show_sources: bool = True, show_context: bool = False) -> None:
        """
        Print the response in a formatted way.
        
        Args:
            show_sources: Whether to show source information
            show_context: Whether to show context chunks
        """
        print(f"\nAI Response:")
        print("=" * 60)
        print(self.response)
        print("=" * 60)
        
        if show_sources and self.sources:
            print(f"\nSources ({len(self.sources)}):")
            for i, source in enumerate(self.sources, 1):
                print(f"  {i}. {source.get('class_id', 'unknown')} ({source.get('source', 'unknown')})")
        
        if show_context and self.context_chunks:
            print(f"\nContext Chunks ({len(self.context_chunks)}):")
            for i, chunk in enumerate(self.context_chunks, 1):
                text = chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
                print(f"  {i}. [{chunk.score:.3f}] {text}")


def run_rag_query(
    question: str,
    *,
    top_k: int = 7,
    filters: Optional[Dict[str, Any]] = None,
    collection: Optional[str] = None,
    gemini_client: Optional[GeminiClient] = None,
    system_prompt: Optional[str] = None
) -> RAGQueryResult:
    """
    Run a RAG query with Gemini generation.
    
    Args:
        question: User's question
        top_k: Number of context chunks to retrieve
        filters: Optional filters for the search
        collection: Optional collection name
        gemini_client: Optional pre-configured Gemini client
        system_prompt: Optional custom system prompt
        
    Returns:
        RAGQueryResult with generated response and context
    """
    try:
        logger.info(f"Running RAG query: '{question}'")
        
        # Step 1: Retrieve relevant chunks
        logger.debug("Retrieving context chunks...")
        context_chunks = run_query(
            question, 
            top_k=top_k, 
            filters=filters, 
            collection=collection
        )
        
        if not context_chunks:
            logger.warning("No context chunks found for query")
            return RAGQueryResult(
                question=question,
                response="I couldn't find any relevant information in the knowledge base to answer your question.",
                context_chunks=[],
                metadata={"success": False, "error": "No context found"}
            )
        
        logger.info(f"Retrieved {len(context_chunks)} context chunks")
        
        # Step 2: Generate response with Gemini
        if gemini_client is None:
            logger.debug("Creating Gemini client...")
            gemini_client = create_gemini_client()
        
        logger.debug("Generating response with Gemini...")
        
        # Convert QueryResult objects to dictionaries for Gemini
        chunk_dicts = []
        for chunk in context_chunks:
            chunk_dict = {
                "text": chunk.text,
                "source": chunk.source,
                "class_id": chunk.class_id,
                "chunk_index": chunk.chunk_index,
                "score": chunk.score
            }
            chunk_dicts.append(chunk_dict)
        
        # Generate response
        gemini_result = gemini_client.generate_response(
            question=question,
            context_chunks=chunk_dicts,
            system_prompt=system_prompt
        )
        
        # Create result object
        result = RAGQueryResult(
            question=question,
            response=gemini_result["response"],
            context_chunks=context_chunks,
            metadata=gemini_result["metadata"]
        )
        
        logger.info("RAG query completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return RAGQueryResult(
            question=question,
            response=f"Error processing your question: {str(e)}",
            context_chunks=[],
            metadata={"success": False, "error": str(e)}
        )


def run_rag_query_with_stats(
    question: str,
    *,
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    collection: Optional[str] = None,
    gemini_client: Optional[GeminiClient] = None,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a RAG query with detailed statistics.
    
    Args:
        question: User's question
        top_k: Number of context chunks to retrieve
        filters: Optional filters for the search
        collection: Optional collection name
        gemini_client: Optional pre-configured Gemini client
        system_prompt: Optional custom system prompt
        
    Returns:
        Dictionary containing results and comprehensive statistics
    """
    import time
    
    start_time = time.time()
    
    try:
        result = run_rag_query(
            question=question,
            top_k=top_k,
            filters=filters,
            collection=collection,
            gemini_client=gemini_client,
            system_prompt=system_prompt
        )
        
        query_time = time.time() - start_time
        
        # Calculate statistics
        stats = {
            "query_time_seconds": query_time,
            "success": result.success,
            "context_chunks_retrieved": len(result.context_chunks),
            "response_length": len(result.response),
            "model_used": result.model_used,
            "sources_count": len(result.sources)
        }
        
        if result.context_chunks:
            stats.update({
                "avg_context_score": sum(c.score for c in result.context_chunks) / len(result.context_chunks),
                "min_context_score": min(c.score for c in result.context_chunks),
                "max_context_score": max(c.score for c in result.context_chunks)
            })
        
        return {
            "status": "success" if result.success else "error",
            "result": result,
            "statistics": stats
        }
        
    except Exception as e:
        query_time = time.time() - start_time
        return {
            "status": "error",
            "error": str(e),
            "query_time_seconds": query_time,
            "result": None
        }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Query the knowledge base with Gemini AI generation")
    parser.add_argument("--question", type=str, required=True,
                       help="Question to ask the AI")
    parser.add_argument("--top-k", type=int, default=SETTINGS.top_k,
                       help="Number of context chunks to retrieve")
    parser.add_argument("--class-id", type=str, default=None,
                       help="Filter results by class folder name")
    parser.add_argument("--collection", type=str, default=None,
                       help="Qdrant collection name")
    parser.add_argument("--system-prompt", type=str, default=None,
                       help="Custom system prompt for Gemini")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--stats", action="store_true",
                       help="Show detailed statistics")
    parser.add_argument("--show-sources", action="store_true", default=True,
                       help="Show source information")
    parser.add_argument("--show-context", action="store_true",
                       help="Show context chunks used")
    
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
            result = run_rag_query_with_stats(
                question=args.question,
                top_k=args.top_k,
                filters=filters,
                collection=args.collection,
                system_prompt=args.system_prompt
            )
            
            if result["status"] == "success":
                stats = result["statistics"]
                print(f"\n[STATS] RAG Query Statistics:")
                print(f"   Query time: {stats['query_time_seconds']:.3f}s")
                print(f"   Success: {stats['success']}")
                print(f"   Context chunks: {stats['context_chunks_retrieved']}")
                print(f"   Response length: {stats['response_length']} chars")
                print(f"   Model used: {stats['model_used']}")
                print(f"   Sources: {stats['sources_count']}")
                
                if 'avg_context_score' in stats:
                    print(f"   Context scores: {stats['min_context_score']:.3f} - {stats['max_context_score']:.3f} (avg: {stats['avg_context_score']:.3f})")
                
                result["result"].print_response(
                    show_sources=args.show_sources,
                    show_context=args.show_context
                )
            else:
                print(f"\n[ERROR] RAG query failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        else:
            # Run simple RAG query
            result = run_rag_query(
                question=args.question,
                top_k=args.top_k,
                filters=filters,
                collection=args.collection,
                system_prompt=args.system_prompt
            )
            
            result.print_response(
                show_sources=args.show_sources,
                show_context=args.show_context
            )
            
    except Exception as e:
        print(f"\n[ERROR] RAG query failed: {e}")
        sys.exit(1)
