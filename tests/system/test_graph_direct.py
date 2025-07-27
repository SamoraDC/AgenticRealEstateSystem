#!/usr/bin/env python3
"""Teste direto do grafo LangGraph."""

import asyncio
from typing import Dict, Any
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from app.utils.logging import setup_logging


class TestState(MessagesState):
    """Estado de teste simplificado."""
    current_agent: str = "test_agent"


def test_node(state: TestState) -> Command:
    """Nó de teste que retorna uma mensagem simples."""
    return Command(
        update={
            "messages": [{
                "role": "assistant", 
                "content": "✅ Teste funcionando!"
            }]
        }
    )


async def test_graph_execution():
    """Testa execução direta do grafo."""
    
    logger = setup_logging()
    logger.info("🔧 TESTE DIRETO DO GRAFO")
    
    try:
        # Criar grafo simples
        logger.info("📋 Criando grafo...")
        graph = StateGraph(TestState)
        
        # Adicionar nó
        graph.add_node("test_node", test_node)
        
        # Configurar fluxo
        graph.add_edge(START, "test_node")
        graph.add_edge("test_node", END)
        
        # Compilar
        logger.info("⚙️ Compilando grafo...")
        compiled_graph = graph.compile()
        logger.info("✅ Grafo compilado")
        
        # Testar com mensagem
        message = {
            "messages": [
                {"role": "user", "content": "teste"}
            ]
        }
        
        logger.info("🚀 Executando astream...")
        
        chunk_count = 0
        async for chunk in compiled_graph.astream(message):
            chunk_count += 1
            logger.info(f"📦 CHUNK #{chunk_count}: {chunk}")
            
            if chunk_count >= 3:
                break
        
        logger.info(f"✅ Teste concluído - {chunk_count} chunks recebidos")
        
    except Exception as e:
        logger.error(f"❌ ERRO: {e}")
        import traceback
        logger.error(f"📋 TRACEBACK:\n{traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(test_graph_execution()) 