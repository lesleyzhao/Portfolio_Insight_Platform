# Vector Database System Guide

## 🎯 Overview

The Portfolio Insight Platform now includes a powerful vector database system that enables semantic search over financial documents. This system downloads S&P 500 financial reports from SEC Edgar and stores them in Qdrant for intelligent querying and RAG (Retrieval-Augmented Generation) operations.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SEC Edgar     │───▶│  SEC Edgar       │───▶│   Qdrant        │
│   (10-K, 10-Q)  │    │  Service         │    │  Vector DB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Document        │    │  OpenAI         │
                       │  Processing      │    │  Embeddings     │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Vector Search   │
                       │  & RAG Queries   │
                       └──────────────────┘
```

## 🚀 Quick Start

### 1. Prerequisites

- **Qdrant**: Vector database (running in Docker)
- **OpenAI API Key**: For generating embeddings
- **Python Dependencies**: All installed via `requirements.txt`

### 2. Start Qdrant

```bash
# Start Qdrant in Docker
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z qdrant/qdrant

# Verify Qdrant is running
curl http://localhost:6333/collections
```

### 3. Set Environment Variables

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-actual-openai-api-key"

# Optional: Configure download parameters
export MAX_COMPANIES=5
export FILINGS_PER_COMPANY=2
export FILING_TYPES="10-K,10-Q"
```

### 4. Test the System

```bash
# Run the test script
python test_vector_system.py
```

### 5. Download and Ingest Reports

```bash
# Download S&P 500 reports and ingest into Qdrant
python scripts/download_and_ingest_reports.py
```

## 📁 File Structure

```
app/services/
├── simple_vector_service.py    # Vector database operations
├── sec_edgar_service.py        # SEC Edgar download service
└── vector_service.py           # Advanced LlamaIndex service (future)

scripts/
└── download_and_ingest_reports.py  # Main ingestion script

test_vector_system.py              # System test script
VECTOR_SYSTEM_GUIDE.md             # This guide
```

## 🔧 Services

### SimpleVectorService

**Purpose**: Core vector database operations using Qdrant directly

**Key Methods**:
- `add_document(content, metadata)` - Add document to vector DB
- `search_documents(query, filters, top_k)` - Semantic search
- `get_document_by_id(doc_id)` - Retrieve specific document
- `get_collection_stats()` - Get database statistics

**Example Usage**:
```python
from app.services.simple_vector_service import SimpleVectorService

# Initialize service
vector_service = SimpleVectorService(openai_api_key="your-key")

# Add document
doc_id = vector_service.add_document(
    content="Apple Inc. financial report content...",
    metadata={
        'ticker': 'AAPL',
        'filing_type': '10-K',
        'filing_date': '2024-01-01'
    }
)

# Search documents
results = vector_service.search_documents(
    query="Apple iPhone revenue trends",
    tickers=['AAPL'],
    top_k=5
)
```

### SECEdgarService

**Purpose**: Download and process SEC Edgar financial filings

**Key Methods**:
- `download_company_filings(ticker, filing_types, limit)` - Download specific company
- `download_sp500_filings(filing_types, limit_per_company, max_companies)` - Download S&P 500
- `extract_filing_content(file_path)` - Extract and clean content
- `get_download_stats()` - Get download statistics

**Example Usage**:
```python
from app.services.sec_edgar_service import SECEdgarService

# Initialize service
sec_service = SECEdgarService()

# Download Apple filings
result = sec_service.download_company_filings(
    ticker='AAPL',
    filing_types=['10-K', '10-Q'],
    limit=3
)

# Extract content from downloaded filing
content_data = sec_service.extract_filing_content(filing_path)
```

## 🔍 Search Capabilities

### Semantic Search

The system supports natural language queries over financial documents:

```python
# Search for risk factors
results = vector_service.search_documents(
    query="What are the main business risks?",
    report_types=['10-K'],
    top_k=10
)

# Search for specific company performance
results = vector_service.search_documents(
    query="How is revenue performing?",
    tickers=['AAPL', 'MSFT'],
    top_k=5
)
```

### Filtering Options

