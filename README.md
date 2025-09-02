# Semantic Search Engine

A comprehensive Retrieval-Augmented Generation (RAG) pipeline that combines multi-document retrieval, semantic caching, and agentic routing for intelligent question answering.

## 🚀 Features

- **Multi-Document Retrieval**: Search across 10-K financial reports and OpenAI documentation
- **Semantic Caching**: FAISS-based caching with similarity matching for faster responses
- **Agentic Routing**: Intelligent query classification and routing to appropriate data sources
- **Sub-Query Division**: Break complex queries into focused sub-questions
- **Web Search Integration**: ARES API for real-time internet search
- **Real-time Interface**: React frontend with WebSocket connectivity
- **Observability**: Comprehensive logging and performance metrics

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React         │────▶│   FastAPI       │────▶│   Qdrant        │
│   Frontend      │     │   Backend       │     │   Vector DB     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   OpenAI API    │
                        │   ARES API      │
                        └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- ARES API key (for web search)
- Qdrant (local or cloud instance)

## 🛠️ Installation

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd Semantic_Search_Engine

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333  # or your Qdrant cloud URL
QDRANT_API_KEY=your_qdrant_api_key_here  # if using cloud

# ARES API Configuration
ARES_API_KEY=your_ares_api_key_here

# Application Configuration
FASTAPI_HOST=localhost
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

### 3. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

### 4. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

The frontend will be available at: http://localhost:3000

### 5. Production Build

```bash
cd frontend
npm run build

# The FastAPI server will automatically serve the built React app
```

## 🔧 Qdrant Setup

### Option 1: Local Qdrant with Docker

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Option 2: Use Pre-built Data from Modules

If you have the data from Module_1:

```bash
# Copy the qdrant_data folder to your project root
cp -r Module_1/Agentic_RAG/qdrant_data ./

# Update QDRANT_URL in .env to point to local path
QDRANT_URL=./qdrant_data
```

## 🎯 Usage

### Web Interface

1. Open http://localhost:8000 (or http://localhost:3000 in development)
2. Enter your question in the search box
3. Configure options:
   - **Allow Web Search**: Enable external search capabilities
   - **Sub-Query Division**: Break complex queries into parts
4. View results with supporting documents and logs

### API Usage

#### Direct Search

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What was Uber revenue in 2021?",
    "allow_web_search": true
  }'
```

#### Sub-Query Search

```bash
curl -X POST "http://localhost:8000/api/search/subquery" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare Lyft and Uber revenue and tell me about latest transport tech",
    "allow_web_search": true
  }'
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws?client_id=unique_id');

// Send search query
ws.send(JSON.stringify({
  type: 'search_query',
  data: {
    query: 'Your question here',
    allow_web_search: true,
    sub_query: false
  }
}));
```

## 📊 Example Queries

### Financial Queries (10-K Documents)
- "What was Uber's revenue in 2021?"
- "Compare Lyft's 2024 performance"
- "Show me the risk factors for Uber"

### OpenAI Documentation Queries
- "How do I use OpenAI's chat completions API?"
- "What are the pricing details for GPT-4?"
- "How to implement fine-tuning with OpenAI?"

### Web Search Queries
- "Latest AI developments in 2024"
- "Current Tesla stock price"
- "Recent changes in tech industry"

### Complex Multi-Part Queries
- "What was Lyft revenue in 2024 and Uber revenue in 2021?"
- "Compare Apple and Microsoft financial performance and tell me about latest AI trends"

## 🏃‍♂️ Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Performance Features

### Semantic Caching
- **Hit Rate**: Tracks cache effectiveness
- **Response Time**: 10x faster for cache hits (~0.1s vs 1-3s)
- **Similarity Matching**: Handles paraphrased queries

### Sub-Query Division
- **Complex Query Handling**: Automatically breaks down multi-part questions
- **Independent Processing**: Each sub-query processed separately
- **Result Aggregation**: Combines results intelligently

### Observability
- **Real-time Logs**: Component-level logging with timestamps
- **Cache Metrics**: Hit/miss rates and performance stats
- **Query Routing**: Visibility into decision-making process

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on correct port
   - Verify CORS settings in backend configuration

2. **API Key Errors**
   - Ensure all API keys are correctly set in `.env`
   - Check API key permissions and usage limits

3. **Qdrant Connection Issues**
   - Verify Qdrant is running and accessible
   - Check QDRANT_URL configuration

4. **Cache Not Working**
   - Check file permissions for cache directory
   - Verify FAISS installation

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging:

```bash
# Backend logs
tail -f logs/app.log

# Or check browser console for frontend logs
```

## 🔍 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Development

### Adding New Data Sources

1. Create a new service in `backend/app/services/`
2. Add routing logic in `router_service.py`
3. Update the route handlers in `rag_service.py`

### Extending the Frontend

1. Add new components in `frontend/src/components/`
2. Update WebSocket message handling in `App.jsx`
3. Extend the API utility functions

## 📝 License

This project is built upon the work from Module_1 (Agentic RAG) and Module_3 (Semantic Cache).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

## 🎉 Acknowledgments

- Module_1: Agentic RAG implementation
- Module_3: Semantic caching system
- OpenAI for embeddings and language models
- Qdrant for vector database
- ARES API for web search capabilities