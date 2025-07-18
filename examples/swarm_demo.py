"""
Demonstração do Sistema Agêntico Imobiliário com LangGraph-Swarm

Este exemplo mostra como os 4 agentes colaboram dinamicamente usando OpenRouter:

AGENTES DISPONÍVEIS:
1. SearchAgent - Busca de imóveis usando ReAct pattern
2. PropertyResponseAgent - Análise detalhada de propriedades
3. SchedulingAgent - Agendamento via Google Calendar  
4. SupervisorAgent - Controle de qualidade usando Chain-of-Drafts

FLUXO EXEMPLO:
User: "Quero um apartamento de 2 quartos em Copacabana por até R$ 800.000"
-> search_agent busca propriedades usando Llama-4-Scout via OpenRouter

User: "Me fale mais sobre o primeiro imóvel da lista"
-> search_agent transfere para property_response_agent
-> property_response_agent analisa propriedade detalhadamente

User: "Gostei! Quero agendar uma visita para amanhã"
-> property_response_agent transfere para scheduling_agent
-> scheduling_agent valida horários e agenda via Google Calendar

-> supervisor_agent monitora tudo e intervém se necessário para garantir qualidade

MODELO: meta-llama/llama-4-scout:free via OpenRouter
PADRÕES: ReAct, Chain-of-Drafts, Swarm Architecture
"""

import asyncio
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from agentic_real_estate.core.config import Settings
from agentic_real_estate.orchestration.swarm_orchestrator import SwarmOrchestrator


async def demonstrate_swarm():
    """Demonstra o funcionamento do swarm de agentes."""
    
    print("🏠 === SISTEMA AGÊNTICO IMOBILIÁRIO COM LANGGRAPH-SWARM ===")
    print("Este exemplo mostra como os agentes colaboram dinamicamente\n")
    
    # Configurar sistema
    settings = Settings()
    orchestrator = SwarmOrchestrator(settings)
    
    print("✅ Swarm configurado com sucesso!")
    print("Agentes disponíveis:")
    print("  🔍 search_agent - Especialista em busca de imóveis")
    print("  📅 scheduling_agent - Especialista em agendamentos") 
    print("  👥 supervisor_agent - Supervisor de qualidade")
    print("\n" + "="*60 + "\n")
    
    # Cenários de demonstração
    scenarios = [
        {
            "name": "Busca Inicial",
            "query": "Procuro um apartamento de 2 quartos em Copacabana, até R$ 800.000",
            "expected_agent": "search_agent"
        },
        {
            "name": "Agendamento de Visita", 
            "query": "Gostei do primeiro imóvel, quero agendar uma visita para amanhã às 14h",
            "expected_agent": "scheduling_agent"
        },
        {
            "name": "Consulta Complexa",
            "query": "Há alguma inconsistência nos preços mostrados? Preciso de uma segunda opinião",
            "expected_agent": "supervisor_agent"
        },
        {
            "name": "Nova Busca",
            "query": "Na verdade, prefiro casas com quintal em Barra da Tijuca",
            "expected_agent": "search_agent" 
        }
    ]
    
    # Executar cenários
    thread_id = "demo_session"
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"🎯 CENÁRIO {i}: {scenario['name']}")
        print(f"👤 Usuário: {scenario['query']}")
        print()
        
        try:
            # Processar consulta através do swarm
            response = await orchestrator.process_query(
                query=scenario['query'],
                thread_id=thread_id
            )
            
            print(f"🤖 Agente Ativo: {response.agent_name}")
            print(f"💬 Resposta: {response.content}")
            
            if response.metadata:
                if response.metadata.get('transfer_context'):
                    print(f"🔄 Contexto da Transferência: {response.metadata['transfer_context']}")
                    
            print(f"📊 Confiança: {response.confidence:.1%}")
            
            if response.suggestions:
                print("💡 Sugestões:")
                for suggestion in response.suggestions:
                    print(f"   • {suggestion}")
                    
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            
        print("\n" + "-"*50 + "\n")
        
        # Pausa para demonstração
        await asyncio.sleep(1)
    
    # Mostrar estado final da conversa
    print("📋 ESTADO FINAL DA CONVERSA:")
    final_state = orchestrator.get_conversation_state(thread_id)
    
    if final_state:
        print(f"🎯 Agente Ativo: {final_state.get('active_agent', 'N/A')}")
        print(f"📝 Mensagens na Conversa: {len(final_state.get('messages', []))}")
        if final_state.get('transfer_context'):
            print(f"🔄 Último Contexto: {final_state['transfer_context']}")
    else:
        print("❌ Não foi possível obter estado da conversa")
        
    print("\n" + "="*60)
    print("🎉 Demonstração concluída!")
    print("\nCaracterísticas demonstradas:")
    print("✅ Transferência automática entre agentes baseada no contexto")
    print("✅ Preservação do histórico da conversa") 
    print("✅ Especialização de cada agente")
    print("✅ Supervisão de qualidade quando necessário")
    print("✅ Observabilidade e rastreamento completo")


async def interactive_demo():
    """Demonstração interativa onde o usuário pode fazer perguntas."""
    
    print("\n🎮 === MODO INTERATIVO ===")
    print("Agora você pode conversar diretamente com o swarm!")
    print("Digite 'sair' para encerrar\n")
    
    settings = Settings()
    orchestrator = SwarmOrchestrator(settings)
    thread_id = "interactive_session"
    
    while True:
        try:
            user_input = input("👤 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
                
            if not user_input:
                continue
                
            print("🤔 Processando...")
            
            response = await orchestrator.process_query(
                query=user_input,
                thread_id=thread_id
            )
            
            print(f"\n🤖 {response.agent_name}: {response.content}")
            
            if response.suggestions:
                print("\n💡 Sugestões:")
                for suggestion in response.suggestions:
                    print(f"   • {suggestion}")
                    
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Demonstração encerrada pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}\n")


async def main():
    """Função principal da demonstração."""
    
    try:
        # Executar demonstração automática
        await demonstrate_swarm()
        
        # Perguntar se usuário quer modo interativo
        choice = input("\n🤔 Deseja testar o modo interativo? (s/n): ").strip().lower()
        
        if choice in ['s', 'sim', 'y', 'yes']:
            await interactive_demo()
            
    except Exception as e:
        print(f"❌ Erro crítico na demonstração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Verificar se as dependências estão instaladas
    try:
        import langgraph_swarm
        import langgraph
        print("✅ Dependências LangGraph-Swarm encontradas")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install langgraph-swarm langgraph")
        exit(1)
    
    # Executar demonstração
    asyncio.run(main()) 