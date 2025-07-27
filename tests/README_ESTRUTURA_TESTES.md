# Estrutura Organizacional dos Testes

Este documento descreve a nova organização do diretório `tests/` do projeto Agentic Real Estate.

## Estrutura de Diretórios

```
tests/
├── integration/          # Testes de integração entre componentes
├── api/                 # Testes específicos da API REST
├── agents/              # Testes dos agentes individuais
├── models/              # Testes de modelos de AI/LLM
├── system/              # Testes do sistema completo (Swarm/orquestração)
├── stress/              # Testes de stress e performance
├── data/                # Testes relacionados a dados e propriedades
├── features/            # Testes de funcionalidades específicas
├── infrastructure/      # Testes de infraestrutura (logging, config, etc.)
├── external/            # Testes de integrações externas (RentCast, etc.)
├── debug/               # Scripts de debugging
├── fixes/               # Scripts de correção
├── utils/               # Utilitários e scripts auxiliares
├── frontend/            # Testes do frontend (HTML)
├── scripts/             # Scripts PowerShell e outros executáveis
└── docs/                # Documentação de testes
```

## Descrição dos Diretórios

### 🔗 integration/
Testes que verificam a interação entre diferentes componentes do sistema:
- `test_api_integration.py` - Integração da API
- `test_frontend_integration.py` - Integração do frontend
- `test_pipeline_integration.py` - Pipeline completo

### 🌐 api/
Testes específicos dos endpoints e funcionalidades da API:
- `test_api_key.py` - Validação de chaves da API
- `test_api_modes.py` - Diferentes modos da API
- `test_api_real.py` - Testes com API real
- `test_api_simulation.py` - Simulação da API

### 🤖 agents/
Testes dos agentes individuais e sua lógica:
- `test_agent.py` - Testes básicos de agentes
- `test_property_agent.py` - Agente de propriedades
- `test_scheduling.py` - Agente de agendamento
- `recreate_property.py` - Recriação de propriedades

### 🧠 models/
Testes relacionados aos modelos de linguagem:
- `test_models.py` - Testes gerais de modelos
- `test_gemma3_model.py` - Modelo Gemma3
- `test_openrouter_*.py` - Integração OpenRouter
- `find_working_models.py` - Descoberta de modelos funcionais

### ⚙️ system/
Testes do sistema completo e orquestração:
- `test_swarm*.py` - Sistema Swarm
- `test_system_*.py` - Testes de sistema
- `test_final_system.py` - Sistema final

### 🚀 stress/
Testes de performance e carga:
- `test_stress_*.py` - Testes de stress
- `demo_stress_testing.py` - Demonstração de stress
- `test_conversation_hooks.py` - Hooks de conversação

### 📊 data/
Testes relacionados aos dados e propriedades:
- `test_properties*.py` - Dados de propriedades
- `test_*mock*.py` - Dados simulados
- `test_property_context.py` - Contexto de propriedades

### ✨ features/
Testes de funcionalidades específicas:
- `test_routing.py` - Sistema de roteamento
- `test_search_filters.py` - Filtros de busca

### 🏗️ infrastructure/
Testes de infraestrutura e configuração:
- `test_logging_system.py` - Sistema de logging
- `test_config_*.py` - Configurações
- `test_datetime_fix.py` - Correções de datetime
- `test_ollama_system.py` - Sistema Ollama

### 🔌 external/
Testes de integrações externas:
- `test_rentcast*.py` - Integração RentCast
- Outros serviços externos

### 🐛 debug/
Scripts para debugging e diagnóstico:
- `debug_*.py` - Scripts de debug
- Ferramentas de diagnóstico

### 🔧 fixes/
Scripts de correção:
- `fix_*.py` - Scripts de correção
- Patches e hotfixes

### 🛠️ utils/
Utilitários e scripts auxiliares:
- `simple_test.py` - Testes simples
- `start_server.py` - Inicialização do servidor
- `hello.py` - Teste básico

### 🎨 frontend/
Testes do frontend:
- `*.html` - Arquivos de teste HTML
- Testes de interface

### 📜 scripts/
Scripts executáveis:
- `*.ps1` - Scripts PowerShell
- Scripts de automação

### 📚 docs/
Documentação:
- `README_TESTING_SYSTEM.md` - Documentação do sistema
- `run_comprehensive_tests.py` - Script principal

## Como Usar

### Executar Testes por Categoria

```powershell
# Testes de API
cd tests/api && python -m pytest

# Testes de agentes
cd tests/agents && python -m pytest

# Testes de sistema
cd tests/system && python -m pytest

# Todos os testes de integração
cd tests/integration && python -m pytest
```

### Executar Scripts Específicos

```powershell
# Scripts PowerShell
cd tests/scripts && .\run_test.ps1

# Utilitários
cd tests/utils && python simple_test.py

# Debug
cd tests/debug && python debug_system.py
```

### Executar Testes Completos

```powershell
# Script principal de testes
cd tests/docs && python run_comprehensive_tests.py
```

## Benefícios da Nova Estrutura

1. **Organização Clara**: Cada tipo de teste tem seu lugar específico
2. **Fácil Navegação**: Encontrar testes relacionados é mais intuitivo
3. **Manutenção Simplificada**: Alterações em uma área não afetam outras
4. **Execução Seletiva**: Executar apenas os testes necessários
5. **Escalabilidade**: Fácil adicionar novos tipos de testes
6. **Documentação**: Cada diretório tem sua própria documentação

## Migração

Todos os arquivos foram reorganizados automaticamente mantendo:
- ✅ Histórico de git preservado
- ✅ Funcionalidade dos testes mantida
- ✅ Referencias internas ajustadas
- ✅ Estrutura de módulos Python válida

## Próximos Passos

1. Atualizar scripts de CI/CD para usar a nova estrutura
2. Revisar imports nos testes se necessário
3. Adicionar testes específicos em suas respectivas categorias
4. Manter a documentação atualizada 