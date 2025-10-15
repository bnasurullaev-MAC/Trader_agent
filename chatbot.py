#!/usr/bin/env python3
"""
Interactive RAG Chatbot for Professional Trading Masterclass
"""

import os
import sys
from pathlib import Path

# Suppress gRPC warnings
os.environ.setdefault("GRPC_VERBOSITY", "NONE")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag_query import run_rag_query


def print_welcome():
    """Print welcome message and instructions."""
    print("=" * 80)
    print("PROFESSIONAL TRADING MASTERCLASS RAG CHATBOT")
    print("=" * 80)
    print("Welcome! I'm your AI assistant for trading and portfolio management questions.")
    print("I have access to a comprehensive knowledge base including:")
    print("  • Trading strategies and techniques")
    print("  • Portfolio management principles")
    print("  • Bond market analysis")
    print("  • Leading indicators and economic data")
    print("  • Risk management frameworks")
    print("\nType your questions and I'll provide comprehensive, detailed, and complete answers!")
    print("=" * 80)


def print_help():
    """Print help information."""
    print("\nAVAILABLE COMMANDS:")
    print("  • Ask any trading or finance question")
    print("  • Type 'help' to see this message")
    print("  • Type 'quit' or 'exit' to end the session")
    print("  • Type 'clear' to clear the screen")
    print("\nEXAMPLE QUESTIONS:")
    print("  • What is the bond pricing formula?")
    print("  • How do I implement a long-short strategy?")
    print("  • What are the key leading indicators?")
    print("  • How do I calculate position sizing?")


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_response(response_text, sources):
    """Format the response for better readability."""
    print("\n" + "=" * 80)
    print("AI RESPONSE")
    print("=" * 80)
    print(response_text)
    
    if sources:
        print("\n" + "=" * 80)
        print("SOURCES")
        print("=" * 80)
        for i, source in enumerate(sources, 1):
            source_name = source.get('class_id', 'Unknown')
            source_type = source.get('source', 'unknown')
            print(f"{i:2d}. {source_name} ({source_type})")
    
    print("\n" + "=" * 80)


def main():
    """Main chatbot loop."""
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_KEY"):
        print("ERROR: GEMINI_KEY environment variable not set!")
        print("Please set your Gemini API key:")
        print("  export GEMINI_KEY='your-api-key-here'")
        print("\nGet your API key from: https://makersuite.google.com/app/apikey")
        return
    
    print_welcome()
    print_help()
    
    print("\nReady to help! What would you like to know?")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for using the RAG Chatbot! Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'clear':
                clear_screen()
                print_welcome()
                continue
            
            elif not user_input:
                print("Please enter a question or type 'help' for assistance.")
                continue
            
            # Process the question
            print(f"\nSearching knowledge base for: '{user_input}'")
            print("Processing your question...")
            
            try:
                result = run_rag_query(user_input, top_k=7, collection="ptm_knowledge_base")
                
                if result.success:
                    format_response(result.response, result.sources)
                else:
                    print("\nSorry, I encountered an error processing your question.")
                    print(f"Error: {result.metadata.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"\nError processing your question: {e}")
                print("Please try rephrasing your question or check your connection.")
            
        except KeyboardInterrupt:
            print("\n\nThank you for using the RAG Chatbot! Goodbye!")
            break
        except EOFError:
            print("\n\nThank you for using the RAG Chatbot! Goodbye!")
            break


if __name__ == "__main__":
    main()
