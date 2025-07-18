#!/usr/bin/env python3

import asyncio
import sys
sys.path.append('.')

from app.orchestration.swarm import SwarmOrchestrator
from langchain_core.messages import HumanMessage

async def test_fix():
    """Teste rápido para verificar se a correção do datetime funcionou."""
    print("🧪 Testando correção do erro datetime...")
    
    try:
        orchestrator = SwarmOrchestrator()
        message = {
            'messages': [HumanMessage(content='hello')],
            'session_id': 'test',
            'current_agent': 'property_agent',
            'context': {
                'property_context': {'address': 'Test Property', 'price': 2500},
                'source': 'test',
                'data_mode': 'real'
            }
        }
        
        result = await orchestrator.process_message(message)
        response_content = result["messages"][-1].content
        
        print("✅ Teste bem-sucedido!")
        print(f"📏 Tamanho da resposta: {len(response_content)} chars")
        print(f"📝 Preview: {response_content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fix())
    if success:
        print("\n🎉 CORREÇÃO FUNCIONOU! Sistema agêntico está operacional.")
    else:
        print("\n❌ CORREÇÃO FALHOU! Ainda há problemas.") 