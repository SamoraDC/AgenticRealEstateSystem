"""
Servidor MCP (Model Context Protocol) para integração com APIs de imóveis usando PydanticAI.

Implementação baseada na documentação oficial do PydanticAI MCP.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Annotated
from decimal import Decimal
import httpx
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from ..models.property import Property, PropertyType, PropertyStatus, Address, Features, SearchCriteria
from ..utils.logging import get_logger
from config.settings import get_settings


# Modelos Pydantic para o MCP
class PropertySearchRequest(BaseModel):
    """Modelo para requisição de busca de propriedades."""
    query: str = Field(description="Consulta em linguagem natural para busca de propriedades")
    city: Optional[str] = Field(default=None, description="Cidade para busca")
    state: Optional[str] = Field(default=None, description="Estado para busca")
    min_price: Optional[float] = Field(default=None, description="Preço mínimo")
    max_price: Optional[float] = Field(default=None, description="Preço máximo")
    bedrooms: Optional[int] = Field(default=None, description="Número de quartos")
    property_type: Optional[str] = Field(default=None, description="Tipo de propriedade")
    limit: int = Field(default=10, description="Limite de resultados")


class PropertySearchResponse(BaseModel):
    """Modelo para resposta de busca de propriedades."""
    properties: List[Dict[str, Any]] = Field(description="Lista de propriedades encontradas")
    total_found: int = Field(description="Total de propriedades encontradas")
    search_time: float = Field(description="Tempo de busca em segundos")
    sources: List[str] = Field(description="Fontes de dados utilizadas")


class PropertyAnalysisRequest(BaseModel):
    """Modelo para análise de propriedades."""
    property_data: Dict[str, Any] = Field(description="Dados da propriedade para análise")
    analysis_type: str = Field(default="general", description="Tipo de análise: general, investment, comparison")


class PropertyAnalysisResponse(BaseModel):
    """Modelo para resposta de análise."""
    analysis: str = Field(description="Análise detalhada da propriedade")
    score: float = Field(description="Score de 0 a 10 da propriedade")
    recommendations: List[str] = Field(description="Recomendações baseadas na análise")


# Dependências para os agentes
class MCPDependencies(BaseModel):
    """Dependências compartilhadas entre os agentes MCP."""
    settings: Any = Field(description="Configurações do sistema")
    logger: Any = Field(description="Logger do sistema")
    http_client: httpx.AsyncClient = Field(description="Cliente HTTP")


# Agentes PydanticAI especializados
class PropertySearchAgent:
    """Agente especializado em busca de propriedades usando PydanticAI."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("property_search_agent")
        
        # Configurar modelo baseado nas configurações
        model_config = self.settings.models
        self.model = OpenAIModel(
            model_name=model_config.search_model,
            base_url=self.settings.apis.openrouter_url,
        )
        
        # Criar agente PydanticAI
        self.agent = Agent(
            model=self.model,
            deps_type=MCPDependencies,
            system_prompt="""
            Você é um especialista em busca de imóveis no Brasil.
            
            Sua função é:
            1. Interpretar consultas em linguagem natural sobre imóveis
            2. Extrair critérios de busca estruturados
            3. Buscar propriedades em múltiplas APIs
            4. Retornar resultados relevantes e bem formatados
            
            Sempre responda em português e seja preciso nas informações.
            """,
            result_type=PropertySearchResponse
        )
    
    async def search_properties(self, request: PropertySearchRequest) -> PropertySearchResponse:
        """Busca propriedades usando o agente PydanticAI."""
        start_time = datetime.now()
        
        # Preparar dependências
        deps = MCPDependencies(
            settings=self.settings,
            logger=self.logger,
            http_client=httpx.AsyncClient(timeout=30.0)
        )
        
        try:
            # Executar busca através do agente
            prompt = f"""
            Busque propriedades com os seguintes critérios:
            - Consulta: {request.query}
            - Cidade: {request.city or 'Qualquer'}
            - Estado: {request.state or 'Qualquer'}
            - Preço mínimo: {request.min_price or 'Sem limite'}
            - Preço máximo: {request.max_price or 'Sem limite'}
            - Quartos: {request.bedrooms or 'Qualquer quantidade'}
            - Tipo: {request.property_type or 'Qualquer tipo'}
            - Limite: {request.limit}
            
            Retorne os resultados estruturados com propriedades relevantes.
            """
            
            result = await self.agent.run(prompt, deps=deps)
            
            # Se o agente não retornou o formato esperado, criar resposta padrão
            if not isinstance(result.data, PropertySearchResponse):
                # Buscar propriedades usando método direto
                properties = await self._direct_search(request, deps)
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return PropertySearchResponse(
                    properties=[prop.dict() for prop in properties],
                    total_found=len(properties),
                    search_time=execution_time,
                    sources=["RentCast", "Mock"]
                )
            
            return result.data
            
        except Exception as e:
            self.logger.error(f"Erro na busca de propriedades: {str(e)}")
            
            # Fallback para busca direta
            properties = await self._direct_search(request, deps)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return PropertySearchResponse(
                properties=[prop.dict() for prop in properties],
                total_found=len(properties),
                search_time=execution_time,
                sources=["Fallback"]
            )
        
        finally:
            await deps.http_client.aclose()
    
    async def _direct_search(self, request: PropertySearchRequest, deps: MCPDependencies) -> List[Property]:
        """Busca direta em APIs quando o agente falha."""
        
        # Converter para SearchCriteria
        criteria = SearchCriteria(
            cities=[request.city] if request.city else [],
            states=[request.state] if request.state else [],
            min_price=Decimal(str(request.min_price)) if request.min_price else None,
            max_price=Decimal(str(request.max_price)) if request.max_price else None,
            min_bedrooms=request.bedrooms,
            limit=request.limit
        )
        
        # Buscar usando RentCast (simulado)
        properties = await self._mock_rentcast_search(criteria)
        
        return properties
    
    async def _mock_rentcast_search(self, criteria: SearchCriteria) -> List[Property]:
        """Busca mock simulando RentCast API."""
        
        properties = []
        
        # Gerar propriedades mock baseadas nos critérios
        neighborhoods = ["Copacabana", "Ipanema", "Leblon", "Botafogo", "Flamengo"]
        property_types = [PropertyType.APARTMENT, PropertyType.HOUSE, PropertyType.CONDO]
        
        for i in range(min(criteria.limit, 8)):
            neighborhood = neighborhoods[i % len(neighborhoods)]
            prop_type = property_types[i % len(property_types)]
            
            # Preço baseado no bairro
            base_prices = {
                "Copacabana": 4500,
                "Ipanema": 6000, 
                "Leblon": 8000,
                "Botafogo": 3500,
                "Flamengo": 4000
            }
            
            base_price = base_prices.get(neighborhood, 4000)
            price = Decimal(base_price + (i * 300))
            
            # Filtrar por preço se especificado
            if criteria.min_price and price < criteria.min_price:
                continue
            if criteria.max_price and price > criteria.max_price:
                continue
            
            address = Address(
                street=f"Rua {neighborhood}",
                number=str(100 + i),
                neighborhood=neighborhood,
                city=criteria.cities[0] if criteria.cities else "Rio de Janeiro",
                state=criteria.states[0] if criteria.states else "RJ",
                country="Brasil",
                postal_code=f"22{i:03d}-000",
                latitude=-22.9068 + (i * 0.001),
                longitude=-43.1729 + (i * 0.001)
            )
            
            bedrooms = 2 + (i % 3)
            
            # Filtrar por quartos se especificado
            if criteria.min_bedrooms and bedrooms < criteria.min_bedrooms:
                continue
            
            features = Features(
                bedrooms=bedrooms,
                bathrooms=1 + (i % 2),
                area_total=60 + (i * 15),
                garage_spaces=1 if i % 2 == 0 else 0,
                has_pool=i % 3 == 0,
                has_gym=i % 4 == 0,
                has_balcony=True,
                allows_pets=i % 2 == 0
            )
            
            property_obj = Property(
                id=i + 1,
                external_id=f"mcp_mock_{i+1}",
                title=f"{prop_type.value.title()} {bedrooms}Q em {neighborhood}",
                description=f"Excelente {prop_type.value} localizado no coração de {neighborhood}. Propriedade com ótima localização e acabamento moderno.",
                property_type=prop_type,
                status=PropertyStatus.FOR_RENT,
                address=address,
                features=features,
                rent_price=price,
                source="MCP-Mock"
            )
            
            properties.append(property_obj)
        
        return properties


