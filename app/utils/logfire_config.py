"""
Configuração do Logfire para observabilidade avançada do sistema agêntico.

Integra o Logfire (nativo do PydanticAI) para rastreamento completo de:
- Execuções de agentes
- Handoffs entre agentes  
- Chamadas de API
- Performance e métricas
- Debugging e troubleshooting
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from pathlib import Path

try:
    import logfire
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    logfire = None

from config.settings import get_settings


class LogfireConfig:
    """Configuração centralizada do Logfire."""
    
    def __init__(self):
        self.settings = get_settings()
        self.configured = False
        self.logger = logging.getLogger(__name__)
        
    def is_available(self) -> bool:
        """Verificar se Logfire está disponível."""
        return LOGFIRE_AVAILABLE
    
    def configure_logfire(self) -> bool:
        """
        Configurar Logfire para observabilidade.
        
        Returns:
            bool: True se configurado com sucesso
        """
        if not self.is_available():
            self.logger.warning("🔥 Logfire não disponível - install com: uv add 'pydantic-ai[logfire]'")
            return False
            
        try:
            # Verificar token
            token = self.settings.observability.logfire_token
            if not token:
                self.logger.info("🔥 Logfire token não configurado - usando modo local")
                
            # Configurar Logfire
            if token:
                logfire.configure(
                    token=token,
                    service_name="agentic-real-estate",
                    service_version=self.settings.app_version,
                    environment=self.settings.environment
                )
                self.logger.info("🔥 Logfire configurado com token")
            else:
                # Modo local/desenvolvimento
                logfire.configure(
                    send_to_logfire=False,  # Não enviar para Logfire cloud
                    service_name="agentic-real-estate",
                    service_version=self.settings.app_version,
                    environment=self.settings.environment
                )
                self.logger.info("🔥 Logfire configurado em modo local")
            
            # Instrumentar PydanticAI
            try:
                logfire.instrument_pydantic_ai()
                self.logger.info("✅ PydanticAI instrumentado")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao instrumentar PydanticAI: {e}")
            
            # Instrumentar HTTPX para rastrear chamadas de API
            try:
                logfire.instrument_httpx()
                self.logger.info("✅ HTTPX instrumentado")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao instrumentar HTTPX: {e}")
            
            self.configured = True
            self.logger.info("✅ Logfire instrumentação ativada")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar Logfire: {e}")
            return False
    
    def create_agent_tracer(self, agent_name: str):
        """
        Criar tracer específico para um agente.
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Tracer configurado ou None se Logfire não disponível
        """
        if not self.is_available() or not self.configured:
            return None
            
        return logfire.span(f"agent.{agent_name}")
    
    def log_agent_execution(
        self,
        agent_name: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log estruturado de execução de agente.
        
        Args:
            agent_name: Nome do agente
            action: Ação executada
            input_data: Dados de entrada
            output_data: Dados de saída
            duration: Duração em segundos
            metadata: Metadados adicionais
        """
        if not self.is_available() or not self.configured:
            return
            
        with logfire.span(f"agent.{agent_name}.{action}") as span:
            span.set_attributes({
                "agent.name": agent_name,
                "agent.action": action,
                "agent.input_size": len(str(input_data)),
                "agent.environment": self.settings.environment
            })
            
            if output_data:
                span.set_attribute("agent.output_size", len(str(output_data)))
                
            if duration:
                span.set_attribute("agent.duration_seconds", duration)
                
            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"agent.{key}", value)
    
    def log_handoff(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log de handoff entre agentes.
        
        Args:
            from_agent: Agente de origem
            to_agent: Agente de destino
            reason: Razão do handoff
            context: Contexto adicional
        """
        if not self.is_available() or not self.configured:
            return
            
        with logfire.span(f"handoff.{from_agent}_to_{to_agent}") as span:
            span.set_attributes({
                "handoff.from_agent": from_agent,
                "handoff.to_agent": to_agent,
                "handoff.reason": reason,
                "handoff.timestamp": logfire.current_timestamp()
            })
            
            if context:
                for key, value in context.items():
                    span.set_attribute(f"handoff.context.{key}", value)
    
    def log_api_call(
        self,
        api_name: str,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        Log de chamadas para APIs externas.
        
        Args:
            api_name: Nome da API (OpenRouter, RentCast, etc.)
            endpoint: Endpoint chamado
            method: Método HTTP
            status_code: Código de status da resposta
            duration: Duração em segundos
            error: Mensagem de erro se houver
        """
        if not self.is_available() or not self.configured:
            return
            
        with logfire.span(f"api.{api_name}") as span:
            span.set_attributes({
                "api.name": api_name,
                "api.endpoint": endpoint,
                "api.method": method,
                "api.timestamp": logfire.current_timestamp()
            })
            
            if status_code:
                span.set_attribute("api.status_code", status_code)
                
            if duration:
                span.set_attribute("api.duration_seconds", duration)
                
            if error:
                span.set_attribute("api.error", error)
                span.record_exception(Exception(error))


@lru_cache()
def get_logfire_config() -> LogfireConfig:
    """Obter instância singleton da configuração Logfire."""
    return LogfireConfig()


def setup_logfire() -> bool:
    """
    Configurar Logfire para o sistema.
    
    Returns:
        bool: True se configurado com sucesso
    """
    config = get_logfire_config()
    return config.configure_logfire()


def instrument_agent_class(agent_class):
    """
    Decorador para instrumentar classes de agentes com Logfire.
    
    Args:
        agent_class: Classe do agente a ser instrumentada
        
    Returns:
        Classe instrumentada
    """
    if not LOGFIRE_AVAILABLE:
        return agent_class
        
    # Adicionar instrumentação automática
    original_init = agent_class.__init__
    
    def instrumented_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Adicionar atributos de rastreamento
        self._logfire_config = get_logfire_config()
        
    agent_class.__init__ = instrumented_init
    return agent_class


# Context managers para rastreamento
class AgentExecutionContext:
    """Context manager para rastreamento de execução de agentes."""
    
    def __init__(self, agent_name: str, action: str):
        self.agent_name = agent_name
        self.action = action
        self.config = get_logfire_config()
        self.span = None
        
    def __enter__(self):
        if self.config.is_available() and self.config.configured:
            self.span = logfire.span(f"agent.{self.agent_name}.{self.action}")
            return self.span.__enter__()
        return None
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            return self.span.__exit__(exc_type, exc_val, exc_tb)


class HandoffContext:
    """Context manager para rastreamento de handoffs."""
    
    def __init__(self, from_agent: str, to_agent: str, reason: str):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.reason = reason
        self.config = get_logfire_config()
        self.span = None
        
    def __enter__(self):
        if self.config.is_available() and self.config.configured:
            self.span = logfire.span(f"handoff.{self.from_agent}_to_{self.to_agent}")
            if self.span:
                span_instance = self.span.__enter__()
                span_instance.set_attributes({
                    "handoff.from_agent": self.from_agent,
                    "handoff.to_agent": self.to_agent,
                    "handoff.reason": self.reason
                })
                return span_instance
        return None
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            return self.span.__exit__(exc_type, exc_val, exc_tb)


# Funções utilitárias
def log_system_startup():
    """Log de inicialização do sistema."""
    if LOGFIRE_AVAILABLE:
        with logfire.span("system.startup") as span:
            settings = get_settings()
            span.set_attributes({
                "system.name": settings.app_name,
                "system.version": settings.app_version,
                "system.environment": settings.environment,
                "system.debug": settings.debug
            })


def log_system_shutdown():
    """Log de shutdown do sistema."""
    if LOGFIRE_AVAILABLE:
        with logfire.span("system.shutdown"):
            pass


def create_performance_logger():
    """Criar logger específico para métricas de performance."""
    return logging.getLogger("performance")