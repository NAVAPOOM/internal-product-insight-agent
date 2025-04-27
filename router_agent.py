from typing import Dict, Any
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouterAgent:
    def __init__(self, model_name: str = "google/flan-t5-base"):
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
        
        template = """
        You are an AI assistant helping a product and engineering team extract insights from internal documents.
        Your job is to analyze the user query and decide which tool to use to best answer it.
        
        Available tools:
        1. QA Tool: Use this tool when the user is asking for specific information from documents, like "What are the issues reported on email notification?" or "What did users say about the search bar?"
        2. Issue Summary Tool: Use this tool when the user provides issue text and wants a summary of reported issues, affected features/components, and severity.
        
        User Query: {query}
        
        If the query is asking for specific information from documents, respond with: QA Tool
        If the query is providing issue text and wants a summary, respond with: Issue Summary Tool
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["query"]
        )
        
        self.chain = self.prompt | self.llm

    
    def route_query(self, query: str) -> Dict[str, Any]:
        logger.info(f"Routing query: {query}")
        
        try:
            result = self.chain.invoke({"query": query})
            response_text = result.strip().lower()
            
            if "qa tool" in response_text:
                tool = "QA Tool"
            elif "issue summary tool" in response_text:
                tool = "Issue Summary Tool"
            else:
                tool = "QA Tool"  # Default fallback
            
            routing_decision = {
                "tool": tool,
                "reasoning": f"Based on analysis of the query: {response_text}",
                "query_type": "question" if tool == "QA Tool" else "issue_summary",
                "reformulated_query": query
            }
            
            return routing_decision
        except Exception as e:
            logger.error(f"Error routing query: {str(e)}")
            return {
                "tool": "QA Tool",
                "reasoning": f"Default routing due to error: {str(e)}",
                "query_type": "question",
                "reformulated_query": query
            }