- **By Ticker**: Filter results to specific companies
- **By Report Type**: Filter by 10-K, 10-Q, 8-K, etc.
- **By Date Range**: Filter by filing date (future enhancement)
- **By Section**: Filter by specific report sections (future enhancement)

## 📊 Data Processing Pipeline

### 1. Download Phase
- Download SEC Edgar filings for S&P 500 companies
- Support for 10-K (annual), 10-Q (quarterly), 8-K (current) reports
- Configurable limits per company and filing type

### 2. Processing Phase
- Extract text content from HTML filings
- Clean and normalize content (remove HTML tags, extra whitespace)
- Extract key sections (Business, Risk Factors, Financial Statements, etc.)
- Generate metadata (ticker, filing type, date, word count, sections)

### 3. Embedding Phase
- Generate OpenAI embeddings for document content
- Store embeddings in Qdrant with metadata
- Support for chunking large documents (future enhancement)

### 4. Search Phase
- Convert queries to embeddings
- Perform cosine similarity search in Qdrant
- Apply filters and return ranked results

## 🎛️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
QDRANT_URL=http://localhost:6333
MAX_COMPANIES=5
FILINGS_PER_COMPANY=2
FILING_TYPES=10-K,10-Q
```

### Download Configuration

- **MAX_COMPANIES**: Number of S&P 500 companies to process
- **FILINGS_PER_COMPANY**: Number of filings per company per type
- **FILING_TYPES**: Comma-separated list of filing types to download

## 🧪 Testing

### Test Scripts

1. **`test_vector_system.py`**: Complete system test
   - Downloads one Apple filing
   - Processes and ingests into Qdrant
   - Tests search functionality

2. **`scripts/download_and_ingest_reports.py`**: Full ingestion
   - Downloads multiple S&P 500 companies
   - Processes all filings
   - Ingests into vector database

### Manual Testing

```python
# Test vector service directly
from app.services.simple_vector_service import SimpleVectorService

vector_service = SimpleVectorService()
stats = vector_service.get_collection_stats()
print(f"Documents in database: {stats['points_count']}")
```

## 📈 Performance Considerations

### Embedding Costs
- OpenAI embeddings cost ~$0.0001 per 1K tokens
- Typical 10-K filing: ~50K-100K tokens
- Estimated cost per filing: $0.005-$0.01

### Storage Requirements
- Each embedding: 1536 dimensions × 4 bytes = ~6KB
- Metadata: ~1-2KB per document
- Estimated storage per filing: ~10KB

### Search Performance
- Qdrant supports sub-millisecond search for small collections
- Performance scales with collection size
- Consider indexing strategies for large datasets

## 🔮 Future Enhancements

### Planned Features
1. **Document Chunking**: Split large documents into smaller chunks
2. **Advanced Filtering**: Date ranges, sections, custom metadata
3. **RAG Integration**: Full LlamaIndex integration for complex queries
4. **Real-time Updates**: Automatic ingestion of new filings
5. **Multi-modal Support**: Support for images, tables, charts
6. **Custom Embeddings**: Support for different embedding models

### API Integration
- REST API endpoints for vector search
- WebSocket support for real-time updates
- Integration with existing portfolio APIs

## 🐛 Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   ```bash
   # Check if Qdrant is running
   docker ps | grep qdrant
   
   # Restart Qdrant if needed
   docker restart qdrant
   ```

2. **OpenAI API Key Error**
   ```bash
   # Set API key
   export OPENAI_API_KEY="your-actual-key"
   
   # Verify it's set
   echo $OPENAI_API_KEY
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Download Failures**
   - Check internet connection
   - Verify SEC Edgar is accessible
   - Check rate limiting (add delays between requests)

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [SEC Edgar Database](https://www.sec.gov/edgar/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)

## 🤝 Contributing

To contribute to the vector system:

1. Add new features to `simple_vector_service.py`
2. Extend `sec_edgar_service.py` for additional data sources
3. Create new test scripts in the root directory
4. Update this guide with new features

---

**Note**: This system is designed for research and educational purposes. Ensure compliance with SEC Edgar terms of service and OpenAI usage policies when using in production.
