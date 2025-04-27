import os
import argparse
import logging
from document_processor import DocumentProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description="Internal AI Assistant")
    parser.add_argument("--documents_dir", type=str, default="documents", help="Directory containing the documents")
    parser.add_argument("--vector_store_dir", type=str, default="chroma_db", help="Directory to store the vector database")
    parser.add_argument("--reindex", action="store_true", help="Reindex the documents")
    
    args = parser.parse_args()
    
    # Check if the vector store already exists
    if not os.path.exists(args.vector_store_dir) or args.reindex:
        logger.info("Indexing documents...")
        
        # Create the document processor
        processor = DocumentProcessor(documents_dir=args.documents_dir)
        
        # Process the documents
        processor.process_documents(persist_directory=args.vector_store_dir)
        
        logger.info("Indexing complete!")
    else:
        logger.info(f"Vector store already exists at {args.vector_store_dir}. Use --reindex to reindex.")
    
    logger.info("Starting API server...")
    
    # Import and run the API server
    from api import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
