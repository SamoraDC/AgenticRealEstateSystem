# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Agentic Real Estate System** - An advanced AI-powered real estate search and scheduling platform built with LangGraph-Swarm architecture. The system uses specialized agents that collaborate dynamically to handle property searches, detailed property analysis, and appointment scheduling.

## Core Architecture

### Agent-Based Swarm System
- **Search Agent (Alex)**: Handles property discovery and filtering using intelligent criteria matching
- **Property Agent (Emma)**: Provides detailed analysis and information about specific properties  
- **Scheduling Agent (Mike)**: Manages appointment booking and calendar integration
- Built with **LangGraph + PydanticAI** for robust type safety and orchestration

### Technology Stack
- **Backend**: Python 3.11+ with FastAPI, PydanticAI, LangGraph
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **AI Models**: OpenRouter integration (using Mistral-7B-Instruct) with fallback to local Ollama
- **Observability**: Logfire + structured logging
- **Package Management**: UV (not pip)

## Development Commands

### Backend Development
```powershell
# Install dependencies (IMPORTANT: Use UV, not pip)
uv add <package-name>

# Activate virtual environment
.venv/Scripts/activate

# Run main application
python main.py

# Start API server
python api_server.py

# Run tests
python -m pytest tests/

# Code formatting and linting
ruff check .
ruff check --fix .
black .
mypy app config
```

### Frontend Development
```bash
cd frontend
npm run dev          # Development server
npm run build        # Production build
npm run preview      # Preview production build
npm run type-check   # TypeScript checking
```

### Testing Commands
```powershell
# Run comprehensive tests
python tests/run_comprehensive_tests.py

# Test specific agents
python tests/test_agent.py
python tests/test_swarm.py

# API integration tests
python tests/test_api_integration.py

# Stress testing
python test_stress_scenarios.py
```

## Important Development Practices

### PowerShell Requirement
- **CRITICAL**: All terminal commands must be executed through PowerShell (.ps1 files)
- Use `.venv/Scripts/activate` for virtual environment activation
- Create .ps1 files for complex command sequences

### Package Management
- **Always use `uv add <package>`** for adding dependencies
- **Never use `pip install` or `uv pip install`**
- Dependencies are managed through pyproject.toml

### Code Architecture

#### Agent Implementation (`app/agents/`)
- Each agent uses PydanticAI with OpenRouter models
- Fallback to Ollama for offline development
- Agents communicate through LangGraph state management

#### Orchestration (`app/orchestration/swarm.py`)
- SwarmOrchestrator coordinates agent interactions
- Intelligent routing based on user intent detection
- Memory system for conversation context

#### API Layer (`api_server.py`)
- FastAPI with property search endpoints
- Mock data for development, real API integration ready
- CORS enabled for frontend communication

### Configuration
- Settings managed via `config/settings.py` with Pydantic
- Environment variables in `.env` file
- API keys for OpenRouter, Google Calendar, property APIs

### Logging and Observability
- Structured logging via `app/utils/logging.py`
- Logfire integration for performance monitoring
- Separate log files for agents, API, errors, and performance

## Key Files and Locations

### Core Application
- `main.py` - Application entry point
- `app/orchestration/swarm.py` - Main swarm orchestrator (881 lines)
- `api_server.py` - FastAPI web server
- `config/settings.py` - Configuration management

### Agent Definitions
- `app/agents/search.py` - Property search agent prompts
- `app/agents/property.py` - Property analysis agent prompts  
- `app/agents/scheduling.py` - Appointment scheduling agent prompts

### Frontend Structure
- `frontend/src/App.tsx` - Main React application
- `frontend/src/components/` - React components
- `frontend/src/services/` - API communication services

### Testing
- `tests/` - Comprehensive test suite
- `test_stress_scenarios.py` - Performance testing
- `examples/` - Demo scripts and usage examples

## Data Modes
The system supports two operational modes:
- **Mock Mode**: Uses generated test data for development
- **Real Mode**: Connects to actual property APIs (RentCast, etc.)

## Workflow Guidelines

### Standard Development Process
1. Read codebase and create plan in todo.md
2. Get approval before implementing changes
3. Make minimal, simple changes
4. Provide detailed explanations of changes
5. Add review section to todo.md when complete
6. Create markdown documentation of changes

### Code Quality
- Follow existing patterns and conventions
- Use type hints consistently
- Maintain Portuguese language for user-facing content
- Write comprehensive tests for new features

### API Integration
- Property search through `/api/properties/search`
- Agent communication via `/api/chat` endpoint
- WebSocket support for real-time updates

This system emphasizes simplicity, observability, and intelligent agent collaboration for delivering a superior real estate search experience.

## Recent Updates

### Model Configuration Fix (Latest)
- **Issue**: OpenRouter models `meta-llama/llama-4-maverick:free` and `google/gemma-3-27b-it:free` were failing with API errors
- **Solution**: Switched to `mistralai/mistral-7b-instruct:free` which is working reliably
- **Memory Fix**: Updated LangGraph configuration to provide required `thread_id` for memory persistence
- **Code Updates**: Fixed deprecated `result.data` to `result.output` for PydanticAI compatibility

All agents now use the working Mistral model and the memory configuration issue is resolved.