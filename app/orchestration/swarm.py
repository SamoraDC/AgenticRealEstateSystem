"""
Orquestrador LangGraph-Swarm com Agentes Inteligentes

Implementação da arquitetura swarm descentralizada com agentes inteligentes.
Integração PydanticAI + LangGraph para respostas dinâmicas.
Fallback inteligente com Ollama para funcionar sem chaves de API.
"""

from typing import Dict, Any, List, Optional, AsyncIterator, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from langgraph.checkpoint.memory import MemorySaver  # 🔥 NOVO: Checkpointer para memória
from langgraph.store.memory import InMemoryStore  # 🔥 NOVO: Store para memória de longo prazo

from ..utils.logging import get_logger, log_handoff, log_performance, log_agent_action, log_api_call, log_error
from ..utils.logfire_config import AgentExecutionContext, HandoffContext, get_logfire_config
from ..utils.ollama_fallback import generate_intelligent_fallback
from config.settings import get_settings
import time
import os
import random
import asyncio


class SwarmState(MessagesState):
    """Estado global do swarm com contexto compartilhado."""
    
    # Contexto de sessão
    session_id: str = Field(default="default")
    user_id: Optional[str] = None
    
    # Estado de busca
    search_intent: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None
    
    # Estado de análise de propriedades
    property_analysis: Optional[Dict[str, Any]] = None
    property_recommendations: Optional[List[Dict[str, Any]]] = None
    
    # Estado de agendamento
    scheduling_intent: Optional[Dict[str, Any]] = None
    calendar_events: Optional[List[Dict[str, Any]]] = None
    
    # Contexto de handoffs
    current_agent: str = Field(default="search_agent")
    handoff_history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


