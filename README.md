# 🏠 Agentic Real Estate System with LangGraph-Swarm

## 🌟 Overview

Advanced artificial intelligence agentic system for real estate search and scheduling, implementing a **swarm architecture** using LangGraph-Swarm, where specialized agents collaborate dynamically to solve complex user queries.

### ✨ Key Features

- 🤖 **Swarm Architecture**: Agents transfer dynamically based on context
- 🧠 **PydanticAI + LangGraph**: Combination of strong typing with advanced orchestration
- 🔄 **Intelligent Handoffs**: Automatic transfers between specialized agents
- 📊 **Complete Observability**: Detailed tracking with Logfire and LangSmith
- 🌐 **Multi-API Integration**: Access to multiple real estate APIs
- 🎯 **Production Ready**: Enterprise-grade reliability and monitoring
- 🚀 **Real-time Dashboard**: Live system monitoring and analytics

## 🏛️ Architecture

### Specialized Agents

#### 🔍 **Search Agent** (PydanticAI + OpenRouter)

- Interprets natural language queries
- Executes intelligent property searches
- Applies filters and relevance ranking
- **Transfers to**: Property Agent (property details) | Scheduling Agent (visit requests)

#### 🏠 **Property Agent** (PydanticAI + OpenRouter)

- Analyzes specific property information
- Provides detailed property insights
- Handles property-specific questions
- **Transfers to**: Search Agent (new search) | Scheduling Agent (visit booking)

#### 📅 **Scheduling Agent** (PydanticAI + OpenRouter)

- Manages appointment scheduling via Google Calendar
- Advanced temporal intelligence
- Commercial hours validation
- **Transfers to**: Search Agent (new search) | Property Agent (property details)

### Agent Transfer Flow (Handoffs)

```mermaid
graph LR
    A[User] --> B[Search Agent]
    B -.->|Property details| C[Property Agent]  
    C -.->|Schedule visit| D[Scheduling Agent]
    D -.->|New search| B
    B -.->|Book visit| D
    C -.->|Similar properties| B
```

**Agents:**
- 👤 **User**: Sistema usuário iniciador
- 🔍 **Search Agent**: Agente de busca de propriedades  
- 🏠 **Property Agent**: Agente de análise de propriedades
- 📅 **Scheduling Agent**: Agente de agendamento

### Technical Stack

- **Core Framework**: LangGraph-Swarm for agent orchestration
- **Agent Implementation**: PydanticAI with OpenRouter integration
- **Observability**: Logfire + LangSmith dual tracing
- **Memory System**: Short-term (thread-scoped) + Long-term (cross-thread)
- **API Server**: FastAPI with real-time dashboard
- **Error Handling**: Multi-layer fallback (Primary → Fallback → Ollama)

## 🚀 Installation and Setup

### Prerequisites

- Python 3.11+
- API keys configured (see `.env.example`)
- Windows or Linux environment

### Installation

```bash
# Clone repository
git clone <repo-url>
cd Agentic-Real-Estate

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies using uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required keys:
OPENROUTER_API_KEY=sk-or-v1-your-key-here
RENTCAST_API_KEY=your-rentcast-key
GOOGLE_API_KEY=your-google-key
LOGFIRE_TOKEN=your-logfire-token (optional)
LANGSMITH_API_KEY=your-langsmith-key (optional)
```

### Core Dependencies

```toml
# AI Framework
"pydantic-ai[logfire,openrouter]>=0.0.14"  # Agents with strong typing
"langgraph>=0.2.0"                         # Graph orchestration
"langgraph-checkpoint>=2.0.0"              # Memory management

# Observability
"logfire>=0.51.0"                          # Native observability
"langsmith>=0.1.0"                         # LangGraph tracing
"structlog>=24.1.0"                        # Structured logging

# API & Integration
"fastapi>=0.115.13"                        # Web API
"httpx>=0.27.0"                            # HTTP client
"openai>=1.40.0"                           # OpenAI compatibility
```

## 🎮 System Usage

### Quick Start

