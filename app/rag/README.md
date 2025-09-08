# RAG (Retrieval-Augmented Generation) Module

This module provides intelligent question-answering capabilities over financial documents using various RAG implementations.

## 🚀 Available Services

### 1. SimpleVectorService
**Basic vector operations with Qdrant**
- ✅ Free Hugging Face embeddings
- ✅ OpenAI embeddings (with fallback)
- ✅ Qdrant vector storage
- ✅ Document search and retrieval

```python
from app.rag import SimpleVectorService

vector_service = SimpleVectorService()
vector_service.add_document("Apple revenue is $394B", {"company": "AAPL"})
results = vector_service.search_documents("Apple revenue")
```

### 2. SimpleRAGService
**Basic RAG without LlamaIndex**
- ✅ Vector search + simple LLM simulation
- ✅ No external dependencies
- ✅ Good for testing and prototyping

```python
from app.rag import SimpleRAGService

rag = SimpleRAGService()
result = rag.query("What is Apple's revenue?")
```

### 3. LlamaIndexRAGService
**Full LlamaIndex RAG with local LLMs**
- ✅ LlamaIndex framework
- ✅ Hugging Face LLM (free)
- ✅ Ollama support (if installed)
- ✅ Advanced query processing

```python
from app.rag import LlamaIndexRAGService

rag = LlamaIndexRAGService()
result = rag.query("What is Apple's revenue?")
```

### 4. GPT4RAGService
**OpenAI GPT-4 RAG (requires API credits)**
- ✅ GPT-4 for high-quality responses
- ✅ OpenAI embeddings
- ✅ Best quality, highest cost

```python
from app.rag import GPT4RAGService

rag = GPT4RAGService()
result = rag.query("What is Apple's revenue?")
```

### 5. HybridGPT4RAGService
**Cost-effective GPT-4 with free embeddings**
- ✅ Hugging Face embeddings (free)
- ✅ GPT-4 for generation (paid)
- ✅ Best cost/quality ratio

```python
from app.rag import HybridGPT4RAGService

rag = HybridGPT4RAGService()
result = rag.query("What is Apple's revenue?")
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Documents     │───▶│  Vector Store    │───▶│   RAG Service   │
│  (SEC Filings)  │    │    (Qdrant)      │    │  (LlamaIndex)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Embeddings     │    │      LLM        │
                       │ (Hugging Face)   │    │ (GPT-4/Local)   │
                       └──────────────────┘    └─────────────────┘
```

## 🔧 Setup Requirements

### For Local RAG (Free)
```bash
# Install dependencies
pip install llama-index llama-index-vector-stores-qdrant
pip install llama-index-llms-ollama llama-index-embeddings-huggingface

# Start Qdrant
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant:latest

# Optional: Install Ollama for better local LLM
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama2
```

### For GPT-4 RAG (Paid)
```bash
# Set OpenAI API key
export OPENAI_API_KEY="your_api_key_here"

# Install OpenAI dependencies
pip install llama-index-llms-openai llama-index-embeddings-openai
```

## 📊 Cost Comparison

| Service | Embeddings | LLM | Quality | Cost | Best For |
|---------|------------|-----|---------|------|----------|
| SimpleRAGService | Hugging Face | Mock | Basic | Free | Testing |
| LlamaIndexRAGService | Hugging Face | GPT-2/Ollama | Good | Free | Local use |
| HybridGPT4RAGService | Hugging Face | GPT-4 | Excellent | Low | Production |
| GPT4RAGService | OpenAI | GPT-4 | Excellent | High | Premium |

## 🧪 Testing

```bash
# Test all RAG services
python app/rag/simple_vector_service.py
python app/rag/simple_rag_service.py
python app/rag/llamaindex_rag_service.py
python app/rag/gpt4_rag_service.py
python app/rag/hybrid_gpt4_rag_service.py
```

## 📈 Performance

- **Vector Search**: ~100ms for 1000 documents
- **LLM Generation**: 
  - GPT-2: ~2-5 seconds
  - GPT-4: ~1-3 seconds
  - Ollama: ~3-10 seconds

## 🔍 Example Queries

- "What is Apple's revenue in 2023?"
- "Which companies have the highest growth?"
- "What are the main risks mentioned in Tesla's 10-K?"
- "Compare Microsoft and Amazon's cloud revenue"

## 🛠️ Customization

Each service can be customized:
- Vector dimensions (384 for Hugging Face, 1536 for OpenAI)
- Similarity search parameters
- LLM temperature and max tokens
- Response modes (compact, tree_summarize, etc.)

## 📝 Notes

- All services use the same Qdrant collection (`financial_documents`)
- Documents are stored with `text` and `metadata` fields for LlamaIndex compatibility
- Vector embeddings are cached for performance
- Services automatically fallback to free alternatives when possible
