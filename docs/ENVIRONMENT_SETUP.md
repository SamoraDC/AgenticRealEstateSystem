# Configuração de Ambiente - Sistema Agêntico Imobiliário

## 🚀 Configuração Rápida

### 1. Instalar Dependências
```bash
pip install poetry
poetry install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```bash
# =============================================================================
# OPENROUTER (MODELO PRINCIPAL) - OBRIGATÓRIO
# =============================================================================
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# =============================================================================
# BANCOS DE DADOS (DESENVOLVIMENTO)
# =============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_real_estate
REDIS_URL=redis://localhost:6379/0

# =============================================================================
# GOOGLE CALENDAR (PARA AGENDAMENTOS)
# =============================================================================
GOOGLE_CALENDAR_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=./google_token.json

# =============================================================================
# OBSERVABILIDADE (OPCIONAL MAS RECOMENDADO)
# =============================================================================
LANGFUSE_SECRET_KEY=sk-lf-your-langfuse-secret-key
LANGFUSE_PUBLIC_KEY=pk-lf-your-langfuse-public-key
LANGFUSE_HOST=https://cloud.langfuse.com

# =============================================================================
# APIS DE IMÓVEIS (MCP)
# =============================================================================
RENTCAST_API_KEY=your-rentcast-api-key
FREEWEBAPI_KEY=your-freewebapi-key

# =============================================================================
# CONFIGURAÇÕES BÁSICAS
# =============================================================================
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-super-secret-key
DEFAULT_TIMEZONE=America/Sao_Paulo
```

## 🔑 Como Obter as Chaves de API

### OpenRouter (OBRIGATÓRIO)
1. Acesse [OpenRouter.ai](https://openrouter.ai)
2. Crie uma conta gratuita
3. Vá em "API Keys" 
4. Crie uma nova chave
5. Use o modelo **meta-llama/llama-4-scout:free** (gratuito!)

### Google Calendar (PARA AGENDAMENTOS)
1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto novo
3. Ative a API Google Calendar
4. Crie credenciais (Service Account)
5. Baixe o arquivo JSON como `google_credentials.json`

### RentCast API (PARA DADOS DE IMÓVEIS)
1. Acesse [RentCast.io](https://rentcast.io)
2. Registre-se para conta gratuita (5.000 calls/dia)
3. Copie sua API key

### LangFuse (OBSERVABILIDADE)
1. Acesse [LangFuse Cloud](https://cloud.langfuse.com)
2. Crie conta gratuita
3. Crie um projeto
4. Copie as chaves pública e privada

## 🏗️ Arquitetura dos Agentes

### 1. SearchAgent 
- **Modelo**: meta-llama/llama-4-scout:free via OpenRouter
- **Padrão**: ReAct (Reasoning + Acting)
- **Função**: Interpretar consultas e buscar imóveis

### 2. PropertyResponseAgent (NOVO!)
- **Modelo**: meta-llama/llama-4-scout:free via OpenRouter  
- **Padrão**: ReAct (Reasoning + Acting)
- **Função**: Analisar propriedades, comparações, descrições personalizadas

### 3. SchedulingAgent
- **Modelo**: meta-llama/llama-4-scout:free via OpenRouter
- **Padrão**: ReAct (Reasoning + Acting)
- **Função**: Agendamentos via Google Calendar

### 4. SupervisorAgent
- **Modelo**: meta-llama/llama-4-scout:free via OpenRouter
- **Padrão**: Chain-of-Drafts
- **Função**: Controle de qualidade e coordenação

## 🔄 Fluxo de Transferências (Handoffs)

```mermaid
graph TD
    A[User Query] --> B[SearchAgent]
    B --> |"Detalhes sobre imóvel"| C[PropertyResponseAgent]
    B --> |"Agendar visita"| D[SchedulingAgent]
    C --> |"Agendar visita"| D
    C --> |"Buscar similares"| B
    B --> |"Validação"| E[SupervisorAgent]
    C --> |"Validação"| E
    D --> |"Validação"| E
    E --> |"Novo requisito"| B
    E --> |"Análise específica"| C
    E --> |"Reagendamento"| D
```

## 🧪 Testar o Sistema

```bash
# Executar demo básico
python -m agentic_real_estate.examples.swarm_demo

# Testar agente específico
python -c "
from agentic_real_estate.agents import PropertyResponseAgent
from agentic_real_estate.core.config import Settings

settings = Settings()
agent = PropertyResponseAgent(settings)
print('PropertyResponseAgent configurado com sucesso!')
"
```

## 🐛 Troubleshooting

### Erro: "OPENROUTER_API_KEY not found"
- Verifique se criou o arquivo `.env`
- Confirme que a chave está correta
- Teste a chave em [OpenRouter.ai](https://openrouter.ai)

### Erro: "Model not found"
- Confirme que está usando `meta-llama/llama-4-scout:free`
- Verifique se sua conta OpenRouter está ativa

### Erro: "Google Calendar authentication failed"
- Verifique se o arquivo `google_credentials.json` existe
- Confirme que a API Google Calendar está ativada
- Execute o processo de autenticação inicial

### Performance Issues
- Verifique sua conexão com OpenRouter
- Monitor usage em [OpenRouter dashboard](https://openrouter.ai/usage)
- Use LangFuse para debug detalhado

## 🚀 Próximos Passos

1. Configure o ambiente mínimo (OpenRouter + variáveis básicas)
2. Execute o swarm_demo para testar
3. Configure Google Calendar para agendamentos
4. Adicione observabilidade com LangFuse
5. Configure APIs de imóveis para dados reais

## 📋 Checklist de Configuração

- [ ] OpenRouter API Key configurada
- [ ] Arquivo .env criado
- [ ] Dependências instaladas
- [ ] Demo executando sem erros
- [ ] Google Calendar configurado (opcional)
- [ ] LangFuse configurado (opcional)
- [ ] APIs de imóveis configuradas (opcional)

**Pronto!** Seu sistema agêntico imobiliário está configurado com **4 agentes colaborativos** usando **meta-llama/llama-4-scout:free** via **OpenRouter**! 🎉 