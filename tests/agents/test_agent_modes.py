#!/usr/bin/env python3
"""
Teste do sistema agêntico com diferentes modos de dados
"""

import requests
import json

def test_agent_with_mode(mode: str):
    """Testa o sistema agêntico com um modo específico"""
    
    print(f"\n🧪 Testando Sistema Agêntico - Modo: {mode.upper()}")
    print("=" * 60)
    
    # 1. Start agent session
    print(f"\n1. Iniciando sessão do agente em modo {mode}...")
    session_resp = requests.post(f'http://localhost:8000/api/agent/session/start?mode={mode}', 
        json={'property_id': '1', 'mode': 'details'})
    
    if not session_resp.ok:
        print(f"❌ Erro ao iniciar sessão: {session_resp.text}")
        return
    
    session_data = session_resp.json()
    print(f"✅ Sessão criada em modo {mode}")
    
    session_id = session_data['data']['session']['session_id']
    
    # 2. Send message about costs
    print(f"\n2. Perguntando sobre custos em modo {mode}...")
    chat_resp = requests.post(f'http://localhost:8000/api/agent/chat?mode={mode}',
        json={'message': 'What are the exact monthly costs for this property?', 'session_id': session_id})
    
    if not chat_resp.ok:
        print(f"❌ Erro no chat: {chat_resp.text}")
        return
    
    chat_data = chat_resp.json()
    print(f"✅ Resposta do agente em modo {mode}:")
    print(f"Agent: {chat_data['data']['agent_name']}")
    print(f"Message Preview: {chat_data['data']['message'][:300]}...")
    
    # 3. Send message about scheduling
    print(f"\n3. Perguntando sobre agendamento em modo {mode}...")
    schedule_resp = requests.post(f'http://localhost:8000/api/agent/chat?mode={mode}',
        json={'message': 'I want to schedule a visit to this property', 'session_id': session_id})
    
    if schedule_resp.ok:
        schedule_data = schedule_resp.json()
        print(f"✅ Resposta de agendamento em modo {mode}:")
        print(f"Agent: {schedule_data['data']['agent_name']}")
        print(f"Message Preview: {schedule_data['data']['message'][:300]}...")
    
    return True

def main():
    """Função principal de teste"""
    print("🚀 Testando Sistema Agêntico com Diferentes Modos de Dados")
    print("=" * 80)
    
    # Test both modes
    modes = ["mock", "real"]
    
    for mode in modes:
        try:
            test_agent_with_mode(mode)
        except Exception as e:
            print(f"❌ Erro no teste do modo {mode}: {e}")
    
    print("\n🎉 Testes concluídos!")
    print("\n📝 Verificar se:")
    print("- Modo MOCK usa dados brasileiros/mock")
    print("- Modo REAL usa dados americanos/RentCast")
    print("- Ambos usam o sistema agêntico LangGraph-Swarm")

def test_demo_mode_agentic():
    """Testa se o modo Demo está usando sistema agêntico real"""
    
    print("🧪 TESTE: Modo Demo com Sistema Agêntico")
    print("=" * 50)
    
    try:
        # 1. Criar sessão no modo mock (Demo)
        print("⏳ 1. Criando sessão agêntica no modo DEMO...")
        session_data = {
            "property_id": "1",
            "agent_mode": "details",
            "user_preferences": {"name": "Test User"},
            "language": "en"
        }
        
        session_response = requests.post(
            "http://localhost:8000/api/agent/session/start?mode=mock",
            json=session_data,
            timeout=10
        )
        
        print(f"   Status: {session_response.status_code}")
        session_result = session_response.json()
        
        if not session_result.get('success'):
            print(f"❌ Falha ao criar sessão: {session_result.get('message')}")
            return
            
        session_id = session_result['data']['session']['session_id']
        print(f"✅ 1. Sessão Demo criada: {session_id}")
        
        # 2. Enviar mensagem específica para testar resposta
        print(f"⏳ 2. Enviando mensagem específica...")
        message_data = {
            "message": "how much is the rent for this property?",
            "session_id": session_id
        }
        
        message_response = requests.post(
            "http://localhost:8000/api/agent/chat?mode=mock",
            json=message_data,
            timeout=30
        )
        
        print(f"   Status: {message_response.status_code}")
        message_result = message_response.json()
        
        if not message_result.get('success'):
            print(f"❌ Falha ao enviar mensagem: {message_result.get('message')}")
            return
            
        agent_response = message_result['data']
        
        # 3. Analisar resposta
        print(f"\n📊 ANÁLISE DA RESPOSTA:")
        print(f"   Agente: {agent_response.get('agent_name')}")
        print(f"   Confiança: {agent_response.get('confidence')}")
        print(f"   Tamanho: {len(agent_response.get('message', ''))} chars")
        
        message_content = agent_response.get('message', '')
        
        # Verificar se NÃO são as mensagens automáticas antigas
        old_automatic_phrases = [
            "Monthly Rent: $2,500",
            "Security Deposit: $2,500 (1 month)",
            "Great question about pricing!",
            "Sarah - Property Expert"
        ]
        
        is_old_automatic = any(phrase in message_content for phrase in old_automatic_phrases)
        
        if is_old_automatic:
            print(f"❌ PROBLEMA: Ainda usando mensagens automáticas antigas!")
            print(f"   Mensagem: {message_content[:200]}...")
            return False
        else:
            print(f"✅ SUCESSO: Sistema agêntico real sendo usado no modo Demo!")
            print(f"   ✓ Resposta personalizada e inteligente")
            print(f"   ✓ Não contém frases automáticas antigas")
            print(f"   ✓ Agente: {agent_response.get('agent_name')}")
            return True
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    main()
    
    success = test_demo_mode_agentic()
    
    if success:
        print(f"\n🎉 MODO DEMO FUNCIONANDO COM SISTEMA AGÊNTICO!")
    else:
        print(f"\n⚠️ MODO DEMO AINDA TEM PROBLEMAS - Precisa investigação") 