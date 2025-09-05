# Semantic Search Engine - RAG Pipeline

## Project Overview

This project implements a comprehensive Retrieval-Augmented Generation (RAG) pipeline that combines multi-document retrieval, semantic caching, and agentic routing for intelligent question answering. The system uses a React frontend with Tailwind CSS and a FastAPI backend with WebSocket support.

## Architecture Components

### 1. Query Interface (Frontend)
- **Framework**: ReactJS with Tailwind CSS
- **Features**:
  - Text input for user questions
  - Toggle for "Allow Web Search" functionality
  - Output area displaying answers, supporting documents, and cache/log messages
  - Real-time updates via WebSocket connection

### 2. RAG Pipeline (Backend)
- **Framework**: FastAPI with WebSocket support
- **Vector Database**: Qdrant for document indexing and retrieval
- **Embeddings**: Nomic AI text embeddings (`nomic-ai/nomic-embed-text-v1.5`)
- **LLM**: OpenAI GPT-4 for answer generation
- **Document Corpus**: Pre-embedded 10-K financial vectors

### 3. Agentic Routing Logic
The system uses intelligent routing to determine the appropriate data source:
- **Local Search**: 10-K financial reports and OpenAI documentation
- **Web Search**: External queries using DuckDuckGo and ARES API
- **Router**: GPT-4 powered classification system

### 4. Semantic Caching
- **Technology**: FAISS for similarity search
- **Functionality**:
  - Stores question embeddings and responses
  - Cosine similarity matching for cache hits
  - Observability logs for cache performance

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── websocket.py           # WebSocket connection handler
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── query.py           # Query models and schemas
│   │   │   └── response.py        # Response models and schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py     # Core RAG pipeline logic
│   │   │   ├── router_service.py  # Query routing logic
│   │   │   ├── cache_service.py   # Semantic caching implementation
│   │   │   ├── qdrant_service.py  # Vector database operations
│   │   │   └── web_search_service.py # External search APIs
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py      # Text embedding utilities
│   │   │   └── config.py          # Configuration management
│   │   └── static/                # Serves React build files
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchInterface.jsx # Main search component
│   │   │   ├── ResultsDisplay.jsx  # Results and logs display
│   │   │   └── ToggleSwitch.jsx    # Web search toggle
│   │   ├── hooks/
│   │   │   └── useWebSocket.js     # WebSocket connection hook
│   │   ├── utils/
│   │   │   └── api.js              # API utility functions
│   │   ├── App.jsx
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── postcss.config.js
├── .env.example
├── .gitignore
├── README.md
└── CLAUDE.md                      # This file
```

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# ARES API Configuration
ARES_API_KEY=your_ares_api_key_here

# Application Configuration
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
REACT_BUILD_PATH=./frontend/build
LOG_LEVEL=INFO

# Semantic Cache Configuration
CACHE_SIMILARITY_THRESHOLD=0.8
FAISS_INDEX_TYPE=IndexFlatL2
EMBEDDING_DIMENSION=768
```

## Key Features

### 1. Multi-Document Retrieval
- Integration with pre-embedded 10-K financial vectors
- OpenAI documentation search capabilities
- Qdrant vector database for efficient similarity search

### 2. Intelligent Query Routing
Based on Module_1 implementation:
- **Router Prompt**: Uses GPT-4 to classify queries into three categories:
  - `OPENAI_QUERY`: OpenAI documentation and API questions
  - `10K_DOCUMENT_QUERY`: Financial reports and company data
  - `INTERNET_QUERY`: Real-time web search requirements

### 3. Semantic Caching System
Based on Module_3 implementation:
- **FAISS Integration**: Fast similarity search with Euclidean distance
- **Nomic Embeddings**: High-quality text embeddings for cache matching
- **Performance Tracking**: Cache hit/miss rates and latency measurements
- **Persistent Storage**: JSON-based cache persistence