class PropertyAnalysisAgent:
    """Agente especializado em análise de propriedades usando PydanticAI."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger("property_analysis_agent")
        
        # Configurar modelo
        model_config = self.settings.models
        self.model = OpenAIModel(
            model_name=model_config.property_model,
            base_url=self.settings.apis.openrouter_url,
        )
        
        # Criar agente PydanticAI
        self.agent = Agent(
            model=self.model,
            deps_type=MCPDependencies,
            system_prompt="""
            Você é um especialista em análise imobiliária no Brasil.
            
            Sua função é:
            1. Analisar propriedades com base em dados fornecidos
            2. Avaliar localização, preço, características e potencial
            3. Fornecer score de 0 a 10 baseado em critérios objetivos
            4. Dar recomendações práticas e acionáveis
            
            Considere fatores como:
            - Localização e infraestrutura
            - Relação custo-benefício
            - Estado de conservação
            - Potencial de valorização
            - Adequação ao perfil do comprador/locatário
            
            Sempre responda em português com análises detalhadas e fundamentadas.
            """,
            result_type=PropertyAnalysisResponse
        )
    
    async def analyze_property(self, request: PropertyAnalysisRequest) -> PropertyAnalysisResponse:
        """Analisa uma propriedade usando o agente PydanticAI."""
        
        # Preparar dependências
        deps = MCPDependencies(
            settings=self.settings,
            logger=self.logger,
            http_client=httpx.AsyncClient(timeout=30.0)
        )
        
        try:
            # Preparar prompt baseado no tipo de análise
            property_info = json.dumps(request.property_data, indent=2, ensure_ascii=False)
            
            analysis_prompts = {
                "general": f"""
                Faça uma análise geral completa desta propriedade:
                
                {property_info}
                
                Avalie todos os aspectos relevantes e forneça um score de 0 a 10.
                """,
                "investment": f"""
                Analise esta propriedade do ponto de vista de investimento:
                
                {property_info}
                
                Foque em potencial de valorização, rentabilidade e riscos.
                """,
                "comparison": f"""
                Analise esta propriedade para comparação com outras opções:
                
                {property_info}
                
                Destaque pontos fortes, fracos e diferenciais competitivos.
                """
            }
            
            prompt = analysis_prompts.get(request.analysis_type, analysis_prompts["general"])
            
            # Executar análise através do agente
            result = await self.agent.run(prompt, deps=deps)
            
            if isinstance(result.data, PropertyAnalysisResponse):
                return result.data
            else:
                # Fallback para análise básica
                return self._basic_analysis(request.property_data)
                
        except Exception as e:
            self.logger.error(f"Erro na análise de propriedade: {str(e)}")
            return self._basic_analysis(request.property_data)
        
        finally:
            await deps.http_client.aclose()
    
    def _basic_analysis(self, property_data: Dict[str, Any]) -> PropertyAnalysisResponse:
        """Análise básica quando o agente falha."""
        
        # Extrair dados básicos
        price = property_data.get("rent_price") or property_data.get("price", 0)
        bedrooms = property_data.get("features", {}).get("bedrooms", 0)
        area = property_data.get("features", {}).get("area_total", 0)
        neighborhood = property_data.get("address", {}).get("neighborhood", "")
        
        # Calcular score básico
        score = 5.0  # Base
        
        # Ajustar por localização
        premium_neighborhoods = ["Ipanema", "Leblon", "Copacabana"]
        if neighborhood in premium_neighborhoods:
            score += 1.5
        
        # Ajustar por área/preço
        if area > 0 and price > 0:
            price_per_sqm = float(price) / area
            if price_per_sqm < 50:  # Bom custo-benefício
                score += 1.0
            elif price_per_sqm > 100:  # Caro
                score -= 0.5
        
        # Ajustar por características
        features = property_data.get("features", {})
        if features.get("has_pool"):
            score += 0.3
        if features.get("has_gym"):
            score += 0.2
        if features.get("garage_spaces", 0) > 0:
            score += 0.5
        
        score = min(max(score, 0), 10)  # Limitar entre 0 e 10
        
        analysis = f"""
        Análise Básica da Propriedade:
        
        📍 Localização: {neighborhood}
        💰 Preço: R$ {price:,.2f}
        🏠 Quartos: {bedrooms}
        📐 Área: {area}m²
        
        Esta propriedade apresenta características interessantes para o mercado atual.
        A localização em {neighborhood} oferece boa infraestrutura e acessibilidade.
        
        Pontos positivos identificados:
        - Localização estratégica
        - Características adequadas ao perfil
        - Potencial de mercado
        """
        
        recommendations = [
            "Verificar documentação completa",
            "Avaliar estado de conservação presencialmente",
            "Pesquisar preços similares na região",
            "Considerar custos adicionais (IPTU, condomínio)"
        ]
        
        return PropertyAnalysisResponse(
            analysis=analysis,
            score=score,
            recommendations=recommendations
        )


# Servidor MCP usando FastMCP
def create_mcp_server() -> FastMCP:
    """Cria e configura o servidor MCP com PydanticAI."""
    
    # Criar servidor FastMCP
    server = FastMCP(
        name="Agentic Real Estate MCP Server",
        description="Servidor MCP para busca e análise de propriedades usando PydanticAI"
    )
    
    # Inicializar agentes
    search_agent = PropertySearchAgent()
    analysis_agent = PropertyAnalysisAgent()
    
    logger = get_logger("mcp_server")
    
    @server.tool()
    async def search_properties(request: PropertySearchRequest) -> PropertySearchResponse:
        """
        Busca propriedades usando critérios especificados.
        
        Esta ferramenta utiliza um agente PydanticAI especializado para:
        - Interpretar consultas em linguagem natural
        - Buscar em múltiplas APIs de imóveis
        - Retornar resultados relevantes e estruturados
        """
        logger.info(f"Iniciando busca de propriedades: {request.query}")
        
        try:
            result = await search_agent.search_properties(request)
            logger.info(f"Busca concluída: {result.total_found} propriedades encontradas")
            return result
            
        except Exception as e:
            logger.error(f"Erro na busca de propriedades: {str(e)}")
            return PropertySearchResponse(
                properties=[],
                total_found=0,
                search_time=0.0,
                sources=["Error"]
            )
    
    @server.tool()
    async def analyze_property(request: PropertyAnalysisRequest) -> PropertyAnalysisResponse:
        """
        Analisa uma propriedade específica.
        
        Esta ferramenta utiliza um agente PydanticAI especializado para:
        - Avaliar características da propriedade
        - Calcular score de atratividade
        - Fornecer recomendações personalizadas
        """
        logger.info(f"Iniciando análise de propriedade: {request.analysis_type}")
        
        try:
            result = await analysis_agent.analyze_property(request)
            logger.info(f"Análise concluída com score: {result.score}")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de propriedade: {str(e)}")
            return PropertyAnalysisResponse(
                analysis="Erro na análise da propriedade.",
                score=0.0,
                recommendations=["Tente novamente mais tarde"]
            )
    
    @server.tool()
    async def get_market_insights(city: str, property_type: str = "apartment") -> Dict[str, Any]:
        """
        Obtém insights do mercado imobiliário para uma cidade específica.
        
        Retorna informações sobre:
        - Preços médios por tipo de propriedade
        - Tendências de mercado
        - Bairros em alta
        """
        logger.info(f"Buscando insights de mercado para {city}")
        
        # Mock de dados de mercado
        market_data = {
            "city": city,
            "property_type": property_type,
            "average_price": 450000.0,
            "price_trend": "stable",
            "hot_neighborhoods": ["Centro", "Zona Sul", "Barra"],
            "market_temperature": "aquecido",
            "recommendations": [
                f"Mercado de {property_type} em {city} está estável",
                "Boa oportunidade para investimento",
                "Considere bairros emergentes para melhor custo-benefício"
            ]
        }
        
        return market_data
    
    logger.info("Servidor MCP configurado com sucesso")
    return server


# Instância global do servidor MCP
mcp_server = create_mcp_server()


# Função para executar o servidor
async def run_mcp_server(host: str = "localhost", port: int = 8000):
    """Executa o servidor MCP."""
    logger = get_logger("mcp_server_runner")
    
    try:
        logger.info(f"Iniciando servidor MCP em {host}:{port}")
        
        # Executar servidor com transporte SSE
        await mcp_server.run(
            transport="sse",
            host=host,
            port=port
        )
        
    except Exception as e:
        logger.error(f"Erro ao executar servidor MCP: {str(e)}")
        raise


if __name__ == "__main__":
    # Executar servidor diretamente
    asyncio.run(run_mcp_server()) 