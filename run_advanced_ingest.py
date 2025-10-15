#!/usr/bin/env python3
"""
Script to run the advanced ingestion process with proper PPTX, DOCX, and PDF parsing.
Excludes CSV and Excel files as requested.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Now import and run
from src.advanced_ingest import ingest_advanced

def main():
    print("[STARTING] Advanced Knowledge Base Ingestion...")
    print("=" * 60)
    print("Processing with proper parsers:")
    print("  [OK] TXT files (transcripts)")
    print("  [OK] PDF files (with pdfplumber)")
    print("  [OK] PPTX files (with python-pptx)")
    print("  [OK] DOCX files (with python-docx)")
    print("  [SKIP] CSV files (excluded)")
    print("  [SKIP] Excel files (excluded)")
    print("=" * 60)
    
    try:
        # Run advanced ingestion
        result = ingest_advanced(
            kb_root="./KB",
            collection="ptm_knowledge_base",
            dry_run=False
        )
        
        print("\n[SUCCESS] Advanced ingestion completed successfully!")
        print(f"[STATS] Statistics:")
        print(f"   - Total chunks: {result.get('total_chunks', 0)}")
        print(f"   - Files processed: {result.get('processed_files', 0)}")
        print(f"   - Successful batches: {result.get('successful_batches', 0)}")
        
        print(f"\n[INFO] Advanced processing includes:")
        print(f"   - Text files (transcripts)")
        print(f"   - PDF files (with proper text and table extraction)")
        print(f"   - PPTX files (with slide and table extraction)")
        print(f"   - DOCX files (with paragraph and table extraction)")
        print(f"   - Rich metadata extraction for all file types")
        
    except Exception as e:
        print(f"\n[ERROR] Advanced ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
