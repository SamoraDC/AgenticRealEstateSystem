"""
Sistema Agêntico de IA para Busca e Agendamento de Imóveis

Ponto de entrada principal do sistema usando arquitetura LangGraph-Swarm.
"""

import asyncio
import logging
from typing import Dict, Any

from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings


async def main() -> None:
    """Ponto de entrada principal da aplicação."""
    
    # Configurar logging
    logger = setup_logging()
    logger.info("🚀 Iniciando Sistema Agêntico de Imóveis")
    
    # Carregar configurações
    settings = get_settings()
    
    # Configurar container de DI
    container = DIContainer()
    await container.setup(settings)
    
    try:
        # Inicializar orquestrador swarm
        orchestrator = container.get(SwarmOrchestrator)
        
        # Exemplo de uso
        initial_message = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Olá! Estou procurando um apartamento de 2 quartos em Copacabana até R$ 4000."
                }
            ]
        }
        
        logger.info("💬 Processando solicitação inicial...")
        
        # Processar com streaming e mostrar resultados detalhados
        chunk_count = 0
        async for chunk in orchestrator.process_stream(initial_message):
            chunk_count += 1
            
            # Verificar se é resposta de um agente específico
            for agent_name in ["search_agent", "property_agent", "scheduling_agent"]:
                if agent_name in chunk:
                    agent_data = chunk[agent_name]
                    messages = agent_data.get("messages", [])
                    if messages:
                        content = messages[-1].get("content", "")
                        logger.info(f"🤖 {agent_name.upper()}: {content[:150]}...")
                    break
            else:
                # Chunk genérico
                logger.info(f"📦 Chunk #{chunk_count}: {list(chunk.keys())}")
        
        logger.info(f"✨ Sistema processou {chunk_count} chunks com sucesso!")
        logger.info("🎯 Sistema Agêntico de Imóveis está operacional e pronto!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante inicialização: {e}")
        raise
    
    finally:
        await container.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 