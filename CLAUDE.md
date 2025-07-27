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

#### Orchestration (`app/orchestration/`)
- **Fixed Implementation** (`swarm_fixed.py`): Stable LangGraph-Swarm + PydanticAI integration
- **Hybrid Implementation** (`swarm_hybrid.py`): Advanced but complex implementation (deprecated)
- **Original Implementation** (`swarm.py`): Legacy custom implementation
- **Current Default**: `swarm_fixed.py` is used by API server for reliable operation

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
- `main.py` - Application entry point (uses legacy swarm.py)
- `app/orchestration/swarm_fixed.py` - **Current production orchestrator** (379 lines)
- `app/orchestration/swarm_hybrid.py` - Complex hybrid implementation (deprecated)
- `app/orchestration/swarm.py` - Original implementation (881 lines, legacy)
- `api_server.py` - FastAPI web server (uses swarm_fixed.py)
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

### Critical Architecture Fix (Latest - July 2025)
- **Major Issue Resolved**: Tool call validation errors in LangGraph-Swarm integration
  - Error: "Found AIMessages with tool_calls that do not have a corresponding ToolMessage"
  - Caused: System timeouts (26+ seconds) and complete failures
  - Impact: Users receiving nonsensical responses about "Brazil rental markets"

- **Solution Implemented**: Fixed LangGraph-Swarm Implementation (`swarm_fixed.py`)
  - **Architecture**: Simplified synchronous PydanticAI execution within LangGraph tools
  - **Benefits**: Maintains all PydanticAI advantages (retry, validation, observability)
  - **Stability**: Eliminates tool validation conflicts and async issues
  - **Performance**: Resolves timeout errors and provides consistent responses

- **Response Quality Improvements**:
  - **Enhanced System Prompts**: More specific, context-aware agent instructions
  - **Better Context Handling**: Proper property information integration
  - **Direct Responses**: Eliminated confusing response prefixes and system messages

- **API Server Updates**:
  - **Import Changed**: From `swarm_hybrid` to `swarm_fixed` for production stability
  - **Default Implementation**: API server now uses the fixed orchestrator
  - **Error Handling**: Improved fallback responses with proper context

### Previous Updates
- **Model Configuration**: Switched to `mistralai/mistral-7b-instruct:free` (working reliably)
- **Memory Fix**: Updated LangGraph configuration with required `thread_id` for persistence
- **Code Updates**: Fixed deprecated `result.data` to `result.output` for PydanticAI compatibility

## Current System State
- ✅ **Production Ready**: Fixed implementation resolves all critical issues
- ✅ **Stable Operation**: No more tool validation errors or timeouts
- ✅ **Quality Responses**: Agents provide relevant, contextual answers
- ✅ **Proper Integration**: LangGraph-Swarm + PydanticAI working harmoniously

## Implementation Recommendations

### For New Development
- **Always use**: `app/orchestration/swarm_fixed.py` for new features
- **Import pattern**: `from app.orchestration.swarm_fixed import get_fixed_swarm_orchestrator`
- **Memory config**: Always provide `thread_id` in config for proper memory persistence
- **Testing**: Use `test_fixed_swarm.py` as a template for new tests

### For Bug Fixes
- **Priority**: Focus on the fixed implementation first
- **Fallback**: Only modify legacy implementations if specifically required
- **Testing**: Ensure fixes work with the current production API server setup

### For API Development
- **Current setup**: API server uses `swarm_fixed.py` by default
- **Integration**: All new endpoints should use `get_fixed_swarm_orchestrator()`
- **Configuration**: Ensure proper `thread_id` and `session_id` handling

### Code Quality Guidelines
- **Response Quality**: Test that agents provide direct, relevant answers
- **Context Handling**: Verify property context is properly passed and used
- **Error Handling**: Ensure fallback responses are contextually appropriate
- **Performance**: Avoid async conflicts that caused the original issues