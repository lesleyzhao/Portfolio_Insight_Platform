#!/usr/bin/env python3
"""
Hybrid GPT-4 RAG Service
Uses Hugging Face embeddings (free) + GPT-4 for generation (paid)
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# LlamaIndex imports
try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logging.warning(f"LlamaIndex not available: {e}")

logger = logging.getLogger(__name__)

class HybridGPT4RAGService:
    """
    Hybrid GPT-4 RAG Service
    Uses Hugging Face embeddings (free) + GPT-4 for generation (paid)
    """
    
    def __init__(self, 
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "financial_documents",
                 model: str = "gpt-4"):
        """
        Initialize Hybrid GPT-4 RAG service
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Vector collection name
            model: OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError("LlamaIndex not available. Install with: pip install llama-index")
        
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.model = model
        
        # Check OpenAI API key
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key or self.openai_api_key == 'your_openai_api_key_here':
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Initialize components
        self._setup_llm()
        self._setup_embeddings()
        self._setup_vector_store()
        self._setup_query_engine()
    
    def _setup_llm(self):
        """Setup OpenAI LLM"""
        try:
            self.llm = OpenAI(
                model=self.model,
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=500
            )
            logger.info(f"Using OpenAI LLM: {self.model}")
        except Exception as e:
            logger.error(f"Failed to setup OpenAI LLM: {e}")
            raise
    
    def _setup_embeddings(self):
        """Setup Hugging Face embeddings (free)"""
        try:
            self.embed_model = HuggingFaceEmbedding(
                model_name="all-MiniLM-L6-v2"
            )
            logger.info("Using Hugging Face embeddings (free)")
        except Exception as e:
            logger.error(f"Failed to setup Hugging Face embeddings: {e}")
            raise
    
    def _setup_vector_store(self):
        """Setup vector store connection"""
        self.qdrant_client = QdrantClient(url=self.qdrant_url)
        
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name
        )
        logger.info(f"Connected to Qdrant collection: {self.collection_name}")
    
    def _setup_query_engine(self):
        """Setup query engine"""
        try:
            # Use Settings for newer LlamaIndex
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            
            # Create index from existing vector store
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            # Create query engine with GPT-4
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=5,
                response_mode="compact",
                verbose=True
            )
            logger.info("Hybrid GPT-4 query engine ready")
            
        except Exception as e:
            logger.error(f"Error setting up query engine: {e}")
            raise
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system using GPT-4
        
        Args:
            question: Natural language question
            
        Returns:
            RAG response with answer and metadata
        """
        try:
            logger.info(f"Processing query with Hybrid GPT-4: {question}")
            response = self.query_engine.query(question)
            
            return {
                'question': question,
                'answer': str(response),
                'source': 'Hybrid GPT-4 RAG',
                'llm_model': self.model,
                'embedding_model': 'Hugging Face (free)',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error in Hybrid GPT-4 query: {e}")
            return {
                'question': question,
                'answer': f"Error processing query: {e}",
                'source': 'Hybrid GPT-4 RAG',
                'llm_model': self.model,
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            return {
                'status': 'active',
                'llm_model': self.model,
                'embedding_model': 'all-MiniLM-L6-v2 (Hugging Face)',
                'vector_store': 'Qdrant',
                'collection_name': self.collection_name,
                'total_vectors': collection_info.vectors_count,
                'llamaindex_available': LLAMAINDEX_AVAILABLE,
                'query_engine_ready': self.query_engine is not None,
                'cost_optimization': 'Free embeddings + Paid generation'
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'status': 'error', 
                'error': str(e),
                'llamaindex_available': LLAMAINDEX_AVAILABLE
            }


def test_hybrid_gpt4_rag():
    """Test the Hybrid GPT-4 RAG service"""
    print("🧠 Testing Hybrid GPT-4 RAG Service")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        rag = HybridGPT4RAGService()
        
        # Get stats
        stats = rag.get_stats()
        print(f"✅ Hybrid GPT-4 RAG Service initialized")
        print(f"   LLM Model: {stats.get('llm_model', 'Unknown')}")
        print(f"   Embedding Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"   Total Vectors: {stats.get('total_vectors', 0)}")
        print(f"   Query Engine Ready: {stats.get('query_engine_ready', False)}")
        print(f"   Cost Optimization: {stats.get('cost_optimization', 'Unknown')}")
        
        # Test query
        print("\n🔍 Testing query...")
        question = "What is Apple's revenue in 2023?"
        result = rag.query(question)
        
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        print(f"Source: {result['source']}")
        print(f"Success: {result['success']}")
        
        print("\n🎉 Hybrid GPT-4 RAG test completed!")
        
    except Exception as e:
        print(f"❌ Hybrid GPT-4 RAG test failed: {e}")
        print("\nTo fix this:")
        print("1. Make sure you have a valid OpenAI API key")
        print("2. Check your OpenAI billing/credits")
        print("3. Ensure Qdrant is running")


if __name__ == "__main__":
    test_hybrid_gpt4_rag()
