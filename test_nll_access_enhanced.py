#!/usr/bin/env python3
"""
Teste Aprimorado de Acesso aos Logs para Cálculo de NLL
Explora em detalhes os logprobs disponíveis e testa múltiplos modelos
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

# Verificar bibliotecas
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

class EnhancedNLLTester:
    """Testador aprimorado de acesso aos logs para cálculo de NLL"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Prompt mais estruturado para melhor análise
        self.test_prompt = "Explain the concept of machine learning in exactly 15 words."
        
        # Modelos Groq que podem suportar logprobs
        self.groq_models_to_test = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant", 
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        self.setup_clients()
    
    def setup_clients(self):
        """Configurar clientes para APIs"""
        if GOOGLE_AVAILABLE and self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            print("✅ Google API configurada")
        else:
            print("❌ Google API não configurada")
        
        if GROQ_AVAILABLE and self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
            print("✅ Groq API configurada")
        else:
            print("❌ Groq API não configurada")
    
    def print_section(self, title: str):
        """Imprimir seção formatada"""
        print(f"\n{'='*70}")
        print(f" {title}")
        print(f"{'='*70}")
    
    def deep_explore_object(self, obj, name: str, depth: int = 0, max_depth: int = 3):
        """Explorar profundamente objeto para encontrar logprobs"""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        print(f"{indent}🔍 Explorando {name} ({type(obj)})")
        
        if hasattr(obj, '__dict__'):
            for attr_name, attr_value in obj.__dict__.items():
                if not attr_name.startswith('_'):
                    print(f"{indent}  - {attr_name}: {type(attr_value)}")
                    
                    # Se contém 'prob' ou 'log', explorar mais
                    if 'prob' in attr_name.lower() or 'log' in attr_name.lower():
                        print(f"{indent}    🎯 INTERESSE: {attr_name} = {attr_value}")
                        if depth < max_depth - 1:
                            self.deep_explore_object(attr_value, f"{name}.{attr_name}", depth + 1, max_depth)
        
        # Se for lista, explorar elementos
        if isinstance(obj, (list, tuple)) and len(obj) > 0:
            print(f"{indent}  📋 Lista com {len(obj)} elementos")
            if len(obj) <= 5:  # Explorar apenas listas pequenas
                for i, item in enumerate(obj):
                    if depth < max_depth - 1:
                        self.deep_explore_object(item, f"{name}[{i}]", depth + 1, max_depth)
    
    async def test_google_gemini_detailed(self) -> Dict[str, Any]:
        """Teste detalhado do Google Gemini com foco em logprobs"""
        
        self.print_section("ANÁLISE DETALHADA - GOOGLE GEMINI 2.0 FLASH LITE")
        
        if not GOOGLE_AVAILABLE or not self.google_api_key:
            return {"status": "error", "error": "API não configurada"}
        
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            print(f"📝 Prompt: {self.test_prompt}")
            print("🔄 Enviando requisição com configuração para logprobs...")
            
            # Configuração específica para tentar obter logprobs
            generation_config = GenerationConfig(
                temperature=0.1,  # Temperatura baixa para análise mais precisa
                max_output_tokens=30,
                candidate_count=1,
                stop_sequences=None,
                response_mime_type="text/plain"
            )
            
            # Fazer requisição
            response = model.generate_content(
                self.test_prompt,
                generation_config=generation_config
            )
            
            print("✅ Resposta recebida")
            print(f"📤 Resposta: {response.text}")
            
            result = {
                "model": "gemini-2.0-flash-lite",
                "provider": "Google",
                "status": "success",
                "response_text": response.text,
                "nll_calculable": False,
                "detailed_analysis": {}
            }
            
            # Análise detalhada dos candidates
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                print(f"\n🎯 ANALISANDO CANDIDATE DETALHADAMENTE:")
                
                # Explorar avg_logprobs
                if hasattr(candidate, 'avg_logprobs'):
                    avg_logprobs = candidate.avg_logprobs
                    print(f"📊 avg_logprobs: {avg_logprobs}")
                    result["detailed_analysis"]["avg_logprobs"] = avg_logprobs
                
                # Explorar logprobs_result em detalhes
                if hasattr(candidate, 'logprobs_result'):
                    print(f"\n🔍 EXPLORANDO LOGPROBS_RESULT:")
                    logprobs_result = candidate.logprobs_result
                    
                    self.deep_explore_object(logprobs_result, "logprobs_result", max_depth=4)
                    
                    # Tentar acessar atributos específicos do logprobs_result
                    if hasattr(logprobs_result, 'chosen_candidates'):
                        print(f"📋 chosen_candidates: {logprobs_result.chosen_candidates}")
                        result["detailed_analysis"]["chosen_candidates"] = str(logprobs_result.chosen_candidates)
                    
                    if hasattr(logprobs_result, 'top_candidates'):
                        print(f"📋 top_candidates: {logprobs_result.top_candidates}")
                        
                        # Explorar top_candidates em detalhes
                        if logprobs_result.top_candidates:
                            print(f"🔍 Explorando {len(logprobs_result.top_candidates)} top_candidates:")
                            
                            total_logprob = 0.0
                            token_count = 0
                            token_details = []
                            
                            for i, candidate_item in enumerate(logprobs_result.top_candidates):
                                print(f"  Candidate {i}:")
                                self.deep_explore_object(candidate_item, f"top_candidate[{i}]", max_depth=3)
                                
                                # Tentar extrair token e logprob
                                if hasattr(candidate_item, 'token'):
                                    token = candidate_item.token
                                    print(f"    Token: '{token}'")
                                    
                                if hasattr(candidate_item, 'log_probability'):
                                    logprob = candidate_item.log_probability
                                    print(f"    Log Probability: {logprob}")
                                    
                                    total_logprob += logprob
                                    token_count += 1
                                    token_details.append({
                                        "token": getattr(candidate_item, 'token', f'token_{i}'),
                                        "logprob": logprob
                                    })
                            
                            # Se conseguimos extrair dados, calcular NLL
                            if token_count > 0:
                                nll = -total_logprob
                                perplexity = math.exp(nll / token_count)
                                
                                result.update({
                                    "nll_calculable": True,
                                    "token_count": token_count,
                                    "total_logprob": total_logprob,
                                    "nll_value": nll,
                                    "perplexity": perplexity,
                                    "token_details": token_details
                                })
                                
                                print(f"\n📊 MÉTRICAS EXTRAÍDAS:")
                                print(f"    Tokens analisados: {token_count}")
                                print(f"    Total logprob: {total_logprob:.4f}")
                                print(f"    NLL: {nll:.4f}")
                                print(f"    Perplexity: {perplexity:.4f}")
                
                # Análise do content para tokens individuais
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    print(f"\n🔍 ANALISANDO CONTENT PARTS:")
                    for i, part in enumerate(candidate.content.parts):
                        print(f"  Part {i}: {type(part)}")
                        self.deep_explore_object(part, f"part[{i}]", max_depth=2)
            
            return result
            
        except Exception as e:
            print(f"❌ Erro detalhado: {e}")
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    async def test_groq_models_comprehensive(self) -> List[Dict[str, Any]]:
        """Testar múltiplos modelos Groq para encontrar suporte a logprobs"""
        
        self.print_section("TESTE ABRANGENTE - MODELOS GROQ")
        
        if not GROQ_AVAILABLE or not self.groq_api_key:
            return [{"status": "error", "error": "Groq não configurado"}]
        
        results = []
        
        for model_name in self.groq_models_to_test:
            print(f"\n🤖 Testando modelo: {model_name}")
            
            try:
                # Primeiro, testar sem logprobs para ver se o modelo funciona
                print("  🔍 Testando funcionalidade básica...")
                
                basic_response = self.groq_client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": self.test_prompt}],
                    temperature=0.1,
                    max_tokens=30
                )
                
                response_text = basic_response.choices[0].message.content
                print(f"  ✅ Funcionalidade básica OK: {response_text[:50]}...")
                
                # Agora tentar com logprobs
                print("  🔍 Testando logprobs...")
                
                try:
                    logprobs_response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": self.test_prompt}],
                        temperature=0.1,
                        max_tokens=30,
                        logprobs=True,
                        top_logprobs=5
                    )
                    
                    print("  ✅ Logprobs suportados!")
                    
                    # Analisar logprobs
                    choice = logprobs_response.choices[0]
                    result = {
                        "model": model_name,
                        "provider": "Groq",
                        "status": "success",
                        "response_text": choice.message.content,
                        "logprobs_available": True,
                        "nll_calculable": False
                    }
                    
                    if hasattr(choice, 'logprobs') and choice.logprobs:
                        logprobs = choice.logprobs
                        
                        if hasattr(logprobs, 'content') and logprobs.content:
                            print(f"    📊 {len(logprobs.content)} tokens com logprobs")
                            
                            total_logprob = 0.0
                            token_details = []
                            
                            for token_logprob in logprobs.content:
                                token = token_logprob.token
                                logprob = token_logprob.logprob
                                
                                total_logprob += logprob
                                token_details.append({
                                    "token": token,
                                    "logprob": logprob
                                })
                            
                            # Calcular NLL
                            nll = -total_logprob
                            perplexity = math.exp(nll / len(logprobs.content))
                            
                            result.update({
                                "nll_calculable": True,
                                "token_count": len(logprobs.content),
                                "total_logprob": total_logprob,
                                "nll_value": nll,
                                "perplexity": perplexity,
                                "token_details": token_details[:5]  # Primeiros 5 tokens
                            })
                            
                            print(f"    📊 NLL: {nll:.4f}, Perplexity: {perplexity:.4f}")
                    
                    results.append(result)
                    
                except Exception as logprob_error:
                    print(f"  ❌ Logprobs não suportados: {logprob_error}")
                    results.append({
                        "model": model_name,
                        "provider": "Groq",
                        "status": "partial",
                        "basic_functionality": True,
                        "logprobs_available": False,
                        "logprobs_error": str(logprob_error)
                    })
                    
            except Exception as e:
                print(f"  ❌ Modelo não funciona: {e}")
                results.append({
                    "model": model_name,
                    "provider": "Groq",
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def analyze_comprehensive_results(self, google_result: Dict, groq_results: List[Dict]):
        """Análise abrangente de todos os resultados"""
        
        self.print_section("ANÁLISE ABRANGENTE DOS RESULTADOS")
        
        print("📊 RESUMO COMPLETO:\n")
        
        # Análise Google
        print("🔵 GOOGLE GEMINI 2.0 FLASH LITE:")
        if google_result["status"] == "success":
            print(f"   ✅ Funcionando")
            print(f"   📊 NLL Calculável: {'✅' if google_result.get('nll_calculable') else '❌'}")
            
            if google_result.get('nll_calculable'):
                print(f"   📈 NLL: {google_result['nll_value']:.4f}")
                print(f"   📈 Perplexity: {google_result['perplexity']:.4f}")
                print(f"   🔢 Tokens: {google_result['token_count']}")
        else:
            print(f"   ❌ Erro: {google_result.get('error')}")
        
        # Análise Groq
        print(f"\n🟢 GROQ MODELS ({len(groq_results)} testados):")
        
        working_models = []
        logprobs_models = []
        nll_models = []
        
        for result in groq_results:
            model = result["model"]
            status = result["status"]
            
            print(f"\n   🤖 {model}:")
            
            if status == "success":
                print(f"      ✅ Totalmente funcional")
                working_models.append(model)
                
                if result.get("logprobs_available"):
                    print(f"      📊 Logprobs: ✅")
                    logprobs_models.append(model)
                    
                    if result.get("nll_calculable"):
                        print(f"      📈 NLL: ✅ ({result['nll_value']:.4f})")
                        nll_models.append((model, result['nll_value']))
                    else:
                        print(f"      📈 NLL: ❌")
                else:
                    print(f"      📊 Logprobs: ❌")
                    
            elif status == "partial":
                print(f"      ⚠️ Funcional básico, sem logprobs")
                working_models.append(model)
                
            else:
                print(f"      ❌ Não funcional: {result.get('error', 'Erro desconhecido')}")
        
        # Estatísticas finais
        print(f"\n📈 ESTATÍSTICAS FINAIS:")
        print(f"   🤖 Modelos funcionais: {len(working_models)}/{len(groq_results) + 1}")
        print(f"   📊 Com logprobs: {len(logprobs_models) + (1 if google_result.get('nll_calculable') else 0)}")
        print(f"   📈 NLL calculável: {len(nll_models) + (1 if google_result.get('nll_calculable') else 0)}")
        
        # Recomendações específicas
        print(f"\n💡 RECOMENDAÇÕES ESPECÍFICAS:")
        
        if nll_models:
            print(f"✅ MELHORES OPÇÕES PARA NLL:")
            for model, nll_value in sorted(nll_models, key=lambda x: x[1]):
                print(f"   🏆 {model}: NLL = {nll_value:.4f}")
        
        if google_result.get('nll_calculable'):
            print(f"✅ Google Gemini: NLL = {google_result['nll_value']:.4f}")
        
        if logprobs_models:
            print(f"\n✅ MODELOS GROQ COM LOGPROBS:")
            for model in logprobs_models:
                print(f"   📊 {model}")
        
        if not nll_models and not google_result.get('nll_calculable'):
            print(f"\n⚠️ ALTERNATIVAS RECOMENDADAS:")
            print(f"   1. Use modelos locais (Ollama/Hugging Face)")
            print(f"   2. APIs especializadas (OpenAI com logprobs)")
            print(f"   3. Estimativas via múltiplo sampling")
    
    async def run_comprehensive_tests(self):
        """Executar todos os testes abrangentes"""
        
        print("🧪 TESTE ABRANGENTE DE ACESSO AOS LOGS NLL")
        print("=" * 70)
        
        # Testar Google Gemini em detalhes
        google_result = await self.test_google_gemini_detailed()
        
        # Testar múltiplos modelos Groq
        groq_results = await self.test_groq_models_comprehensive()
        
        # Análise final
        self.analyze_comprehensive_results(google_result, groq_results)
        
        # Salvar resultados
        all_results = {
            "google_gemini": google_result,
            "groq_models": groq_results,
            "test_prompt": self.test_prompt,
            "timestamp": "2024-12-19"
        }
        
        try:
            with open("comprehensive_nll_results.json", 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Resultados detalhados salvos em: comprehensive_nll_results.json")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
        
        return all_results

async def main():
    """Função principal"""
    
    tester = EnhancedNLLTester()
    await tester.run_comprehensive_tests()
    
    print(f"\n🏁 Teste abrangente concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 