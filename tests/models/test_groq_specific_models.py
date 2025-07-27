#!/usr/bin/env python3
"""
TESTE ESPECÍFICO: Modelos Groq para Acesso aos Logs NLL

MODELOS A TESTAR:
1. llama-3.3-70b-versatile
2. meta-llama/llama-4-scout-17b-16e-instruct
3. meta-llama/llama-4-maverick-17b-128e-instruct
4. moonshotai/kimi-k2-instruct
5. qwen/qwen3-32b

OBJETIVO: Verificar qual modelo suporta logprobs para calcular NLL
"""

import os
import json
import math
import asyncio
import traceback
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class GroqSpecificModelTester:
    """Testador específico para modelos Groq solicitados"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Modelos específicos solicitados
        self.models_to_test = [
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-scout-17b-16e-instruct", 
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "moonshotai/kimi-k2-instruct",
            "qwen/qwen3-32b"
        ]
        
        # Prompt de teste otimizado
        self.test_prompt = "Explain machine learning in exactly 20 words."
        
        # Configurar cliente
        if self.groq_api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                print("✅ Cliente Groq configurado")
            except ImportError:
                print("❌ Biblioteca Groq não disponível")
                self.client = None
        else:
            print("❌ GROQ_API_KEY não encontrada")
            self.client = None
    
    def print_section(self, title: str):
        """Imprimir seção formatada"""
        print(f"\n{'='*70}")
        print(f" {title}")
        print(f"{'='*70}")
    
    async def test_model_comprehensive(self, model_name: str) -> Dict[str, Any]:
        """Teste abrangente de um modelo específico"""
        
        print(f"\n🤖 TESTANDO: {model_name}")
        print("-" * 50)
        
        if not self.client:
            return {
                "model": model_name,
                "status": "error",
                "error": "Cliente Groq não disponível"
            }
        
        result = {
            "model": model_name,
            "basic_functionality": False,
            "logprobs_supported": False,
            "nll_calculable": False,
            "status": "unknown"
        }
        
        # TESTE 1: Funcionalidade básica
        print("🔍 Teste 1: Funcionalidade básica...")
        try:
            basic_response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": self.test_prompt}],
                temperature=0.3,
                max_tokens=30
            )
            
            response_text = basic_response.choices[0].message.content
            print(f"✅ Funcionalidade básica OK")
            print(f"📤 Resposta: {response_text[:60]}...")
            
            result.update({
                "basic_functionality": True,
                "response_text": response_text,
                "status": "partial"
            })
            
        except Exception as e:
            print(f"❌ Funcionalidade básica FALHOU: {e}")
            result.update({
                "status": "error",
                "error": str(e)
            })
            return result
        
        # TESTE 2: Suporte a logprobs
        print("\n🔍 Teste 2: Suporte a logprobs...")
        try:
            logprobs_response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": self.test_prompt}],
                temperature=0.1,
                max_tokens=30,
                logprobs=True,
                top_logprobs=5
            )
            
            print("✅ Logprobs suportados!")
            result["logprobs_supported"] = True
            
            # TESTE 3: Análise detalhada dos logprobs
            print("\n🔍 Teste 3: Análise de logprobs...")
            choice = logprobs_response.choices[0]
            
            if hasattr(choice, 'logprobs') and choice.logprobs:
                logprobs = choice.logprobs
                print(f"📊 Estrutura logprobs: {type(logprobs)}")
                
                # Verificar atributos do logprobs
                logprobs_attrs = []
                for attr in dir(logprobs):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(logprobs, attr)
                            if not callable(value):
                                logprobs_attrs.append(f"{attr}: {type(value)}")
                        except:
                            continue
                
                print(f"📋 Atributos logprobs: {logprobs_attrs}")
                
                # Verificar tokens individuais
                if hasattr(logprobs, 'content') and logprobs.content:
                    print(f"🎯 TOKENS ENCONTRADOS: {len(logprobs.content)}")
                    
                    total_logprob = 0.0
                    token_details = []
                    
                    for i, token_logprob in enumerate(logprobs.content):
                        if i < 5:  # Mostrar apenas primeiros 5 tokens
                            token = getattr(token_logprob, 'token', 'N/A')
                            logprob = getattr(token_logprob, 'logprob', 0.0)
                            
                            print(f"  Token {i}: '{token}' -> logprob: {logprob:.4f}")
                            
                            total_logprob += logprob
                            token_details.append({
                                "token": token,
                                "logprob": logprob
                            })
                            
                            # Verificar alternativas
                            if hasattr(token_logprob, 'top_logprobs') and token_logprob.top_logprobs:
                                print(f"    🔄 Alternativas:")
                                for j, alt in enumerate(token_logprob.top_logprobs[:3]):
                                    alt_token = getattr(alt, 'token', 'N/A')
                                    alt_logprob = getattr(alt, 'logprob', 0.0)
                                    print(f"      {j+1}. '{alt_token}': {alt_logprob:.4f}")
                    
                    # CALCULAR NLL
                    if token_details:
                        nll = -total_logprob
                        perplexity = math.exp(nll / len(token_details))
                        
                        result.update({
                            "nll_calculable": True,
                            "status": "success",
                            "nll_value": nll,
                            "perplexity": perplexity,
                            "token_count": len(logprobs.content),
                            "total_logprob": total_logprob,
                            "token_details": token_details,
                            "logprobs_response_text": choice.message.content
                        })
                        
                        print(f"\n📊 MÉTRICAS CALCULADAS:")
                        print(f"    ✅ NLL: {nll:.4f}")
                        print(f"    ✅ Perplexity: {perplexity:.4f}")
                        print(f"    ✅ Tokens analisados: {len(logprobs.content)}")
                        print(f"    ✅ Total logprob: {total_logprob:.4f}")
                
            else:
                print("❌ Logprobs não encontrados na resposta")
                
        except Exception as e:
            print(f"❌ Logprobs NÃO suportados: {e}")
            result["logprobs_error"] = str(e)
        
        return result
    
    async def test_all_models(self) -> List[Dict[str, Any]]:
        """Testar todos os modelos solicitados"""
        
        self.print_section("TESTE DE MODELOS GROQ ESPECÍFICOS")
        
        print(f"🎯 Testando {len(self.models_to_test)} modelos para acesso aos logs NLL")
        print(f"📝 Prompt de teste: {self.test_prompt}")
        
        results = []
        
        for model_name in self.models_to_test:
            result = await self.test_model_comprehensive(model_name)
            results.append(result)
            
            # Pausa entre testes para não sobrecarregar a API
            await asyncio.sleep(1)
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]):
        """Analisar e apresentar resultados finais"""
        
        self.print_section("ANÁLISE FINAL DOS RESULTADOS")
        
        # Categorizar resultados
        working_models = []
        logprobs_models = []
        nll_models = []
        error_models = []
        
        print("📊 RESUMO POR MODELO:\n")
        
        for result in results:
            model = result["model"]
            status = result["status"]
            
            print(f"🤖 {model}:")
            
            if status == "success":
                print(f"   ✅ Status: TOTALMENTE FUNCIONAL")
                print(f"   ✅ Funcionalidade básica: SIM")
                print(f"   ✅ Logprobs: SIM")
                print(f"   ✅ NLL calculável: SIM")
                print(f"   📊 NLL: {result['nll_value']:.4f}")
                print(f"   📊 Perplexity: {result['perplexity']:.4f}")
                print(f"   📊 Tokens: {result['token_count']}")
                
                working_models.append(model)
                logprobs_models.append(model)
                nll_models.append((model, result['nll_value']))
                
            elif status == "partial":
                print(f"   ⚠️ Status: PARCIALMENTE FUNCIONAL")
                print(f"   ✅ Funcionalidade básica: SIM")
                print(f"   ❌ Logprobs: NÃO")
                print(f"   ❌ NLL calculável: NÃO")
                
                working_models.append(model)
                
            else:
                print(f"   ❌ Status: NÃO FUNCIONAL")
                print(f"   ❌ Erro: {result.get('error', 'Desconhecido')}")
                
                error_models.append((model, result.get('error', 'Desconhecido')))
            
            print()
        
        # Estatísticas finais
        self.print_section("ESTATÍSTICAS FINAIS")
        
        total_models = len(results)
        print(f"📈 RESUMO ESTATÍSTICO:")
        print(f"   🤖 Total de modelos testados: {total_models}")
        print(f"   ✅ Modelos funcionais: {len(working_models)}")
        print(f"   📊 Com suporte a logprobs: {len(logprobs_models)}")
        print(f"   🎯 NLL calculável: {len(nll_models)}")
        print(f"   ❌ Com erros: {len(error_models)}")
        
        # Recomendações específicas
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if nll_models:
            print(f"🏆 MODELOS RECOMENDADOS PARA NLL:")
            # Ordenar por melhor NLL (menor valor)
            for model, nll_value in sorted(nll_models, key=lambda x: x[1]):
                print(f"   ⭐ {model}: NLL = {nll_value:.4f}")
        else:
            print(f"❌ NENHUM MODELO SUPORTA CÁLCULO DIRETO DE NLL")
        
        if logprobs_models:
            print(f"\n✅ MODELOS COM LOGPROBS:")
            for model in logprobs_models:
                print(f"   📊 {model}")
        
        if working_models and not logprobs_models:
            print(f"\n⚠️ MODELOS APENAS COM FUNCIONALIDADE BÁSICA:")
            basic_only = [m for m in working_models if m not in logprobs_models]
            for model in basic_only:
                print(f"   🔧 {model}")
        
        if error_models:
            print(f"\n❌ MODELOS COM PROBLEMAS:")
            for model, error in error_models:
                print(f"   🚫 {model}: {error}")
        
        return {
            "total_tested": total_models,
            "working_models": working_models,
            "logprobs_models": logprobs_models,
            "nll_models": nll_models,
            "error_models": error_models
        }
    
    async def run_comprehensive_test(self):
        """Executar teste completo"""
        
        print("🧪 TESTE ESPECÍFICO DE MODELOS GROQ PARA NLL")
        print("=" * 70)
        print("Verificando acesso aos logs para cálculo de Negative Log Likelihood")
        
        # Testar todos os modelos
        results = await self.test_all_models()
        
        # Analisar resultados
        summary = self.analyze_results(results)
        
        # Salvar resultados detalhados
        output_data = {
            "test_info": {
                "prompt": self.test_prompt,
                "models_tested": self.models_to_test,
                "timestamp": "2024-12-19"
            },
            "results": results,
            "summary": summary
        }
        
        try:
            with open("groq_specific_models_nll_test.json", 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Resultados detalhados salvos em: groq_specific_models_nll_test.json")
        except Exception as e:
            print(f"❌ Erro ao salvar resultados: {e}")
        
        return results

async def main():
    """Função principal"""
    
    tester = GroqSpecificModelTester()
    results = await tester.run_comprehensive_test()
    
    print(f"\n🏁 Teste específico de modelos Groq concluído!")
    print(f"📁 Verifique os resultados detalhados no arquivo JSON gerado.")

if __name__ == "__main__":
    asyncio.run(main()) 