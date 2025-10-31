import os
from typing import List, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

ENABLE_RAG = os.getenv("ENABLE_RAG", "false").lower() == "true"
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vectorstore")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

class RAGService:
    def __init__(self):
        self.enabled = ENABLE_RAG
        self.vectorstore = None
        
        if self.enabled:
            try:
                # Initialize embeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                
                # Try to load existing vectorstore
                if os.path.exists(VECTOR_DB_PATH):
                    self.vectorstore = Chroma(
                        persist_directory=VECTOR_DB_PATH,
                        embedding_function=self.embeddings
                    )
                    print(f"✓ RAG enabled: Loaded vectorstore from {VECTOR_DB_PATH}")
                else:
                    print(f"⚠ RAG enabled but no vectorstore found at {VECTOR_DB_PATH}")
                    print("  Add documents to ./data/papers/ and run the indexing script")
            except Exception as e:
                print(f"⚠ RAG initialization failed: {e}")
                self.enabled = False

    def retrieve_context(self, query: str, k: int = 3) -> Optional[str]:
        """Retrieve relevant context for a query"""
        if not self.enabled or not self.vectorstore:
            return None
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            if docs:
                context = "\n\n".join([doc.page_content for doc in docs])
                return context
            return None
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return None

    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """Add documents to the vectorstore"""
        if not self.enabled:
            return False
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            
            chunks = text_splitter.create_documents(texts, metadatas=metadatas)
            
            if not self.vectorstore:
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=VECTOR_DB_PATH
                )
            else:
                self.vectorstore.add_documents(chunks)
            
            self.vectorstore.persist()
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

rag_service = RAGService()
