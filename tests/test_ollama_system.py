#!/usr/bin/env python3
"""
Teste do Sistema Ollama para Fallback Inteligente
"""

import asyncio
import httpx
from app.utils.ollama_fallback import get_ollama_fallback, generate_intelligent_fallback

async def test_ollama_availability():
    """Testar se Ollama está disponível."""
    
    print("🔍 Testing Ollama Availability")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            print("📡 Checking if Ollama is running...")
            response = await client.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]
                
                print(f"✅ Ollama is running!")
                print(f"📦 Available models: {len(models)}")
                
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    print(f"   • {name} ({size // 1024 // 1024} MB)")
                
                # Verificar se gemma3n:e2b está disponível
                if "gemma3n:e2b" in model_names:
                    print(f"✅ Target model 'gemma3n:e2b' is available!")
                    return True, True
                else:
                    print(f"⚠️ Target model 'gemma3n:e2b' not found")
                    return True, False
                    
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return False, False
                
    except Exception as e:
        print(f"❌ Ollama not available: {e}")
        print("💡 Make sure Ollama is installed and running:")
        print("   • Install: https://ollama.ai/")
        print("   • Start: ollama serve")
        return False, False

async def test_model_pull():
    """Testar pull do modelo gemma3n:e2b."""
    
    print("\n🔄 Testing Model Pull")
    print("=" * 50)
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            print("📥 Attempting to pull model 'gemma3n:e2b'...")
            print("⏳ This may take a few minutes for first-time download...")
            
            response = await client.post(
                "http://localhost:11434/api/pull",
                json={"name": "gemma3n:e2b"},
                timeout=300.0
            )
            
            if response.status_code == 200:
                print("✅ Model pull successful!")
                return True
            else:
                print(f"❌ Model pull failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during model pull: {e}")
        return False

async def test_ollama_generation():
    """Testar geração de resposta com Ollama."""
    
    print("\n🧪 Testing Ollama Generation")
    print("=" * 50)
    
    try:
        ollama = get_ollama_fallback()
        
        # Teste 1: Search Agent
        print("🔍 Testing search agent response...")
        search_response = await ollama.generate_response(
            "search_agent",
            "I'm looking for a 2-bedroom apartment in Miami",
            {},
            "mock"
        )
        print(f"✅ Search response ({len(search_response)} chars):")
        print(f"📝 Preview: {search_response[:150]}...")
        
        # Teste 2: Property Agent
        print("\n🏠 Testing property agent response...")
        property_context = {
            "formattedAddress": "467 Nw 8th St, Apt 3, Miami, FL 33136",
            "price": 1450,
            "bedrooms": 0,
            "bathrooms": 1,
            "squareFootage": 502,
            "propertyType": "Apartment",
            "yearBuilt": 1950
        }
        
        property_response = await ollama.generate_response(
            "property_agent",
            "How much is the rent for this property?",
            property_context,
            "mock"
        )
        print(f"✅ Property response ({len(property_response)} chars):")
        print(f"📝 Preview: {property_response[:150]}...")
        
        # Teste 3: Scheduling Agent
        print("\n📅 Testing scheduling agent response...")
        scheduling_response = await ollama.generate_response(
            "scheduling_agent",
            "I'd like to schedule a visit to this property",
            property_context,
            "mock"
        )
        print(f"✅ Scheduling response ({len(scheduling_response)} chars):")
        print(f"📝 Preview: {scheduling_response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama generation failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

async def test_fallback_function():
    """Testar função principal de fallback."""
    
    print("\n🎯 Testing Main Fallback Function")
    print("=" * 50)
    
    try:
        response = await generate_intelligent_fallback(
            "property_agent",
            "Tell me about this property",
            {
                "formattedAddress": "Test Property, Miami, FL",
                "price": 2000,
                "bedrooms": 2,
                "bathrooms": 2
            },
            "mock"
        )
        
        print(f"✅ Fallback function successful ({len(response)} chars):")
        print(f"📝 Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Fallback function failed: {e}")
        return False

async def main():
    """Executar todos os testes."""
    
    print("🚀 Ollama Fallback System Test")
    print("=" * 70)
    
    # Teste 1: Verificar disponibilidade
    ollama_running, model_available = await test_ollama_availability()
    
    # Teste 2: Pull do modelo se necessário
    if ollama_running and not model_available:
        model_pulled = await test_model_pull()
        if not model_pulled:
            print("\n❌ Cannot proceed without model. Please install manually:")
            print("   ollama pull gemma3n:e2b")
            return
    elif not ollama_running:
        print("\n❌ Cannot proceed without Ollama running.")
        return
    
    # Teste 3: Geração de respostas
    generation_success = await test_ollama_generation()
    
    # Teste 4: Função principal
    fallback_success = await test_fallback_function()
    
    # Resumo final
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY:")
    print(f"   Ollama Running: {'✅' if ollama_running else '❌'}")
    print(f"   Model Available: {'✅' if model_available else '❌'}")
    print(f"   Generation: {'✅' if generation_success else '❌'}")
    print(f"   Fallback Function: {'✅' if fallback_success else '❌'}")
    
    if all([ollama_running, generation_success, fallback_success]):
        print("\n🎉 All tests passed! Ollama fallback system is ready!")
        print("💡 The system will now use Ollama when OpenRouter fails.")
    else:
        print("\n⚠️ Some tests failed. Please check Ollama installation.")

if __name__ == "__main__":
    asyncio.run(main()) 