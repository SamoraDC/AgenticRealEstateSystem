# Configuração do Logfire - Sistema Agêntico

## Visão Geral

O **Logfire** é a plataforma de observabilidade nativa do PydanticAI, desenvolvida pela mesma equipe. Oferece rastreamento completo de agentes, métricas de performance e debugging avançado.

## Instalação

### 1. Instalar PydanticAI com Logfire

```bash
uv add "pydantic-ai[logfire]"
```

### 2. Instalar CLI do Logfire

```bash
uv run pip install logfire
```

## Configuração

### 1. Autenticação

```bash
# Autenticar com Logfire
uv run logfire auth

# Seguir instruções no navegador para login
```

### 2. Criar/Configurar Projeto

```bash
# Criar novo projeto
uv run logfire projects new

# OU usar projeto existente
uv run logfire projects use <project-name>
```

Isso criará um diretório `.logfire/` com as configurações.

### 3. Configurar Token (Opcional)

Adicione ao `.env`:

```env
LOGFIRE_TOKEN=your_logfire_token_here
```

## Funcionalidades Implementadas

### 1. Instrumentação Automática

- **PydanticAI**: Rastreamento de agentes automaticamente
- **HTTPX**: Monitoramento de chamadas API (OpenRouter, RentCast)
- **FastAPI**: Middleware para todas as requisições

### 2. Logs Estruturados

#### Agentes
```python
log_agent_action(
    agent_name="search_agent",
    action="property_search",
    details={"properties_found": 15, "duration": 2.3}
)
```

#### Handoffs
```python
log_handoff(
    from_agent="search_agent",
    to_agent="property_agent",
    reason="user_wants_details"
)
```

#### Performance
```python
log_performance(
    operation="swarm_processing",
    duration=1.5,
    agent="search_agent"
)
```

#### API Calls
```python
log_api_call(
    api_name="OpenRouter",
    endpoint="/chat/completions",
    method="POST",
    status_code=200,
    duration=0.8
)
```

### 3. Context Managers

#### Execução de Agentes
```python
with AgentExecutionContext("search_agent", "search_properties") as span:
    # Código do agente
    result = await agent.run(prompt)
```

#### Handoffs
```python
with HandoffContext("agent_a", "agent_b", "user_request") as span:
    # Lógica de handoff
    pass
```

## Dashboard Logfire

### 1. Acessar Dashboard

- URL: https://logfire.pydantic.dev
- Login com conta configurada

### 2. Visualizações Disponíveis

#### Traces de Agentes
- Fluxo completo de execução
- Tempo de resposta por agente
- Handoffs entre agentes
- Erros e exceções

#### Métricas de API
- Chamadas OpenRouter/RentCast
- Latência e throughput
- Taxa de erro
- Uso de tokens

#### Performance
- Operações mais lentas
- Gargalos do sistema
- Tendências de performance

### 3. Queries Úteis

#### Agentes Mais Usados
```sql
SELECT agent_name, COUNT(*) as executions
FROM traces 
WHERE span_name LIKE 'agent.%'
GROUP BY agent_name
ORDER BY executions DESC
```

#### APIs com Maior Latência
```sql
SELECT api_name, AVG(duration_seconds) as avg_duration
FROM traces
WHERE span_name LIKE 'api.%'
GROUP BY api_name
ORDER BY avg_duration DESC
```

#### Erros por Agente
```sql
SELECT agent_name, COUNT(*) as errors
FROM traces
WHERE status = 'error'
GROUP BY agent_name
ORDER BY errors DESC
```

## Modo Local (Desenvolvimento)

### Configuração Sem Token

O sistema funciona em modo local mesmo sem token Logfire:

```python
# Em logfire_config.py
logfire.configure(
    send_to_logfire=False,  # Apenas logs locais
    service_name="agentic-real-estate",
    environment="development"
)
```

### Visualização Local

#### 1. otel-tui (Terminal UI)

```bash
# Instalar otel-tui
docker run --rm -it -p 4318:4318 ymtdzzz/otel-tui:latest

# Configurar endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

#### 2. Jaeger (Web UI)

```bash
# Executar Jaeger
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14268:14268 \
  jaegertracing/all-in-one:latest

# Acessar: http://localhost:16686
```

## Estrutura de Dados

### Spans Principais

- `system.startup` - Inicialização do sistema
- `agent.{name}.{action}` - Execução de agentes
- `handoff.{from}_to_{to}` - Transferências entre agentes
- `api.{provider}` - Chamadas para APIs externas
- `swarm_orchestrator.process_message` - Processamento de mensagens

### Atributos Padrão

- `agent.name` - Nome do agente
- `agent.action` - Ação executada
- `agent.duration_seconds` - Duração da execução
- `api.endpoint` - Endpoint da API
- `api.status_code` - Código de status HTTP
- `handoff.reason` - Razão do handoff

## Troubleshooting

### 1. Logfire Não Disponível

```
⚠️ Logfire não disponível - install com: uv add 'pydantic-ai[logfire]'
```

**Solução**: Instalar dependências corretas

### 2. Token Não Configurado

```
🔥 Logfire token não configurado - usando modo local
```

**Solução**: Executar `uv run logfire auth` ou configurar `LOGFIRE_TOKEN`

### 3. Erro de Conectividade

```
❌ Erro ao configurar Logfire: Connection error
```

**Solução**: Verificar conexão de rede ou usar modo local

### 4. Logs Não Aparecem

1. Verificar se instrumentação está ativada
2. Confirmar que token está correto
3. Checar se projeto existe no Logfire

## Teste do Sistema

Execute o teste completo:

```bash
uv run python test_logging_system.py
```

### Saída Esperada

```
🚀 Iniciando testes do sistema de logging...
🧪 Testando logging básico...
✅ Logging básico funcionando
🧪 Testando loggers especializados...
✅ Loggers especializados funcionando
🧪 Testando logging estruturado...
✅ Logging estruturado funcionando
🧪 Testando integração Logfire...
🔥 Logfire disponível: True
🔥 Logfire configurado: True
✅ Integração Logfire funcionando
🎉 Testes do sistema de logging concluídos!
```

## Benefícios

### 1. Debugging Avançado
- Rastreamento completo de execuções
- Identificação rápida de problemas
- Contexto detalhado de erros

### 2. Monitoramento de Performance
- Métricas em tempo real
- Alertas de latência
- Otimização baseada em dados

### 3. Análise de Uso
- Agentes mais utilizados
- Padrões de handoff
- Eficiência do sistema

### 4. Observabilidade Completa
- Logs estruturados
- Traces distribuídos
- Métricas de negócio

## Próximos Passos

1. **Configurar Alertas**: Definir alertas para erros e latência alta
2. **Dashboards Customizados**: Criar visualizações específicas do negócio
3. **Análise de Custos**: Monitorar uso de tokens e APIs
4. **Otimização**: Usar dados para melhorar performance

## Recursos Adicionais

- [Documentação Logfire](https://logfire.pydantic.dev/docs/)
- [PydanticAI + Logfire](https://ai.pydantic.dev/logfire/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Exemplos Práticos](https://github.com/pydantic/logfire-examples)