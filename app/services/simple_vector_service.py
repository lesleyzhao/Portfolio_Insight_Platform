"""
Simple Vector Database Service for Financial Document Storage and Retrieval
Uses Qdrant directly without LlamaIndex to avoid import issues
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
import openai

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, SearchRequest

logger = logging.getLogger(__name__)


class SimpleVectorService:
    """Simple service for managing financial documents in Qdrant vector database"""
    
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
        
        # Initialize OpenAI client
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for embeddings")
        
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Collection name for financial documents
        self.collection_name = "financial_documents"
        
        # Initialize collection if it doesn't exist
        self._ensure_collection_exists()
    
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
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
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
            
            # Get embedding for the content
            embedding = self._get_embedding(content)
            
            # Create point for Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'document_id': document_id,
                    'content': content,
                    'metadata': metadata,
                    'created_at': datetime.now().isoformat()
                }
            )
            
            # Add point to collection
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
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
            # Get embedding for query
            query_embedding = self._get_embedding(query)
            
            # Build filter if needed
            filter_conditions = []
            if tickers:
                filter_conditions.append(FieldCondition(
                    key="metadata.ticker",
                    match=MatchValue(any=tickers)
                ))
            if report_types:
                filter_conditions.append(FieldCondition(
                    key="metadata.report_type",
                    match=MatchValue(any=report_types)
                ))
            
            # Create filter
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=top_k,
                with_payload=True
            )
            
            # Format results
            results = []
            for result in search_results:
                payload = result.payload
                results.append({
                    'content': payload.get('content', ''),
                    'metadata': payload.get('metadata', {}),
                    'score': result.score,
                    'document_id': payload.get('document_id', '')
                })
            
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
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id)
                    )]
                ),
                limit=1,
                with_payload=True
            )
            
            if results[0]:
                payload = results[0][0].payload
                return {
                    'content': payload.get('content', ''),
                    'metadata': payload.get('metadata', {}),
                    'document_id': payload.get('document_id', '')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {e}")
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
        vector_service = SimpleVectorService()
        
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
