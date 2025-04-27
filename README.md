# Internal Product Insight Agent

## Project Overview

Internal Product Insight Agent is an AI assistant designed to help product and engineering teams analyze internal documents and team reports, especially focusing on product issues (bugs) and user feedback.

The system leverages Large Language Models (LLMs) and vector databases to search, analyze, and provide insights with high accuracy and efficiency.

---

## Key Features

- **Document-Based Q&A (QA Tool)**:  
  Retrieve relevant information from internal documents to answer specific questions, such as  
  _"What issues have been reported about email notifications?"_ or _"What did users say about the search bar?"_

- **Issue Summarization (Issue Summary Tool)**:  
  Analyze and summarize issue descriptions, identifying:
  - Reported problems
  - Affected features/components
  - Severity level
  - Recommendations for resolution

- **Intelligent Query Routing (Router Agent)**:  
  Use LLMs to analyze queries and intelligently decide which tool to route them to.

- **Conversation Context Management**:  
  Maintain conversation history for better context-aware interactions.

- **RESTful API**:  
  Provide a REST API interface for external applications.

---

## System Architecture

\`\`\`
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Document       │────▶│  Vector Store   │◀───▶│  QA Tool        │
│  Processor      │     │  (Chroma)       │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│                 │     │                 │     │                 │
│  FastAPI        │◀───▶│  Agent          │────▶│  Router Agent   │
│  Wrapper        │     │  Controller     │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  Issue Summary  │
                        │  Tool           │
                        │                 │
                        └─────────────────┘
\`\`\`

## Core Components

### 1. Document Processor (`document_processor.py`)

Handles loading documents (TXT, PDF), splitting texts, creating embeddings, and building the vector store.

**Main functions:**

- Load documents with metadata
- Smart text splitting
- Create vector store with Chroma
- Support similarity search

---

### 2. QA Tool (`qa_tool.py`)

Retrieves related content from the vector store to answer user questions.

**Main functions:**

- Retrieve documents based on the query
- Use LLM to generate context-aware answers
- Provide source references

---

### 3. Issue Summary Tool (`issue_summary_tool.py`)

Analyzes issue descriptions and generates structured summaries.

**Main functions:**

- Identify reported issues
- Detect affected features/components
- Assess severity (Low, Medium, High)
- Suggest next steps or possible fixes

---

### 4. Router Agent (`router_agent.py`)

Analyzes user queries and determines which tool to use.

**Main functions:**

- Analyze queries via LLM
- Route to the appropriate tool (QA Tool or Issue Summary Tool)
- Reformulate queries if necessary

---

### 5. Agent Controller (`agent_controller.py`)

Coordinates the interaction between API and tools.

**Main functions:**

- Receive queries from API
- Send queries to Router Agent
- Forward to the appropriate tool
- Aggregate and return responses

---

### 6. FastAPI Wrapper (`api.py`)

Provides RESTful API endpoints for external access.

**Main functions:**

- Expose APIs
- Health check endpoints
- (Optionally) Handle authentication and rate limiting

---

## Installation and Usage

### System Requirements

- Python 3.9+
- Docker & Docker Compose (recommended for deployment)

---

## Installation via Docker (Recommended)

1. **Clone the repository**:
   \`\`\`
   git clone https://github.com/NAVAPOOM/internal-product-insight-agent.git
   cd internal-product-insight-agent
   \`\`\`

2. **Prepare your documents**:
   Place your TXT documents inside the `documents/` directory.

3. **Build and run containers**:
   \`\`\`
   docker-compose up --build
   \`\`\`

4. **Check system health**:
   \`\`\`
   curl http://localhost:8000/health
   \`\`\`

## Project Structure

\`\`\`
internal-product-insight-agent/
├── documents/                  # Source documents
├── chroma_db/                   # Vector store
├── logs/                        # Application logs
├── document_processor.py        # Document processor
├── qa_tool.py                   # QA tool
├── issue_summary_tool.py        # Issue summarization tool
├── router_agent.py              # Query router
├── agent_controller.py          # Central controller
├── api.py                       # FastAPI server
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker build configuration
├── docker-compose.yml           # Docker orchestration
├── .dockerignore                # Docker ignore rules
└── README.md                    # Project documentation
\`\`\`

## API Endpoints

### 1. `/query` (POST)

Submit a user query to the system.

**Request**:
\`\`\`
{
  "query": "What issues are reported about email notifications?"
}
\`\`\`

**Response**:
\`\`\`
{
  "response": {
    "routing": {
      "tool": "QA Tool",
      "reasoning": "This query seeks specific information about email notification issues."
    },
    "response": {
      "answer": "Email notifications are delayed or missing.",
      "sources": [
        {"source": "bug_report.txt", "page": 2}
      ]
    },
    "query": "What issues are reported about email notifications?"
  }
}
\`\`\`

### 2. `/health` (GET)

Check the system status.

**Response**:
\`\`\`
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-04-27T12:00:00Z"
}
\`\`\`

---

## Future Enhancements

- Add support for new document types (DOCX, HTML, etc.)
- Improve router agent for more nuanced query understanding
- Implement trend analysis or anomaly detection
- Build a simple frontend UI
- Add multi-tool chaining (e.g., chain QA + summarization)

---

## Conclusion

Internal Product Insight Agent is a powerful AI system for extracting insights from internal documents and team reports, helping product and engineering teams make faster and more informed decisions.  
By combining LLMs and vector databases, it provides highly relevant and structured answers for real-world business needs.
