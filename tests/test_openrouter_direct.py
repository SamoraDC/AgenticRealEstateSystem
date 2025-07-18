#!/usr/bin/env python3
"""
Teste direto da API OpenRouter para diagnosticar problemas.
"""

import asyncio
import httpx
import os
from config.settings import get_settings

async def test_openrouter_direct():
    """Testar chamada direta ao OpenRouter."""
    
    # Carregar configurações
    settings = get_settings()
    api_key = settings.apis.openrouter_key
    
    print(f"🔑 API Key loaded: {bool(api_key)}")
    print(f"🔑 Key starts with: {api_key[:15]}..." if api_key else "No key")
    print(f"🔑 Key length: {len(api_key)}" if api_key else "No key")
    
    if not api_key or api_key.strip() == "":
        print("❌ No API key found!")
        return
    
    # Teste de chamada direta
    try:
        async with httpx.AsyncClient() as client:
            print("\n🧪 Testing direct OpenRouter API call...")
            
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-4-maverick:free",
                    "messages": [{"role": "user", "content": "Hello, respond with just 'API working!'"}],
                    "temperature": 0.1,
                    "max_tokens": 50
                },
                timeout=30.0
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"✅ API Response: {content}")
                print("✅ OpenRouter API is working correctly!")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception during API call: {e}")
        return False

async def test_pydantic_ai():
    """Testar PydanticAI com OpenRouter."""
    
    try:
        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openrouter import OpenRouterProvider
        
        settings = get_settings()
        api_key = settings.apis.openrouter_key
        
        print("\n🤖 Testing PydanticAI with OpenRouter...")
        
        model = OpenAIModel(
            "meta-llama/llama-4-maverick:free",
            provider=OpenRouterProvider(api_key=api_key),
        )
        agent = Agent(model)
        
        response = await agent.run("Say 'PydanticAI working!' and nothing else.")
        content = str(response.data)
        
        print(f"✅ PydanticAI Response: {content}")
        print("✅ PydanticAI is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ PydanticAI Error: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

async def main():
    """Executar todos os testes."""
    print("🔍 OpenRouter API Diagnostic Test")
    print("=" * 50)
    
    # Teste 1: Configuração
    print("\n1️⃣ Testing configuration...")
    settings = get_settings()
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")
    
    # Teste 2: API direta
    print("\n2️⃣ Testing direct API...")
    api_works = await test_openrouter_direct()
    
    # Teste 3: PydanticAI
    print("\n3️⃣ Testing PydanticAI...")
    pydantic_works = await test_pydantic_ai()
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY:")
    print(f"   Direct API: {'✅ Working' if api_works else '❌ Failed'}")
    print(f"   PydanticAI: {'✅ Working' if pydantic_works else '❌ Failed'}")
    
    if api_works and pydantic_works:
        print("\n🎉 All tests passed! OpenRouter should work in the system.")
    else:
        print("\n⚠️ Some tests failed. This explains the fallback behavior.")

if __name__ == "__main__":
    asyncio.run(main()) 