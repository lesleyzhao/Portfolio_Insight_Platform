#!/usr/bin/env python3
"""
Test script for RAG Service with LlamaIndex
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rag_service import RAGService, test_rag_service

if __name__ == "__main__":
    test_rag_service()
