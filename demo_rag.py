#!/usr/bin/env python3
"""
Demo script for RAG functionality with Gemini AI integration.

This script demonstrates the enhanced query capabilities that combine
semantic search with AI-generated responses.
"""

import os
import sys
from pathlib import Path

# Suppress gRPC warnings
os.environ.setdefault("GRPC_VERBOSITY", "NONE")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modules directly
from src.rag_query import run_rag_query


def main() -> None:
    """Demo the RAG functionality."""
    
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_KEY"):
        print("GEMINI_KEY environment variable not set!")
        print("Please set your Gemini API key:")
        print("  export GEMINI_KEY='your-api-key-here'")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        return
    
    print("RAG Demo with Gemini AI")
    print("=" * 50)
    
    # Single comprehensive question
    question = "What is the general formula used to price a coupon-bearing bond?"
    
    print(f"\nQuestion: {question}")
    print("=" * 80)
    
    try:
        result = run_rag_query(question, top_k=7, collection="ptm_knowledge_base")
        
        if result.success:
            print("\n" + "=" * 80)
            print("COMPREHENSIVE ANSWER")
            print("=" * 80)
            print(result.response)
            print("\n" + "=" * 80)
            print("SOURCES")
            print("=" * 80)
            for i, source in enumerate(result.sources, 1):
                print(f"{i}. {source.get('class_id', 'unknown')} ({source.get('source', 'unknown')})")
        else:
            print(f"Error: {result.metadata.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    main()
