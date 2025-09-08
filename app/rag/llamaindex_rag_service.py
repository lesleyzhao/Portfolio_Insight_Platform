#!/usr/bin/env python3
"""
LlamaIndex RAG Service
Integrates LlamaIndex with our existing Qdrant vector database
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# LlamaIndex imports
try:
    from llama_index.core import VectorStoreIndex, Document, ServiceContext, StorageContext
    from llama_index.llms.ollama import Ollama
    from llama_index.llms.huggingface import HuggingFaceLLM
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logging.warning(f"LlamaIndex not available: {e}")

logger = logging.getLogger(__name__)

class LlamaIndexRAGService:
    """
    LlamaIndex RAG Service
    Provides intelligent querying over financial documents using LlamaIndex
    """
    
    def __init__(self, 
                 qdrant_url: str = "http://localhost:6333",
                 collection_name: str = "financial_documents",
                 llm_model: str = "llama2"):
        """
        Initialize LlamaIndex RAG service
        
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
            # Try a better Hugging Face model for text generation
            self.llm = HuggingFaceLLM(
                model_name="microsoft/DialoGPT-small",  # Use smaller model for better compatibility
                device_map="auto",
                max_new_tokens=150,
                pad_token_id=50256,  # Fix the tokenizer warning
                eos_token_id=50256
            )
            logger.info("Using Hugging Face LLM (DialoGPT-small)")
        except Exception as e:
            logger.warning(f"Hugging Face LLM not available: {e}")
            try:
                # Try a different model
                self.llm = HuggingFaceLLM(
                    model_name="gpt2",
                    device_map="auto",
                    max_new_tokens=100
                )
                logger.info("Using Hugging Face LLM (GPT-2)")
            except Exception as e2:
                logger.warning(f"GPT-2 not available: {e2}")
                try:
                    # Fallback to Ollama (if available)
                    self.llm = Ollama(model=self.llm_model)
                    logger.info(f"Using Ollama LLM: {self.llm_model}")
                except Exception as e3:
                    logger.error(f"Failed to setup LLM: {e3}")
                    # Use a simple mock LLM for testing
                    self.llm = None
                    logger.warning("Using mock LLM for testing")
    
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
        try:
            # Use Settings instead of ServiceContext (newer LlamaIndex)
            from llama_index.core import Settings
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            
            # Create index from existing vector store
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=self.vector_store
            )
            
            # Create query engine with better configuration
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=3,  # Reduce to get more focused results
                response_mode="compact",
                verbose=True  # Enable verbose output for debugging
            )
            logger.info("LlamaIndex query engine ready")
            
        except Exception as e:
            logger.error(f"Error setting up query engine: {e}")
            # Create a simple fallback
            self.query_engine = None
            logger.warning("Using fallback query engine")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system using LlamaIndex
        
        Args:
            question: Natural language question
            
        Returns:
            RAG response with answer and metadata
        """
        try:
            if self.query_engine is None:
                return self._fallback_query(question)
            
            logger.info(f"Processing query with LlamaIndex: {question}")
            response = self.query_engine.query(question)
            
            return {
                'question': question,
                'answer': str(response),
                'source': 'LlamaIndex',
                'llm_model': self.llm_model,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error in LlamaIndex query: {e}")
            return self._fallback_query(question)
    
    def _fallback_query(self, question: str) -> Dict[str, Any]:
        """Fallback query when LlamaIndex is not available"""
        # Try to provide a meaningful response using vector search
        try:
            from app.services.simple_vector_service import SimpleVectorService
            vector_service = SimpleVectorService()
            
            # Search for relevant documents
            results = vector_service.search_documents(question, top_k=3)
            
            if results:
                # Extract key information from search results
                companies = []
                revenues = []
                
                for result in results:
                    metadata = result.get('metadata', {})
                    content = result.get('content', '')
                    
                    if 'company' in metadata:
                        companies.append(metadata['company'])
                    
                    # Extract revenue information
                    if 'revenue' in content.lower() or '$' in content:
                        # Find revenue numbers in the content
                        import re
                        revenue_matches = re.findall(r'\$[\d.]+ billion', content)
                        if revenue_matches:
                            revenues.extend(revenue_matches)
                
                # Generate a simple response
                if companies and revenues:
                    answer = f"Based on the available financial data: {', '.join(set(companies))} companies show revenues including {', '.join(set(revenues[:3]))}."
                elif companies:
                    answer = f"Found financial information for: {', '.join(set(companies))}."
                else:
                    answer = f"Found relevant financial documents, but specific revenue data for '{question}' is not clearly stated."
            else:
                answer = f"No relevant financial documents found for: {question}"
            
            return {
                'question': question,
                'answer': answer,
                'source': 'Vector Search Fallback',
                'llm_model': 'None',
                'success': True
            }
            
        except Exception as e:
            return {
                'question': question,
                'answer': f"LlamaIndex query engine is not available. Question: {question}",
                'source': 'Fallback',
                'llm_model': 'None',
                'success': False,
                'error': f'LlamaIndex not properly configured: {e}'
            }
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the RAG system
        
        Args:
            documents: List of LlamaIndex Document objects
        """
        try:
            if self.index is None:
                logger.error("Index not available for adding documents")
                return
            
            # Add to existing index
            for doc in documents:
                self.index.insert(doc)
            logger.info(f"Added {len(documents)} documents to LlamaIndex")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            return {
                'status': 'active',
                'llm_model': self.llm_model,
                'embedding_model': 'all-MiniLM-L6-v2',
                'vector_store': 'Qdrant',
                'collection_name': self.collection_name,
                'total_vectors': collection_info.vectors_count,
                'llamaindex_available': LLAMAINDEX_AVAILABLE,
                'query_engine_ready': self.query_engine is not None
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'status': 'error', 
                'error': str(e),
                'llamaindex_available': LLAMAINDEX_AVAILABLE
            }


def test_llamaindex_rag():
    """Test the LlamaIndex RAG service"""
    print("🧠 Testing LlamaIndex RAG Service")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        rag = LlamaIndexRAGService()
        
        # Get stats
        stats = rag.get_stats()
        print(f"✅ LlamaIndex RAG Service initialized")
        print(f"   LLM Model: {stats.get('llm_model', 'Unknown')}")
        print(f"   Embedding Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"   Total Vectors: {stats.get('total_vectors', 0)}")
        print(f"   Query Engine Ready: {stats.get('query_engine_ready', False)}")
        
        # Test query
        print("\n🔍 Testing query...")
        question = "What is Apple's revenue?"
        result = rag.query(question)
        
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        print(f"Source: {result['source']}")
        print(f"Success: {result['success']}")
        
        print("\n🎉 LlamaIndex RAG test completed!")
        
    except Exception as e:
        print(f"❌ LlamaIndex RAG test failed: {e}")
        print("\nTo fix this:")
        print("1. Make sure Qdrant is running: docker ps | grep qdrant")
        print("2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("3. Download a model: ollama pull llama2")


if __name__ == "__main__":
    test_llamaindex_rag()
