from typing import Dict, Any, List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import logging
import torch

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QATool:
    def __init__(self, vector_store_dir: str = "chroma_db", model_name: str = "google/flan-t5-base"):
        """
        Initialize the QA tool.
        
        Args:
            vector_store_dir: Directory containing the vector store
            model_name: LLM model to use
        """
        # Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = Chroma(persist_directory=vector_store_dir, embedding_function=self.embeddings)
        
        # Initialize HuggingFace LLM
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True
        )
        
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.1,
            top_p=0.95,
            repetition_penalty=1.15,
            do_sample=True
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)
        
        # Create custom prompt
        template = """
        You are an AI assistant helping a product and engineering team extract insights from internal documents.
        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer in a structured way, providing specific details from the documents when available.
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 1}),
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using the QA chain.
        
        Args:
            question: Question to answer
            
        Returns:
            Dictionary containing the answer and sources
        """
        logger.info(f"Answering question: {question}")
        
        try:
            result = self.qa_chain.invoke({"query": question})
            
            # Extract source documents
            sources = []
            for doc in result.get("source_documents", []):
                source = {
                    "content": doc.page_content,
                    "source": doc.metadata.get("source", "Unknown")
                }
                sources.append(source)
            
            # Create structured response
            response = {
                "query": question,
                "answer": result["result"],
                "sources": sources
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                "query": question,
                "answer": "I encountered an error while trying to answer your question.",
                "error": str(e)
            }