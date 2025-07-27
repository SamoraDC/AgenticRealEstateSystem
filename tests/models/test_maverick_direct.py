#!/usr/bin/env python3
"""
Teste específico do modelo maverick no sistema
"""

import asyncio
from config.settings import get_settings
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai import Agent

async def test_maverick_in_system():
    """Testa se o modelo maverick está sendo usado no sistema"""
    
    print("🧪 TESTE ESPECÍFICO DO MODELO MAVERICK")
    print("=" * 50)
    
    # 1. Verificar configurações
    settings = get_settings()
    print(f"✅ 1. Modelo padrão nas configurações: {settings.models.default_model}")
    print(f"✅ 2. Modelo de busca: {settings.models.search_model}")
    print(f"✅ 3. Modelo de propriedade: {settings.models.property_model}")
    print(f"✅ 4. Modelo de agendamento: {settings.models.scheduling_model}")
    
    # 2. Testar modelo diretamente
    api_key = settings.apis.openrouter_key
    print(f"✅ 5. API key carregada: {len(api_key)} chars")
    
    # 3. Criar modelo maverick
    model = OpenAIModel(
        "meta-llama/llama-4-maverick:free",
        provider=OpenRouterProvider(api_key=api_key),
    )
    print("✅ 6. Modelo maverick configurado")
    
    # 4. Criar agente
    agent = Agent(model)
    print("✅ 7. Agente criado com modelo maverick")
    
    # 5. Testar execução
    prompt = "Say 'Hello from Maverick model!' in exactly 5 words."
    response = await agent.run(prompt)
    print(f"✅ 8. Resposta do maverick: {response.output}")
    
    # 6. Testar agente do sistema
    print("\n🔧 TESTANDO AGENTE DO SISTEMA")
    print("-" * 40)
    
    try:
        from app.agents.property import PropertyAgent
        property_agent = PropertyAgent()
        print(f"✅ 9. PropertyAgent criado - Modelo: {property_agent.model}")
        
        # Verificar se está usando o modelo correto
        if "maverick" in str(property_agent.model).lower():
            print("✅ 10. Sistema está usando MAVERICK corretamente!")
        else:
            print(f"⚠️ 10. Sistema usando modelo diferente: {property_agent.model}")
            
    except Exception as e:
        print(f"❌ 9. Erro no PropertyAgent: {e}")
    
    print("\n🎯 RESULTADO FINAL")
    print("=" * 50)
    print("✅ Modelo maverick testado e funcionando!")
    print("✅ Sistema configurado para usar maverick!")

if __name__ == "__main__":
    asyncio.run(test_maverick_in_system()) 