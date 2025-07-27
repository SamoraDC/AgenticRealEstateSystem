#!/usr/bin/env python3
"""
Teste final do sistema agêntico com dados mock e real
"""

import asyncio
import requests
import json
import time

def test_api_health():
    """Testa se o API está funcionando"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ API Health: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False

def test_agentic_session_with_data_mode(data_mode: str):
    """Testa sessão agêntica com modo de dados específico"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTANDO SISTEMA AGÊNTICO COM DADOS {data_mode.upper()}")
    print(f"{'='*60}")
    
    try:
        # 1. Criar sessão
        print(f"⏳ 1. Criando sessão agêntica com dados {data_mode}...")
        session_data = {
            "property_id": "1",
            "agent_mode": "details",
            "user_preferences": {"name": "Test User"},
            "language": "en"
        }
        
        session_response = requests.post(
            f"http://localhost:8000/api/agent/session/start?mode={data_mode}",
            json=session_data,
            timeout=10
        )
        
        print(f"   Status: {session_response.status_code}")
        session_result = session_response.json()
        print(f"   Response: {json.dumps(session_result, indent=2)}")
        
        if not session_result.get('success'):
            print(f"❌ Falha ao criar sessão: {session_result.get('message')}")
            return False
            
        session_id = session_result['data']['session']['session_id']
        print(f"✅ 1. Sessão criada: {session_id}")
        
        # 2. Enviar mensagem
        print(f"⏳ 2. Enviando mensagem para agente...")
        message_data = {
            "message": "hello, tell me about this property",
            "session_id": session_id
        }
        
        message_response = requests.post(
            f"http://localhost:8000/api/agent/chat?mode={data_mode}",
            json=message_data,
            timeout=30
        )
        
        print(f"   Status: {message_response.status_code}")
        message_result = message_response.json()
        print(f"   Response: {json.dumps(message_result, indent=2)}")
        
        if not message_result.get('success'):
            print(f"❌ Falha ao enviar mensagem: {message_result.get('message')}")
            return False
            
        agent_response = message_result['data']
        print(f"✅ 2. Resposta do agente recebida:")
        print(f"   Agente: {agent_response.get('agent_name')}")
        print(f"   Mensagem: {agent_response.get('message')[:100]}...")
        print(f"   Confiança: {agent_response.get('confidence')}")
        
        # 3. Verificar se é resposta real do agente
        message_content = agent_response.get('message', '')
        agent_name = agent_response.get('agent_name', '')
        
        # Verificar se não são respostas automáticas/mock
        is_real_agent = (
            'Emma' in agent_name and 
            len(message_content) > 50 and
            agent_response.get('confidence', 0) > 0.5
        )
        
        if is_real_agent:
            print(f"✅ 3. SISTEMA AGÊNTICO FUNCIONANDO com dados {data_mode.upper()}!")
            print(f"   ✓ Agente real: {agent_name}")
            print(f"   ✓ Resposta personalizada: {len(message_content)} chars")
            print(f"   ✓ Confiança alta: {agent_response.get('confidence')}")
        else:
            print(f"❌ 3. Sistema usando respostas automáticas:")
            print(f"   - Agente: {agent_name}")
            print(f"   - Confiança: {agent_response.get('confidence')}")
            print(f"   - Tamanho: {len(message_content)} chars")
            
        return is_real_agent
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print("🚀 TESTE FINAL DO SISTEMA AGÊNTICO")
    print("=" * 60)
    
    # Aguardar servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # 1. Testar saúde da API
    if not test_api_health():
        print("❌ API não está funcionando. Verifique se o servidor está rodando.")
        return
    
    # 2. Testar com dados mock (Demo Mode)
    mock_success = test_agentic_session_with_data_mode('mock')
    
    # 3. Testar com dados reais
    real_success = test_agentic_session_with_data_mode('real')
    
    # 4. Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO FINAL DOS TESTES")
    print(f"{'='*60}")
    print(f"🎭 Sistema Agêntico com dados MOCK: {'✅ FUNCIONANDO' if mock_success else '❌ FALHANDO'}")
    print(f"🌐 Sistema Agêntico com dados REAL: {'✅ FUNCIONANDO' if real_success else '❌ FALHANDO'}")
    
    if mock_success and real_success:
        print(f"\n🎉 SUCESSO TOTAL! Sistema agêntico funcionando nos dois modos!")
        print(f"   ✓ Modo Demo: Sistema agêntico + dados mock")
        print(f"   ✓ Modo Real: Sistema agêntico + API real")
        print(f"   ✓ Nunca mais respostas automáticas!")
    elif mock_success:
        print(f"\n⚠️ PARCIAL: Sistema agêntico funciona apenas com dados mock")
    elif real_success:
        print(f"\n⚠️ PARCIAL: Sistema agêntico funciona apenas com dados reais")
    else:
        print(f"\n❌ FALHA TOTAL: Sistema ainda usando respostas automáticas")

if __name__ == "__main__":
    main() 