```python
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings

# Initialize system
settings = get_settings()
orchestrator = SwarmOrchestrator()

# Process user query
result = await orchestrator.process_message({
    "messages": [{"role": "user", "content": "I need a 2-bedroom apartment in Miami under $3000"}]
})

print(f"Response: {result['messages'][-1]['content']}")
```

### Starting the API Server

```bash
# Development server
python api_server.py

# Production server
uvicorn api_server:app --host 0.0.0.0 --port 8000

# Access API documentation
open http://localhost:8000/api/docs

# Access real-time dashboard
open http://localhost:8000/dashboard/
```

### Interactive Demo

```bash
# Run the main system
python main.py

# Or start with specific configuration
python main.py --debug --data-mode=real
```

## 📊 Real-time Dashboard

### Dashboard Features

Access the comprehensive monitoring dashboard at: **http://localhost:8000/dashboard/**

- **🚀 System Status**: Uptime, active sessions, total calls
- **🤖 Agent Performance**: Success rates, average duration, call counts
- **🌐 API Monitoring**: External API performance and error tracking
- **🔄 Recent Handoffs**: Agent transition tracking with reasoning
- **📋 System Logs**: Real-time log streaming with error filtering

### Dashboard Capabilities

- **Real-time Updates**: WebSocket-based live data (3-second refresh)
- **Performance Metrics**: Detailed per-agent and per-API statistics
- **Error Tracking**: Immediate notification of system issues
- **Mobile Responsive**: Professional interface for all devices
- **Auto-reconnection**: Automatic recovery from connection drops

## 🔧 Advanced Configuration

### Agent Customization

```python
# Custom agent configuration
from app.orchestration.swarm import create_pydantic_agent

# Create specialized agent
agent = await create_pydantic_agent(
    agent_name="luxury_search_agent",
    model_name="mistralai/mistral-7b-instruct:free"
)
```

### Observability Setup

```bash
# Logfire configuration
export LOGFIRE_TOKEN="your_logfire_token"

# LangSmith configuration  
export LANGSMITH_API_KEY="your_langsmith_key"
export LANGSMITH_PROJECT="agentic-real-estate"
export LANGCHAIN_TRACING_V2="true"
```

### Memory Configuration

```python
# Configure memory systems
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# Thread-scoped memory for conversations
checkpointer = MemorySaver()

# Cross-thread memory for long-term context
store = InMemoryStore()
```

## 🔍 Use Cases and Examples

### 1. Property Search with Details

```
👤 "2-bedroom apartment in downtown Miami under $2500"
🔍 search_agent: [finds matching properties]
👤 "Tell me more about the first one"
🔄 Automatic: search_agent → property_agent  
🏠 property_agent: [provides detailed property analysis]
```

### 2. Search to Scheduling Flow

```
👤 "Show me condos in Brickell with ocean view"
🔍 search_agent: [finds properties with ocean views]
👤 "I'd like to visit the penthouse tomorrow at 2pm"
🔄 Automatic: search_agent → scheduling_agent
📅 scheduling_agent: [schedules appointment and confirms]
```

### 3. Property Analysis and Comparison

```
👤 "What's the price per square foot of this property?"
🏠 property_agent: [calculates and explains pricing]
👤 "Show me similar properties in the area"
🔄 Automatic: property_agent → search_agent
🔍 search_agent: [finds comparable properties]
```

## 📈 System Monitoring and Analytics

### Performance Metrics

- **Agent Success Rate**: % of successful agent executions
- **Average Response Time**: Mean duration per agent call
- **Handoff Frequency**: Rate of agent-to-agent transfers
- **API Health**: External API uptime and performance
- **Error Rate**: System error frequency and types

### Observability Tools

#### Logfire Integration

- Native PydanticAI instrumentation
- Detailed agent execution traces
- Real-time performance monitoring
- Error context and debugging

#### LangSmith Integration

- LangGraph workflow tracing
- Node-level performance analysis
- State transition tracking
- Conversation flow visualization

#### Custom Dashboard

- Real-time system metrics
- Agent performance analytics
- API call monitoring
- Error tracking and alerting

## 🧪 Development and Testing

### Project Structure

