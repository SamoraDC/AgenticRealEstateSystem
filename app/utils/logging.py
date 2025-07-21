"""
Sistema de logging otimizado para o sistema agêntico.

Integrado com Logfire (PydanticAI) para observabilidade avançada.
Seguindo melhores práticas de observabilidade e estruturação de logs.
"""

import logging
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from functools import lru_cache
from pathlib import Path

# Importar configuração do Logfire
try:
    from .logfire_config import setup_logfire, get_logfire_config, log_system_startup
    LOGFIRE_INTEGRATION = True
except ImportError:
    LOGFIRE_INTEGRATION = False


class JSONFormatter(logging.Formatter):
    """Formatador JSON para logs estruturados."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatar log como JSON estruturado."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar contexto extra se disponível
        if hasattr(record, "extra") and record.extra:
            log_data.update(record.extra)
            
        # Adicionar informações de exceção
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class AgentFilter(logging.Filter):
    """Filtro para adicionar contexto de agentes aos logs."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Adicionar informações de contexto aos logs."""
        # Adicionar contexto padrão
        if not hasattr(record, "agent"):
            record.agent = "system"
        
        if not hasattr(record, "session_id"):
            record.session_id = "default"
            
        return True


def create_file_handler(
    log_file: str,
    level: str = "INFO",
    format_type: str = "json"
) -> logging.Handler:
    """
    Criar handler para arquivo de log específico.
    
    Args:
        log_file: Nome do arquivo de log
        level: Nível de log
        format_type: Tipo de formatação
        
    Returns:
        Handler configurado
    """
    # Garantir que a pasta logs existe
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    # Criar handler
    file_handler = logging.FileHandler(log_path / log_file)
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Configurar formatador
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    file_handler.setFormatter(formatter)
    file_handler.addFilter(AgentFilter())
    
    return file_handler


@lru_cache()
def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    enable_console: bool = True,
    enable_logfire: bool = True
) -> logging.Logger:
    """
    Configurar sistema de logging com melhores práticas.
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Tipo de formatação (json, text)
        enable_console: Habilitar saída no console
        enable_logfire: Habilitar integração com Logfire
    
    Returns:
        Logger configurado
    """
    # Configurar logger principal
    logger = logging.getLogger("agentic_real_estate")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Configurar Logfire se disponível
    if enable_logfire and LOGFIRE_INTEGRATION:
        try:
            setup_logfire()
            log_system_startup()
            logger.info("🔥 Logfire integração ativada")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar Logfire: {e}")
    
    # Configurar formatador
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Configurar handler para console
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(AgentFilter())
        logger.addHandler(console_handler)
    
    # Configurar handlers para arquivos específicos
    log_files = {
        "app.log": "INFO",
        "agents.log": "DEBUG", 
        "handoffs.log": "INFO",
        "performance.log": "INFO",
        "api.log": "DEBUG",
        "errors.log": "ERROR"
    }
    
    for log_file, file_level in log_files.items():
        try:
            file_handler = create_file_handler(log_file, file_level, format_type)
            logger.addHandler(file_handler)
        except (FileNotFoundError, PermissionError) as e:
            logger.warning(f"⚠️ Não foi possível criar {log_file}: {e}")
    
    logger.info("Sistema de logging configurado")
    return logger


