#!/usr/bin/env python3
"""
Simple LlamaIndex Example
Shows how LlamaIndex works with local LLMs
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def simple_llamaindex_example():
    """Simple example of LlamaIndex with local LLM"""
    print("🧠 LlamaIndex Simple Example")
    print("=" * 40)
    
    try:
        # Import LlamaIndex
        from llama_index import Document, VectorStoreIndex, ServiceContext
        from llama_index.llms import Ollama
        from llama_index.embeddings import HuggingFaceEmbedding
        
        print("✅ LlamaIndex imported successfully")
        
        # Create sample documents
        documents = [
            Document(text="Apple Inc. reported revenue of $394.3 billion in 2023."),
            Document(text="Microsoft's revenue was $211.9 billion in 2023."),
            Document(text="Google's parent company Alphabet had revenue of $282.8 billion in 2023.")
        ]
        
        print(f"✅ Created {len(documents)} sample documents")
        
        # Setup LLM (try Ollama first)
        try:
            llm = Ollama(model="llama2")
            print("✅ Using Ollama LLM (local)")
        except:
            print("⚠️  Ollama not available, using Hugging Face")
            from llama_index.llms import HuggingFaceLLM
            llm = HuggingFaceLLM(model_name="microsoft/DialoGPT-medium")
        
        # Setup embeddings
        embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
        print("✅ Using Hugging Face embeddings (local)")
        
        # Create service context
        service_context = ServiceContext.from_defaults(
            llm=llm,
            embed_model=embed_model
        )
        
        # Create index
        index = VectorStoreIndex.from_documents(
            documents, 
            service_context=service_context
        )
        print("✅ Created vector index")
        
        # Create query engine
        query_engine = index.as_query_engine()
        print("✅ Created query engine")
        
        # Test queries
        queries = [
            "What is Apple's revenue?",
            "Which company had the highest revenue?",
            "What was Microsoft's revenue in 2023?"
        ]
        
        print("\n🔍 Testing queries:")
        for query in queries:
            print(f"\nQuestion: {query}")
            try:
                response = query_engine.query(query)
                print(f"Answer: {response}")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n🎉 LlamaIndex example completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTo fix this:")
        print("1. Install LlamaIndex: pip install llama-index")
        print("2. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("3. Download a model: ollama pull llama2")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_llamaindex_example()
