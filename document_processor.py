import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, documents_dir: str, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.documents_dir = documents_dir
        self.embedding_model = embedding_model
        
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vector_store = None
        
    def load_documents(self) -> List[Document]:
        documents = []
        for filename in os.listdir(self.documents_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(self.documents_dir, filename)
                logger.info(f"Loading document: {file_path}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(page_content=content, metadata={"source": filename})
                    documents.append(doc)
                    logger.info(f"Loaded {filename}")
                except Exception as e:
                    logger.error(f"Error loading {filename}: {str(e)}")
        
        return documents
    
    def split_documents(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(chunks)} chunks")
        return chunks
    
    def create_vector_store(self, documents: List[Document], persist_directory: str = "chroma_db") -> Any:
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=persist_directory
        )
        
        logger.info(f"Created vector store with {len(documents)} documents")
        return self.vector_store
    
    def process_documents(self, persist_directory: str = "chroma_db") -> Any:
        documents = self.load_documents()
        chunks = self.split_documents(documents)
        vector_store = self.create_vector_store(chunks, persist_directory)
        return vector_store