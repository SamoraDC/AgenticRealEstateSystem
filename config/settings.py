"""
Configurações centrais do sistema agêntico.

Seguindo melhores práticas de configuração hierárquica e tipagem forte.
"""

import os
from functools import lru_cache
from typing import Dict, Any, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseConfig(BaseSettings):
    """Configurações de banco de dados."""
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras que não pertencem a este modelo
    )
    
    url: str = Field(default="sqlite:///./real_estate.db")
    echo: bool = Field(default=False)
    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)


class RedisConfig(BaseSettings):
    """Configurações do Redis."""
    
    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    url: str = Field(default="redis://localhost:6379/0")
    password: Optional[str] = None
    max_connections: int = Field(default=10)


class ModelConfig(BaseSettings):
    """Configurações de modelos LLM."""
    
    model_config = SettingsConfigDict(
        env_prefix="LLM_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    # Configurações globais
    provider: str = Field(default="openrouter")
    default_model: str = Field(default="meta-llama/llama-4-maverick:free")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)
    
    # Configurações por agente
    search_model: str = Field(default="meta-llama/llama-4-maverick:free")
    property_model: str = Field(default="meta-llama/llama-4-maverick:free")
    scheduling_model: str = Field(default="meta-llama/llama-4-maverick:free")


class APIConfig(BaseSettings):
    """Configurações de APIs externas."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    # OpenRouter
    openrouter_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_url: str = Field(default="https://openrouter.ai/api/v1")
    
    # RentCast API - Configuração principal
    rentcast_api_key: str = Field(
        default="01e1101b77c54f1b8e804ba212a4ccfc",
        description="Chave da API RentCast"
    )
    rentcast_base_url: str = Field(
        default="https://api.rentcast.io/v1",
        description="URL base da API RentCast"
    )
    
    # Google Calendar
    google_credentials_path: str = Field(default="credentials.json")
    google_token_path: str = Field(default="token.json")
    google_calendar_credentials: Optional[str] = Field(
        default=None,
        description="Credenciais do Google Calendar (JSON)"
    )
    
    # Outras APIs de imóveis
    freewebapi_key: Optional[str] = Field(default=None, alias="FREEWEBAPI_KEY")
    
    # Rate limiting
    max_requests_per_minute: int = Field(default=60, description="Máximo de requests por minuto")
    request_timeout: int = Field(default=30, description="Timeout de requests em segundos")


class SecurityConfig(BaseSettings):
    """Configurações de segurança."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    token_expire_minutes: int = Field(default=30)
    rate_limit_requests: int = Field(default=100)
    rate_limit_window: int = Field(default=60)


class ObservabilityConfig(BaseSettings):
    """Configurações de observabilidade."""
    
    model_config = SettingsConfigDict(
        env_prefix="OBS_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    # Metrics
    metrics_enabled: bool = Field(default=True)
    metrics_port: int = Field(default=8090)
    
    # Tracing
    tracing_enabled: bool = Field(default=True)
    jaeger_endpoint: Optional[str] = None
    
    # Logfire
    logfire_token: Optional[str] = Field(default=None, alias="LOGFIRE_TOKEN")


class ResilienceConfig(BaseSettings):
    """Configurações de resiliência."""
    
    model_config = SettingsConfigDict(
        env_prefix="RESILIENCE_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    # Circuit Breaker
    circuit_enabled: bool = Field(default=True)
    failure_threshold: int = Field(default=5)
    recovery_timeout: int = Field(default=60)
    
    # Retry
    max_retries: int = Field(default=3)
    retry_delay: float = Field(default=1.0)
    retry_backoff: float = Field(default=2.0)
    
    # Timeout
    default_timeout: float = Field(default=30.0)


class SwarmConfig(BaseSettings):
    """Configurações específicas do Swarm."""
    
    model_config = SettingsConfigDict(
        env_prefix="SWARM_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignorar variáveis extras
    )
    
    # Handoff
    handoff_timeout: float = Field(default=5.0)
    max_handoffs: int = Field(default=10)
    
    # Context
    context_window: int = Field(default=4000)
    context_overlap: int = Field(default=200)
    
    # Agent-specific
    agents: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "search": {
                "model": "meta-llama/llama-4-maverick:free",
                "temperature": 0.1,
                "max_tokens": 2000,
                "priority": 1
            },
            "property": {
                "model": "meta-llama/llama-4-maverick:free", 
                "temperature": 0.2,
                "max_tokens": 3000,
                "priority": 2
            },
            "scheduling": {
                "model": "meta-llama/llama-4-maverick:free",
                "temperature": 0.1,
                "max_tokens": 1500,
                "priority": 3
            }
        }
    )


class Settings(BaseSettings):
    """Configurações principais do sistema."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Meta
    app_name: str = Field(default="Agentic Real Estate")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # Sub-configurações
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    models: ModelConfig = Field(default_factory=ModelConfig)
    apis: APIConfig = Field(default_factory=APIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    resilience: ResilienceConfig = Field(default_factory=ResilienceConfig)
    swarm: SwarmConfig = Field(default_factory=SwarmConfig)
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings() 