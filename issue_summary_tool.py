from typing import Dict, Any
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import logging
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IssueSummaryTool:
    def __init__(self, model_name: str = "google/flan-t5-base"):
        """
        Initialize the issue summary tool.
        
        Args:
            model_name: LLM model to use
        """
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
        You are an AI assistant helping a product and engineering team analyze issue reports.
        Analyze the following issue text and provide a structured summary.
        
        Issue Text:
        {issue_text}
        
        Provide a summary with the following information:
        1. Reported Issues: List the main problems described
        2. Affected Features/Components: Identify which parts of the system are affected
        3. Severity: Determine the severity (Low, Medium, High) based on impact
        4. Recommendations: Suggest possible next steps or solutions
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["issue_text"]
        )
        
        self.chain = self.prompt | self.llm
    
    def summarize_issue(self, issue_text: str) -> Dict[str, Any]:
        logger.info(f"Summarizing issue (first 100 chars): {issue_text[:100]}...")
        
        try:
            result = self.chain.invoke({"issue_text": issue_text})
            summary_text = result["summary"]

            response = {
                "summary_text": summary_text,
                "issue_text": issue_text[:200] + "..." if len(issue_text) > 200 else issue_text
            }
            return response

        except Exception as e:
            logger.error(f"Error summarizing issue: {str(e)}")
            return {
                "error": str(e),
                "issue_text": issue_text[:200] + "..." if len(issue_text) > 200 else issue_text
            }