### 4. Web Search Integration
- **ARES API**: Real-time internet search capabilities
- **Fallback Mechanism**: Automatic web search when local documents insufficient
- **Configurable**: Toggle-based user control

### 5. Observability Features
- **Cache Performance**: Hit/miss rates, time savings, response latencies
- **Query Logs**: Detailed logging of routing decisions and data sources
- **Real-time Updates**: Live cache status and performance metrics

## Development Commands

### Backend Setup
```bash
# Install dependencies from root-level pyproject.toml
uv sync
# Run the backend server
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Note**: This project uses `uv` for dependency management instead of `pip` and `requirements.txt`. The `pyproject.toml` file is located in the project root and defines all dependencies and Python version requirements (>=3.11).

### Frontend Setup
```bash
cd frontend
npm install
npm run build  # For production build served by FastAPI
# OR
npm start      # For development with hot reload
```

### Testing
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

## API Endpoints

### REST Endpoints
- `GET /`: Serves React application
- `GET /health`: Health check endpoint
- `POST /api/search`: Direct search API (alternative to WebSocket)

### WebSocket Endpoints
- `WS /ws`: Main WebSocket connection for real-time search

## Data Sources

### 10-K Financial Data
- **Companies**: Lyft 2024, Uber 2021 SEC filings
- **Format**: Pre-embedded vectors in Qdrant
- **Metadata**: Company name, section, filing details

### OpenAI Documentation
- **Content**: Official OpenAI API documentation
- **Coverage**: Tools, APIs, models, usage guidelines
- **Format**: Embedded text chunks with metadata

## Performance Optimizations

### Semantic Cache Benefits
- **Response Time**: 10x faster for cache hits (~0.1s vs 1-3s)
- **API Cost Reduction**: Eliminates redundant API calls
- **Similarity Matching**: Handles paraphrased and similar queries

### Vector Search Optimization
- **FAISS Index**: Efficient L2 distance calculations
- **Batch Processing**: Optimized embedding generation
- **Index Persistence**: Reduced startup times

## Security Considerations

- **API Key Management**: Environment-based configuration
- **CORS Configuration**: Proper frontend-backend communication
- **Input Validation**: Query sanitization and length limits
- **Rate Limiting**: Protection against API abuse

## Monitoring and Logging

### Cache Metrics
- Hit/miss ratios
- Average response times
- Cache size and performance

### System Metrics
- Query volume and patterns
- Routing decision accuracy
- API response times
- Error rates and types

## Future Enhancements

### Sub-Query Division
Implementation of complex query breakdown:
```python
def sub_queries(user_query):
    """Break complex queries into focused sub-questions"""
    # GPT-4 powered query division logic
    # Process each sub-query independently
    # Aggregate results intelligently
```

### Advanced Caching
- **Temporal Caching**: Time-based cache invalidation
- **Context-Aware Caching**: User session-based caching
- **Distributed Caching**: Multi-node cache coordination

### Enhanced Routing
- **Confidence Scoring**: Route decision confidence levels
- **Multi-Source Queries**: Simultaneous search across sources
- **Learning Router**: Adaptive routing based on success rates

## Deployment

### Local Development
1. Set up environment variables
2. Install dependencies (backend and frontend)
3. Start Qdrant locally or use cloud instance
4. Run backend server
5. Build and serve frontend

### Production Deployment
- **Containerization**: Docker support for all components
- **Load Balancing**: Multiple FastAPI instances
- **Database**: Production Qdrant cluster
- **Monitoring**: Comprehensive logging and metrics
- **Caching**: Redis for distributed semantic cache

## Contributing

1. Follow the existing code structure from Module_1 and Module_3
2. Maintain consistent error handling and logging
3. Add appropriate tests for new features
4. Update documentation for API changes
5. Ensure semantic cache performance is maintained

## License

This project builds upon the work from Module_1 (Agentic RAG) and Module_3 (Semantic Cache), following their respective licensing terms.