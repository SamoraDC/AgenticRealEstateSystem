#!/usr/bin/env python3
"""
Teste de diferentes modelos OpenRouter para identificar qual funciona
"""

import asyncio
from config.settings import get_settings
from app.utils.logging import get_logger

# Modelos para testar
MODELS_TO_TEST = [
    "meta-llama/llama-4-scout:free",
    "meta-llama/llama-4-maverick:free", 
    "mistralai/mistral-small-3.2-24b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "openai/gpt-4o-mini"  # Controle - sabemos que funciona
]

async def test_model(model_name: str):
    """Testa um modelo específico"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO: {model_name}")
    print(f"{'='*60}")
    
    settings = get_settings()
    
    try:
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openrouter import OpenRouterProvider
        from pydantic_ai import Agent
        
        print("✅ 1. Imports PydanticAI successful")
        
        # Configurar modelo
        api_key = settings.apis.openrouter_key
        print(f"✅ 2. API key loaded: {len(api_key)} chars")
        
        model = OpenAIModel(
            model_name,
            provider=OpenRouterProvider(api_key=api_key),
        )
        print(f"✅ 3. Model configured: {model_name}")
        
        # Criar agente
        agent = Agent(model)
        print("✅ 4. Agent created successfully")
        
        # Testar execução simples
        prompt = "Say hello in exactly 10 words."
        print("⏳ 5. Testing simple execution...")
        
        response = await agent.run(prompt)
        print(f"✅ 6. Response received: {response.data}")
        print(f"✅ 7. Response type: {type(response.data)}")
        print(f"✅ 8. SUCCESS - {model_name} works perfectly!")
        
        return True, response.data
        
    except Exception as e:
        print(f"❌ ERROR with {model_name}: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        
        # Detalhes específicos do erro
        if "datetime" in str(e):
            print("❌ DATETIME VALIDATION ERROR - Model response format issue")
        elif "validation" in str(e):
            print("❌ PYDANTIC VALIDATION ERROR - Response structure issue")
        elif "timeout" in str(e).lower():
            print("❌ TIMEOUT ERROR - Model too slow or unavailable")
        elif "rate" in str(e).lower():
            print("❌ RATE LIMIT ERROR - Too many requests")
        elif "auth" in str(e).lower():
            print("❌ AUTHENTICATION ERROR - API key issue")
        else:
            print(f"❌ UNKNOWN ERROR: {str(e)[:200]}")
        
        return False, str(e)

async def test_all_models():
    """Testa todos os modelos"""
    print("🚀 INICIANDO TESTE DE MODELOS OPENROUTER")
    print("=" * 80)
    
    results = {}
    working_models = []
    broken_models = []
    
    for model in MODELS_TO_TEST:
        success, result = await test_model(model)
        results[model] = (success, result)
        
        if success:
            working_models.append(model)
        else:
            broken_models.append(model)
        
        # Pausa entre testes para evitar rate limit
        await asyncio.sleep(2)
    
    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL")
    print("="*80)
    
    print(f"\n✅ MODELOS QUE FUNCIONAM ({len(working_models)}):")
    for model in working_models:
        print(f"   • {model}")
    
    print(f"\n❌ MODELOS COM PROBLEMAS ({len(broken_models)}):")
    for model in broken_models:
        error = results[model][1]
        print(f"   • {model}")
        print(f"     Erro: {error[:100]}...")
    
    print(f"\n🎯 RECOMENDAÇÃO:")
    if working_models:
        best_model = working_models[0]
        print(f"   Use: {best_model}")
        print(f"   Este modelo foi testado e funciona perfeitamente!")
    else:
        print("   ⚠️ Nenhum modelo funcionou - verifique API key ou conectividade")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_all_models()) 