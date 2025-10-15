"""
Advanced ingestion module with proper PPTX, DOCX, and PDF parsing.
Excludes CSV and Excel files as requested.
"""

from __future__ import annotations
import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from tqdm import tqdm
except ImportError as e:
    raise ImportError(
        "tqdm package is required. Install with: pip install tqdm"
    ) from e

from .config import SETTINGS
from .utils import batched, sha1
from .chunkers import Chunk, chunk_text
from .embeddings import EmbeddingModel
from .index_qdrant import connect, recreate_collection, upsert_points
from .file_parsers import parse_file_by_type, get_file_metadata

logger = logging.getLogger(__name__)

def build_payload(base_meta: Dict[str, Any], text: str, idx: int) -> Dict[str, Any]:
    """Build payload for Qdrant point with proper ID generation."""
    if not isinstance(text, str):
        raise TypeError("Text must be a string")
    
    if not isinstance(base_meta, dict):
        raise TypeError("Base metadata must be a dictionary")
    
    # Create a unique ID using class_id, index, and text hash
    class_id = base_meta.get('class_id', 'unknown')
    text_hash = sha1(text[:64])[:8]  # Use first 8 chars of hash
    # Convert to integer for Qdrant compatibility
    unique_id = int(sha1(f"{class_id}-{idx}-{text_hash}")[:16], 16)
    
    return {
        "id": unique_id,
        **base_meta,
        "text": text,
        "text_length": len(text),
        "word_count": len(text.split())
    }

def process_advanced_file(file_path: Path, class_id: str, video_number: str, settings: Any) -> List[tuple[str, Dict[str, Any]]]:
    """Process a single file using advanced parsers."""
    chunks_data = []
    
    try:
        logger.debug(f"Processing file: {file_path}")
        
        # Parse the file based on its type
        file_text = parse_file_by_type(file_path)
        
        if file_text.strip():
            # Get file metadata
            metadata = get_file_metadata(file_path)
            
            # Determine source type
            file_extension = file_path.suffix.lower()
            source_type = file_extension[1:]  # Remove the dot
            
            # Create base metadata
            base_meta = {
                "class_id": class_id,
                "source": source_type,
                "file_path": str(file_path),
                "video_number": video_number,
                "file_name": file_path.name,
                "file_size": metadata.get("file_size", 0),
                **metadata  # Include all metadata
            }
            
            # Chunk the text
            file_chunks = chunk_text(
                file_text,
                max_words=settings.max_chunk_words,
                overlap_words=settings.chunk_overlap_words,
                base_meta=base_meta,
            )
            
            for i, chunk in enumerate(file_chunks):
                payload = build_payload(chunk.metadata, chunk.text, i)
                chunks_data.append((chunk.text, payload))
                logger.debug(f"Created {source_type} chunk {i} for {class_id}")
        else:
            logger.warning(f"File {file_path} produced no text content")
            
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
    
    return chunks_data

def process_text_file(text_file: Path, video_folder: Optional[Path], settings: Any) -> List[tuple[str, Dict[str, Any]]]:
    """Process a single text file and its associated video folder."""
    # Extract video number from filename
    filename = text_file.stem
    video_number = filename.replace("PTM Video ", "").split(" - ")[0]
    class_id = f"PTM_Video_{video_number}"
    
    chunks_data = []
    
    # Process main text file
    try:
        logger.debug(f"Processing text file: {text_file}")
        
        # Read text file normally
        with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()
        
        if raw_text.strip():
            t_chunks = chunk_text(
                raw_text,
                max_words=settings.max_chunk_words,
                overlap_words=settings.chunk_overlap_words,
                base_meta={
                    "class_id": class_id, 
                    "source": "transcript",
                    "file_path": str(text_file),
                    "video_number": video_number
                },
            )
            
            for i, chunk in enumerate(t_chunks):
                payload = build_payload(chunk.metadata, chunk.text, i)
                chunks_data.append((chunk.text, payload))
                logger.debug(f"Created transcript chunk {i} for {class_id}")
        else:
            logger.warning(f"Empty text file: {text_file}")
            
    except Exception as e:
        logger.error(f"Error processing text file {text_file}: {e}")
    
    # Process supporting files in video folder (PDF, PPTX, DOCX only)
    if video_folder and video_folder.exists():
        try:
            logger.debug(f"Processing video folder: {video_folder}")
            
            # Process PDF files
            for pdf_file in video_folder.glob("*.pdf"):
                pdf_chunks = process_advanced_file(pdf_file, class_id, video_number, settings)
                chunks_data.extend(pdf_chunks)
            
            # Process PPTX files
            for pptx_file in video_folder.glob("*.pptx"):
                pptx_chunks = process_advanced_file(pptx_file, class_id, video_number, settings)
                chunks_data.extend(pptx_chunks)
            
            # Process DOCX files
            for docx_file in video_folder.glob("*.docx"):
                docx_chunks = process_advanced_file(docx_file, class_id, video_number, settings)
                chunks_data.extend(docx_chunks)
                    
        except Exception as e:
            logger.error(f"Error processing video folder {video_folder}: {e}")
    
    if not chunks_data:
        logger.warning(f"No chunks created for {text_file}")
    
    return chunks_data

