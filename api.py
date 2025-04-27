from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from agent_controller import AgentController
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Internal AI Assistant API",
    description="API for an AI assistant that helps extract insights from internal documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือแก้เป็นเฉพาะ Origin ที่ต้องการ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent Controller
agent_controller = AgentController(vector_store_dir="chroma_db")

# Define request/response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: Dict[str, Any]

# Main query endpoint
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest = Body(...)):
    """
    Process a user query and route it to the appropriate tool.
    """
    try:
        response = agent_controller.process_query(request.query)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, workers=1)
