from __future__ import annotations
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union

logger = logging.getLogger(__name__)

def read_text(path: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    Read text from a file with error handling.
    
    Args:
        path: Path to the text file
        encoding: Text encoding to use
        
    Returns:
        Contents of the file as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file can't be decoded with the specified encoding
        OSError: If there's an error reading the file
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise OSError(f"Path is not a file: {file_path}")
    
    try:
        content = file_path.read_text(encoding=encoding, errors="strict")
        logger.debug(f"Successfully read {len(content)} characters from {file_path}")
        return content
    except UnicodeDecodeError as e:
        logger.warning(f"Unicode decode error for {file_path}, trying with errors='ignore'")
        return file_path.read_text(encoding=encoding, errors="ignore")
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        raise

def list_classes(kb_root: Union[str, Path]) -> List[Path]:
    """
    List all class directories in the knowledge base root.
    
    Args:
        kb_root: Root directory of the knowledge base
        
    Returns:
        List of Path objects representing class directories
        
    Raises:
        FileNotFoundError: If kb_root doesn't exist
        NotADirectoryError: If kb_root is not a directory
    """
    root = Path(kb_root)
    
    if not root.exists():
        raise FileNotFoundError(f"Knowledge base root does not exist: {root}")
    
    if not root.is_dir():
        raise NotADirectoryError(f"Knowledge base root is not a directory: {root}")
    
    try:
        class_dirs = [p for p in root.iterdir() if p.is_dir()]
        logger.info(f"Found {len(class_dirs)} class directories in {root}")
        return class_dirs
    except PermissionError as e:
        logger.error(f"Permission denied accessing {root}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error listing directories in {root}: {e}")
        raise

def sha1(s: str) -> str:
    """
    Generate SHA1 hash of a string.
    
    Args:
        s: String to hash
        
    Returns:
        SHA1 hash as hexadecimal string
        
    Raises:
        TypeError: If input is not a string
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {type(s)}")
    
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

def save_json(path: Union[str, Path], obj: Any, indent: int = 2, ensure_ascii: bool = False) -> None:
    """
    Save object to JSON file with error handling.
    
    Args:
        path: Path where to save the JSON file
        obj: Object to serialize to JSON
        indent: JSON indentation level
        ensure_ascii: Whether to escape non-ASCII characters
        
    Raises:
        TypeError: If object is not JSON serializable
        OSError: If there's an error writing the file
    """
    file_path = Path(path)
    
    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=ensure_ascii, indent=indent)
        
        logger.debug(f"Successfully saved JSON to {file_path}")
        
    except TypeError as e:
        logger.error(f"Object is not JSON serializable: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        raise

def load_json(path: Union[str, Path]) -> Any:
    """
    Load object from JSON file with error handling.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Deserialized object from JSON
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        OSError: If there's an error reading the file
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        
        logger.debug(f"Successfully loaded JSON from {file_path}")
        return obj
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        raise

def batched(iterable: Iterable, n: int) -> Iterable[List]:
    """
    Yield batches of items from an iterable.
    
    Args:
        iterable: Source iterable
        n: Batch size
        
    Yields:
        Lists of items, each containing up to n items
        
    Raises:
        ValueError: If batch size is not positive
    """
    if n <= 0:
        raise ValueError("Batch size must be positive")
    
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    
    if batch:  # Yield remaining items
        yield batch

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        Path object of the directory
        
    Raises:
        OSError: If directory cannot be created or accessed
    """
    dir_path = Path(path)
    
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    except Exception as e:
        logger.error(f"Failed to create directory {dir_path}: {e}")
        raise

def get_file_size(path: Union[str, Path]) -> int:
    """
    Get file size in bytes.
    
    Args:
        path: Path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        OSError: If there's an error accessing the file
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        return file_path.stat().st_size
    except Exception as e:
        logger.error(f"Failed to get size of {file_path}: {e}")
        raise