@lru_cache()
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obter logger configurado.
    
    Args:
        name: Nome do logger (opcional)
    
    Returns:
        Logger configurado
    """
    if name:
        return logging.getLogger(f"agentic_real_estate.{name}")
    return logging.getLogger("agentic_real_estate")


def get_specialized_logger(log_type: str) -> logging.Logger:
    """
    Obter logger especializado para tipo específico.
    
    Args:
        log_type: Tipo de log (agents, handoffs, performance, api, errors)
        
    Returns:
        Logger especializado
    """
    logger = logging.getLogger(f"agentic_real_estate.{log_type}")
    
    # Configurar handler específico se não existir
    if not logger.handlers:
        log_file = f"{log_type}.log"
        try:
            file_handler = create_file_handler(log_file)
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)
        except Exception as e:
            main_logger = get_logger()
            main_logger.warning(f"⚠️ Erro ao criar logger {log_type}: {e}")
    
    return logger


def log_agent_action(
    agent_name: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    level: str = "INFO"
) -> None:
    """
    Log estruturado para ações de agentes.
    
    Args:
        agent_name: Nome do agente
        action: Ação realizada
        details: Detalhes adicionais
        level: Nível do log
    """
    logger = get_specialized_logger("agents")
    
    log_data = {
        "agent": agent_name,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    # Log também no Logfire se disponível
    if LOGFIRE_INTEGRATION:
        try:
            config = get_logfire_config()
            config.log_agent_execution(
                agent_name=agent_name,
                action=action,
                input_data=details or {},
                metadata=log_data
            )
        except Exception:
            pass  # Falhar silenciosamente
    
    getattr(logger, level.lower())(
        f"Agent {agent_name} performed {action}",
        extra=log_data
    )


def log_handoff(
    from_agent: str,
    to_agent: str,
    reason: str,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log específico para handoffs entre agentes.
    
    Args:
        from_agent: Agente de origem
        to_agent: Agente de destino
        reason: Razão do handoff
        context: Contexto adicional
    """
    logger = get_specialized_logger("handoffs")
    
    log_data = {
        "from_agent": from_agent,
        "to_agent": to_agent,
        "handoff_reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        log_data["context"] = context
    
    # Log também no Logfire se disponível
    if LOGFIRE_INTEGRATION:
        try:
            config = get_logfire_config()
            config.log_handoff(from_agent, to_agent, reason, context)
        except Exception:
            pass  # Falhar silenciosamente
    
    logger.info(
        f"Handoff: {from_agent} -> {to_agent} ({reason})",
        extra=log_data
    )


def log_performance(
    operation: str,
    duration: float,
    agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log de performance para operações.
    
    Args:
        operation: Nome da operação
        duration: Duração em segundos
        agent: Nome do agente (opcional)
        details: Detalhes adicionais
    """
    logger = get_specialized_logger("performance")
    
    log_data = {
        "operation": operation,
        "duration_seconds": duration,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if agent:
        log_data["agent"] = agent
    
    if details:
        log_data.update(details)
    
    # Log como warning se duração for alta
    level = "warning" if duration > 5.0 else "info"
    
    getattr(logger, level)(
        f"Operation {operation} completed in {duration:.2f}s",
        extra=log_data
    )


def log_api_call(
    api_name: str,
    endpoint: str,
    method: str,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    error: Optional[str] = None
) -> None:
    """
    Log de chamadas para APIs externas.
    
    Args:
        api_name: Nome da API
        endpoint: Endpoint chamado
        method: Método HTTP
        status_code: Código de status
        duration: Duração em segundos
        error: Mensagem de erro
    """
    logger = get_specialized_logger("api")
    
    log_data = {
        "api_name": api_name,
        "endpoint": endpoint,
        "method": method,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if status_code:
        log_data["status_code"] = status_code
    
    if duration:
        log_data["duration_seconds"] = duration
    
    if error:
        log_data["error"] = error
    
    # Log também no Logfire se disponível
    if LOGFIRE_INTEGRATION:
        try:
            config = get_logfire_config()
            config.log_api_call(api_name, endpoint, method, status_code, duration, error)
        except Exception:
            pass  # Falhar silenciosamente
    
    level = "error" if error else "info"
    message = f"API {api_name} {method} {endpoint}"
    if status_code:
        message += f" -> {status_code}"
    if error:
        message += f" ERROR: {error}"
    
    getattr(logger, level)(message, extra=log_data)


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    agent: Optional[str] = None
) -> None:
    """
    Log estruturado de erros.
    
    Args:
        error: Exceção ocorrida
        context: Contexto adicional
        agent: Nome do agente (se aplicável)
    """
    logger = get_specialized_logger("errors")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        log_data["context"] = context
    
    if agent:
        log_data["agent"] = agent
    
    logger.error(
        f"Error: {type(error).__name__}: {error}",
        extra=log_data,
        exc_info=True
    ) 