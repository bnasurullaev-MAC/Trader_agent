#!/usr/bin/env python3
"""
Advanced Interactive RAG Chatbot with conversation history
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Suppress gRPC warnings
os.environ.setdefault("GRPC_VERBOSITY", "NONE")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag_query import run_rag_query


class RAGChatbot:
    """Advanced RAG Chatbot with conversation history."""
    
    def __init__(self):
        self.conversation_history = []
        self.session_start = datetime.now()
        self.question_count = 0
        self.history_file = Path("conversation_history.json")
        self.load_conversation_history()
    
    def save_conversation_history(self):
        """Save conversation history to JSON file."""
        try:
            # Convert datetime objects to strings for JSON serialization
            history_data = {
                "conversation_history": [],
                "session_info": {
                    "total_sessions": len([h for h in self.conversation_history if h.get('session_start')]),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            for entry in self.conversation_history:
                entry_copy = entry.copy()
                if 'timestamp' in entry_copy:
                    entry_copy['timestamp'] = entry_copy['timestamp'].isoformat()
                history_data["conversation_history"].append(entry_copy)
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n[INFO] Conversation history saved to {self.history_file}")
            
        except Exception as e:
            print(f"\n[WARNING] Failed to save conversation history: {e}")
    
    def load_conversation_history(self):
        """Load conversation history from JSON file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert timestamp strings back to datetime objects
                for entry in data.get("conversation_history", []):
                    if 'timestamp' in entry:
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                
                self.conversation_history = data.get("conversation_history", [])
                print(f"\n[INFO] Loaded {len(self.conversation_history)} previous conversations")
            else:
                print(f"\n[INFO] No previous conversation history found. Starting fresh.")
                
        except Exception as e:
            print(f"\n[WARNING] Failed to load conversation history: {e}")
            self.conversation_history = []
        
    def print_welcome(self):
        """Print welcome message and instructions."""
        print("=" * 80)
        print("ADVANCED PROFESSIONAL TRADING MASTERCLASS RAG CHATBOT")
        print("=" * 80)
        print("Welcome! I'm your AI assistant for trading and portfolio management.")
        print("I have access to a comprehensive knowledge base including:")
        print("  • Trading strategies and techniques")
        print("  • Portfolio management principles") 
        print("  • Bond market analysis")
        print("  • Leading indicators and economic data")
        print("  • Risk management frameworks")
        print("\nFeatures:")
        print("  • Conversation history tracking")
        print("  • Context-aware responses")
        print("  • Comprehensive, detailed answers")
        print("  • Source citations")
        print("  • Session statistics")
        print("=" * 80)
    
    def print_help(self):
        """Print help information."""
        print("\nAVAILABLE COMMANDS:")
        print("  • Ask any trading or finance question")
        print("  • Type 'help' to see this message")
        print("  • Type 'history' to see conversation history")
        print("  • Type 'stats' to see session statistics")
        print("  • Type 'save' to save current conversation")
        print("  • Type 'clear' to clear the screen")
        print("  • Type 'quit' or 'exit' to end the session")
        print("\nEXAMPLE QUESTIONS:")
        print("  • What is the bond pricing formula?")
        print("  • How do I implement a long-short strategy?")
        print("  • What are the key leading indicators?")
        print("  • How do I calculate position sizing?")
        print("  • What are the risks of portfolio management?")
    
    def print_history(self):
        """Print conversation history."""
        if not self.conversation_history:
            print("\nNo conversation history yet.")
            return
        
        print("\nCONVERSATION HISTORY:")
        print("=" * 50)
        for i, entry in enumerate(self.conversation_history, 1):
            print(f"{i}. Q: {entry['question']}")
            print(f"   A: {entry['response'][:100]}...")
            print(f"   Sources: {len(entry['sources'])}")
            print()
    
    def print_stats(self):
        """Print session statistics."""
        session_duration = datetime.now() - self.session_start
        print(f"\nSESSION STATISTICS:")
        print("=" * 30)
        print(f"Questions asked: {self.question_count}")
        print(f"Session duration: {session_duration}")
        print(f"Average response time: {session_duration.total_seconds() / max(self.question_count, 1):.1f}s")
        print(f"Conversation entries: {len(self.conversation_history)}")
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_response(self, question, response_text, sources):
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
    
    def add_to_history(self, question, response, sources):
        """Add question and response to conversation history."""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'response': response,
            'sources': sources
        })
    
    def get_context_from_history(self, current_question):
        """Get relevant context from conversation history."""
        if not self.conversation_history:
            return current_question
        
        # Add recent context to the question
        recent_questions = [entry['question'] for entry in self.conversation_history[-3:]]
        context = f"Previous questions: {'; '.join(recent_questions)}\n\nCurrent question: {current_question}"
        return context
    
    def process_question(self, question):
        """Process a user question."""
        self.question_count += 1
        
        # Add context from conversation history
        contextual_question = self.get_context_from_history(question)
        
        print(f"\nProcessing question {self.question_count}: '{question}'")
        print("Searching knowledge base...")
        
        try:
            result = run_rag_query(contextual_question, top_k=7, collection="ptm_knowledge_base")
            
            if result.success:
                self.format_response(question, result.response, result.sources)
                self.add_to_history(question, result.response, result.sources)
                return True
            else:
                print("\nSorry, I encountered an error processing your question.")
                print(f"Error: {result.metadata.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"\nError processing your question: {e}")
            print("Please try rephrasing your question or check your connection.")
            return False
    
    def run(self):
        """Main chatbot loop."""
        # Check if Gemini API key is set
        if not os.getenv("GEMINI_KEY"):
            print("ERROR: GEMINI_KEY environment variable not set!")
            print("Please set your Gemini API key:")
            print("  export GEMINI_KEY='your-api-key-here'")
            print("\nGet your API key from: https://makersuite.google.com/app/apikey")
            return
        
        self.print_welcome()
        self.print_help()
        
        print("\nReady to help! What would you like to know?")
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\nThank you for using the RAG Chatbot!")
                    print(f"Session summary: {self.question_count} questions asked")
                    # Auto-save conversation history before exiting
                    self.save_conversation_history()
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'history':
                    self.print_history()
                    continue
                
                elif user_input.lower() == 'stats':
                    self.print_stats()
                    continue
                
                elif user_input.lower() == 'save':
                    self.save_conversation_history()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.clear_screen()
                    self.print_welcome()
                    continue
                
                elif not user_input:
                    print("Please enter a question or type 'help' for assistance.")
                    continue
                
                # Process the question
                self.process_question(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\nThank you for using the RAG Chatbot!")
                print(f"Session summary: {self.question_count} questions asked")
                # Auto-save conversation history before exiting
                self.save_conversation_history()
                break
            except EOFError:
                print(f"\n\nThank you for using the RAG Chatbot!")
                print(f"Session summary: {self.question_count} questions asked")
                # Auto-save conversation history before exiting
                self.save_conversation_history()
                break


def main():
    """Main function to run the chatbot."""
    chatbot = RAGChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()
