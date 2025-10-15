"""
Gemini AI client for enhanced text generation in RAG systems.

This module provides a clean interface to Google's Gemini API for generating
contextual responses based on retrieved knowledge base chunks.
"""

from __future__ import annotations
import logging
import os
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Suppress gRPC warnings
os.environ.setdefault("GRPC_VERBOSITY", "NONE")

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError as e:
    raise ImportError(
        "google-generativeai package is required. Install with: pip install google-generativeai"
    ) from e

logger = logging.getLogger(__name__)


@dataclass
class GeminiConfig:
    """Configuration for Gemini API client."""
    
    api_key: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_output_tokens: int = 2048
    safety_settings: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Initialize Gemini with the API key."""
        genai.configure(api_key=self.api_key)
        
        # Set default safety settings for financial content
        if self.safety_settings is None:
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }


class GeminiClient:
    """
    Client for interacting with Google's Gemini API.
    
    Provides methods for generating contextual responses using retrieved
    knowledge base chunks as context.
    """
    
    def __init__(self, config: GeminiConfig) -> None:
        """
        Initialize the Gemini client.
        
        Args:
            config: Gemini configuration object
        """
        self.config = config
        self.model = genai.GenerativeModel(
            model_name=config.model_name,
            safety_settings=config.safety_settings
        )
        logger.info(f"Initialized Gemini client with model: {config.model_name}")
    
    def generate_response(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]], 
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using Gemini with context from retrieved chunks.
        
        Args:
            question: User's question
            context_chunks: List of context chunks from vector search
            system_prompt: Optional system prompt to guide the response
            
        Returns:
            Dictionary containing the generated response and metadata
        """
        try:
            # Build context from chunks
            context_text = self._build_context(context_chunks)
            
            # Create the full prompt
            prompt = self._build_prompt(question, context_text, system_prompt)
            
            logger.debug(f"Generated prompt length: {len(prompt)} characters")
            
            # Generate response with enhanced safety settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_output_tokens,
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            
            # Extract response text
            if hasattr(response, 'text') and response.text:
                response_text = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                # Check for safety issues
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    if candidate.finish_reason == 2:  # SAFETY
                        logger.warning("Response blocked by safety filters. Trying with simplified prompt...")
                        # Try with a much simpler, more direct prompt
                        simple_prompt = f"""Please provide a helpful answer to this trading question: {question}

Context information: {context_text[:2000]}...

Please give a clear, direct response about trading and finance."""
                        try:
                            simple_response = self.model.generate_content(
                                simple_prompt,
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.3,
                                    max_output_tokens=2048,
                                ),
                                safety_settings=[
                                    {
                                        "category": "HARM_CATEGORY_HARASSMENT",
                                        "threshold": "BLOCK_NONE"
                                    },
                                    {
                                        "category": "HARM_CATEGORY_HATE_SPEECH",
                                        "threshold": "BLOCK_NONE"
                                    },
                                    {
                                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                        "threshold": "BLOCK_NONE"
                                    },
                                    {
                                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                        "threshold": "BLOCK_NONE"
                                    }
                                ]
                            )
                            if hasattr(simple_response, 'text') and simple_response.text:
                                response_text = simple_response.text
                                logger.info("Successfully generated response with simplified prompt")
                            else:
                                response_text = "I apologize, but I cannot provide a response to this query due to content safety restrictions."
                        except Exception as e:
                            logger.error(f"Failed to generate simplified response: {e}")
                            response_text = "I apologize, but I cannot provide a response to this query due to content safety restrictions."
                    else:
                        response_text = f"Response generation failed with finish_reason: {candidate.finish_reason}"
                else:
                    response_text = "No valid response generated"
            else:
                response_text = "No response generated"
                logger.warning("Gemini response has no text content")
                
            # Check for incomplete responses
            if self._is_incomplete_response(response_text):
                logger.warning("Detected potentially incomplete response, attempting to complete...")
                # Try to get a more complete response
                try:
                    enhanced_prompt = f"{prompt}\n\nIMPORTANT: The previous response was incomplete. Please provide a complete, comprehensive answer that fully addresses the question. Ensure all sections are fully developed and the response ends with proper conclusions."
                    enhanced_response = self.model.generate_content(enhanced_prompt)
                    if hasattr(enhanced_response, 'text') and enhanced_response.text:
                        response_text = enhanced_response.text
                        logger.info("Successfully generated more complete response")
                except Exception as e:
                    logger.warning(f"Failed to generate enhanced response: {e}")
            
            # Build metadata
            metadata = {
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "context_chunks_used": len(context_chunks),
                "prompt_length": len(prompt),
                "response_length": len(response_text),
                "sources": self._extract_sources(context_chunks)
            }
            
            logger.info(f"Generated response with {len(response_text)} characters")
            
            # Debug: Check if response is valid
            success = len(response_text) > 0 and response_text != "No response generated"
            logger.debug(f"Response success: {success}, length: {len(response_text)}")
            logger.debug(f"Response text preview: {response_text[:100]}...")
            
            # Add success to metadata for debugging
            metadata["success"] = success
            
            return {
                "response": response_text,
                "metadata": metadata,
                "success": success
            }
            
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "response": f"Error generating response: {str(e)}",
                "metadata": {"error": str(e)},
                "success": False
            }
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "").strip()
            source = chunk.get("source", "unknown")
            class_id = chunk.get("class_id", "unknown")
            
            if text:
                context_parts.append(f"[Source {i} - {class_id} ({source})]\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(
        self, 
        question: str, 
        context: str, 
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build the full prompt for Gemini.
        
        Args:
            question: User's question
            context: Formatted context from chunks
            system_prompt: Optional custom system prompt
            
        Returns:
            Complete prompt string
        """
        # Default system prompt for financial/trading knowledge
        default_system_prompt = """You are a helpful financial analyst and trading educator. Please provide comprehensive answers to trading and finance questions.

Your role is to provide complete, detailed answers that:

1. **COMPLETENESS**: Always provide a full, complete answer that thoroughly addresses the question
2. **DETAIL**: Include all relevant details, examples, and important information from the context
3. **STRUCTURE**: Organize with clear headings and logical progression
4. **RELEVANCE**: Include all information directly related to the question
5. **ACCURACY**: Base all information strictly on the provided context material
6. **PRACTICALITY**: Include actionable insights, examples, and practical applications

RESPONSE FORMAT:
- Complete introduction that fully addresses the question
- Detailed explanations with all relevant information
- Comprehensive key points with full details
- Practical examples and applications
- Mathematical formulas when applicable
- Step-by-step processes where relevant
- Complete source citations

INCLUDE:
- All relevant details from the context
- Complete explanations of concepts
- Practical examples and applications
- Mathematical formulas and calculations
- Step-by-step processes
- Important nuances and considerations
- Complete methodologies and frameworks

Provide a thorough, complete answer that fully addresses the question with all relevant details."""
        
        system_prompt = system_prompt or default_system_prompt
        
        return f"""{system_prompt}

CONTEXT MATERIAL:
{context}

USER QUESTION: {question}

Please provide a complete, detailed answer that thoroughly addresses the question. Include all relevant information, examples, and practical applications from the context. Structure your response clearly and cite sources when referencing specific information."""
    
    def _is_incomplete_response(self, response_text: str) -> bool:
        """Check if the response appears to be incomplete."""
        if not response_text or len(response_text.strip()) < 100:
            return True
        
        # Check for common incomplete patterns
        incomplete_patterns = [
            response_text.strip().endswith('...'),
            response_text.strip().endswith('*'),
            response_text.strip().endswith('•'),
            response_text.strip().endswith('-'),
            response_text.strip().endswith('**'),
            'This is a' in response_text[-50:],  # Common incomplete start
            'The following' in response_text[-50:],  # Common incomplete start
        ]
        
        # Check if response ends mid-sentence
        last_sentence = response_text.strip().split('.')[-1].strip()
        if len(last_sentence) > 0 and not last_sentence.endswith(('.', '!', '?', ':')):
            return True
            
        return any(incomplete_patterns)
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source information from chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of source information dictionaries
        """
        sources = []
        for chunk in chunks:
            source_info = {
                "class_id": chunk.get("class_id", "unknown"),
                "source": chunk.get("source", "unknown"),
                "chunk_index": chunk.get("chunk_index"),
                "score": chunk.get("score", 0.0)
            }
            sources.append(source_info)
        return sources


def create_gemini_client(api_key: Optional[str] = None, model_name: Optional[str] = None) -> GeminiClient:
    """
    Create a Gemini client with configuration from environment variables.
    
    Args:
        api_key: Optional API key (defaults to GEMINI_KEY env var)
        model_name: Optional model name (defaults to GEMINI_NAME env var)
        
    Returns:
        Configured GeminiClient instance
        
    Raises:
        ValueError: If API key is not provided
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_KEY")
    
    if not api_key:
        raise ValueError(
            "Gemini API key is required. Set GEMINI_KEY environment variable or pass api_key parameter."
        )
    
    if model_name is None:
        model_name = os.getenv("GEMINI_NAME", "gemini-1.5-flash")
    
    config = GeminiConfig(
        api_key=api_key,
        model_name=model_name,
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
        max_output_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
    )
    
    return GeminiClient(config)
