from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "pandas package is required for Excel processing. Install with: pip install pandas openpyxl"
    ) from e

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    """Represents a text chunk with associated metadata."""
    text: str
    metadata: Dict[str, Any]

def chunk_text(
    text: str, 
    *, 
    max_words: int = 1000, 
    overlap_words: int = 200, 
    base_meta: Optional[Dict[str, Any]] = None,
    min_words: int = 10
) -> List[Chunk]:
    """
    Split text into overlapping chunks based on word count.
    
    Args:
        text: Input text to chunk
        max_words: Maximum words per chunk
        overlap_words: Number of words to overlap between chunks
        base_meta: Base metadata to include in each chunk
        min_words: Minimum words required for a valid chunk
        
    Returns:
        List of Chunk objects
        
    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    
    if overlap_words < 0:
        raise ValueError("overlap_words must be non-negative")
    
    if overlap_words >= max_words:
        raise ValueError("overlap_words must be less than max_words")
    
    if min_words < 0:
        raise ValueError("min_words must be non-negative")
    
    # Handle empty or whitespace-only text
    text = text.strip()
    if not text:
        logger.warning("Empty text provided for chunking")
        return []
    
    words = text.split()
    if len(words) < min_words:
        logger.warning(f"Text has only {len(words)} words, less than minimum {min_words}")
        return []
    
    chunks: List[Chunk] = []
    start = 0
    base_meta = base_meta or {}
    
    logger.debug(f"Chunking text with {len(words)} words into chunks of max {max_words} words")

    while start < len(words):
        end = min(start + max_words, len(words))
        piece = " ".join(words[start:end]).strip()
        
        # Only create chunk if it meets minimum word requirement
        if piece and len(piece.split()) >= min_words:
            idx = len(chunks)
            meta = {**base_meta, "chunk_index": idx, "word_count": len(piece.split())}
            chunks.append(Chunk(text=piece, metadata=meta))
            logger.debug(f"Created chunk {idx} with {len(piece.split())} words")
        
        if end == len(words):
            break
        
        start = end - overlap_words
        if start < 0:
            start = 0
    
    logger.info(f"Created {len(chunks)} chunks from text")
    return chunks

def excel_to_text_summaries(
    xlsx_path: Union[str, Path], 
    base_meta: Dict[str, Any],
    max_preview_rows: int = 10,
    max_columns_preview: int = 8
) -> List[Chunk]:
    """
    Convert Excel file to text summaries for each sheet.
    
    Args:
        xlsx_path: Path to the Excel file
        base_meta: Base metadata to include in chunks
        max_preview_rows: Maximum number of rows to include in preview
        max_columns_preview: Maximum number of columns to include in preview
        
    Returns:
        List of Chunk objects containing sheet summaries
        
    Raises:
        FileNotFoundError: If the Excel file doesn't exist
        ValueError: If the file is not a valid Excel file
        PermissionError: If the file cannot be accessed
    """
    file_path = Path(xlsx_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")
    
    if not file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm']:
        raise ValueError(f"File must be an Excel file (.xlsx, .xls, or .xlsm), got: {file_path.suffix}")
    
    chunks: List[Chunk] = []
    
    try:
        logger.info(f"Processing Excel file: {file_path}")
        xl = pd.ExcelFile(file_path)
        
        if not xl.sheet_names:
            logger.warning(f"No sheets found in {file_path}")
            return chunks
        
        for sheet_name in xl.sheet_names:
            try:
                logger.debug(f"Processing sheet: {sheet_name}")
                df = xl.parse(sheet_name)
                
                # Handle empty sheets
                if df.empty:
                    logger.debug(f"Sheet '{sheet_name}' is empty, skipping")
                    continue
                
                # Clean column names and handle duplicates
                df.columns = [str(col).strip() for col in df.columns]
                if df.columns.duplicated().any():
                    df.columns = pd.Index([f"{col}_{i}" if col in df.columns[:i] else col 
                                         for i, col in enumerate(df.columns)])
                
                # Get preview data
                preview_df = df.head(max_preview_rows)
                
                # Identify column types
                numeric_cols = preview_df.select_dtypes(include=["number"]).columns.tolist()
                text_cols = [c for c in preview_df.columns if c not in numeric_cols]
                
                # Build summary lines
                lines = [f"Excel Sheet '{sheet_name}' Summary:"]
                lines.append(f"Dimensions: {len(df)} rows × {len(df.columns)} columns")
                
                # Add column information
                if text_cols:
                    preview_text_cols = text_cols[:max_columns_preview]
                    lines.append(f"Text columns ({len(text_cols)}): {', '.join(preview_text_cols)}")
                    if len(text_cols) > max_columns_preview:
                        lines.append(f"... and {len(text_cols) - max_columns_preview} more")
                
                if numeric_cols:
                    lines.append(f"Numeric columns ({len(numeric_cols)}):")
                    preview_numeric_cols = numeric_cols[:max_columns_preview]
                    
                    try:
                        desc = df[preview_numeric_cols].describe()
                        for col in preview_numeric_cols:
                            try:
                                stats = desc[col]
                                mean_val = stats.get('mean', 'N/A')
                                min_val = stats.get('min', 'N/A')
                                max_val = stats.get('max', 'N/A')
                                lines.append(f"  {col}: mean={mean_val}, min={min_val}, max={max_val}")
                            except Exception as e:
                                logger.debug(f"Could not get stats for column {col}: {e}")
                                lines.append(f"  {col}: stats unavailable")
                        
                        if len(numeric_cols) > max_columns_preview:
                            lines.append(f"  ... and {len(numeric_cols) - max_columns_preview} more numeric columns")
                            
                    except Exception as e:
                        logger.warning(f"Could not generate numeric stats for sheet {sheet_name}: {e}")
                        lines.append(f"Numeric statistics unavailable")
                
                # Add data preview
                if not preview_df.empty:
                    try:
                        # Limit columns for preview
                        preview_columns = preview_df.columns[:max_columns_preview]
                        preview_data = preview_df[preview_columns]
                        
                        # Convert to CSV string
                        preview_csv = preview_data.to_csv(index=False).strip()
                        lines.append(f"Data Preview (first {len(preview_data)} rows):")
                        lines.append(preview_csv)
                        
                        if len(preview_df.columns) > max_columns_preview:
                            lines.append(f"... and {len(preview_df.columns) - max_columns_preview} more columns")
                            
                    except Exception as e:
                        logger.warning(f"Could not generate preview for sheet {sheet_name}: {e}")
                        lines.append("Data preview unavailable")
                
                # Create chunk
                summary_text = "\n".join(lines)
                meta = {
                    **base_meta, 
                    "source": "excel", 
                    "sheet": sheet_name,
                    "rows": len(df),
                    "columns": len(df.columns)
                }
                chunks.append(Chunk(text=summary_text, metadata=meta))
                logger.debug(f"Created summary for sheet '{sheet_name}' with {len(summary_text)} characters")
                
            except Exception as e:
                logger.error(f"Error processing sheet '{sheet_name}' in {file_path}: {e}")
                # Continue processing other sheets
                continue
        
        logger.info(f"Successfully processed {len(chunks)} sheets from {file_path}")
        return chunks
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to process Excel file {file_path}: {e}")
        raise ValueError(f"Invalid Excel file: {e}") from e
    finally:
        # Ensure Excel file is properly closed
        try:
            if 'xl' in locals():
                xl.close()
        except Exception:
            pass  # Ignore cleanup errors
