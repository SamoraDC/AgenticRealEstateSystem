#!/usr/bin/env python3
"""
Teste de Acesso aos Logs para Cálculo de Negative Log Likelihood (NLL)
Testa os modelos:
1. gemini-2.0-flash-lite (Google API)
2. meta-llama/llama-4-scout-17b-16e-instruct (Groq API)
"""

import os
import json
import asyncio
import traceback
import math
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se as bibliotecas estão disponíveis
try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GOOGLE_AVAILABLE = True
except ImportError:
    print("❌ Google Generative AI não disponível")
    GOOGLE_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    print("❌ Groq não disponível")
    GROQ_AVAILABLE = False

class NLLTester:
    """Testador de acesso aos logs para cálculo de NLL"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Prompt de teste para ambos os modelos
        self.test_prompt = """Complete this sentence with exactly 10 words: "The future of artificial intelligence in real estate will be"""
        
        # Configurar clientes
        self.setup_clients()
    
    def setup_clients(self):
        """Configurar clientes para APIs"""
        
        # Google Client
        if GOOGLE_AVAILABLE and self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            print("✅ Google API configurada")
        else:
            print("❌ Google API não configurada (chave faltando ou biblioteca indisponível)")
        
        # Groq Client
        if GROQ_AVAILABLE and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            print("✅ Groq API configurada")
        else:
            print("❌ Groq API não configurada (chave faltando ou biblioteca indisponível)")
    
    def print_section(self, title: str):
        """Imprimir seção formatada"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    async def test_google_gemini_logs(self) -> Dict[str, Any]:
        """Testar acesso aos logs do Google Gemini 2.0 Flash Lite"""
        
        self.print_section("TESTANDO GOOGLE GEMINI 2.0 FLASH LITE")
        
        if not GOOGLE_AVAILABLE or not self.google_api_key:
            return {
                "model": "gemini-2.0-flash-lite",
                "provider": "Google",
                "status": "error",
                "error": "API não configurada ou biblioteca indisponível",
                "logprobs_available": False,
                "nll_calculable": False
            }
        
        try:
            # Configurar modelo
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            print(f"📝 Prompt: {self.test_prompt}")
            print("🔄 Enviando requisição...")
            
            # Configuração para tentar obter logprobs
            generation_config = GenerationConfig(
                temperature=0.7,
                max_output_tokens=50,
                candidate_count=1
            )
            
            # Fazer a requisição
            response = model.generate_content(
                self.test_prompt,
                generation_config=generation_config
            )
            
            print("✅ Resposta recebida")
            print(f"📤 Resposta: {response.text}")
            
            # Analisar estrutura da resposta
            result = {
                "model": "gemini-2.0-flash-lite",
                "provider": "Google",
                "status": "success",
                "response_text": response.text,
                "response_structure": {},
                "logprobs_available": False,
                "nll_calculable": False,
                "raw_response": {}
            }
            
            # Verificar atributos disponíveis na resposta
            print("\n🔍 Analisando estrutura da resposta:")
            
            for attr in dir(response):
                if not attr.startswith('_'):
                    try:
                        value = getattr(response, attr)
                        if not callable(value):
                            print(f"  - {attr}: {type(value)}")
                            result["response_structure"][attr] = str(type(value))
                    except:
                        continue
            
            # Verificar se há informações de log probability
            if hasattr(response, 'candidates'):
                print(f"\n🔍 Candidates disponíveis: {len(response.candidates)}")
                
                for i, candidate in enumerate(response.candidates):
                    print(f"  Candidate {i}:")
                    
                    for attr in dir(candidate):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(candidate, attr)
                                if not callable(value):
                                    print(f"    - {attr}: {type(value)}")
                                    
                                    # Procurar por logprobs ou probabilidades
                                    if 'prob' in attr.lower() or 'log' in attr.lower():
                                        print(f"      🎯 POTENCIAL LOGPROB: {attr} = {value}")
                                        result["logprobs_available"] = True
                            except:
                                continue
            
            # Verificar se há informações de finish_reason
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    print(f"  Finish reason: {candidate.finish_reason}")
                
                # Verificar safety ratings
                if hasattr(candidate, 'safety_ratings'):
                    print(f"  Safety ratings: {candidate.safety_ratings}")
            
            # Verificar se há usage metadata
            if hasattr(response, 'usage_metadata'):
                print(f"  Usage metadata: {response.usage_metadata}")
                result["usage_metadata"] = str(response.usage_metadata)
            
            # Tentar serializar resposta completa para análise
            try:
                # Converter para dicionário se possível
                if hasattr(response, 'to_dict'):
                    result["raw_response"] = response.to_dict()
                    print("✅ Resposta serializada com sucesso")
                else:
                    result["raw_response"] = {"note": "Não foi possível serializar"}
            except Exception as e:
                print(f"⚠️ Erro ao serializar resposta: {e}")
                result["raw_response"] = {"error": str(e)}
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao testar Google Gemini: {e}")
            traceback.print_exc()
            
            return {
                "model": "gemini-2.0-flash-lite",
                "provider": "Google",
                "status": "error",
                "error": str(e),
                "logprobs_available": False,
                "nll_calculable": False
            }
    
    async def test_groq_llama_logs(self) -> Dict[str, Any]:
        """Testar acesso aos logs do Groq LLaMA"""
        
        self.print_section("TESTANDO META LLAMA 4 SCOUT (GROQ)")
        
        if not GROQ_AVAILABLE or not self.groq_api_key:
            return {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "provider": "Groq",
                "status": "error",
                "error": "API não configurada ou biblioteca indisponível",
                "logprobs_available": False,
                "nll_calculable": False
            }
        
        try:
            print(f"📝 Prompt: {self.test_prompt}")
            print("🔄 Enviando requisição...")
            
            # Fazer requisição com logprobs habilitados
            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "user", "content": self.test_prompt}
                ],
                temperature=0.7,
                max_tokens=50,
                logprobs=True,  # Tentar habilitar logprobs
                top_logprobs=5  # Top 5 tokens mais prováveis
            )
            
            print("✅ Resposta recebida")
            
            # Extrair texto da resposta
            response_text = response.choices[0].message.content
            print(f"📤 Resposta: {response_text}")
            
            result = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct", 
                "provider": "Groq",
                "status": "success",
                "response_text": response_text,
                "logprobs_available": False,
                "nll_calculable": False,
                "token_count": 0,
                "total_logprob": 0.0,
                "nll_value": 0.0,
                "raw_response": {}
            }
            
            # Verificar se logprobs estão disponíveis
            print("\n🔍 Analisando logprobs:")
            
            choice = response.choices[0]
            if hasattr(choice, 'logprobs') and choice.logprobs:
                print("✅ Logprobs encontrados!")
                result["logprobs_available"] = True
                
                # Analisar estrutura dos logprobs
                logprobs = choice.logprobs
                
                print(f"  Estrutura logprobs: {type(logprobs)}")
                
                for attr in dir(logprobs):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(logprobs, attr)
                            if not callable(value):
                                print(f"    - {attr}: {type(value)}")
                        except:
                            continue
                
                # Verificar tokens e suas probabilidades
                if hasattr(logprobs, 'content') and logprobs.content:
                    print(f"\n🔍 Analisando {len(logprobs.content)} tokens:")
                    
                    total_logprob = 0.0
                    token_details = []
                    
                    for i, token_logprob in enumerate(logprobs.content):
                        token = token_logprob.token
                        logprob = token_logprob.logprob
                        
                        print(f"    Token {i}: '{token}' -> logprob: {logprob:.4f}")
                        
                        total_logprob += logprob
                        token_details.append({
                            "token": token,
                            "logprob": logprob
                        })
                        
                        # Verificar top alternatives se disponível
                        if hasattr(token_logprob, 'top_logprobs') and token_logprob.top_logprobs:
                            print(f"      Top alternatives:")
                            for alt in token_logprob.top_logprobs[:3]:  # Top 3
                                print(f"        '{alt.token}': {alt.logprob:.4f}")
                    
                    # Calcular NLL
                    nll = -total_logprob
                    perplexity = math.exp(nll / len(logprobs.content))
                    
                    result.update({
                        "nll_calculable": True,
                        "token_count": len(logprobs.content),
                        "total_logprob": total_logprob,
                        "nll_value": nll,
                        "perplexity": perplexity,
                        "token_details": token_details
                    })
                    
                    print(f"\n📊 MÉTRICAS CALCULADAS:")
                    print(f"    Total logprob: {total_logprob:.4f}")
                    print(f"    NLL: {nll:.4f}")
                    print(f"    Perplexity: {perplexity:.4f}")
                    print(f"    Tokens: {len(logprobs.content)}")
                
            else:
                print("❌ Logprobs não encontrados na resposta")
            
            # Serializar resposta completa
            try:
                result["raw_response"] = response.model_dump() if hasattr(response, 'model_dump') else str(response)
            except:
                result["raw_response"] = {"note": "Não foi possível serializar"}
            
            return result
            
        except Exception as e:
            print(f"❌ Erro ao testar Groq LLaMA: {e}")
            traceback.print_exc()
            
            return {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "provider": "Groq", 
                "status": "error",
                "error": str(e),
                "logprobs_available": False,
                "nll_calculable": False
            }
    
    def calculate_nll_comparison(self, results: List[Dict[str, Any]]):
        """Comparar resultados de NLL entre modelos"""
        
        self.print_section("COMPARAÇÃO DE RESULTADOS NLL")
        
        print("📊 RESUMO DOS TESTES:\n")
        
        for result in results:
            model = result["model"]
            provider = result["provider"]
            status = result["status"]
            
            print(f"🤖 {model} ({provider}):")
            print(f"   Status: {'✅' if status == 'success' else '❌'} {status}")
            
            if status == "success":
                print(f"   Logprobs disponíveis: {'✅' if result['logprobs_available'] else '❌'}")
                print(f"   NLL calculável: {'✅' if result['nll_calculable'] else '❌'}")
                
                if result['nll_calculable']:
                    print(f"   NLL: {result['nll_value']:.4f}")
                    print(f"   Perplexity: {result['perplexity']:.4f}")
                    print(f"   Tokens: {result['token_count']}")
            else:
                print(f"   Erro: {result.get('error', 'Desconhecido')}")
            
            print()
        
        # Conclusões
        print("🎯 CONCLUSÕES:")
        
        successful_nll = [r for r in results if r.get('nll_calculable', False)]
        
        if successful_nll:
            print(f"✅ {len(successful_nll)} modelo(s) permitem cálculo de NLL")
            
            if len(successful_nll) > 1:
                # Comparar NLL values
                best_nll = min(successful_nll, key=lambda x: x['nll_value'])
                print(f"🏆 Melhor NLL: {best_nll['model']} (NLL: {best_nll['nll_value']:.4f})")
        else:
            print("❌ Nenhum modelo permite cálculo direto de NLL")
        
        # Recommendations
        print("\n💡 RECOMENDAÇÕES:")
        
        google_result = next((r for r in results if r['provider'] == 'Google'), None)
        groq_result = next((r for r in results if r['provider'] == 'Groq'), None)
        
        if groq_result and groq_result.get('logprobs_available'):
            print("✅ Use Groq para cálculos de NLL - logprobs completos disponíveis")
        
        if google_result and not google_result.get('logprobs_available'):
            print("⚠️ Google Gemini pode não fornecer logprobs diretos - considere métodos alternativos")
        
        print("\n📋 MÉTODOS ALTERNATIVOS PARA NLL:")
        print("1. Use modelos locais (Ollama, Hugging Face) com acesso completo aos logits")
        print("2. Implemente estimativa de NLL via sampling múltiplo")
        print("3. Use APIs especializadas em evaluation (como Anthropic's evaluation suite)")
    
    async def run_tests(self):
        """Executar todos os testes"""
        
        self.print_section("INICIANDO TESTES DE ACESSO AOS LOGS NLL")
        
        print("🔍 Verificando configuração:")
        print(f"   Google API Key: {'✅' if self.google_api_key else '❌'}")
        print(f"   Groq API Key: {'✅' if self.groq_api_key else '❌'}")
        print(f"   Google Library: {'✅' if GOOGLE_AVAILABLE else '❌'}")
        print(f"   Groq Library: {'✅' if GROQ_AVAILABLE else '❌'}")
        
        results = []
        
        # Testar Google Gemini
        google_result = await self.test_google_gemini_logs()
        results.append(google_result)
        
        # Testar Groq LLaMA
        groq_result = await self.test_groq_llama_logs()
        results.append(groq_result)
        
        # Comparar resultados
        self.calculate_nll_comparison(results)
        
        # Salvar resultados
        self.save_results(results)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]]):
        """Salvar resultados em arquivo"""
        
        output_file = "nll_test_results.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n💾 Resultados salvos em: {output_file}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")

async def main():
    """Função principal"""
    
    print("🧪 TESTE DE ACESSO AOS LOGS PARA CÁLCULO DE NLL")
    print("=" * 60)
    print("Testando:")
    print("1. Google Gemini 2.0 Flash Lite")
    print("2. Meta LLaMA 4 Scout (Groq)")
    print("=" * 60)
    
    tester = NLLTester()
    results = await tester.run_tests()
    
    print(f"\n🏁 Teste concluído! Resultados detalhados salvos em 'nll_test_results.json'")

if __name__ == "__main__":
    asyncio.run(main()) 