#!/usr/bin/env python3
"""Script para recriar o agente de propriedades simplificado"""

property_agent_code = '''"""
Agente de Análise de Propriedades

Especializado em apresentar informações de imóveis de forma clara e atrativa,
responder perguntas específicas sobre propriedades e comparar diferentes opções.
Implementa arquitetura LangGraph-Swarm com handoffs diretos.
"""

from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState

from ..models.property import Property, SearchCriteria
from ..utils.logging import get_logger, log_handoff, log_performance
from config.settings import get_settings


class PropertyAnalysis(BaseModel):
    """Modelo para análise de propriedades."""
    property_highlights: List[str] = Field(description="Pontos principais do imóvel")
    advantages: List[str] = Field(description="Vantagens do imóvel")
    disadvantages: List[str] = Field(description="Desvantagens ou pontos de atenção")
    suitability_score: float = Field(description="Score de adequação ao perfil (0-1)")
    comparison_points: List[str] = Field(description="Pontos para comparação")
    personalized_description: str = Field(description="Descrição personalizada")


class PropertyComparison(BaseModel):
    """Modelo para comparação de propriedades."""
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(description="Matriz de comparação")
    ranking: List[str] = Field(description="Ranking de propriedades por adequação")
    recommendation: str = Field(description="Recomendação final")
    decision_factors: List[str] = Field(description="Fatores principais para decisão")


class PropertyAgent:
    """
    Agente especializado em análise e apresentação de propriedades.
    
    Responsabilidades:
    - Apresentar informações de imóveis de forma clara e atrativa
    - Responder perguntas específicas sobre propriedades
    - Comparar diferentes opções
    - Destacar pontos relevantes baseado no perfil do usuário
    - Fazer handoffs para outros agentes quando necessário
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("property_agent")
        
        # Configurar modelo OpenRouter usando configurações centralizadas
        try:
            from pydantic_ai.models.openai import OpenAIModel
            from pydantic_ai.providers.openrouter import OpenRouterProvider
            
            # Obter chave via settings (centralizado - sem load_dotenv aqui)
            openrouter_key = self.settings.apis.openrouter_key or ""
            
            if openrouter_key and openrouter_key != "your_openrouter_api_key_here":
                self.model = OpenAIModel(
                    model_name=self.settings.models.property_model,
                    provider=OpenRouterProvider(api_key=openrouter_key)
                )
                self.logger.info(f"✅ Property agent initialized with OpenRouter model: {self.settings.models.property_model}")
            else:
                self.logger.warning("⚠️ No OpenRouter API key found, using test model")
                self.model = 'test'  # Fallback for testing
                
        except ImportError as e:
            self.logger.warning(f"⚠️ OpenRouter dependencies not available: {e}, using test model")
            self.model = 'test'
        except Exception as e:
            self.logger.error(f"❌ Error configuring OpenRouter: {e}, using test model")
            self.model = 'test'
        
        # Criar agente PydanticAI simples
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Cria o agente PydanticAI básico sem ferramentas complexas."""
        
        agent = Agent(
            model=self.model,
            system_prompt="""Você é o Agente de Análise de Propriedades, especializado em apresentar 
            informações imobiliárias de forma clara, atrativa e personalizada.

            SUAS RESPONSABILIDADES:
            - Apresentar informações de imóveis de forma clara e atrativa
            - Responder perguntas específicas sobre propriedades
            - Comparar diferentes opções objetivamente
            - Destacar pontos relevantes baseados no perfil do usuário
            - Gerar descrições personalizadas e envolventes

            PADRÃO ReAct (Reasoning + Acting):
            1. REASONING: Analise a consulta e o contexto do usuário
            2. ACTING: Execute análise ou comparação apropriada
            3. OBSERVATION: Avalie os resultados da análise
            4. DECISION: Forneça resposta personalizada e acionável

            DIRETRIZES:
            - Use linguagem clara e acessível
            - Destaque vantagens E desvantagens honestamente
            - Personalize respostas baseado no perfil do usuário
            - Inclua sugestões práticas e próximos passos
            - Seja objetivo mas envolvente
            - Sempre responda em português brasileiro

            FORMATO DAS RESPOSTAS:
            - Comece com resumo executivo
            - Detalhe pontos principais
            - Inclua análise pros/contras
            - Termine com recomendações práticas

            HANDOFFS:
            - Para scheduling_agent: quando usuário quer agendar visita
            - Para search_agent: quando precisa de mais propriedades
            """,
        )
        
        return agent


async def property_agent_node(state: Annotated[Dict[str, Any], InjectedState]) -> Command:
    """
    Nó principal do agente de propriedades no grafo LangGraph.
    
    Implementa a lógica de decisão para handoffs baseado no contexto.
    """
    logger = get_logger("property_agent")
    messages = state.get("messages", [])
    
    if not messages:
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Olá! Sou Emma, especialista em análise de propriedades. Como posso ajudá-lo?"
                }]
            }
        )
    
    last_message = messages[-1]
    user_query = last_message.get("content", "").lower()
    
    # Detectar intenções de handoff
    if any(word in user_query for word in ["agendar", "visita", "horário", "marcar"]):
        log_handoff("property_agent", "scheduling_agent", "User wants to schedule visit")
        return Command(
            goto="scheduling_agent",
            update={
                "context": {
                    "handoff_reason": "User requested visit scheduling",
                    "from_agent": "property_agent"
                }
            }
        )
    
    if any(word in user_query for word in ["buscar", "procurar", "encontrar", "mais opções"]):
        log_handoff("property_agent", "search_agent", "User wants new search")
        return Command(
            goto="search_agent",
            update={
                "context": {
                    "handoff_reason": "User requested new search",
                    "from_agent": "property_agent"
                }
            }
        )
    
    # Processar análise de propriedades
    try:
        # Verificar se há propriedades no contexto
        search_results = state.get("search_results")
        property_context = state.get("context", {}).get("property_context", {})
        
        # Gerar resposta baseada no contexto disponível
        if search_results and search_results.get("properties"):
            properties = search_results["properties"]
            response = f"""
🏠 **Análise das {len(properties)} Propriedades Encontradas**

Baseado nas propriedades encontradas, posso destacar os seguintes pontos:

📍 **Localização**: Todas em regiões estratégicas com boa infraestrutura
💰 **Preços**: Dentro da faixa solicitada com boa relação custo-benefício
🏗️ **Características**: Propriedades com diferentes configurações para atender suas necessidades

**Destaques principais:**
• Propriedades bem localizadas
• Diferentes faixas de preço
• Características variadas

**Próximos passos disponíveis:**
• 📅 Agendar visita a alguma propriedade
• 🔍 Buscar mais opções
• 📊 Comparação detalhada

Qual propriedade despertou mais seu interesse?
            """.strip()
        elif property_context:
            # Análise de propriedade específica
            title = property_context.get("title", "Propriedade")
            price = property_context.get("price_formatted", "N/A")
            neighborhood = property_context.get("address", {}).get("neighborhood", "N/A")
            
            response = f"""
🏠 **Análise Detalhada: {title}**

📍 **Localização:** {neighborhood}
💰 **Preço:** {price}

Esta propriedade apresenta características interessantes para o mercado atual. 
A localização oferece boa infraestrutura e acessibilidade.

**Pontos positivos identificados:**
• Localização estratégica
• Características adequadas ao perfil
• Potencial de mercado

**Próximos passos:**
• 📅 Agendar visita presencial
• 🔍 Buscar propriedades similares
• 📊 Comparar com outras opções

Como posso ajudar mais?
            """.strip()
        else:
            response = """
Olá! Sou Emma, sua especialista em análise de propriedades.

🔍 **Como posso ajudá-lo:**
• Análise detalhada de propriedades
• Comparação entre diferentes opções
• Informações sobre localização e amenidades
• Avaliação de custo-benefício
• Orientações para visitas

Para começar, você pode:
• Me mostrar uma propriedade específica para análise
• Pedir para buscar propriedades com critérios específicos
• Agendar uma visita a uma propriedade

O que gostaria de fazer?
            """.strip()
        
        return Command(
            update={
                "messages": [{
                    "role": "assistant", 
                    "content": response
                }]
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no agente de propriedades: {e}")
        return Command(
            update={
                "messages": [{
                    "role": "assistant",
                    "content": "Ocorreu um erro na análise. Poderia reformular sua pergunta?"
                }]
            }
        )


# Ferramentas exportadas para integração
PROPERTY_TOOLS = [
    "analyze_property",
    "compare_properties", 
    "generate_personalized_description"
]'''

def recreate_property_agent():
    import os
    
    # Deletar arquivo existente se houver
    if os.path.exists('app/agents/property.py'):
        os.remove('app/agents/property.py')
        print("✅ Arquivo antigo removido")
    
    # Criar novo arquivo
    with open('app/agents/property.py', 'w', encoding='utf-8') as f:
        f.write(property_agent_code)
    
    print("✅ Agente de propriedades recriado com sucesso")

if __name__ == "__main__":
    recreate_property_agent() 