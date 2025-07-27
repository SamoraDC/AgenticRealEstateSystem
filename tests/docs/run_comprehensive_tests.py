#!/usr/bin/env python3
"""
Script Principal - Testes Abrangentes do Real Estate Assistant
Executa stress testing, hooks de conversa e validação completa do sistema agêntico
"""

import asyncio
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

# Adicionar diretório de testes ao path
sys.path.append(str(Path(__file__).parent / "tests"))

from tests.test_stress_testing_pydantic import RealEstateStressTester
from tests.test_conversation_hooks import ConversationAnalyzer, ConversationSimulator
from tests.test_pipeline_integration import RealEstateTestPipeline

def print_banner():
    """Imprime banner do sistema de testes"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     REAL ESTATE ASSISTANT - TESTE ABRANGENTE                ║
║                                                                              ║
║  🏠 Sistema de Stress Testing com PydanticAI                                ║
║  🗣️  Hooks de Conversa e Análise de Fluxo                                   ║
║  🔄 Pipeline Integrado de Validação                                         ║
║  📊 Relatórios Detalhados de Performance                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def run_stress_test_only(concurrent_users: int = 3, questions_per_user: int = 5):
    """Executa apenas stress testing"""
    print("🚀 EXECUTANDO STRESS TEST ISOLADO")
    print("="*40)
    
    tester = RealEstateStressTester()
    
    print(f"📋 Configuração:")
    print(f"   • Usuários Simultâneos: {concurrent_users}")
    print(f"   • Perguntas por Usuário: {questions_per_user}")
    print(f"   • Total de Usuários Virtuais: {len(tester.virtual_users)}")
    
    # Executar teste
    results = await tester.run_stress_test(concurrent_users, questions_per_user)
    
    # Gerar relatório
    report = tester.generate_test_report(results)
    print(report)
    
    return results

async def run_conversation_analysis():
    """Executa análise de conversas"""
    print("💬 EXECUTANDO ANÁLISE DE CONVERSAS")
    print("="*40)
    
    analyzer = ConversationAnalyzer()
    analyzer.create_standard_hooks()
    
    simulator = ConversationSimulator(analyzer)
    
    # Scripts de conversa para teste
    test_scripts = [
        # Conversa 1: Busca simples
        [
            {"user_input": "Hi, I'm looking for an apartment", "agent_type": "search_agent", "phase": "greeting"},
            {"user_input": "I need 1 bedroom under $2000", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "Tell me about this property", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Can I schedule a viewing?", "agent_type": "scheduling_agent", "phase": "scheduling"}
        ],
        # Conversa 2: Busca complexa
        [
            {"user_input": "Hello, I need help finding a place", "agent_type": "search_agent", "phase": "greeting"},
            {"user_input": "Looking for 2 bedrooms in Miami", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "What's the price range?", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "Show me property details", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "What about parking?", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Let's schedule a tour", "agent_type": "scheduling_agent", "phase": "scheduling"}
        ],
        # Conversa 3: Cenário de família
        [
            {"user_input": "Hi, we're a family looking for a home", "agent_type": "search_agent", "phase": "greeting"},
            {"user_input": "We need 3 bedrooms and good schools", "agent_type": "search_agent", "phase": "search_criteria"},
            {"user_input": "Tell me about this family property", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Is it safe for children?", "agent_type": "property_agent", "phase": "property_details"},
            {"user_input": "Can we visit this weekend?", "agent_type": "scheduling_agent", "phase": "scheduling"}
        ]
    ]
    
    print(f"📝 Executando {len(test_scripts)} simulações de conversa...")
    
    # Executar simulações
    for i, script in enumerate(test_scripts, 1):
        print(f"   Conversa {i}: {len(script)} interações")
        await simulator.simulate_conversation(f"user_profile_{i}", script)
    
    # Gerar relatório
    report = analyzer.generate_conversation_report()
    print(report)
    
    return analyzer.analyze_patterns()

async def run_full_pipeline():
    """Executa pipeline completo"""
    print("🔄 EXECUTANDO PIPELINE COMPLETO")
    print("="*40)
    
    pipeline = RealEstateTestPipeline()
    results = await pipeline.run_full_pipeline()
    
    return results

async def run_quick_validation():
    """Executa validação rápida do sistema"""
    print("⚡ EXECUTANDO VALIDAÇÃO RÁPIDA")
    print("="*40)
    
    print("1️⃣ Teste de stress leve...")
    stress_results = await run_stress_test_only(concurrent_users=2, questions_per_user=3)
    
    print("\n2️⃣ Análise de conversa básica...")
    conversation_results = await run_conversation_analysis()
    
    # Resumo rápido
    print("\n📊 RESUMO DA VALIDAÇÃO RÁPIDA:")
    print("="*40)
    
    if stress_results:
        success_rate = stress_results.get("execution_stats", {}).get("success_rate", 0)
        avg_time = stress_results.get("execution_stats", {}).get("average_response_time", 0)
        grade = stress_results.get("performance_grade", "N/A")
        
        print(f"✅ Taxa de Sucesso: {success_rate:.1f}%")
        print(f"⏱️  Tempo Médio: {avg_time:.2f}s")
        print(f"🎯 Nota de Performance: {grade}")
    
    if conversation_results:
        total_convs = conversation_results.get("total_conversations", 0)
        avg_duration = conversation_results.get("average_duration", 0)
        
        print(f"💬 Conversas Analisadas: {total_convs}")
        print(f"⏰ Duração Média: {avg_duration:.2f}s")
    
    # Status geral
    if stress_results and conversation_results:
        success_rate = stress_results.get("execution_stats", {}).get("success_rate", 0)
        if success_rate >= 90:
            print("🟢 STATUS: Sistema funcionando bem!")
        elif success_rate >= 70:
            print("🟡 STATUS: Sistema estável, melhorias recomendadas")
        else:
            print("🔴 STATUS: Sistema precisa de atenção")
    
    return {"stress": stress_results, "conversation": conversation_results}

def create_test_summary(results):
    """Cria resumo dos testes executados"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"""