async def search_agent_node(state: SwarmState) -> dict:
    """Nó do agente de busca: entende a intenção de busca usando PydanticAI."""
    logger = get_logger("search_agent")
    
    # Instrumentação Logfire para rastreamento de execução
    with AgentExecutionContext("search_agent", "property_search") as span:
        start_time = time.time()
        
        # 🔥 CORREÇÃO: Acessar mensagens corretamente no LangGraph
        messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
        if not messages:
            logger.warning("No messages in state for search_agent")
            return {"messages": [AIMessage(content="Olá! Sou Alex, especialista em busca de imóveis. Como posso ajudá-lo?")]}
        
        # Extrair mensagem do usuário (compatível com dict e LangChain messages)
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            user_message = last_message.content
        else:
            user_message = last_message.get("content", "")
        
        context = state.get("context", {})
        data_mode = context.get("data_mode", "mock")
        
        # Log estruturado da execução do agente
        log_agent_action(
            agent_name="search_agent",
            action="process_search_request",
            details={
                "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
                "data_mode": data_mode,
                "session_id": state.get("session_id", "default")
            }
        )
        
        settings = get_settings()
        api_key = settings.apis.openrouter_key

        # Verificação corrigida da chave - não usar fallback se a chave existir
        if not api_key or api_key == "your_openrouter_api_key_here" or api_key.strip() == "":
            logger.warning("❌ No valid OpenRouter key found. Using Ollama fallback.")
            fallback_response = await generate_intelligent_fallback("search_agent", user_message, state.get("context", {}).get("property_context", {}), "mock")
            
            # Log do fallback
            log_agent_action(
                agent_name="search_agent",
                action="ollama_fallback_response",
                details={"reason": "no_api_key", "response_length": len(fallback_response)}
            )
            
            return {"messages": [AIMessage(content=fallback_response)]}

        try:
            logger.info(f"🧠 Using search agent for property search in {data_mode.upper()} mode: '{user_message}' (Key: {api_key[:10]}...)")
            
            # Try to get available properties from the system
            available_properties = []
            filtered_properties = []
            try:
                # Import here to avoid circular imports
                import requests
                import json
                
                # Get properties from the Mock API directly
                if data_mode == "mock":
                    # Use FastAPI Mock endpoint
                    response = requests.get("http://localhost:8000/api/properties/search")
                    if response.status_code == 200:
                        data = response.json()
                        available_properties = data.get("properties", [])
                        logger.info(f"🏠 Found {len(available_properties)} total properties in {data_mode} mode")
                        
                        # 🔥 NOVO: Filtrar propriedades baseadas na mensagem do usuário
                        filtered_properties = filter_properties_by_user_intent(user_message, available_properties)
                        logger.info(f"🎯 Filtered to {len(filtered_properties)} matching properties")
                    else:
                        logger.warning(f"Mock API returned status {response.status_code}")
                else:
                    # For real mode, we'd use actual API calls
                    logger.info("Real API mode not implemented yet")
                    available_properties = []
                
                # Log da busca de propriedades
                log_api_call(
                    api_name="MockAPI",
                    endpoint="/api/properties/search",
                    method="GET",
                    status_code=200,
                    duration=None
                )
                
            except Exception as e:
                logger.warning(f"Could not get available properties: {e}")
                log_error(e, context={"agent": "search_agent", "operation": "get_properties"})
            
            # 🔥 NOVO: Criar resumo inteligente das propriedades
            property_summary = create_intelligent_property_summary(user_message, filtered_properties, available_properties)

            # Create comprehensive search prompt
            prompt = f"""You are Alex, a professional real estate search specialist. You help clients find properties that match their needs and provide market insights.

User's Message: "{user_message}"
Data Mode: {data_mode.upper()}

{property_summary}

INSTRUCTIONS:
1. If the user asks for properties with specific features (pool, gym, etc.), analyze the available properties above
2. If you find matching properties, mention them specifically by address and key details
3. If no exact matches, suggest similar alternatives from the available properties
4. If the user is just starting their search, help them define criteria and show what's available
5. Keep responses concise but informative (3-5 sentences)
6. Use appropriate emojis to make responses engaging
7. Always end with a helpful question or suggestion to move the search forward
8. Be professional but friendly and conversational

SEARCH STRATEGY:
- For specific requests (like "pool"), look for properties that might have that feature
- For general requests, show a variety of options with different features and price points
- Always encourage the user to be more specific about their needs
- Guide them toward viewing properties that match their criteria

Respond now as Alex, using the available property information to help with their search."""

            # Usar modelo Gemma-3 que está funcionando
            model = OpenAIModel(
                "google/gemma-3-27b-it:free",  # Modelo gratuito que funciona
                provider=OpenRouterProvider(api_key=api_key),
            )
            agent = Agent(model)
            
            # Log da chamada LLM
            llm_start = time.time()
            response = await agent.run(prompt)
            llm_duration = time.time() - llm_start
            
            log_api_call(
                api_name="OpenRouter",
                endpoint="/chat/completions",
                method="POST",
                status_code=200,
                duration=llm_duration
            )
            
            # Check if response is too short or truncated
            response_content = str(response.data)
            if len(response_content.strip()) < 10:
                logger.warning(f"⚠️ Search response too short ({len(response_content)} chars): '{response_content}'")
                # Try with a simpler prompt
                simple_prompt = f"""You are Alex, a real estate search specialist. A user said: "{user_message}"

Respond helpfully about property search in 2-3 sentences. Be friendly and ask what they're looking for."""
                
                retry_response = await agent.run(simple_prompt)
                retry_content = str(retry_response.data)
                if len(retry_content.strip()) > len(response_content.strip()):
                    response_content = retry_content
                    logger.info(f"✅ Search retry successful: {len(response_content)} chars")
            
            # Log da resposta bem-sucedida
            duration = time.time() - start_time
            log_agent_action(
                agent_name="search_agent",
                action="llm_response_success",
                details={
                    "response_length": len(response_content),
                    "properties_found": len(available_properties),
                    "duration_seconds": duration
                }
            )
            
            logger.info(f"✅ PydanticAI search agent response: {len(response_content)} chars")
            logger.info(f"📝 Search response preview: {response_content[:100]}...")
            return {"messages": [AIMessage(content=response_content)]}

        except Exception as e:
            logger.error(f"❌ PydanticAI call failed for search agent: {e}")
            log_error(e, context={"agent": "search_agent", "operation": "llm_call"})
            
            logger.info("🔄 Falling back to Ollama intelligent response generator")
            fallback_response = await generate_intelligent_fallback("search_agent", user_message, state.get("context", {}).get("property_context", {}), "mock")
            
            # Log do fallback por erro
            log_agent_action(
                agent_name="search_agent",
                action="ollama_fallback_response",
                details={"reason": "llm_error", "error": str(e), "response_length": len(fallback_response)}
            )
            
            return {"messages": [AIMessage(content=fallback_response)]}


