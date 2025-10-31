"""
Script to index toxicology documents for RAG (Retrieval-Augmented Generation)

Usage:
    python index_documents.py [--directory PATH] [--extensions .txt,.pdf,.md]
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.rag_service import rag_service


def load_documents(directory: str, extensions: list):
    """Load documents from directory"""
    documents = []
    
    for ext in extensions:
        if ext == '.txt' or ext == '.md':
            loader = DirectoryLoader(
                directory,
                glob=f"**/*{ext}",
                loader_cls=TextLoader
            )
        elif ext == '.pdf':
            loader = DirectoryLoader(
                directory,
                glob=f"**/*{ext}",
                loader_cls=PyPDFLoader
            )
        else:
            continue
        
        try:
            docs = loader.load()
            documents.extend(docs)
            print(f"✓ Loaded {len(docs)} {ext} files")
        except Exception as e:
            print(f"⚠ Error loading {ext} files: {e}")
    
    return documents


def main():
    parser = argparse.ArgumentParser(
        description='Index toxicology documents for RAG'
    )
    parser.add_argument(
        '--directory',
        default='./data/papers',
        help='Directory containing documents to index'
    )
    parser.add_argument(
        '--extensions',
        default='.txt,.md,.pdf',
        help='Comma-separated file extensions to index'
    )
    
    args = parser.parse_args()
    
    directory = args.directory
    extensions = args.extensions.split(',')
    
    print("=" * 60)
    print("🔬 ToxicoGPT Document Indexing")
    print("=" * 60)
    print(f"Directory: {directory}")
    print(f"Extensions: {', '.join(extensions)}")
    print()
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        print(f"   Creating directory...")
        os.makedirs(directory, exist_ok=True)
        print(f"   ✓ Directory created")
        print()
        print("   Add your toxicology documents to this folder and run again.")
        return
    
    # Load documents
    print("📂 Loading documents...")
    documents = load_documents(directory, extensions)
    
    if not documents:
        print("⚠ No documents found!")
        print(f"  Add documents to {directory} and run again.")
        return
    
    print(f"✓ Loaded {len(documents)} total documents")
    print()
    
    # Extract text and metadata
    print("📝 Processing documents...")
    texts = []
    metadatas = []
    
    for doc in documents:
        texts.append(doc.page_content)
        metadatas.append({
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", 0)
        })
    
    # Index documents
    print("🔍 Indexing documents...")
    success = rag_service.add_documents(texts, metadatas)
    
    if success:
        print("✅ Documents indexed successfully!")
        print()
        print("RAG is now enabled. Your chatbot will use these documents")
        print("to provide more accurate toxicology information.")
    else:
        print("❌ Failed to index documents")
        print("   Check the error messages above")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
