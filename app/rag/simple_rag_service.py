#!/usr/bin/env python3
"""
Simple RAG Service without LlamaIndex
Direct implementation using our existing vector database
"""

import logging
from typing import List, Dict, Any
from app.services.simple_vector_service import SimpleVectorService
from app.services.sec_edgar_service import SECEdgarService

logger = logging.getLogger(__name__)

class SimpleRAGService:
    """
    Simple RAG Service without LlamaIndex
    Uses our existing vector database + local LLM
    """
    
    def __init__(self):
        self.vector_service = SimpleVectorService()
        self.sec_service = SECEdgarService()
    
    def query(self, question: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: Natural language question
            max_results: Maximum number of relevant documents to return
            
        Returns:
            RAG response with relevant documents and answer
        """
        try:
            # 1. Search for relevant documents
            search_results = self.vector_service.search_documents(
                query=question,
                top_k=max_results
            )
            
            # 2. Extract relevant content
            relevant_docs = []
            for result in search_results:
                doc_info = {
                    'ticker': result.get('metadata', {}).get('ticker', 'Unknown'),
                    'filing_type': result.get('metadata', {}).get('filing_type', 'Unknown'),
                    'score': result.get('score', 0),
                    'content_preview': result.get('payload', {}).get('content', '')[:200] + '...'
                }
                relevant_docs.append(doc_info)
            
            # 3. Generate answer (simple template-based for now)
            answer = self._generate_answer(question, relevant_docs)
            
            return {
                'question': question,
                'answer': answer,
                'relevant_documents': relevant_docs,
                'total_documents_found': len(relevant_docs)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                'question': question,
                'answer': f"Sorry, I encountered an error: {str(e)}",
                'relevant_documents': [],
                'total_documents_found': 0
            }
    
    def _generate_answer(self, question: str, docs: List[Dict]) -> str:
        """
        Generate answer based on relevant documents
        This is a simple template-based approach
        For production, you'd use a local LLM here
        """
        if not docs:
            return "I couldn't find any relevant information to answer your question."
        
        # Simple template-based answer
        answer_parts = []
        
        # Add context from documents
        for i, doc in enumerate(docs, 1):
            ticker = doc['ticker']
            filing_type = doc['filing_type']
            score = doc['score']
            
            answer_parts.append(
                f"Based on {ticker}'s {filing_type} filing (relevance: {score:.2f}):"
            )
            answer_parts.append(f"  {doc['content_preview']}")
        
        # Add simple answer based on question keywords
        question_lower = question.lower()
        if 'revenue' in question_lower:
            answer_parts.insert(0, "Here's what I found about revenue:")
        elif 'profit' in question_lower:
            answer_parts.insert(0, "Here's what I found about profit:")
        elif 'apple' in question_lower:
            answer_parts.insert(0, "Here's what I found about Apple:")
        else:
            answer_parts.insert(0, "Here's what I found:")
        
        return "\n".join(answer_parts)
    
    def add_documents_from_sec(self, ticker: str, filing_types: List[str] = ['10-K']) -> Dict[str, Any]:
        """
        Add SEC documents to the RAG system
        
        Args:
            ticker: Company ticker symbol
            filing_types: List of filing types to download
            
        Returns:
            Result of document addition
        """
        try:
            # Download SEC filings
            download_result = self.sec_service.download_company_filings(
                ticker=ticker,
                filing_types=filing_types,
                limit=2
            )
            
            if download_result['total_downloaded'] == 0:
                return {
                    'status': 'error',
                    'message': 'No documents downloaded',
                    'ticker': ticker
                }
            
            # Process and add to vector database
            added_docs = 0
            for filing in download_result['downloaded_filings']:
                try:
                    # Extract content
                    content = self.sec_service.extract_filing_content(filing['file_path'])
                    
                    if content['success']:
                        # Add to vector database
                        doc_id = self.vector_service.add_document(
                            content=content['content'],
                            metadata={
                                'ticker': ticker,
                                'filing_type': filing['filing_type'],
                                'file_path': filing['file_path'],
                                'downloaded_at': filing['downloaded_at']
                            }
                        )
                        added_docs += 1
                        logger.info(f"Added document {doc_id} for {ticker}")
                
                except Exception as e:
                    logger.error(f"Error processing filing {filing['file_path']}: {e}")
            
            return {
                'status': 'success',
                'ticker': ticker,
                'documents_added': added_docs,
                'total_downloaded': download_result['total_downloaded']
            }
            
        except Exception as e:
            logger.error(f"Error adding documents for {ticker}: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'ticker': ticker
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            # Get vector service stats
            vector_stats = self.vector_service.get_collection_info()
            
            return {
                'status': 'active',
                'vector_database': 'Qdrant',
                'embedding_model': 'Hugging Face (all-MiniLM-L6-v2)',
                'total_documents': vector_stats.get('vectors_count', 0),
                'collection_name': vector_stats.get('collection_name', 'unknown'),
                'rag_type': 'Simple Template-based'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


def test_simple_rag():
    """Test the simple RAG service"""
    print("🧠 Testing Simple RAG Service")
    print("=" * 40)
    
    try:
        # Initialize RAG service
        rag = SimpleRAGService()
        
        # Get stats
        stats = rag.get_stats()
        print(f"✅ RAG Service initialized")
        print(f"   Total Documents: {stats.get('total_documents', 0)}")
        print(f"   Embedding Model: {stats.get('embedding_model', 'Unknown')}")
        print(f"   RAG Type: {stats.get('rag_type', 'Unknown')}")
        
        # Test query
        print("\n🔍 Testing query...")
        question = "What is Apple's revenue?"
        result = rag.query(question)
        
        print(f"Question: {result['question']}")
        print(f"Answer: {result['answer']}")
        print(f"Relevant Documents: {result['total_documents_found']}")
        
        print("\n🎉 Simple RAG test completed!")
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")


if __name__ == "__main__":
    test_simple_rag()
