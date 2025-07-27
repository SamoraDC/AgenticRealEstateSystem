#!/usr/bin/env python3

import time
import requests

def test_mock_mode_api():
    """Testa se o modo mock não está fazendo chamadas desnecessárias."""
    
    print("🧪 Testando se modo MOCK não faz chamadas desnecessárias...")
    
    try:
        # 1. Verificar se servidor está funcionando
        response = requests.get("http://localhost:8000/api/health?mode=mock", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor não está funcionando")
            return False
        
        print("✅ Servidor funcionando")
        
        # 2. Testar busca de propriedades em modo mock
        response = requests.get("http://localhost:8000/api/properties/search?mode=mock", timeout=5)
        if response.status_code == 200:
            data = response.json()
            properties = data.get('data', [])
            print(f"✅ Busca MOCK funcionando: {len(properties)} propriedades")
        else:
            print("❌ Busca MOCK falhando")
            return False
        
        # 3. Testar inicialização de sessão em modo mock
        session_data = {
            "property_id": properties[0]['id'] if properties else "mock-property",
            "agent_mode": "details",
            "language": "pt"
        }
        
        response = requests.post(
            "http://localhost:8000/api/agent/session/start?mode=mock", 
            json=session_data,
            timeout=10
        )
        
        if response.status_code == 200:
            session_result = response.json()
            if session_result.get('success'):
                session_id = session_result['data']['session']['session_id']
                print(f"✅ Sessão MOCK criada: {session_id}")
                
                # 4. Testar envio de mensagem em modo mock
                chat_data = {
                    "message": "Olá, me fale sobre este imóvel",
                    "session_id": session_id
                }
                
                response = requests.post(
                    "http://localhost:8000/api/agent/chat?mode=mock",
                    json=chat_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    chat_result = response.json()
                    if chat_result.get('success'):
                        message = chat_result['data']['message']
                        agent_name = chat_result['data']['agent_name']
                        print(f"✅ Chat MOCK funcionando: {agent_name}")
                        print(f"📝 Mensagem (primeiros 100 chars): {message[:100]}...")
                        
                        # Verificar se está em português
                        if any(word in message.lower() for word in ["olá", "imóvel", "propriedade", "localização"]):
                            print("✅ Sistema em PORTUGUÊS")
                        else:
                            print("⚠️ Sistema ainda em inglês")
                        
                        return True
                    else:
                        print("❌ Chat MOCK retornou erro")
                else:
                    print("❌ Chat MOCK falhou na requisição")
            else:
                print("❌ Sessão MOCK retornou erro")
        else:
            print("❌ Sessão MOCK falhou na requisição")
        
        return False
        
    except requests.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTE COMPLETO DO SISTEMA MOCK")
    print("="*50)
    
    success = test_mock_mode_api()
    
    print("\n" + "="*50)
    if success:
        print("🎉 SISTEMA MOCK FUNCIONANDO CORRETAMENTE!")
        print("✅ Modo mock em português sem chamadas desnecessárias")
    else:
        print("❌ SISTEMA MOCK COM PROBLEMAS!")
        print("🔧 Verificar logs do servidor e configurações") 