def process_trade_template_file(template_file: Path, settings) -> List[tuple]:
    """Process a trade template file (DOCX/DOC) and return chunks."""
    chunks_data = []
    
    try:
        # Extract text content from the template file
        if template_file.suffix.lower() in ['.docx', '.doc']:
            text_content = parse_file_by_type(template_file)
        else:
            logger.warning(f"Unsupported file type for trade template: {template_file}")
            return chunks_data
        
        if not text_content:
            logger.warning(f"No content extracted from trade template: {template_file}")
            return chunks_data
        
        # Ensure text_content is a string
        if not isinstance(text_content, str):
            logger.warning(f"Expected string but got {type(text_content)} for trade template: {template_file}")
            return chunks_data
        
        # Create base metadata for trade template
        base_meta = {
            "class_id": "Trade_Template",
            "source": "trade_template",
            "file_name": template_file.name,
            "file_type": template_file.suffix.lower(),
            "content_type": "trade_template",
            "template_name": template_file.stem,
            "priority": "high"  # Mark as high priority for trade-related queries
        }
        
        # Chunk the content
        chunk_objects = chunk_text(text_content, max_words=settings.max_chunk_words, overlap_words=settings.chunk_overlap_words)
        
        for idx, chunk_obj in enumerate(chunk_objects):
            chunk_text_content = chunk_obj.text
            payload = build_payload(base_meta, chunk_text_content, idx)
            chunks_data.append((chunk_text_content, payload))
        
        logger.info(f"Processed trade template {template_file.name}: {len(chunk_objects)} chunks")
        
    except Exception as e:
        logger.error(f"Error processing trade template {template_file}: {e}")
    
    return chunks_data

