from typing import Dict, Any
from qa_tool import QATool
from issue_summary_tool import IssueSummaryTool
from router_agent import RouterAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentController:
    def __init__(self, vector_store_dir: str = "chroma_db"):
        self.qa_tool = QATool(vector_store_dir=vector_store_dir)
        self.issue_summary_tool = IssueSummaryTool()
        self.router = RouterAgent()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        logger.info(f"Processing query: {query}")
        
        try:
            # Route the query
            routing_decision = self.router.route_query(query)
            
            # Execute the appropriate tool
            if routing_decision["tool"] == "QA Tool":
                tool_response = self.qa_tool.answer_question(routing_decision["reformulated_query"])
            elif routing_decision["tool"] == "Issue Summary Tool":
                tool_response = self.issue_summary_tool.summarize_issue(routing_decision["reformulated_query"])
            else:
                tool_response = {
                    "error": f"Unknown tool: {routing_decision['tool']}",
                    "query": query
                }
            
            # Create the final response
            response = {
                "routing": routing_decision,
                "response": tool_response,
                "query": query
            }
            
            return response
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "error": str(e),
                "query": query
            }