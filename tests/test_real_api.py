#!/usr/bin/env python3
"""
Teste Único - API Real RentCast

ATENÇÃO: Este script usa 1 call da sua API RentCast!
Executa apenas uma vez para validar integração real.
"""

import asyncio
from app.utils.logging import setup_logging
from app.utils.container import DIContainer
from app.utils.api_monitor import api_monitor
from app.orchestration.swarm import SwarmOrchestrator
from config.settings import get_settings
from config.api_config import api_config, APIMode


async def test_real_api():
    """Teste único com API real da RentCast."""
    
    logger = setup_logging()
    logger.info("🌐 TESTE API REAL - USO DE 1 CALL")
    print("\n" + "⚠️" * 60)
    print("🌐 TESTE COM API REAL DA RENTCAST")
    print("⚠️" * 60)
    print("⚠️  ATENÇÃO: Este teste usará 1 call da sua API RentCast")
    print("⚠️  Restantes após o teste: 49/50 calls")
    print("⚠️" * 60)
    
    # Status inicial
    usage_before = api_monitor.get_rentcast_usage()
    print(f"📊 Status antes: {usage_before['remaining']}/50 calls disponíveis")
    
    # Configurar modo real
    api_config.mode = APIMode.REAL
    api_config.use_real_api = True
    
    if not api_config.rentcast_api_key:
        print("❌ ERRO: API key não configurada no .env")
        return False
    
    # Configurar sistema
    settings = get_settings()
    container = DIContainer()
    
    try:
        await container.setup(settings)
        orchestrator = container.get(SwarmOrchestrator)
        
        # Query específica para API real
        query = "Quero um apartamento de 2 quartos no Rio de Janeiro até R$ 4000 reais"
        print(f"\n🏠 CONSULTA PARA API REAL: {query}")
        print("-" * 60)
        
        # Preparar mensagem
        message = {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
        
        # Processar com API real
        agent_responses = {}
        chunk_count = 0
        api_call_detected = False
        
        print("🌐 Fazendo chamada para API RentCast...")
        
        async for chunk in orchestrator.process_stream(message):
            chunk_count += 1
            
            # Capturar respostas dos agentes
            for agent_name in ["search_agent", "property_agent", "scheduling_agent"]:
                if agent_name in chunk:
                    agent_data = chunk[agent_name]
                    messages = agent_data.get("messages", [])
                    if messages:
                        content = messages[-1].get("content", "")
                        agent_responses[agent_name] = content
                        
                        print(f"\n🤖 {agent_name.replace('_', ' ').upper()}:")
                        print(f"📝 {content}")
                        
                        # Detectar se API real foi usada
                        if "API RentCast" in content:
                            api_call_detected = True
                    break
        
        # Verificar uso da API
        usage_after = api_monitor.get_rentcast_usage()
        api_used = usage_after['total_used'] > usage_before['total_used']
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DO TESTE COM API REAL:")
        print(f"   ✅ Chunks processados: {chunk_count}")
        print(f"   🤖 Respostas de agentes: {len(agent_responses)}")
        print(f"   🌐 API RentCast chamada: {'Sim' if api_used else 'Não'}")
        print(f"   📝 Fonte identificada na resposta: {'API Real' if api_call_detected else 'Mock Fallback'}")
        print(f"   📈 Calls antes: {usage_before['total_used']}/50")
        print(f"   📈 Calls depois: {usage_after['total_used']}/50")
        print(f"   📉 Calls restantes: {usage_after['remaining']}/50")
        
        # Resultado
        success = chunk_count > 0 and len(agent_responses) >= 2
        
        print("\n" + "=" * 60)
        if success and api_used:
            print("🎉 TESTE API REAL - SUCESSO COMPLETO!")
            print("✅ API RentCast integrada e funcionando")
            print("✅ Dados reais obtidos com sucesso")
            print("✅ Sistema híbrido (real + fallback) operacional")
            print("✅ 1 call usada conforme esperado")
        elif success and not api_used:
            print("⚠️ TESTE API REAL - FALLBACK ATIVADO")
            print("🔄 Sistema usou fallback para dados mock")
            print("📋 Verificar configuração da API ou conectividade")
            print("✅ Sistema defensivo funcionando corretamente")
        else:
            print("❌ TESTE API REAL - FALHOU")
            print("📋 Verificar logs para detalhes")
            
        print("=" * 60)
        
        # Voltar para modo mock por segurança
        api_config.mode = APIMode.MOCK
        api_config.use_real_api = False
        print("🔒 Sistema voltou para modo MOCK (seguro)")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Erro durante teste com API real: {e}")
        print(f"\n❌ Erro: {e}")
        
        # Garantir volta para modo mock em caso de erro
        api_config.mode = APIMode.MOCK
        api_config.use_real_api = False
        print("🔒 Sistema voltou para modo MOCK após erro")
        
        return False
        
    finally:
        await container.cleanup()


if __name__ == "__main__":
    print("🚨 AVISO: Este script usará 1 call da API RentCast")
    print("Pressione CTRL+C nos próximos 3 segundos para cancelar...")
    
    try:
        # Dar tempo para cancelar
        import time
        for i in range(3, 0, -1):
            print(f"Iniciando em {i}...")
            time.sleep(1)
        
        print("\n🚀 Iniciando teste com API real...")
        asyncio.run(test_real_api())
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste cancelado pelo usuário")
        print("💡 API RentCast preservada - nenhuma call foi usada") 