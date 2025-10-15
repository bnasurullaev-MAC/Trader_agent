from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Union

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
    from qdrant_client.http.exceptions import UnexpectedResponse
except ImportError as e:
    raise ImportError(
        "qdrant-client package is required. Install with: pip install qdrant-client"
    ) from e

logger = logging.getLogger(__name__)

def connect(host: str, port: int, api_key: Optional[str] = None) -> QdrantClient:
    """
    Connect to Qdrant server with error handling.
    
    Args:
        host: Qdrant server host
        port: Qdrant server port
        api_key: Optional API key for authentication
        
    Returns:
        Connected QdrantClient instance
        
    Raises:
        ConnectionError: If connection to Qdrant fails
        ValueError: If connection parameters are invalid
    """
    if not isinstance(host, str) or not host.strip():
        raise ValueError("Host must be a non-empty string")
    
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError("Port must be an integer between 1 and 65535")
    
    try:
        logger.info(f"Connecting to Qdrant at {host}:{port}")
        # Use HTTP instead of HTTPS for local development
        client = QdrantClient(host=host, port=port, api_key=api_key, https=False)
        
        # Test connection
        client.get_collections()
        logger.info("Successfully connected to Qdrant")
        return client
        
    except Exception as e:
        logger.error(f"Failed to connect to Qdrant at {host}:{port}: {e}")
        raise ConnectionError(f"Failed to connect to Qdrant: {e}") from e

def recreate_collection(client: QdrantClient, collection: str, vector_size: int) -> None:
    """
    Recreate a Qdrant collection with the specified vector configuration.
    
    Args:
        client: Connected QdrantClient instance
        collection: Name of the collection to recreate
        vector_size: Dimension of the vectors
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If collection recreation fails
    """
    if not isinstance(collection, str) or not collection.strip():
        raise ValueError("Collection name must be a non-empty string")
    
    if not isinstance(vector_size, int) or vector_size <= 0:
        raise ValueError("Vector size must be a positive integer")
    
    try:
        logger.info(f"Recreating collection '{collection}' with vector size {vector_size}")
        
        client.recreate_collection(
            collection_name=collection,
            vectors_config=rest.VectorParams(
                size=vector_size, 
                distance=rest.Distance.COSINE
            ),
        )
        
        logger.info(f"Successfully recreated collection '{collection}'")
        
    except Exception as e:
        logger.error(f"Failed to recreate collection '{collection}': {e}")
        raise RuntimeError(f"Failed to recreate collection '{collection}': {e}") from e

def upsert_points(
    client: QdrantClient, 
    collection: str, 
    vectors: List[List[float]], 
    payloads: List[Dict[str, Any]]
) -> None:
    """
    Upsert points to a Qdrant collection.
    
    Args:
        client: Connected QdrantClient instance
        collection: Name of the collection
        vectors: List of vectors to upsert
        payloads: List of payload dictionaries
        
    Raises:
        ValueError: If parameters are invalid or mismatched
        RuntimeError: If upsert operation fails
    """
    if not isinstance(vectors, list) or not isinstance(payloads, list):
        raise ValueError("Vectors and payloads must be lists")
    
    if len(vectors) != len(payloads):
        raise ValueError(f"Vectors ({len(vectors)}) and payloads ({len(payloads)}) must have the same length")
    
    if not vectors:
        logger.warning("No vectors to upsert")
        return
    
    try:
        logger.debug(f"Upserting {len(vectors)} points to collection '{collection}'")
        
        # Validate vectors and create points
        points = []
        for i, (vector, payload) in enumerate(zip(vectors, payloads)):
            if not isinstance(vector, list):
                raise ValueError(f"Vector at index {i} must be a list")
            
            if not isinstance(payload, dict):
                raise ValueError(f"Payload at index {i} must be a dictionary")
            
            point_id = payload.get("id")
            if not point_id:
                raise ValueError(f"Payload at index {i} must contain an 'id' field")
            
            points.append(
                rest.PointStruct(
                    id=point_id, 
                    vector=vector, 
                    payload=payload
                )
            )
        
        # Perform upsert
        client.upsert(collection_name=collection, points=points)
        logger.info(f"Successfully upserted {len(points)} points to collection '{collection}'")
        
    except Exception as e:
        logger.error(f"Failed to upsert points to collection '{collection}': {e}")
        raise RuntimeError(f"Failed to upsert points: {e}") from e

def search(
    client: QdrantClient, 
    collection: str, 
    query_vector: List[float], 
    top_k: int, 
    filters: Optional[Dict[str, Any]] = None
) -> List[Any]:
    """
    Search for similar vectors in a Qdrant collection.
    
    Args:
        client: Connected QdrantClient instance
        collection: Name of the collection to search
        query_vector: Query vector for similarity search
        top_k: Number of results to return
        filters: Optional filters to apply
        
    Returns:
        List of search results
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If search operation fails
    """
    if not isinstance(query_vector, list):
        raise ValueError("Query vector must be a list")
    
    if not isinstance(top_k, int) or top_k <= 0:
        raise ValueError("Top K must be a positive integer")
    
    try:
        logger.debug(f"Searching collection '{collection}' with top_k={top_k}")
        
        # Build query filter if provided
        qp_filter = None
        if filters:
            if not isinstance(filters, dict):
                raise ValueError("Filters must be a dictionary")
            
            must_conditions = []
            for key, value in filters.items():
                if not isinstance(key, str) or not key.strip():
                    raise ValueError(f"Filter key must be a non-empty string, got: {key}")
                
                must_conditions.append(
                    rest.FieldCondition(
                        key=key, 
                        match=rest.MatchValue(value=value)
                    )
                )
            
            qp_filter = rest.Filter(must=must_conditions)
            logger.debug(f"Applied filters: {list(filters.keys())}")
        
        # Perform search
        results = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qp_filter,
        )
        
        logger.info(f"Search returned {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Failed to search collection '{collection}': {e}")
        raise RuntimeError(f"Failed to search collection: {e}") from e

def get_collection_info(client: QdrantClient, collection: str) -> Dict[str, Any]:
    """
    Get information about a collection.
    
    Args:
        client: Connected QdrantClient instance
        collection: Name of the collection
        
    Returns:
        Dictionary containing collection information
        
    Raises:
        ValueError: If collection name is invalid
        RuntimeError: If operation fails
    """
    if not isinstance(collection, str) or not collection.strip():
        raise ValueError("Collection name must be a non-empty string")
    
    try:
        info = client.get_collection(collection)
        logger.debug(f"Retrieved info for collection '{collection}'")
        return info
        
    except Exception as e:
        logger.error(f"Failed to get info for collection '{collection}': {e}")
        raise RuntimeError(f"Failed to get collection info: {e}") from e

def delete_collection(client: QdrantClient, collection: str) -> None:
    """
    Delete a collection from Qdrant.
    
    Args:
        client: Connected QdrantClient instance
        collection: Name of the collection to delete
        
    Raises:
        ValueError: If collection name is invalid
        RuntimeError: If deletion fails
    """
    if not isinstance(collection, str) or not collection.strip():
        raise ValueError("Collection name must be a non-empty string")
    
    try:
        logger.info(f"Deleting collection '{collection}'")
        client.delete_collection(collection)
        logger.info(f"Successfully deleted collection '{collection}'")
        
    except Exception as e:
        logger.error(f"Failed to delete collection '{collection}': {e}")
        raise RuntimeError(f"Failed to delete collection: {e}") from e
