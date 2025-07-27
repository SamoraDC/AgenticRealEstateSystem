#!/usr/bin/env python3
"""
Teste REAL da API RentCast - Verificação de Suporte ao Brasil

Este script faz chamadas reais para a API RentCast para verificar:
1. Se a API suporta cidades brasileiras
2. Qual é a estrutura real da resposta
3. Confirmar modelo LLM utilizado

⚠️ ATENÇÃO: Este script usará calls reais da API RentCast!
"""

import os
import asyncio
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from config.settings import get_settings
from app.utils.logging import setup_logging
from app.utils.api_monitor import api_monitor

async def test_rentcast_brasil():
    """Teste específico para verificar suporte ao Brasil na API RentCast."""
    
    logger = setup_logging()
    settings = get_settings()
    
    print("🔍 TESTE REAL - API RentCast com Cidades Brasileiras")
    print("=" * 60)
    
    # 1. Confirmar modelo LLM
    print(f"🤖 Modelo LLM Configurado: {settings.models.default_model}")
    print(f"🔧 Provider: {settings.models.provider}")
    print(f"🌐 OpenRouter URL: {settings.apis.openrouter_url}")
    
    # 2. Verificar chave da API
    api_key = settings.apis.rentcast_api_key
    print(f"🔑 RentCast API Key: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else api_key}")
    
    # 3. Status atual do monitor
    usage = api_monitor.get_rentcast_usage()
    print(f"📊 Uso atual: {usage['total_used']}/50 calls ({usage['percentage_used']:.1f}%)")
    
    if not api_monitor.can_use_rentcast():
        print("❌ Limite de API atingido - cancelando teste")
        return False
    
    print("\n🌐 TESTANDO CIDADES BRASILEIRAS:")
    print("-" * 40)
    
    # Cidades brasileiras para testar
    cidades_brasil = [
        {"city": "Rio de Janeiro", "state": "RJ"},
        {"city": "São Paulo", "state": "SP"},
        {"city": "Belo Horizonte", "state": "MG"},
        {"city": "Salvador", "state": "BA"},
        {"city": "Brasília", "state": "DF"}
    ]
    
    # Headers para API RentCast
    headers = {
        "X-API-Key": api_key,
        "accept": "application/json"
    }
    
    base_url = "https://api.rentcast.io/v1"
    
    for i, cidade in enumerate(cidades_brasil, 1):
        print(f"\n🏙️ TESTE {i}/5: {cidade['city']}, {cidade['state']}")
        print("-" * 30)
        
        # Parâmetros para a busca
        params = {
            "city": cidade["city"],
            "state": cidade["state"],
            "propertyType": "Apartment",
            "status": "ForRent",
            "bedrooms": 2,
            "maxRent": 5000
        }
        
        print(f"📋 Parâmetros enviados:")
        for key, value in params.items():
            print(f"   {key}: {value}")
        
        try:
            print(f"🌐 Fazendo chamada para: {base_url}/listings/rental/long-term")
            
            response = requests.get(
                f"{base_url}/listings/rental/long-term",
                headers=headers,
                params=params,
                timeout=15
            )
            
            print(f"📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                api_monitor.record_rentcast_call()
                
                print(f"✅ Resposta recebida com sucesso!")
                print(f"📊 Estrutura da resposta:")
                
                # Mostrar estrutura da resposta
                if isinstance(data, dict):
                    print(f"   Tipo: dict")
                    print(f"   Chaves: {list(data.keys())}")
                    
                    if 'listings' in data:
                        listings = data['listings']
                        print(f"   Listings encontrados: {len(listings)}")
                        
                        if listings:
                            print(f"   Primeiro listing:")
                            first_listing = listings[0]
                            for key, value in first_listing.items():
                                print(f"     {key}: {type(value).__name__} = {value}")
                        else:
                            print(f"   ⚠️ Nenhum listing encontrado para {cidade['city']}")
                    
                    # Mostrar resposta completa (limitada)
                    print(f"\n📄 RESPOSTA COMPLETA (primeiros 1000 chars):")
                    response_text = json.dumps(data, indent=2, ensure_ascii=False)
                    print(response_text[:1000])
                    if len(response_text) > 1000:
                        print("... (resposta truncada)")
                
                else:
                    print(f"   Tipo: {type(data).__name__}")
                    print(f"   Conteúdo: {str(data)[:500]}")
            
            elif response.status_code == 404:
                print(f"❌ 404 - Endpoint não encontrado")
                print(f"📄 Resposta: {response.text[:500]}")
            
            elif response.status_code == 401:
                print(f"❌ 401 - Erro de autenticação")
                print(f"📄 Resposta: {response.text[:500]}")
            
            elif response.status_code == 400:
                print(f"❌ 400 - Parâmetros inválidos")
                print(f"📄 Resposta: {response.text[:500]}")
            
            else:
                print(f"❌ Erro {response.status_code}")
                print(f"📄 Resposta: {response.text[:500]}")
        
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout - API não respondeu em 15 segundos")
        
        except requests.exceptions.ConnectionError:
            print(f"🌐 Erro de conexão - Verifique internet")
        
        except Exception as e:
            print(f"❌ Erro inesperado: {str(e)}")
        
        # Pausa entre requests para não sobrecarregar
        if i < len(cidades_brasil):
            print("⏳ Aguardando 2 segundos...")
            await asyncio.sleep(2)
    
    # Status final
    usage_final = api_monitor.get_rentcast_usage()
    calls_used = usage_final['total_used'] - usage['total_used']
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE:")
    print(f"   🔢 Calls utilizadas: {calls_used}")
    print(f"   📈 Total usado: {usage_final['total_used']}/50")
    print(f"   🔋 Restantes: {usage_final['remaining']}")
    print(f"   🤖 Modelo LLM: {settings.models.default_model}")
    
    return True

async def test_rentcast_usa_comparison():
    """Teste comparativo com cidades americanas (que sabemos que funcionam)."""
    
    print("\n🇺🇸 TESTE COMPARATIVO - CIDADES AMERICANAS:")
    print("-" * 50)
    
    settings = get_settings()
    api_key = settings.apis.rentcast_api_key
    
    headers = {
        "X-API-Key": api_key,
        "accept": "application/json"
    }
    
    # Cidades americanas conhecidas
    cidades_usa = [
        {"city": "Miami", "state": "FL"},
        {"city": "New York", "state": "NY"}
    ]
    
    for cidade in cidades_usa:
        print(f"\n🏙️ Testando: {cidade['city']}, {cidade['state']}")
        
        params = {
            "city": cidade["city"],
            "state": cidade["state"],
            "propertyType": "Apartment",
            "status": "ForRent",
            "bedrooms": 2,
            "maxRent": 3000
        }
        
        try:
            response = requests.get(
                "https://api.rentcast.io/v1/listings/rental/long-term",
                headers=headers,
                params=params,
                timeout=15
            )
            
            print(f"📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                api_monitor.record_rentcast_call()
                
                if 'listings' in data:
                    print(f"✅ {len(data['listings'])} propriedades encontradas")
                    if data['listings']:
                        first = data['listings'][0]
                        print(f"   Exemplo: {first.get('propertyType', 'N/A')} - ${first.get('rent', 0)}/mês")
                else:
                    print(f"⚠️ Estrutura inesperada: {list(data.keys())}")
            else:
                print(f"❌ Erro {response.status_code}: {response.text[:200]}")
        
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("🚨 AVISO: Este script usará calls reais da API RentCast!")
    print("Pressione CTRL+C nos próximos 5 segundos para cancelar...")
    
    try:
        import time
        for i in range(5, 0, -1):
            print(f"Iniciando em {i}...")
            time.sleep(1)
        
        print("\n🚀 Iniciando teste com API real...")
        asyncio.run(test_rentcast_brasil())
        
        print("\n🔄 Teste comparativo com EUA...")
        asyncio.run(test_rentcast_usa_comparison())
        
    except KeyboardInterrupt:
        print("\n⏹️ Teste cancelado pelo usuário")
        print("💡 API RentCast preservada - nenhuma call foi usada") 