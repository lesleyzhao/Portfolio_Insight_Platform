"""
SEC Edgar Service for downloading financial reports
Uses sec-edgar-downloader to fetch 10-K, 10-Q, and other SEC filings
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re
from pathlib import Path

from sec_edgar_downloader import Downloader
import pandas as pd

logger = logging.getLogger(__name__)


class SECEdgarService:
    """Service for downloading and processing SEC Edgar financial reports"""
    
    def __init__(self, download_dir: str = "./sec_filings"):
        """
        Initialize the SEC Edgar service
        
        Args:
            download_dir: Directory to store downloaded filings
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Initialize the downloader
        self.downloader = Downloader(
            download_folder=self.download_dir,
            company_name="Portfolio Insight Platform",
            email_address="contact@example.com"
        )
        
        # S&P 500 tickers (subset for testing)
        self.sp500_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'JNJ', 'V', 'PG', 'JPM', 'HD', 'MA', 'DIS', 'PYPL', 'BAC',
            'ADBE', 'CMCSA', 'NFLX', 'XOM', 'PFE', 'TMO', 'ABT', 'COST', 'PEP',
            'AVGO', 'TXN', 'QCOM', 'DHR', 'ACN', 'VZ', 'NKE', 'MRK', 'LIN',
            'T', 'WMT', 'CRM', 'ABBV', 'ORCL', 'AMD', 'NEE', 'PM', 'UNP',
            'RTX', 'HON', 'SPGI', 'LOW', 'INTU', 'IBM', 'AMAT', 'GE', 'CAT',
            'BKNG', 'AXP', 'SYK', 'SBUX', 'GILD', 'ISRG', 'ADP', 'CVX', 'MDT',
            'BLK', 'TJX', 'ZTS', 'LMT', 'CI', 'ANTM', 'TGT', 'DE', 'MMM',
            'SO', 'DUK', 'AON', 'ICE', 'FIS', 'ITW', 'SPG', 'AEP', 'SRE',
            'ECL', 'APD', 'CL', 'EMR', 'EXC', 'XEL', 'A', 'PEG', 'ETN', 'GIS'
        ]
    
    def download_company_filings(self, 
                                ticker: str, 
                                filing_types: List[str] = ['10-K', '10-Q'],
                                limit: int = 5) -> Dict[str, Any]:
        """
        Download filings for a specific company
        
        Args:
            ticker: Company ticker symbol
            filing_types: List of filing types to download
            limit: Maximum number of filings per type
            
        Returns:
            Dictionary with download results
        """
        results = {
            'ticker': ticker,
            'downloaded_filings': [],
            'errors': [],
            'total_downloaded': 0
        }
        
        try:
            for filing_type in filing_types:
                try:
                    logger.info(f"Downloading {filing_type} filings for {ticker}")
                    
                    # Download filings
                    self.downloader.get(
                        ticker_or_cik=ticker,
                        form=filing_type,
                        limit=limit,
                        download_details=True
                    )
                    
                    # Find downloaded files
                    ticker_dir = self.download_dir / "sec-edgar-filings" / ticker
                    if ticker_dir.exists():
                        filing_files = self._find_filing_files(ticker_dir, filing_type)
                        
                        for file_path in filing_files:
                            filing_info = {
                                'ticker': ticker,
                                'filing_type': filing_type,
                                'file_path': str(file_path),
                                'downloaded_at': datetime.now().isoformat()
                            }
                            results['downloaded_filings'].append(filing_info)
                            results['total_downloaded'] += 1
                    
                    logger.info(f"Downloaded {filing_type} filings for {ticker}")
                    
                except Exception as e:
                    error_msg = f"Error downloading {filing_type} for {ticker}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            return results
            
        except Exception as e:
            error_msg = f"Error downloading filings for {ticker}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
    
    def download_sp500_filings(self, 
                              filing_types: List[str] = ['10-K', '10-Q'],
                              limit_per_company: int = 3,
                              max_companies: int = 10) -> Dict[str, Any]:
        """
        Download filings for S&P 500 companies
        
        Args:
            filing_types: List of filing types to download
            limit_per_company: Maximum filings per company per type
            max_companies: Maximum number of companies to process
            
        Returns:
            Dictionary with download results
        """
        results = {
            'total_companies': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'company_results': [],
            'total_filings': 0
        }
        
        try:
            # Process subset of S&P 500 companies
            companies_to_process = self.sp500_tickers[:max_companies]
            
            for i, ticker in enumerate(companies_to_process):
                logger.info(f"Processing {ticker} ({i+1}/{len(companies_to_process)})")
                
                company_result = self.download_company_filings(
                    ticker=ticker,
                    filing_types=filing_types,
                    limit=limit_per_company
                )
                
                results['company_results'].append(company_result)
                results['total_companies'] += 1
                results['total_filings'] += company_result['total_downloaded']
                
                if company_result['total_downloaded'] > 0:
                    results['successful_downloads'] += 1
                else:
                    results['failed_downloads'] += 1
                
                # Add small delay to avoid rate limiting
                import time
                time.sleep(1)
            
            logger.info(f"Completed S&P 500 download: {results['total_filings']} filings from {results['total_companies']} companies")
            return results
            
        except Exception as e:
            logger.error(f"Error downloading S&P 500 filings: {e}")
            raise
    
    def _find_filing_files(self, ticker_dir: Path, filing_type: str) -> List[Path]:
        """Find filing files in the ticker directory"""
        filing_files = []
        
        try:
            # Look in the specific filing type directory
            filing_type_dir = ticker_dir / filing_type
            if filing_type_dir.exists():
                for file_path in filing_type_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix in ['.txt', '.html', '.htm']:
                        filing_files.append(file_path)
            
            return filing_files
            
        except Exception as e:
            logger.error(f"Error finding filing files for {ticker_dir}: {e}")
            return []
    
    def extract_filing_content(self, file_path: str) -> Dict[str, Any]:
        """
        Extract content from a filing file
        
        Args:
            file_path: Path to the filing file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            file_path = Path(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract metadata from file path
            path_parts = file_path.parts
            ticker = None
            filing_type = None
            filing_date = None
            
            for part in path_parts:
                if part in self.sp500_tickers:
                    ticker = part
                elif part in ['10-K', '10-Q', '8-K', 'DEF-14A']:
                    filing_type = part
                elif re.match(r'\d{4}-\d{2}-\d{2}', part):
                    filing_date = part
            
            # Clean content (remove HTML tags, extra whitespace)
            cleaned_content = self._clean_filing_content(content)
            
            # Extract key sections
            sections = self._extract_filing_sections(cleaned_content)
            
            result = {
                'file_path': str(file_path),
                'ticker': ticker,
                'filing_type': filing_type,
                'filing_date': filing_date,
                'content': cleaned_content,
                'sections': sections,
                'word_count': len(cleaned_content.split()),
                'extracted_at': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return {}
    
    def _clean_filing_content(self, content: str) -> str:
        """Clean filing content by removing HTML tags and extra whitespace"""
        try:
            # Remove HTML tags
            import re
            content = re.sub(r'<[^>]+>', ' ', content)
            
            # Remove extra whitespace
            content = re.sub(r'\s+', ' ', content)
            
            # Remove common SEC filing artifacts
            content = re.sub(r'Page \d+ of \d+', '', content)
            content = re.sub(r'Table of Contents', '', content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return content
    
    def _extract_filing_sections(self, content: str) -> Dict[str, str]:
        """Extract key sections from filing content"""
        sections = {}
        
        try:
            # Common section patterns
            section_patterns = {
                'business': r'(?i)item\s+1\.?\s*business.*?(?=item\s+2)',
                'risk_factors': r'(?i)item\s+1a\.?\s*risk\s+factors.*?(?=item\s+2)',
                'legal_proceedings': r'(?i)item\s+3\.?\s*legal\s+proceedings.*?(?=item\s+4)',
                'financial_statements': r'(?i)item\s+8\.?\s*financial\s+statements.*?(?=item\s+9)',
                'management_discussion': r'(?i)item\s+7\.?\s*management.*?discussion.*?(?=item\s+8)'
            }
            
            for section_name, pattern in section_patterns.items():
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    sections[section_name] = match.group(0).strip()
            
            return sections
            
        except Exception as e:
            logger.error(f"Error extracting sections: {e}")
            return {}
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get statistics about downloaded filings"""
        try:
            stats = {
                'total_companies': 0,
                'total_filings': 0,
                'filing_types': {},
                'companies': []
            }
            
            if self.download_dir.exists():
                for ticker_dir in self.download_dir.iterdir():
                    if ticker_dir.is_dir():
                        company_stats = {
                            'ticker': ticker_dir.name,
                            'filings': 0,
                            'filing_types': {}
                        }
                        
                        for filing_file in ticker_dir.rglob('*'):
                            if filing_file.is_file():
                                company_stats['filings'] += 1
                                stats['total_filings'] += 1
                                
                                # Determine filing type from filename
                                filing_type = 'unknown'
                                for ftype in ['10-K', '10-Q', '8-K', 'DEF-14A']:
                                    if ftype in filing_file.name:
                                        filing_type = ftype
                                        break
                                
                                company_stats['filing_types'][filing_type] = company_stats['filing_types'].get(filing_type, 0) + 1
                                stats['filing_types'][filing_type] = stats['filing_types'].get(filing_type, 0) + 1
                        
                        stats['companies'].append(company_stats)
                        stats['total_companies'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting download stats: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Test the SEC Edgar service
    try:
        # Initialize service
        sec_service = SECEdgarService()
        
        # Test downloading filings for Apple
        print("Downloading Apple filings...")
        apple_result = sec_service.download_company_filings(
            ticker='AAPL',
            filing_types=['10-K', '10-Q'],
            limit=2
        )
        
        print(f"Apple download result: {apple_result}")
        
        # Test extracting content from a filing
        if apple_result['downloaded_filings']:
            first_filing = apple_result['downloaded_filings'][0]
            content = sec_service.extract_filing_content(first_filing['file_path'])
            print(f"Extracted content: {len(content.get('content', ''))} characters")
            print(f"Sections found: {list(content.get('sections', {}).keys())}")
        
        # Get download stats
        stats = sec_service.get_download_stats()
        print(f"Download stats: {stats}")
        
    except Exception as e:
        print(f"Error testing SEC Edgar service: {e}")
