"""
RAG (Retrieval-Augmented Generation) Module

This module contains all RAG-related services for the Portfolio Insight Platform.

Available Services:
- SimpleVectorService: Basic vector operations with Qdrant
- SimpleRAGService: Basic RAG without LlamaIndex
- LlamaIndexRAGService: Full LlamaIndex RAG with local LLMs
- GPT4RAGService: OpenAI GPT-4 RAG (requires API credits)
- HybridGPT4RAGService: Cost-effective GPT-4 with free embeddings
"""

from .simple_vector_service import SimpleVectorService
from .simple_rag_service import SimpleRAGService
from .llamaindex_rag_service import LlamaIndexRAGService
from .gpt4_rag_service import GPT4RAGService
from .hybrid_gpt4_rag_service import HybridGPT4RAGService

__all__ = [
    'SimpleVectorService',
    'SimpleRAGService', 
    'LlamaIndexRAGService',
    'GPT4RAGService',
    'HybridGPT4RAGService'
]