def ingest_advanced(kb_root: str, collection: str, dry_run: bool = False) -> Dict[str, Any]:
    """Advanced ingestion process with proper file parsing."""
    logger.info(f"Starting advanced ingestion process: {kb_root}")
    logger.info(f"Target collection: {collection}")
    logger.info(f"Dry run mode: {dry_run}")
    logger.info("Processing: TXT, PDF, PPTX, DOCX files only")
    
    try:
        # Initialize embedding model
        logger.info(f"Loading embedding model: {SETTINGS.embedding_model}")
        embed = EmbeddingModel(SETTINGS.embedding_model)
        
        # Connect to Qdrant (unless dry run)
        client = None
        if not dry_run:
            client = connect(SETTINGS.qdrant_host, SETTINGS.qdrant_port, SETTINGS.qdrant_api_key)
            recreate_collection(client, collection, embed.get_embedding_dimension())
        
        # Get text files from KB root
        kb_path = Path(kb_root)
        text_files = list(kb_path.glob("PTM Video *.txt"))
        logger.info(f"Found {len(text_files)} text files in {kb_root}")
        
        # Also process Trade Template directory
        trade_template_dir = kb_path / "Trade Template"
        trade_template_files = []
        if trade_template_dir.exists():
            trade_template_files = list(trade_template_dir.glob("*.docx")) + list(trade_template_dir.glob("*.doc"))
            logger.info(f"Found {len(trade_template_files)} trade template files")
        else:
            logger.info("No Trade Template directory found")
        
        if not text_files and not trade_template_files:
            logger.warning("No text files or trade template files found")
            return {"status": "warning", "message": "No files found to process"}
        
        # Process all text files
        all_texts: List[str] = []
        all_payloads: List[Dict[str, Any]] = []
        processed_files = 0
        
        for text_file in tqdm(text_files, desc="Processing files", disable=not sys.stdout.isatty()):
            try:
                # Find corresponding video folder
                video_number = text_file.stem.replace("PTM Video ", "").split(" - ")[0]
                # Handle both "Video 4" and "Video 04" formats
                video_folder = kb_path / f"Video {video_number}"
                if not video_folder.exists():
                    # Try with zero-padded format
                    video_folder = kb_path / f"Video {video_number.zfill(2)}"
                
                chunks_data = process_text_file(text_file, video_folder, SETTINGS)
                for text, payload in chunks_data:
                    all_texts.append(text)
                    all_payloads.append(payload)
                processed_files += 1
                
            except Exception as e:
                logger.error(f"Failed to process text file {text_file}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_files}/{len(text_files)} text files")
        
        # Process trade template files
        if trade_template_files:
            logger.info("Processing trade template files...")
            for template_file in tqdm(trade_template_files, desc="Processing trade templates", disable=not sys.stdout.isatty()):
                try:
                    chunks_data = process_trade_template_file(template_file, SETTINGS)
                    for text, payload in chunks_data:
                        all_texts.append(text)
                        all_payloads.append(payload)
                    processed_files += 1
                    logger.info(f"Processed trade template: {template_file.name}")
                except Exception as e:
                    logger.error(f"Failed to process trade template {template_file}: {e}")
                    continue
        
        logger.info(f"Total processed files: {processed_files}")
        logger.info(f"Total chunks to embed: {len(all_texts)}")
        
        if not all_texts:
            logger.warning("No chunks to process")
            return {"status": "warning", "message": "No chunks to process"}
        
        # Process in batches
        total_batches = 0
        successful_batches = 0
        
        for batch in tqdm(
            batched(zip(all_texts, all_payloads), SETTINGS.batch_size), 
            desc="Embedding and indexing" if not dry_run else "Processing embeddings",
            disable=not sys.stdout.isatty()
        ):
            total_batches += 1
            try:
                texts = [t for t, _ in batch]
                payloads = [p for _, p in batch]
                
                # Generate embeddings with explicit batch size
                vectors = embed.encode(texts, batch_size=SETTINGS.batch_size)
                
                # Upload to Qdrant (unless dry run)
                if not dry_run and client:
                    upsert_points(client, collection, vectors.tolist(), payloads)
                
                successful_batches += 1
                logger.debug(f"Processed batch {total_batches} with {len(texts)} items")
                
            except Exception as e:
                logger.error(f"Failed to process batch {total_batches}: {e}")
                continue
        
        # Return statistics
        stats = {
            "status": "success",
            "total_chunks": len(all_texts),
            "processed_files": processed_files,
            "total_files": len(text_files),
            "successful_batches": successful_batches,
            "total_batches": total_batches,
            "dry_run": dry_run
        }
        
        logger.info("Advanced ingestion completed successfully ✅")
        logger.info(f"Statistics: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Advanced ingestion failed: {e}")
        raise RuntimeError(f"Advanced ingestion failed: {e}") from e

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description="Advanced ingestion with proper file parsing")
    parser.add_argument("--kb-root", type=str, default=SETTINGS.kb_root, 
                       help="Root directory of the knowledge base")
    parser.add_argument("--collection", type=str, default=SETTINGS.collection,
                       help="Name of the Qdrant collection")
    parser.add_argument("--dry-run", action="store_true",
                       help="Process data without uploading to Qdrant")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        stats = ingest_advanced(args.kb_root, args.collection, dry_run=args.dry_run)
        
        if stats["status"] == "success":
            print(f"\n[SUCCESS] Advanced ingestion completed successfully!")
            print(f"   Total chunks processed: {stats['total_chunks']}")
            print(f"   Files processed: {stats['processed_files']}/{stats['total_files']}")
            print(f"   Successful batches: {stats['successful_batches']}/{stats['total_batches']}")
            if args.dry_run:
                print("   (Dry run mode - no data uploaded)")
        else:
            print(f"\n[WARNING] Advanced ingestion completed with warnings: {stats.get('message', 'Unknown issue')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] Advanced ingestion failed: {e}")
        sys.exit(1)
