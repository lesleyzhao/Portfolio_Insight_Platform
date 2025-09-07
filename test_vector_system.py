#!/usr/bin/env python3
"""
Test script for the vector database system
Downloads a few S&P 500 reports and tests vector search
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.services.sec_edgar_service import SECEdgarService
from app.services.simple_vector_service import SimpleVectorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_system():
    """Test the complete vector system"""
    
    # Check if OpenAI API key is set
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key or openai_api_key == 'your_openai_api_key_here':
        logger.error("Please set OPENAI_API_KEY environment variable")
        logger.info("You can set it with: export OPENAI_API_KEY='your-actual-api-key'")
        return False
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        sec_service = SECEdgarService()
        vector_service = SimpleVectorService(openai_api_key=openai_api_key)
        
        # Test downloading a single company's filings
        logger.info("Testing SEC Edgar download...")
        test_result = sec_service.download_company_filings(
            ticker='AAPL',
            filing_types=['10-K'],
            limit=1
        )
        
        logger.info(f"Download result: {test_result}")
        
        if test_result['total_downloaded'] > 0:
            # Process the downloaded filing
            filing_info = test_result['downloaded_filings'][0]
            logger.info(f"Processing filing: {filing_info['file_path']}")
            
            # Extract content
            content_data = sec_service.extract_filing_content(filing_info['file_path'])
            logger.info(f"Extracted content: {len(content_data.get('content', ''))} characters")
            
            if content_data.get('content'):
                # Prepare metadata
                metadata = {
                    'ticker': content_data.get('ticker', 'AAPL'),
                    'filing_type': content_data.get('filing_type', '10-K'),
                    'filing_date': content_data.get('filing_date'),
                    'file_path': filing_info['file_path'],
                    'word_count': content_data.get('word_count', 0),
                    'sections': list(content_data.get('sections', {}).keys()),
                    'downloaded_at': filing_info['downloaded_at'],
                    'ingested_at': '2024-01-01T00:00:00'
                }
                
                # Add to vector database
                logger.info("Adding document to vector database...")
                doc_id = vector_service.add_document(
                    content=content_data['content'][:5000],  # Limit content for testing
                    metadata=metadata
                )
                
                logger.info(f"Added document with ID: {doc_id}")
                
                # Test search
                logger.info("Testing vector search...")
                search_results = vector_service.search_documents(
                    query="Apple iPhone products revenue",
                    top_k=3
                )
                
                logger.info(f"Search results: {len(search_results)} documents found")
                for i, result in enumerate(search_results):
                    logger.info(f"  {i+1}. {result['metadata']['ticker']} {result['metadata']['filing_type']} (score: {result['score']:.3f})")
                
                # Get collection stats
                stats = vector_service.get_collection_stats()
                logger.info(f"Collection stats: {stats}")
                
                return True
            else:
                logger.error("No content extracted from filing")
                return False
        else:
            logger.error("No filings downloaded")
            return False
            
    except Exception as e:
        logger.error(f"Error testing system: {e}")
        return False


if __name__ == "__main__":
    print("Testing Vector Database System")
    print("=" * 40)
    
    success = test_system()
    
    if success:
        print("\n✅ System test completed successfully!")
    else:
        print("\n❌ System test failed!")
        print("\nTo run this test:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-actual-api-key'")
        print("2. Make sure Qdrant is running: docker ps | grep qdrant")
        print("3. Run this script again: python test_vector_system.py")