async def property_agent_node(state: SwarmState) -> dict:
    """Nó do agente de propriedades: analisa uma propriedade específica usando OpenRouter direto."""
    logger = get_logger("property_agent")
    
    # 🔥 CORREÇÃO: Acessar mensagens corretamente no LangGraph
    messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
    if not messages:
        logger.warning("No messages in state for property_agent")
        return {"messages": [AIMessage(content="Olá! Sou Emma, especialista em análise de propriedades. Como posso ajudá-lo?")]}
    
    # Extrair mensagem do usuário (compatível com dict e LangChain messages)
    last_message = messages[-1]
    if hasattr(last_message, 'content'):
        user_message = last_message.content
    else:
        user_message = last_message.get("content", "")
    
    context = state.get("context", {})
    property_context = context.get("property_context", {})
    data_mode = context.get("data_mode", "mock")  # Get data mode from context
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key

    # Verificação corrigida da chave - não usar fallback se a chave existir
    if not api_key or api_key == "your_openrouter_api_key_here" or api_key.strip() == "":
        logger.warning("❌ No valid OpenRouter key found. Using Ollama fallback.")
        fallback_response = await generate_intelligent_fallback("property_agent", user_message, property_context, data_mode)
        return {"messages": [AIMessage(content=fallback_response)]}
        
    try:
        logger.info(f"🧠 Using direct OpenRouter call for property analysis in {data_mode.upper()} mode: '{user_message}' (Key: {api_key[:10]}...)")
        logger.info(f"🏠 Property context: {property_context.get('formattedAddress', 'No address') if property_context else 'No property context'}")
        
        # Create property details string
        property_details = ""
        if property_context:
            # Format price safely
            price_value = property_context.get('price', 'N/A')
            if isinstance(price_value, (int, float)):
                price_formatted = f"${price_value:,}/month"
            else:
                price_formatted = f"${price_value}/month"
            
            # Format square footage safely
            sqft_value = property_context.get('squareFootage', 'N/A')
            if isinstance(sqft_value, (int, float)):
                sqft_formatted = f"{sqft_value:,} sq ft"
            else:
                sqft_formatted = f"{sqft_value} sq ft"
            
            property_details = f"""
PROPERTY DETAILS:
• Address: {property_context.get('formattedAddress', 'N/A')}
• Price: {price_formatted}
• Bedrooms: {property_context.get('bedrooms', 'N/A')}
• Bathrooms: {property_context.get('bathrooms', 'N/A')}
• Square Footage: {sqft_formatted}
• Property Type: {property_context.get('propertyType', 'N/A')}
• Year Built: {property_context.get('yearBuilt', 'N/A')}
• City: {property_context.get('city', 'N/A')}, {property_context.get('state', 'N/A')}
"""
        else:
            property_details = "No specific property information available."

        # Create comprehensive prompt with property context
        prompt = f"""You are Emma, a professional real estate property expert. You provide clear, objective, and helpful information about properties while being conversational and engaging.

{property_details}

User's Question: "{user_message}"

INSTRUCTIONS:
1. If the user asks about price/rent/cost, provide the exact price from the property details above
2. Always reference the specific property address when answering
3. Be objective and informative but maintain a friendly, professional tone
4. Use appropriate emojis to make responses engaging
5. Keep responses concise but comprehensive (2-4 sentences)
6. Always end with a question or suggestion to continue the conversation
7. If asked about aspects not in the property details, acknowledge what you don't know but offer related helpful information

CONVERSATION FLOW:
- Never ask the user to provide information you already have
- Always use the property details provided above
- Encourage questions about other aspects (neighborhood, amenities, scheduling visits)
- Maintain conversation momentum unless the user clearly indicates they want to end

Respond now as Emma, using the property information provided above to answer the user's question directly and professionally."""

        # Usar chamada direta ao OpenRouter
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemma-3-27b-it:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                },
                timeout=45.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Check if response is too short or truncated
                if len(content.strip()) < 10:
                    logger.warning(f"⚠️ Response too short ({len(content)} chars): '{content}'")
                    # Try again with different parameters
                    retry_response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.5,
                            "max_tokens": 1200,
                            "top_p": 0.8
                        },
                        timeout=45.0
                    )
                    
                    if retry_response.status_code == 200:
                        retry_result = retry_response.json()
                        retry_content = retry_result["choices"][0]["message"]["content"]
                        if len(retry_content.strip()) > len(content.strip()):
                            content = retry_content
                            logger.info(f"✅ Retry successful: {len(content)} chars")
                
                logger.info(f"✅ Direct OpenRouter call successful: {len(content)} chars")
                logger.info(f"📝 Response preview: {content[:100]}...")
                return {"messages": [AIMessage(content=content)]}
            else:
                logger.error(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code}")

    except Exception as e:
        logger.error(f"❌ Direct OpenRouter call failed for property agent: {e}")
        logger.info("🔄 Falling back to Ollama intelligent response generator")
        fallback_response = await generate_intelligent_fallback("property_agent", user_message, property_context, data_mode)
        return {"messages": [AIMessage(content=fallback_response)]}


