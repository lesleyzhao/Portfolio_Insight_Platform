"""
Vector Database Service for Financial Document Storage and Retrieval
Uses Qdrant for vector storage and LlamaIndex for RAG operations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
# Simplified imports to avoid circular import issues
try:
    from llama_index.core import VectorStoreIndex, Document, StorageContext
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.core.node_parser import SimpleNodeParser
    from llama_index.core.schema import MetadataMode
    LLAMA_INDEX_AVAILABLE = True
except ImportError as e:
    print(f"LlamaIndex import error: {e}")
    LLAMA_INDEX_AVAILABLE = False

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing financial documents in Qdrant vector database"""
    
    def __init__(self, qdrant_url: str = "http://localhost:6333", openai_api_key: Optional[str] = None):
        """
        Initialize the vector service
        
        Args:
            qdrant_url: Qdrant server URL
            openai_api_key: OpenAI API key for embeddings
        """
        self.qdrant_url = qdrant_url
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)
        
        # Initialize OpenAI embeddings
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        self.embedding_model = OpenAIEmbedding(api_key=self.openai_api_key)
        
        # Collection name for financial documents
        self.collection_name = "financial_documents"
        
        # Initialize collection if it doesn't exist
        self._ensure_collection_exists()
        
        # Initialize LlamaIndex components
        self._setup_llamaindex()
    
    def _ensure_collection_exists(self):
        """Create the collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def _setup_llamaindex(self):
        """Setup LlamaIndex components"""
        try:
            # Create Qdrant vector store
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name
            )
            
            # Create storage context
            self.storage_context = StorageContext.from_defaults(
                vector_store=self.vector_store
            )
            
            # Create node parser for chunking documents
            self.node_parser = SimpleNodeParser.from_defaults(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            # Load existing index or create new one
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=self.storage_context,
                    embed_model=self.embedding_model
                )
                logger.info("Loaded existing vector index")
            except Exception:
                # Create new index if none exists
                self.index = VectorStoreIndex.from_documents(
                    documents=[],
                    storage_context=self.storage_context,
                    embed_model=self.embedding_model
                )
                logger.info("Created new vector index")
                
        except Exception as e:
            logger.error(f"Error setting up LlamaIndex: {e}")
            raise
    
    def add_document(self, 
                    content: str, 
                    metadata: Dict[str, Any], 
                    document_id: Optional[str] = None) -> str:
        """
        Add a document to the vector database
        
        Args:
            content: Document text content
            metadata: Document metadata (ticker, company, report_type, etc.)
            document_id: Optional document ID
            
        Returns:
            Document ID
        """
        try:
            # Generate document ID if not provided
            if not document_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ticker = metadata.get('ticker', 'UNKNOWN')
                report_type = metadata.get('report_type', 'DOC')
                document_id = f"{ticker}_{report_type}_{timestamp}"
            
            # Create LlamaIndex document
            document = Document(
                text=content,
                metadata={
                    **metadata,
                    'document_id': document_id,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            # Parse document into nodes
            nodes = self.node_parser.get_nodes_from_documents([document])
            
            # Add nodes to the index
            self.index.insert_nodes(nodes)
            
            logger.info(f"Added document {document_id} to vector database")
            return document_id
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def search_documents(self, 
                        query: str, 
                        tickers: Optional[List[str]] = None,
                        report_types: Optional[List[str]] = None,
                        top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents using semantic similarity
        
        Args:
            query: Search query
            tickers: Optional list of tickers to filter by
            report_types: Optional list of report types to filter by
            top_k: Number of results to return
            
        Returns:
            List of matching documents with metadata and scores
        """
        try:
            # Create query engine
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
                response_mode="no_text"  # We only want metadata and scores
            )
            
            # Build filter if needed
            filters = []
            if tickers:
                filters.append(FieldCondition(
                    key="ticker",
                    match=MatchValue(any=tickers)
                ))
            if report_types:
                filters.append(FieldCondition(
                    key="report_type",
                    match=MatchValue(any=report_types)
                ))
            
            # Perform search
            if filters:
                # Note: LlamaIndex filtering is more complex, 
                # for now we'll do post-filtering
                response = query_engine.query(query)
            else:
                response = query_engine.query(query)
            
            # Extract results
            results = []
            if hasattr(response, 'source_nodes'):
                for node in response.source_nodes:
                    result = {
                        'content': node.text,
                        'metadata': node.metadata,
                        'score': getattr(node, 'score', 0.0)
                    }
                    results.append(result)
            
            # Apply post-filtering if needed
            if tickers or report_types:
                filtered_results = []
                for result in results:
                    metadata = result['metadata']
                    if tickers and metadata.get('ticker') not in tickers:
                        continue
                    if report_types and metadata.get('report_type') not in report_types:
                        continue
                    filtered_results.append(result)
                results = filtered_results
            
            logger.info(f"Found {len(results)} documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            # Search for document with specific ID
            results = self.search_documents(
                query="",  # Empty query to get all documents
                top_k=1000  # Large number to get all documents
            )
            
            for result in results:
                if result['metadata'].get('document_id') == document_id:
                    return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the vector database
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Note: LlamaIndex doesn't have direct delete by ID
            # This would require more complex implementation
            # For now, we'll mark it as a TODO
            logger.warning(f"Delete document {document_id} not implemented yet")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Collection statistics
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            stats = {
                'collection_name': self.collection_name,
                'vectors_count': collection_info.vectors_count,
                'indexed_vectors_count': collection_info.indexed_vectors_count,
                'points_count': collection_info.points_count,
                'segments_count': collection_info.segments_count,
                'status': collection_info.status
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            raise
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection_exists()
            self._setup_llamaindex()
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise


# Example usage and testing
if __name__ == "__main__":
    # Test the vector service
    try:
        # Initialize service
        vector_service = VectorService()
        
        # Test adding a document
        test_metadata = {
            'ticker': 'AAPL',
            'company': 'Apple Inc.',
            'report_type': '10-K',
            'filing_date': '2024-01-01',
            'sector': 'Technology'
        }
        
        test_content = """
        Apple Inc. is a multinational technology company that designs, develops, and sells consumer electronics, 
        computer software, and online services. The company's hardware products include the iPhone smartphone, 
        iPad tablet computer, Mac personal computer, iPod portable media player, Apple Watch smartwatch, 
        Apple TV digital media player, AirPods wireless earbuds and HomePod smart speaker.
        """
        
        doc_id = vector_service.add_document(
            content=test_content,
            metadata=test_metadata
        )
        
        print(f"Added document with ID: {doc_id}")
        
        # Test search
        results = vector_service.search_documents(
            query="Apple iPhone products",
            top_k=5
        )
        
        print(f"Search results: {len(results)} documents found")
        for result in results:
            print(f"- {result['metadata']['ticker']}: {result['score']:.3f}")
        
        # Test collection stats
        stats = vector_service.get_collection_stats()
        print(f"Collection stats: {stats}")
        
    except Exception as e:
        print(f"Error testing vector service: {e}")
