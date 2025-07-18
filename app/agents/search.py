"""
Property Search Agent

Implementation using native LangGraph tools for handoffs and tools.
No LangChain dependencies, following Swarm architecture.
"""

from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState, ToolNode
from langgraph.types import Command

from ..models.property import Property, SearchCriteria, SearchResult
from ..utils.logging import get_logger
from config.settings import get_settings

class SearchIntent(BaseModel):
    """Result of search interpretation."""
    criteria: SearchCriteria = Field(..., description="Extracted criteria")
    confidence: float = Field(..., description="Interpretation confidence (0-1)")
    clarification_needed: bool = Field(default=False, description="Needs clarification")
    clarification_message: Optional[str] = Field(None, description="Clarification message")
    reasoning: str = Field(..., description="Interpretation reasoning")

class SearchState(MessagesState):
    """Search agent specific state."""
    search_intent: Optional[SearchIntent] = None
    search_results: Optional[SearchResult] = None
    context: Dict[str, Any] = Field(default_factory=dict)

def interpret_search_query(
    query: str,
    state: Annotated[SearchState, InjectedState]
) -> SearchIntent:
    """
    Native LangGraph tool for interpreting search queries.
    
    This tool uses strong Pydantic typing and doesn't depend on LangChain.
    """
    logger = get_logger()
    settings = get_settings()
    
    # For now, use mock data without real model to save API calls
    # The model will be used only when necessary for final tests
    mock_intent = SearchIntent(
        criteria=SearchCriteria(),
        confidence=0.8,
        clarification_needed=False,
        reasoning="Mock interpretation to preserve API usage"
    )
    return mock_intent
    
    # Configurar agente PydanticAI
    agent = Agent(
        model=model,
        result_type=SearchIntent,
        system_prompt="""
        Você é um especialista em interpretação de consultas imobiliárias.
        
        RESPONSABILIDADES:
        1. Extrair critérios de busca de consultas em linguagem natural
        2. Identificar quando informações estão faltando
        3. Fornecer raciocínio claro para suas interpretações
        4. Detectar ambiguidades que precisam de clarificação
        
        EXEMPLOS:
        - "apartamento 2 quartos Copacabana até 5000" →
          property_types=[APARTMENT], min_bedrooms=2, neighborhoods=[Copacabana], max_price=5000
        - "casa família grande" → 
          property_types=[HOUSE], clarification_needed=True (qual cidade? quantos quartos?)
        
        DIRETRIZES:
        - Seja preciso na extração de entidades
        - Considere sinônimos regionais (apto=apartamento)
        - Identifique preferências implícitas
        - Marque clarification_needed=True quando necessário
        """
    )
    
    try:
        # Processar consulta
        result = agent.run_sync(
            user_prompt=f"Interprete esta consulta de busca: {query}",
            message_history=state.get("messages", [])
        )
        
        logger.info(f"Consulta interpretada: {result.data.criteria}")
        return result.data
        
    except Exception as e:
        logger.error(f"Erro na interpretação: {e}")
        # Retornar interpretação básica em caso de erro
        return SearchIntent(
            criteria=SearchCriteria(),
            confidence=0.0,
            clarification_needed=True,
            clarification_message=f"Não consegui interpretar a consulta. Poderia ser mais específico sobre localização, tipo de imóvel e faixa de preço?",
            reasoning=f"Erro na interpretação: {str(e)}"
        )

def execute_property_search(
    criteria: SearchCriteria,
    state: Annotated[SearchState, InjectedState]
) -> SearchResult:
    """
    Native tool for executing property searches.
    
    Integrates with external APIs through MCP server.
    """
    logger = get_logger()
    
    # TODO: Implement real integration with property APIs
    # For now, return mock results
    mock_properties = [
        Property(
            id=1,
            title="Miami Beach Apartment",
            description="Beautiful apartment with ocean view",
            property_type="apartment",
            status="for_rent",
            address={
                "street": "Collins Avenue",
                "number": "100",
                "neighborhood": "South Beach",
                "city": "Miami",
                "state": "FL"
            },
            features={
                "bedrooms": 2,
                "bathrooms": 1,
                "area_built": 800.0
            },
            rent_price=2500.00
        )
    ]
    
    result = SearchResult(
        properties=mock_properties,
        total_count=len(mock_properties),
        search_criteria=criteria,
        execution_time=0.5
    )
    
    logger.info(f"Search executed: {len(mock_properties)} properties found")
    return result

def transfer_to_property_agent() -> Command:
    """
    Ferramenta de handoff nativa do LangGraph para transferir para o agente de propriedades.
    
    Usa Command do LangGraph em vez de ferramentas do LangChain.
    """
    return Command(
        goto="property_agent",
        update={
            "context": {
                "handoff_reason": "Properties found, transferring for detailed analysis"
            }
        }
    )

