#!/usr/bin/env python3
"""
Debug do estado do SwarmOrchestrator
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from app.orchestration.swarm import SwarmOrchestrator

async def debug_swarm_state():
    """Debug do estado do SwarmOrchestrator"""
    
    print("🔍 DEBUG DO ESTADO DO SWARM ORCHESTRATOR")
    print("=" * 50)
    
    try:
        # 1. Criar SwarmOrchestrator
        print("⏳ 1. Criando SwarmOrchestrator...")
        orchestrator = SwarmOrchestrator()
        print("✅ 1. SwarmOrchestrator criado")
        
        # 2. Criar mensagem de teste
        print("⏳ 2. Criando mensagem de teste...")
        message = {
            "messages": [HumanMessage(content="Hello, how much is the rent?")],
            "session_id": "debug-session",
            "current_agent": "property_agent",
            "context": {
                "property_context": {
                    "formattedAddress": "123 Test St, Miami, FL",
                    "price": 2500,
                    "bedrooms": 2,
                    "bathrooms": 1,
                    "squareFootage": 1000
                },
                "data_mode": "mock"
            }
        }
        print("✅ 2. Mensagem criada")
        print(f"📝 Tipo das mensagens: {type(message['messages'][0])}")
        print(f"📝 Conteúdo da mensagem: {message['messages'][0].content}")
        
        # 3. Processar mensagem
        print("⏳ 3. Processando mensagem...")
        result = await orchestrator.process_message(message)
        print("✅ 3. Mensagem processada")
        
        # 4. Analisar resultado
        print(f"📊 Tipo do resultado: {type(result)}")
        print(f"📊 Chaves do resultado: {list(result.keys()) if hasattr(result, 'keys') else 'Não é dict'}")
        
        if hasattr(result, 'get') and result.get("messages"):
            messages = result["messages"]
            print(f"📊 Número de mensagens no resultado: {len(messages)}")
            if messages:
                last_message = messages[-1]
                print(f"📊 Tipo da última mensagem: {type(last_message)}")
                if hasattr(last_message, 'content'):
                    print(f"📊 Conteúdo da resposta: {last_message.content[:100]}...")
                
        print("✅ DEBUG CONCLUÍDO")
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        print(f"📝 Traceback completo: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_swarm_state()) 