📋 RESUMO EXECUTIVO - TESTES REAL ESTATE ASSISTANT
Data: {timestamp}
{'='*60}

🎯 TESTES EXECUTADOS:
"""
    
    if isinstance(results, dict):
        if "stress" in results:
            summary += "✅ Stress Testing\n"
        if "conversation" in results:
            summary += "✅ Análise de Conversas\n"
    elif isinstance(results, list):
        summary += f"✅ Pipeline Completo ({len(results)} cenários)\n"
    
    summary += f"""
🔧 PRÓXIMOS PASSOS RECOMENDADOS:
• Monitorar métricas de performance continuamente
• Implementar melhorias baseadas nas recomendações
• Executar testes regulares para validar estabilidade
• Expandir cenários de teste conforme novos recursos

📊 Para análise detalhada, consulte os logs acima.
"""
    
    return summary

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de Testes Abrangentes - Real Estate Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python run_comprehensive_tests.py --quick          # Validação rápida
  python run_comprehensive_tests.py --stress         # Apenas stress test
  python run_comprehensive_tests.py --conversation   # Apenas análise de conversa
  python run_comprehensive_tests.py --full           # Pipeline completo
  python run_comprehensive_tests.py --stress --users 5 --questions 8  # Stress personalizado
        """
    )
    
    # Opções de teste
    parser.add_argument("--quick", action="store_true", help="Executa validação rápida")
    parser.add_argument("--stress", action="store_true", help="Executa apenas stress testing")
    parser.add_argument("--conversation", action="store_true", help="Executa apenas análise de conversas")
    parser.add_argument("--full", action="store_true", help="Executa pipeline completo")
    
    # Parâmetros do stress test
    parser.add_argument("--users", type=int, default=3, help="Número de usuários simultâneos (padrão: 3)")
    parser.add_argument("--questions", type=int, default=5, help="Perguntas por usuário (padrão: 5)")
    
    # Opções gerais
    parser.add_argument("--verbose", "-v", action="store_true", help="Saída detalhada")
    
    args = parser.parse_args()
    
    # Se nenhuma opção específica, executar validação rápida
    if not any([args.quick, args.stress, args.conversation, args.full]):
        args.quick = True
    
    print_banner()
    
    start_time = time.time()
    results = None
    
    try:
        if args.quick:
            results = await run_quick_validation()
        elif args.stress:
            results = await run_stress_test_only(args.users, args.questions)
        elif args.conversation:
            results = await run_conversation_analysis()
        elif args.full:
            results = await run_full_pipeline()
        
        # Gerar resumo
        if results:
            summary = create_test_summary(results)
            print(summary)
        
        execution_time = time.time() - start_time
        print(f"\n⏱️ Tempo total de execução: {execution_time:.2f}s")
        print("✅ Testes concluídos com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante execução dos testes: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Configurar event loop para Windows se necessário
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main()) 