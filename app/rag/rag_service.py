#!/usr/bin/env python3
"""
RAG Service using LlamaIndex
Integrates with our existing vector database and provides intelligent querying
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# LlamaIndex imports
try:
    from llama_index import VectorStoreIndex, Document, ServiceContext
    from llama_index.llms import Ollama, HuggingFaceLLM
    from llama_index.embeddings import HuggingFaceEmbedding
    from llama_index.vector_stores import QdrantVectorStore
    from llama_index.storage.storage_context import StorageContext
    from qdrant_client import QdrantClient
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False
    logging.warning("LlamaIndex not available. Install with: pip install llama-index")

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG Service using LlamaIndex
    Provides intelligent querying over financial documents
    """
    
    def __init__(self, 
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "financial_documents",
                 llm_model: str = "llama2"):
        """
        Initialize RAG service
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Vector collection name
            llm_model: LLM model to use (llama2, gpt4all, etc.)
        """
        if not LLAMAINDEX_AVAILABLE:
            raise ImportError("LlamaIndex not available. Install with: pip install llama-index")
        
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.llm_model = llm_model
        
        # Initialize components
        self._setup_llm()
        self._setup_embeddings()
        self._setup_vector_store()
        self._setup_query_engine()
    
    def _setup_llm(self):
        """Setup LLM (local or cloud)"""
        try:
            # Try Ollama first (local, free)
            self.llm = Ollama(model=self.llm_model)
            logger.info(f"Using Ollama LLM: {self.llm_model}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            try:
                # Fallback to Hugging Face
                self.llm = HuggingFaceLLM(
                    model_name="microsoft/DialoGPT-medium",
                    device_map="auto"
                )
                logger.info("Using Hugging Face LLM")
            except Exception as e2:
                logger.error(f"Failed to setup LLM: {e2}")
                raise
    
    def _setup_embeddings(self):
        """Setup embeddings (local)"""
        self.embed_model = HuggingFaceEmbedding(
            model_name="all-MiniLM-L6-v2"
        )
        logger.info("Using Hugging Face embeddings")
    
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
        # Create service context
        service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embed_model
        )
        
        # Create index from existing vector store
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            service_context=service_context
        )
        
        # Create query engine
        self.query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )
        logger.info("RAG query engine ready")
    
    def query(self, question: str) -> str:
        """
        Query the RAG system
        
        Args:
            question: Natural language question
            
        Returns:
            Answer from the RAG system
        """
        try:
            logger.info(f"Processing query: {question}")
            response = self.query_engine.query(question)
            return str(response)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the RAG system
        
        Args:
            documents: List of LlamaIndex Document objects
        """
        try:
            # Add to existing index
            for doc in documents:
                self.index.insert(doc)
            logger.info(f"Added {len(documents)} documents to RAG system")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            return {
                "status": "active",
                "llm_model": self.llm_model,
                "embedding_model": "all-MiniLM-L6-v2",
                "vector_store": "Qdrant",
                "collection_name": self.collection_name,
                "total_vectors": collection_info.vectors_count,
                "llamaindex_available": LLAMAINDEX_AVAILABLE
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"status": "error", "error": str(e)}


def test_rag_service():
    """Test the RAG service"""
    print("🧠 Testing RAG Service with LlamaIndex")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        rag = RAGService()
        
        # Get stats
        stats = rag.get_stats()
        print(f"✅ RAG Service initialized")
        print(f"   LLM Model: {stats.get('llm_model', 'Unknown')}")
        print(f"   Embedding Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"   Total Vectors: {stats.get('total_vectors', 0)}")
        
        # Test query
        print("\n🔍 Testing query...")
        question = "What is Apple's revenue?"
        answer = rag.query(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        
        print("\n🎉 RAG Service test completed!")
        
    except Exception as e:
        print(f"❌ RAG Service test failed: {e}")
        print("\nTo fix this:")
        print("1. Install LlamaIndex: pip install llama-index")
        print("2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("3. Download a model: ollama pull llama2")


if __name__ == "__main__":
    test_rag_service()