# Configuração das ferramentas nativas
SEARCH_TOOLS = [
    interpret_search_query,
    execute_property_search,
    transfer_to_property_agent
]

def search_agent_node(state: SearchState) -> Command:
    """
    Nó principal do agente de busca no grafo LangGraph.
    
    Implementa a lógica de decisão para handoffs baseado no contexto.
    """
    logger = get_logger()
    messages = state.get("messages", [])
    
    if not messages:
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Olá! Sou seu assistente de busca de imóveis. Como posso ajudá-lo?"
                }]
            }
        )
    
    last_message = messages[-1]
    user_query = last_message.get("content", "")
    
    try:
        # Interpretar consulta
        intent = interpret_search_query(user_query, state)
        
        # Atualizar estado
        updated_state = {
            "search_intent": intent,
            "context": {"last_query": user_query}
        }
        
        # Verificar se precisa de clarificação
        if intent.clarification_needed:
            return Command(
                update={
                    **updated_state,
                    "messages": [{
                        "role": "assistant",
                        "content": intent.clarification_message
                    }]
                }
            )
        
        # Executar busca
        search_results = execute_property_search(intent.criteria, state)
        updated_state["search_results"] = search_results
        
        # Verificar se encontrou propriedades
        if search_results.is_empty:
            return Command(
                update={
                    **updated_state,
                    "messages": [{
                        "role": "assistant",
                        "content": "Não encontrei propriedades com esses critérios. Poderia tentar com critérios mais amplos?"
                    }]
                }
            )
        
        # Transferir para agente de propriedades para análise detalhada
        return Command(
            goto="property_agent",
            update={
                **updated_state,
                "context": {
                    **updated_state["context"],
                    "handoff_reason": f"Found {len(search_results.properties)} properties",
                    "search_completed": True
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no agente de busca: {e}")
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Ocorreu um erro durante a busca. Poderia tentar novamente?"
                }]
            }
        )

class SearchAgent:
    """
    Agente de Busca usando arquitetura LangGraph-Swarm.
    
    Implementa ferramentas nativas sem dependências do LangChain.
    """
    
    def __init__(self):
        self.logger = get_logger("search_agent")
        self.settings = get_settings()
        
        # Configurar modelo OpenRouter
        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider
            
            # Obter chave via settings (centralizado)
            openrouter_key = self.settings.apis.openrouter_key or ""
            
            if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
                self.model = OpenAIModel(
                    model_name=self.settings.models.search_model,
                    provider=OpenRouterProvider(api_key=openrouter_key)
                )
                self.logger.info(f"✅ Search agent initialized with OpenRouter model: {self.settings.models.search_model}")
            else:
                self.logger.warning("⚠️ No OpenRouter API key found, using test model")
                self.model = 'test'  # Fallback for testing
                
        except ImportError as e:
            self.logger.warning(f"⚠️ OpenRouter dependencies not available: {e}, using test model")
            self.model = 'test'
        except Exception as e:
            self.logger.error(f"❌ Error configuring OpenRouter: {e}, using test model")
            self.model = 'test'
        
        # Criar agente PydanticAI
        self.agent = self._create_agent()
        
        # Configurar ToolNode com ferramentas nativas
        self.tool_node = ToolNode(SEARCH_TOOLS)
    
    def _create_agent(self) -> Agent:
        """Cria o agente PydanticAI com ferramentas especializadas."""
        
        agent = Agent(
            model=self.model,
            system_prompt="""
            Você é um especialista em busca de imóveis no mercado americano.
            
            RESPONSABILIDADES:
            1. Interpretar consultas de busca em linguagem natural
            2. Extrair critérios específicos (localização, preço, tipo, características)
            3. Executar buscas inteligentes
            4. Apresentar resultados de forma organizada
            5. Fazer handoffs apropriados para outros agentes
            
            PADRÃO ReAct (Reasoning + Acting):
            1. REASONING: Analise a consulta e identifique critérios
            2. ACTING: Execute a busca com critérios otimizados
            3. OBSERVATION: Avalie a qualidade dos resultados
            4. DECISION: Determine próximos passos ou handoffs
            
            DIRETRIZES:
            - Faça perguntas específicas quando critérios estão vagos
            - Considere sinônimos e variações regionais
            - Sugira alternativas quando busca falha
            - Sempre responda em inglês (interface em inglês)
            
            HANDOFFS:
            - Para property_agent: quando encontrar propriedades relevantes
            - Para scheduling_agent: quando usuário quer agendar visita
            """,
        )
        
        return agent
    
    def get_node_function(self):
        """Retorna a função do nó para uso no grafo LangGraph."""
        return search_agent_node
    
    def get_tools(self):
        """Retorna as ferramentas para integração com outros agentes."""
        return SEARCH_TOOLS 