```
Agentic-Real-Estate/
├── app/                        # Main application
│   ├── agents/                 # Individual agent implementations
│   ├── api/                    # FastAPI routes and dashboard
│   ├── orchestration/          # LangGraph-Swarm orchestrator
│   ├── utils/                  # Utilities (logging, observability)
│   └── models/                 # Pydantic models
├── config/                     # Configuration management
├── docs/                       # Documentation
├── tests/                      # Test suites
└── api_server.py              # FastAPI application entry point
```

### Running Tests

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio

# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/agents/          # Agent tests
python -m pytest tests/orchestration/   # Swarm tests
python -m pytest tests/api/            # API tests

# Run with coverage
python -m pytest --cov=app tests/
```

### Development Workflow

```bash
# Enable debug mode
export DEBUG=true

# Start development server with auto-reload
python api_server.py

# Monitor logs in real-time
tail -f logs/agentic_real_estate.log

# Access interactive documentation
open http://localhost:8000/api/docs
```

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
# Build production image
docker build -t agentic-real-estate .

# Run container
docker run -d \
  --name agentic-real-estate \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your-key \
  -e RENTCAST_API_KEY=your-key \
  agentic-real-estate
```

### Environment Variables

```bash
# Production configuration
export ENVIRONMENT=production
export DEBUG=false
export OPENROUTER_API_KEY=your-production-key
export RENTCAST_API_KEY=your-production-key
export LOGFIRE_TOKEN=your-logfire-token
export LANGSMITH_API_KEY=your-langsmith-key

# Database configuration (if using external DB)
export DB_URL=postgresql://user:pass@host:5432/dbname
export REDIS_URL=redis://host:6379/0
```

### Scaling Considerations

- **Load Balancing**: Use multiple instances behind a load balancer
- **Redis Integration**: Distributed caching and session storage
- **Database**: PostgreSQL for persistent data storage
- **Monitoring**: Production-grade observability with alerts

## 🔧 Troubleshooting

### Common Issues

#### 1. Unicode Encoding Errors (Windows)

**Fixed**: All emoji characters replaced with ASCII equivalents

```
Error: 'charmap' codec can't encode character
Solution: System automatically uses ASCII logging
```

#### 2. OpenRouter API Authentication

**Enhanced**: Comprehensive debugging infrastructure

```bash
# Check API key configuration
python test_api_key.py

# Enable debug logging
export DEBUG=true
```

#### 3. Agent Handoff Issues

**Monitoring**: Real-time handoff tracking in dashboard

```
Check dashboard for handoff history and routing decisions
```

### Debug Tools

```bash
# Syntax check
python -m py_compile app/orchestration/swarm.py

# API key validation
python test_api_key.py

# System health check
curl http://localhost:8000/api/health

# Dashboard metrics
curl http://localhost:8000/dashboard/api/metrics
```

## 📚 Additional Documentation

- [🏗️ System Architecture](docs/LANGGRAPH_SWARM_VERIFICATION_SUMMARY.md)
- [🔧 Complete System Improvements](docs/COMPLETE_SYSTEM_IMPROVEMENTS_SUMMARY.md)
- [🐛 API Debugging Guide](docs/OPENROUTER_API_DEBUGGING_CHANGES.md)
- [📊 Dashboard Usage Guide](app/api/dashboard.py)

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PydanticAI patterns for agent implementation
- Use LangGraph best practices for orchestration
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure observability for new components

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Useful Links

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [Logfire Documentation](https://logfire.pydantic.dev/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [OpenRouter API Documentation](https://openrouter.ai/docs)

## 🎯 System Status

✅ **Production Ready**: All core features implemented and tested
✅ **Comprehensive Monitoring**: Real-time dashboard and observability
✅ **Error Handling**: Multi-layer fallback and recovery mechanisms
✅ **Documentation**: Complete setup and usage documentation
✅ **Testing**: Comprehensive test suite and debugging tools

---

**Developed with ❤️ using PydanticAI + LangGraph-Swarm**

**System Version**: 1.0.0 | **Last Updated**: 2024
**Enterprise-grade AI Agent System for Real Estate Operations**
