from __future__ import annotations
import logging
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    raise ImportError(
        "sentence-transformers package is required. Install with: pip install sentence-transformers"
    ) from e

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Handles text embeddings using SentenceTransformers models."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2") -> None:
        """
        Initialize the embedding model.
        
        Args:
            model_name: Name of the SentenceTransformers model to use
            
        Raises:
            ValueError: If model_name is empty or invalid
            RuntimeError: If model loading fails
        """
        if not model_name or not isinstance(model_name, str):
            raise ValueError("Model name must be a non-empty string")
        
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            self.dim = self.model.get_sentence_embedding_dimension()
            self.model_name = model_name
            logger.info(f"Model loaded successfully. Embedding dimension: {self.dim}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise RuntimeError(f"Failed to load embedding model '{model_name}'") from e

    def encode(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            batch_size: Optional batch size for processing (defaults to model's default)
            
        Returns:
            numpy array of embeddings with shape (len(texts), embedding_dim)
            
        Raises:
            ValueError: If texts is empty or contains non-string elements
            RuntimeError: If encoding fails
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        if not all(isinstance(text, str) for text in texts):
            raise ValueError("All texts must be strings")
        
        try:
            # Filter out empty strings
            filtered_texts = [text for text in texts if text.strip()]
            if not filtered_texts:
                logger.warning("All texts are empty after filtering")
                return np.empty((len(texts), self.dim), dtype="float32")
            
            logger.debug(f"Encoding {len(filtered_texts)} texts (filtered from {len(texts)})")
            
            # Use model's default batch size if none provided
            if batch_size is None:
                batch_size = 32  # Default batch size
                
            # Ensure batch_size is an integer
            batch_size = int(batch_size) if batch_size is not None else 32
                
            embeddings = self.model.encode(
                filtered_texts,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=batch_size
            ).astype("float32")
            
            # Handle case where some texts were filtered out
            if len(filtered_texts) < len(texts):
                # Create full result array with zero embeddings for empty texts
                full_embeddings = np.zeros((len(texts), self.dim), dtype="float32")
                filtered_idx = 0
                for i, text in enumerate(texts):
                    if text.strip():
                        full_embeddings[i] = embeddings[filtered_idx]
                        filtered_idx += 1
                return full_embeddings
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise RuntimeError("Failed to encode texts") from e

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension of the model."""
        return self.dim

    def get_model_name(self) -> str:
        """Get the name of the loaded model."""
        return self.model_name
