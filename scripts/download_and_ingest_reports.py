#!/usr/bin/env python3
"""
Script to download S&P 500 financial reports and ingest them into Qdrant
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.sec_edgar_service import SECEdgarService
from app.services.simple_vector_service import SimpleVectorService as VectorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def download_and_ingest_reports(
    max_companies: int = 5,
    filings_per_company: int = 2,
    filing_types: List[str] = ['10-K', '10-Q'],
    openai_api_key: str = None
) -> Dict[str, Any]:
    """
    Download S&P 500 reports and ingest them into Qdrant
    
    Args:
        max_companies: Maximum number of companies to process
        filings_per_company: Number of filings per company
        filing_types: Types of filings to download
        openai_api_key: OpenAI API key for embeddings
    
    Returns:
        Dictionary with results
    """
    results = {
        'start_time': datetime.now().isoformat(),
        'companies_processed': 0,
        'total_filings_downloaded': 0,
        'total_filings_ingested': 0,
        'errors': [],
        'company_results': []
    }
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        sec_service = SECEdgarService()
        vector_service = VectorService(openai_api_key=openai_api_key)
        
        # Download S&P 500 filings
        logger.info(f"Downloading filings for {max_companies} companies...")
        download_results = sec_service.download_sp500_filings(
            filing_types=filing_types,
            limit_per_company=filings_per_company,
            max_companies=max_companies
        )
        
        results['companies_processed'] = download_results['total_companies']
        results['total_filings_downloaded'] = download_results['total_filings']
        
        # Process each company's filings
        for company_result in download_results['company_results']:
            ticker = company_result['ticker']
            logger.info(f"Processing filings for {ticker}...")
            
            company_ingestion_result = {
                'ticker': ticker,
                'filings_processed': 0,
                'filings_ingested': 0,
                'errors': []
            }
            
            # Process each downloaded filing
            for filing_info in company_result['downloaded_filings']:
                try:
                    logger.info(f"Processing filing: {filing_info['file_path']}")
                    
                    # Extract content from filing
                    content_data = sec_service.extract_filing_content(filing_info['file_path'])
                    
                    if not content_data.get('content'):
                        logger.warning(f"No content extracted from {filing_info['file_path']}")
                        continue
                    
                    # Prepare metadata for vector database
                    metadata = {
                        'ticker': content_data.get('ticker', ticker),
                        'filing_type': content_data.get('filing_type', filing_info['filing_type']),
                        'filing_date': content_data.get('filing_date'),
                        'file_path': filing_info['file_path'],
                        'word_count': content_data.get('word_count', 0),
                        'sections': list(content_data.get('sections', {}).keys()),
                        'downloaded_at': filing_info['downloaded_at'],
                        'ingested_at': datetime.now().isoformat()
                    }
                    
                    # Add to vector database
                    document_id = vector_service.add_document(
                        content=content_data['content'],
                        metadata=metadata
                    )
                    
                    company_ingestion_result['filings_processed'] += 1
                    company_ingestion_result['filings_ingested'] += 1
                    results['total_filings_ingested'] += 1
                    
                    logger.info(f"Successfully ingested {ticker} {filing_info['filing_type']} as {document_id}")
                    
                except Exception as e:
                    error_msg = f"Error processing {filing_info['file_path']}: {str(e)}"
                    logger.error(error_msg)
                    company_ingestion_result['errors'].append(error_msg)
                    results['errors'].append(error_msg)
            
            results['company_results'].append(company_ingestion_result)
        
        # Get final statistics
        results['end_time'] = datetime.now().isoformat()
        results['vector_db_stats'] = vector_service.get_collection_stats()
        
        logger.info(f"Completed ingestion: {results['total_filings_ingested']} filings ingested")
        return results
        
    except Exception as e:
        error_msg = f"Error in download_and_ingest_reports: {str(e)}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        results['end_time'] = datetime.now().isoformat()
        return results


def test_vector_search(vector_service: VectorService) -> None:
    """Test vector search functionality"""
    try:
        logger.info("Testing vector search...")
        
        # Test queries
        test_queries = [
            "What are the main business risks?",
            "How is the company performing financially?",
            "What are the revenue trends?",
            "What are the competitive advantages?",
            "How is the company managing debt?"
        ]
        
        for query in test_queries:
            logger.info(f"Testing query: {query}")
            results = vector_service.search_documents(query, top_k=3)
            
            logger.info(f"Found {len(results)} results for: {query}")
            for i, result in enumerate(results):
                metadata = result['metadata']
                logger.info(f"  {i+1}. {metadata.get('ticker', 'Unknown')} {metadata.get('filing_type', 'Unknown')} (score: {result.get('score', 0):.3f})")
        
    except Exception as e:
        logger.error(f"Error testing vector search: {e}")


def main():
    """Main function"""
    # Get OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Configuration
    max_companies = int(os.getenv('MAX_COMPANIES', '5'))
    filings_per_company = int(os.getenv('FILINGS_PER_COMPANY', '2'))
    filing_types = os.getenv('FILING_TYPES', '10-K,10-Q').split(',')
    
    logger.info(f"Starting download and ingestion process...")
    logger.info(f"Max companies: {max_companies}")
    logger.info(f"Filings per company: {filings_per_company}")
    logger.info(f"Filing types: {filing_types}")
    
    # Download and ingest reports
    results = download_and_ingest_reports(
        max_companies=max_companies,
        filings_per_company=filings_per_company,
        filing_types=filing_types,
        openai_api_key=openai_api_key
    )
    
    # Save results
    results_file = Path("ingestion_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("INGESTION SUMMARY")
    print("="*50)
    print(f"Companies processed: {results['companies_processed']}")
    print(f"Total filings downloaded: {results['total_filings_downloaded']}")
    print(f"Total filings ingested: {results['total_filings_ingested']}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    # Test vector search if we have data
    if results['total_filings_ingested'] > 0:
        try:
            vector_service = VectorService(openai_api_key=openai_api_key)
            test_vector_search(vector_service)
        except Exception as e:
            logger.error(f"Error testing vector search: {e}")
    
    print("\nIngestion completed!")


if __name__ == "__main__":
    main()