async def scheduling_agent_node(state: SwarmState) -> dict:
    """Nó do agente de agendamento: agenda visitas usando OpenRouter direto."""
    logger = get_logger("scheduling_agent")
    
    # 🔥 CORREÇÃO: Acessar mensagens corretamente no LangGraph
    messages = state.messages if hasattr(state, 'messages') else state.get("messages", [])
    if not messages:
        logger.warning("No messages in state for scheduling_agent")
        return {"messages": [AIMessage(content="Olá! Sou Mike, especialista em agendamento. Como posso ajudá-lo?")]}
    
    # Extrair mensagem do usuário (compatível com dict e LangChain messages)
    last_message = messages[-1]
    if hasattr(last_message, 'content'):
        user_message = last_message.content
    else:
        user_message = last_message.get("content", "")
    
    context = state.get("context", {})
    property_context = context.get("property_context", {})
    data_mode = context.get("data_mode", "mock")  # Get data mode from context
    
    settings = get_settings()
    api_key = settings.apis.openrouter_key

    # Verificação corrigida da chave - não usar fallback se a chave existir
    if not api_key or api_key == "your_openrouter_api_key_here" or api_key.strip() == "":
        logger.warning("❌ No valid OpenRouter key found. Using Ollama fallback.")
        fallback_response = await generate_intelligent_fallback("scheduling_agent", user_message, property_context, data_mode)
        return {"messages": [AIMessage(content=fallback_response)]}
        
    try:
        logger.info(f"🧠 Using direct OpenRouter call for scheduling in {data_mode.upper()} mode: '{user_message}' (Key: {api_key[:10]}...)")
        
        # Create property details string for scheduling context
        property_details = ""
        if property_context:
            # Format price safely
            price_value = property_context.get('price', 'N/A')
            if isinstance(price_value, (int, float)):
                price_formatted = f"${price_value:,}/month"
            else:
                price_formatted = f"${price_value}/month"
            
            property_details = f"""
PROPERTY FOR VIEWING:
• Address: {property_context.get('formattedAddress', 'N/A')}
• Price: {price_formatted}
• Type: {property_context.get('propertyType', 'N/A')}
• Bedrooms: {property_context.get('bedrooms', 'N/A')} | Bathrooms: {property_context.get('bathrooms', 'N/A')}
"""
        else:
            property_details = "Property details will be confirmed upon scheduling."

        # Create comprehensive scheduling prompt
        prompt = f"""You are Mike, a professional scheduling assistant for real estate property viewings. You help clients schedule visits efficiently and provide all necessary details.

{property_details}

User's Request: "{user_message}"

INSTRUCTIONS:
1. Always reference the specific property address when discussing the viewing
2. Provide specific available time slots (suggest 2-3 options within the next 3-5 days)
3. Mention what to bring (ID, proof of income if applicable)
4. Specify viewing duration (typically 30-45 minutes)
5. Keep responses concise but complete (2-4 sentences)
6. Use appropriate emojis to make responses engaging
7. Always end with a clear next step or confirmation request
8. Be professional but friendly and accommodating

AVAILABLE TIME SUGGESTIONS:
- Weekdays: 10:00 AM, 2:00 PM, 4:00 PM
- Weekends: 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM

CONVERSATION FLOW:
- Confirm the property they want to view
- Offer specific time slots
- Explain what to expect during the visit
- Provide contact information for any changes
- Maintain momentum toward booking confirmation

Respond now as Mike, helping them schedule their property viewing professionally and efficiently."""

        # Usar chamada direta ao OpenRouter
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemma-3-27b-it:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 1000,
                    "top_p": 0.9,
                    "frequency_penalty": 0.0,
                    "presence_penalty": 0.0
                },
                timeout=45.0
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Check if response is too short or truncated
                if len(content.strip()) < 10:
                    logger.warning(f"⚠️ Scheduling response too short ({len(content)} chars): '{content}'")
                    # Try again with different parameters
                    retry_response = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "google/gemma-3-27b-it:free",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.4,
                            "max_tokens": 1200,
                            "top_p": 0.8
                        },
                        timeout=45.0
                    )
                    
                    if retry_response.status_code == 200:
                        retry_result = retry_response.json()
                        retry_content = retry_result["choices"][0]["message"]["content"]
                        if len(retry_content.strip()) > len(content.strip()):
                            content = retry_content
                            logger.info(f"✅ Scheduling retry successful: {len(content)} chars")
                
                logger.info(f"✅ Direct OpenRouter call successful: {len(content)} chars")
                logger.info(f"📝 Scheduling response preview: {content[:100]}...")
                return {"messages": [AIMessage(content=content)]}
            else:
                logger.error(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenRouter API error: {response.status_code}")

    except Exception as e:
        logger.error(f"❌ Direct OpenRouter call failed for scheduling agent: {e}")
        logger.info("🔄 Falling back to Ollama intelligent response generator")
        fallback_response = await generate_intelligent_fallback("scheduling_agent", user_message, property_context, data_mode)
        return {"messages": [AIMessage(content=fallback_response)]}


def route_message(state: SwarmState) -> Literal["search_agent", "property_agent", "scheduling_agent", END]:
    """
    Roteador inteligente baseado no contexto e histórico.
    
    Determina qual agente deve processar a próxima mensagem.
    """
    messages = state.get("messages", [])
    current_agent = state.get("current_agent", "property_agent")
    context = state.get("context", {})
    
    # Se não há mensagens, começar com property_agent se temos contexto de propriedade
    if not messages:
        if context.get("property_context"):
            return "property_agent"
        return "search_agent"
    
    last_message = messages[-1]
    
    # Extract content from LangChain message or dict
    if hasattr(last_message, 'content'):
        user_content = last_message.content.lower()
    else:
        user_content = last_message.get("content", "").lower()
    
    # Log para debug
    logger = get_logger("swarm_router")
    logger.info(f"🔀 Routing message: '{user_content[:100]}...'")
    
    # Detectar intenções específicas em inglês com mais precisão
    
    # Scheduling keywords - mais específicos
    scheduling_keywords = [
        "schedule", "visit", "appointment", "tour", "viewing", "book", "reserve",
        "when can i", "available times", "calendar", "meet", "show me the property",
        "see the property", "arrange", "set up"
    ]
    
    # Search keywords - quando quer propriedades diferentes ou com características específicas
    search_keywords = [
        # Busca explícita
        "find", "search", "look for", "looking for", "want", "need", "show me", 
        "different", "other properties", "another property", "similar", "alternatives", 
        "compare", "what else", "more options", "available", "any properties",
        
        # Características específicas que indicam busca
        "with pool", "has pool", "pool", "with gym", "has gym", "gym", 
        "with parking", "parking", "with balcony", "balcony", "with garden", "garden",
        "with terrace", "terrace", "oceanview", "ocean view", "waterfront",
        
        # Comparações e preferências
        "cheaper", "more expensive", "bigger", "smaller", "larger", "more bedrooms", 
        "less bedrooms", "more bathrooms", "pet friendly", "furnished", "unfurnished",
        
        # Tipos de propriedade quando buscando novos
        "a house", "an apartment", "a condo", "a townhouse", "a studio", "a loft",
        
        # Localização diferente
        "in miami", "in downtown", "near beach", "close to", "downtown area",
        
        # Frases que indicam busca
        "is there", "are there", "do you have", "any other", "something else",
        "what about", "how about", "instead", "rather than"
    ]
    
    # Property details keywords - sobre propriedade atual específica
    property_keywords = [
        "this property", "this apartment", "this house", "this unit", "this place",
        "tell me about", "details", "information", "how much", "how big", "size",
        "square feet", "sq ft", "rent", "price", "cost", "monthly", "utilities",
        "year built", "when built", "age", "condition", "features", "included",
        # Additional keywords for size questions
        "big", "large", "small", "area", "space", "footage"
    ]
    
    # Location/neighborhood keywords - sobre área da propriedade atual
    location_keywords = [
        "neighborhood", "area around", "surrounding area", "nearby", "close by",
        "transportation", "commute", "schools", "restaurants", "shopping",
        "safety", "crime", "walkability", "public transport"
    ]
    
    # Prioridade de roteamento
    
    # 1. Se menciona scheduling explicitamente -> scheduling_agent
    if any(keyword in user_content for keyword in scheduling_keywords):
        logger.info(f"🗓️ Routing to scheduling_agent (matched: scheduling)")
        return "scheduling_agent"
    
    # 2. Se quer buscar outras propriedades ou propriedades com características específicas -> search_agent  
    if any(keyword in user_content for keyword in search_keywords):
        logger.info(f"🔍 Routing to search_agent (matched: search)")
        return "search_agent"
    
    # 3. Se pergunta sobre detalhes específicos da propriedade atual -> property_agent
    if any(keyword in user_content for keyword in property_keywords) and context.get("property_context"):
        logger.info(f"🏠 Routing to property_agent (matched: property details)")
        return "property_agent"
    
    # 4. Se pergunta sobre localização/área da propriedade atual -> property_agent
    if any(keyword in user_content for keyword in location_keywords) and context.get("property_context"):
        logger.info(f"📍 Routing to property_agent (matched: location)")
        return "property_agent"
    
    # 5. Se temos property_context e pergunta é sobre amenities da propriedade atual -> property_agent
    if context.get("property_context") and any(word in user_content for word in ["amenities", "facilities", "what does it have"]):
        logger.info(f"🏢 Routing to property_agent (matched: amenities)")
        return "property_agent"
    
    # 6. Se temos property_context mas pergunta é geral -> property_agent
    if context.get("property_context"):
        logger.info(f"🏠 Routing to property_agent (default with property context)")
        return "property_agent"
    
    # 7. Caso contrário -> search_agent para ajudar a encontrar propriedades
    logger.info(f"🔍 Routing to search_agent (default)")
    return "search_agent"


class SwarmOrchestrator:
    """
    Orquestrador LangGraph-Swarm com Agentes Inteligentes.
    
    Coordena agentes especializados que usam lógica contextual através de handoffs diretos,
    sem supervisor central. Inclui sistema de memória de curto e longo prazo.
    """
    
    def __init__(self):
        self.logger = get_logger("swarm_orchestrator")
        self.settings = get_settings()
        
        # 🔥 NOVO: Sistema de memória
        self.checkpointer = MemorySaver()  # Memória de curto prazo (thread-scoped)
        self.store = InMemoryStore()  # Memória de longo prazo (cross-thread)
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construir grafo LangGraph-Swarm com agentes inteligentes e memória."""
        
        # Criar grafo com estado customizado
        graph = StateGraph(SwarmState)
        
        # Adicionar nós dos agentes inteligentes
        graph.add_node("search_agent", search_agent_node)
        graph.add_node("property_agent", property_agent_node)  
        graph.add_node("scheduling_agent", scheduling_agent_node)
        
        # Usar roteamento condicional baseado na mensagem
        graph.add_conditional_edges(
            START,
            route_message,
            {
                "search_agent": "search_agent",
                "property_agent": "property_agent", 
                "scheduling_agent": "scheduling_agent"
            }
        )
        
        # Cada agente termina após processar - sem loops
        graph.add_edge("search_agent", END)
        graph.add_edge("property_agent", END)
        graph.add_edge("scheduling_agent", END)
        
        # 🔥 NOVO: Compilar grafo com sistema de memória
        compiled_graph = graph.compile(
            checkpointer=self.checkpointer,  # Memória de curto prazo
            store=self.store  # Memória de longo prazo
        )
        
        self.logger.info("LangGraph-Swarm with intelligent routing and memory system built successfully")
        return compiled_graph
    
    async def process_message(self, message: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processar mensagem através do swarm com agentes inteligentes e memória.
        
        Args:
            message: Mensagem do usuário
            config: Configuração com thread_id para memória persistente
            
        Returns:
            Resposta processada pelo swarm
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🤖 Processing message with intelligent agents: {message}")
            
            # 🔥 NOVO: Usar config com thread_id para memória persistente
            if config:
                self.logger.info(f"🧠 Using persistent memory with thread_id: {config.get('configurable', {}).get('thread_id')}")
                result = await self.graph.ainvoke(message, config)
            else:
                # Fallback para compatibilidade
                self.logger.warning("No config provided, using default execution without persistent memory")
                result = await self.graph.ainvoke(message)
            
            # Calcular tempo de execução
            execution_time = time.time() - start_time
            log_performance("swarm_message_processing", execution_time)
            
            self.logger.info(f"✅ SwarmOrchestrator completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            raise
    
    async def process_stream(self, message: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Processar mensagem com streaming.
        
        Args:
            message: Mensagem do usuário
            
        Yields:
            Chunks da resposta em tempo real
        """
        try:
            self.logger.info(f"📨 Starting astream with message: {message}")
            
            chunk_count = 0
            async for chunk in self.graph.astream(message):
                chunk_count += 1
                self.logger.info(f"📦 Generated chunk #{chunk_count}: {chunk}")
                yield chunk
                
            self.logger.info(f"✅ Streaming completed - {chunk_count} chunks generated")
                
        except Exception as e:
            self.logger.error(f"Error in streaming: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            yield {"error": str(e)}
    
    def get_graph_visualization(self) -> str:
        """Obter visualização do grafo (para debug)."""
        try:
            return self.graph.get_graph().draw_mermaid()
        except Exception as e:
            self.logger.warning(f"Could not generate graph visualization: {e}")
            return "Graph visualization not available"


def filter_properties_by_user_intent(user_message: str, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtrar propriedades baseadas na intenção do usuário.
    
    Args:
        user_message: Mensagem do usuário
        properties: Lista de propriedades disponíveis
        
    Returns:
        Lista de propriedades filtradas
    """
    if not properties:
        return []
    
    user_lower = user_message.lower()
    filtered = []
    
    # Extrair critérios da mensagem do usuário
    criteria = {
        'min_bedrooms': None,
        'max_bedrooms': None,
        'min_bathrooms': None,
        'max_bathrooms': None,
        'min_price': None,
        'max_price': None,
        'amenities': [],
        'property_type': None,
        'location': None
    }
    
    # Detectar número de quartos
    if 'bedroom' in user_lower or 'br' in user_lower:
        import re
        bedroom_matches = re.findall(r'(\d+)\s*(?:bedroom|br)', user_lower)
        if bedroom_matches:
            criteria['min_bedrooms'] = int(bedroom_matches[0])
            if 'more than' in user_lower or 'at least' in user_lower:
                criteria['min_bedrooms'] = int(bedroom_matches[0])
            elif 'exactly' in user_lower or 'with' in user_lower:
                criteria['min_bedrooms'] = int(bedroom_matches[0])
                criteria['max_bedrooms'] = int(bedroom_matches[0])
    
    # Detectar número de banheiros
    if 'bathroom' in user_lower or 'bath' in user_lower:
        import re
        bathroom_matches = re.findall(r'(\d+)\s*(?:bathroom|bath)', user_lower)
        if bathroom_matches:
            criteria['min_bathrooms'] = int(bathroom_matches[0])
            if 'exactly' in user_lower or 'with' in user_lower:
                criteria['max_bathrooms'] = int(bathroom_matches[0])
    
    # Detectar amenidades
    amenity_keywords = {
        'pool': ['pool', 'swimming'],
        'gym': ['gym', 'fitness'],
        'parking': ['parking', 'garage'],
        'balcony': ['balcony'],
        'garden': ['garden', 'yard'],
        'terrace': ['terrace', 'deck'],
        'ocean': ['ocean', 'sea', 'beach'],
        'waterfront': ['waterfront', 'water view']
    }
    
    for amenity, keywords in amenity_keywords.items():
        if any(keyword in user_lower for keyword in keywords):
            criteria['amenities'].append(amenity)
    
    # Detectar tipo de propriedade
    if 'house' in user_lower:
        criteria['property_type'] = 'house'
    elif 'apartment' in user_lower or 'apt' in user_lower:
        criteria['property_type'] = 'apartment'
    elif 'condo' in user_lower:
        criteria['property_type'] = 'condo'
    elif 'studio' in user_lower:
        criteria['property_type'] = 'studio'
    
    # Detectar localização
    location_keywords = ['miami', 'downtown', 'beach', 'brickell', 'coral gables', 'aventura']
    for location in location_keywords:
        if location in user_lower:
            criteria['location'] = location
    
    # Aplicar filtros
    for prop in properties:
        matches = True
        
        # Filtrar por quartos
        if criteria['min_bedrooms'] is not None:
            if prop.get('bedrooms', 0) < criteria['min_bedrooms']:
                matches = False
        if criteria['max_bedrooms'] is not None:
            if prop.get('bedrooms', 0) > criteria['max_bedrooms']:
                matches = False
        
        # Filtrar por banheiros
        if criteria['min_bathrooms'] is not None:
            if prop.get('bathrooms', 0) < criteria['min_bathrooms']:
                matches = False
        if criteria['max_bathrooms'] is not None:
            if prop.get('bathrooms', 0) > criteria['max_bathrooms']:
                matches = False
        
        # Filtrar por localização
        if criteria['location']:
            address = prop.get('formattedAddress', '').lower()
            if criteria['location'] not in address:
                matches = False
        
        # Filtrar por amenidades (simulado - em produção seria baseado em dados reais)
        if criteria['amenities']:
            # Para demonstração, vamos assumir que algumas propriedades têm amenidades
            prop_amenities = []
            if prop.get('price', 0) > 2000:  # Propriedades mais caras tendem a ter mais amenidades
                prop_amenities.extend(['pool', 'gym', 'parking'])
            if prop.get('squareFootage', 0) > 1000:
                prop_amenities.extend(['balcony', 'garden'])
            if 'ocean' in prop.get('formattedAddress', '').lower() or 'bay' in prop.get('formattedAddress', '').lower():
                prop_amenities.extend(['ocean', 'waterfront'])
            
            # Verificar se pelo menos uma amenidade solicitada está presente
            if not any(amenity in prop_amenities for amenity in criteria['amenities']):
                matches = False
        
        if matches:
            filtered.append(prop)
    
    return filtered


def create_intelligent_property_summary(user_message: str, filtered_properties: List[Dict[str, Any]], all_properties: List[Dict[str, Any]]) -> str:
    """
    Criar resumo inteligente das propriedades baseado na intenção do usuário.
    
    Args:
        user_message: Mensagem do usuário
        filtered_properties: Propriedades filtradas
        all_properties: Todas as propriedades disponíveis
        
    Returns:
        Resumo formatado das propriedades
    """
    if not all_properties:
        return "\n\nNo property data available at the moment."
    
    user_lower = user_message.lower()
    
    # Se há propriedades filtradas, mostrar elas primeiro
    if filtered_properties:
        summary = f"\n\n🎯 PROPERTIES MATCHING YOUR CRITERIA ({len(filtered_properties)} found):\n"
        for i, prop in enumerate(filtered_properties[:5], 1):  # Mostrar até 5
            price = prop.get('price', 0)
            bedrooms = prop.get('bedrooms', 0)
            bathrooms = prop.get('bathrooms', 0)
            sqft = prop.get('squareFootage', 0)
            address = prop.get('formattedAddress', 'N/A')
            
            summary += f"{i}. 🏠 {address}\n"
            summary += f"   💰 ${price:,}/month | 🛏️ {bedrooms}BR/🚿{bathrooms}BA | 📐 {sqft:,} sq ft\n"
        
        if len(filtered_properties) > 5:
            summary += f"\n... and {len(filtered_properties) - 5} more matching properties available!\n"
        
        # Mostrar algumas alternativas se há mais propriedades
        if len(all_properties) > len(filtered_properties):
            summary += f"\n🔍 OTHER AVAILABLE OPTIONS ({len(all_properties) - len(filtered_properties)} more):\n"
            other_props = [p for p in all_properties if p not in filtered_properties][:3]
            for i, prop in enumerate(other_props, 1):
                price = prop.get('price', 0)
                bedrooms = prop.get('bedrooms', 0)
                bathrooms = prop.get('bathrooms', 0)
                address = prop.get('formattedAddress', 'N/A')
                summary += f"{i}. 🏠 {address} - ${price:,}/month, {bedrooms}BR/{bathrooms}BA\n"
    
    else:
        # Nenhuma propriedade atende aos critérios específicos
        summary = f"\n\n🔍 NO EXACT MATCHES FOUND for your specific criteria.\n"
        summary += f"📋 AVAILABLE PROPERTIES ({len(all_properties)} total):\n"
        
        # Mostrar uma variedade de propriedades
        sample_properties = all_properties[:5]
        for i, prop in enumerate(sample_properties, 1):
            price = prop.get('price', 0)
            bedrooms = prop.get('bedrooms', 0)
            bathrooms = prop.get('bathrooms', 0)
            sqft = prop.get('squareFootage', 0)
            address = prop.get('formattedAddress', 'N/A')
            
            summary += f"{i}. 🏠 {address}\n"
            summary += f"   💰 ${price:,}/month | 🛏️ {bedrooms}BR/🚿{bathrooms}BA | 📐 {sqft:,} sq ft\n"
        
        if len(all_properties) > 5:
            summary += f"\n... and {len(all_properties) - 5} more properties available!\n"
        
        summary += f"\n💡 Try adjusting your criteria or let me know what specific features you're looking for!"
    
    return summary


# Instância global do orquestrador
_swarm_orchestrator = None

def get_swarm_orchestrator() -> SwarmOrchestrator:
    """Obter instância singleton do SwarmOrchestrator."""
    global _swarm_orchestrator
    if _swarm_orchestrator is None:
        _swarm_orchestrator = SwarmOrchestrator()
    return _swarm_orchestrator

def create_swarm_graph():
    """Criar e retornar o grafo Swarm para testes."""
    orchestrator = get_swarm_orchestrator()
    return orchestrator.graph 