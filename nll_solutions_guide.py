#!/usr/bin/env python3
"""
GUIA COMPLETO: Soluções para Cálculo de Negative Log Likelihood (NLL)

RESULTADOS DOS TESTES:
- Google Gemini 2.0 Flash Lite: ❌ Tem avg_logprobs mas não logprobs por token
- Groq LLaMA 4 Scout: ❌ Não suporta logprobs  
- Groq outros modelos: ❌ Descontinuados ou sem suporte a logprobs

SOLUÇÕES ALTERNATIVAS IMPLEMENTADAS:
1. OpenAI API (GPT models) - logprobs completos ✅
2. Estimação via Multiple Sampling 
3. Integração com Hugging Face Transformers
4. Métodos de aproximação matemática
"""

import os
import json
import math
import asyncio
import traceback
from typing import Dict, List, Optional, Any, Tuple
from dotenv import load_dotenv

load_dotenv()

# === SOLUÇÃO 1: OpenAI API com Logprobs ===
class OpenAINLLCalculator:
    """Calculador de NLL usando OpenAI API que suporta logprobs completos"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    async def calculate_nll_openai(self, text: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Calcular NLL usando OpenAI API com logprobs"""
        
        if not self.api_key:
            return {"error": "OPENAI_API_KEY não configurada"}
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            print(f"🤖 Testando {model} com logprobs...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": f"Complete: {text}"}
                ],
                max_tokens=50,
                temperature=0.1,
                logprobs=True,
                top_logprobs=5
            )
            
            choice = response.choices[0]
            
            if hasattr(choice, 'logprobs') and choice.logprobs:
                logprobs = choice.logprobs
                
                if hasattr(logprobs, 'content') and logprobs.content:
                    total_logprob = 0.0
                    token_details = []
                    
                    for token_info in logprobs.content:
                        token = token_info.token
                        logprob = token_info.logprob
                        
                        total_logprob += logprob
                        token_details.append({
                            "token": token,
                            "logprob": logprob
                        })
                    
                    nll = -total_logprob
                    perplexity = math.exp(nll / len(logprobs.content))
                    
                    return {
                        "status": "success",
                        "model": model,
                        "provider": "OpenAI",
                        "nll_value": nll,
                        "perplexity": perplexity,
                        "token_count": len(logprobs.content),
                        "total_logprob": total_logprob,
                        "token_details": token_details,
                        "response_text": choice.message.content
                    }
            
            return {"error": "Logprobs não encontrados na resposta"}
            
        except ImportError:
            return {"error": "OpenAI library não instalada (pip install openai)"}
        except Exception as e:
            return {"error": f"Erro OpenAI: {e}"}

# === SOLUÇÃO 2: Estimação via Multiple Sampling ===
class SamplingNLLEstimator:
    """Estimador de NLL via amostragem múltipla"""
    
    def __init__(self, api_key: str, provider: str = "google"):
        self.api_key = api_key
        self.provider = provider
        
    async def estimate_nll_via_sampling(self, prompt: str, target_completion: str, 
                                       num_samples: int = 10) -> Dict[str, Any]:
        """Estimar NLL via amostragem múltipla"""
        
        print(f"🎲 Estimando NLL via {num_samples} amostras...")
        
        try:
            if self.provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-2.0-flash-lite')
                
                # Gerar múltiplas amostras com diferentes temperaturas
                temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]
                samples = []
                
                for temp in temperatures:
                    for i in range(num_samples // len(temperatures)):
                        response = model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=temp,
                                max_output_tokens=50
                            )
                        )
                        
                        samples.append({
                            "temperature": temp,
                            "sample": i,
                            "response": response.text.strip(),
                            "similarity": self._calculate_similarity(response.text.strip(), target_completion)
                        })
                
                # Estimar probabilidade baseada na frequência de respostas similares
                similar_samples = [s for s in samples if s["similarity"] > 0.8]
                estimated_prob = len(similar_samples) / len(samples)
                estimated_nll = -math.log(max(estimated_prob, 1e-10))  # Evitar log(0)
                
                return {
                    "status": "success",
                    "method": "sampling_estimation",
                    "estimated_nll": estimated_nll,
                    "estimated_probability": estimated_prob,
                    "similar_samples": len(similar_samples),
                    "total_samples": len(samples),
                    "samples": samples[:5]  # Primeiras 5 amostras
                }
                
        except Exception as e:
            return {"error": f"Erro na estimação: {e}"}
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcular similaridade simples entre textos"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0

# === SOLUÇÃO 3: Hugging Face Transformers (Local) ===
class HuggingFaceNLLCalculator:
    """Calculador de NLL usando modelos locais do Hugging Face"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        
    async def calculate_nll_local(self, text: str, model_name: str = "gpt2") -> Dict[str, Any]:
        """Calcular NLL usando modelo local Hugging Face"""
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            print(f"🔧 Carregando modelo local: {model_name}")
            
            # Carregar modelo e tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Tokenizar texto
            inputs = tokenizer.encode(text, return_tensors="pt")
            
            # Calcular logits
            with torch.no_grad():
                outputs = model(inputs, labels=inputs)
                loss = outputs.loss
                logits = outputs.logits
            
            # Calcular NLL por token
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = inputs[..., 1:].contiguous()
            
            # Calcular probabilidades
            log_probs = torch.nn.functional.log_softmax(shift_logits, dim=-1)
            
            # Extrair log probabilities para tokens verdadeiros
            token_log_probs = []
            for i in range(shift_labels.size(1)):
                token_id = shift_labels[0, i].item()
                token_log_prob = log_probs[0, i, token_id].item()
                token = tokenizer.decode([token_id])
                
                token_log_probs.append({
                    "token": token,
                    "token_id": token_id,
                    "logprob": token_log_prob
                })
            
            # Calcular métricas finais
            total_log_prob = sum(t["logprob"] for t in token_log_probs)
            nll = -total_log_prob
            perplexity = math.exp(loss.item())
            
            return {
                "status": "success",
                "method": "local_huggingface",
                "model": model_name,
                "nll_value": nll,
                "perplexity": perplexity,
                "token_count": len(token_log_probs),
                "total_logprob": total_log_prob,
                "token_details": token_log_probs,
                "cross_entropy_loss": loss.item()
            }
            
        except ImportError:
            return {"error": "Transformers não instalado (pip install transformers torch)"}
        except Exception as e:
            return {"error": f"Erro Hugging Face: {e}"}

# === SOLUÇÃO 4: Aproximação Matemática ===
class MathematicalNLLApproximator:
    """Aproximador de NLL usando métodos matemáticos"""
    
    def approximate_nll_length_based(self, text: str, avg_entropy_per_char: float = 4.5) -> Dict[str, Any]:
        """Aproximar NLL baseado no comprimento e entropia média"""
        
        # Estimativas baseadas em estudos de entropia da linguagem natural
        # Referência: Shannon (1951), Brown et al. (1992)
        
        char_count = len(text)
        word_count = len(text.split())
        
        # Entropia estimada por caractere (bits)
        estimated_entropy_bits = char_count * avg_entropy_per_char
        estimated_entropy_nats = estimated_entropy_bits * math.log(2)  # Converter para nats
        
        # Aproximação baseada em frequência de palavras
        unique_words = len(set(text.lower().split()))
        repetition_factor = word_count / unique_words if unique_words > 0 else 1
        
        # Ajustar por complexidade
        complexity_factor = 1.0
        if any(char.isupper() for char in text):
            complexity_factor *= 0.95  # Texto com maiúsculas é mais previsível
        if any(char.isdigit() for char in text):
            complexity_factor *= 1.1   # Números são menos previsíveis
        
        approximate_nll = estimated_entropy_nats * complexity_factor / repetition_factor
        approximate_perplexity = math.exp(approximate_nll / word_count)
        
        return {
            "status": "success",
            "method": "mathematical_approximation",
            "approximate_nll": approximate_nll,
            "approximate_perplexity": approximate_perplexity,
            "char_count": char_count,
            "word_count": word_count,
            "unique_words": unique_words,
            "repetition_factor": repetition_factor,
            "complexity_factor": complexity_factor,
            "entropy_per_char_bits": avg_entropy_per_char
        }

# === MAIN: Demonstração de Todas as Soluções ===
class ComprehensiveNLLSuite:
    """Suite completa para cálculo e estimação de NLL"""
    
    def __init__(self):
        self.openai_calc = OpenAINLLCalculator()
        self.sampling_est = SamplingNLLEstimator(
            os.getenv("GOOGLE_API_KEY", ""), "google"
        )
        self.hf_calc = HuggingFaceNLLCalculator()
        self.math_approx = MathematicalNLLApproximator()
        
    async def run_all_solutions(self, test_text: str) -> Dict[str, Any]:
        """Executar todas as soluções disponíveis"""
        
        print("🧪 EXECUTANDO TODAS AS SOLUÇÕES DE NLL")
        print("=" * 60)
        print(f"📝 Texto de teste: {test_text}")
        print("=" * 60)
        
        results = {}
        
        # 1. OpenAI API
        print("\n🔵 SOLUÇÃO 1: OpenAI API")
        try:
            openai_result = await self.openai_calc.calculate_nll_openai(test_text)
            results["openai"] = openai_result
            
            if openai_result.get("status") == "success":
                print(f"✅ NLL: {openai_result['nll_value']:.4f}")
                print(f"✅ Perplexity: {openai_result['perplexity']:.4f}")
            else:
                print(f"❌ {openai_result.get('error')}")
        except Exception as e:
            results["openai"] = {"error": str(e)}
            print(f"❌ Erro: {e}")
        
        # 2. Sampling Estimation  
        print("\n🟡 SOLUÇÃO 2: Estimação via Sampling")
        try:
            sampling_result = await self.sampling_est.estimate_nll_via_sampling(
                "Complete this text:", test_text, num_samples=5
            )
            results["sampling"] = sampling_result
            
            if sampling_result.get("status") == "success":
                print(f"✅ NLL Estimado: {sampling_result['estimated_nll']:.4f}")
                print(f"✅ Probabilidade: {sampling_result['estimated_probability']:.4f}")
            else:
                print(f"❌ {sampling_result.get('error')}")
        except Exception as e:
            results["sampling"] = {"error": str(e)}
            print(f"❌ Erro: {e}")
        
        # 3. Hugging Face Local
        print("\n🟢 SOLUÇÃO 3: Hugging Face Local")
        try:
            hf_result = await self.hf_calc.calculate_nll_local(test_text, "distilgpt2")
            results["huggingface"] = hf_result
            
            if hf_result.get("status") == "success":
                print(f"✅ NLL: {hf_result['nll_value']:.4f}")
                print(f"✅ Perplexity: {hf_result['perplexity']:.4f}")
            else:
                print(f"❌ {hf_result.get('error')}")
        except Exception as e:
            results["huggingface"] = {"error": str(e)}
            print(f"❌ Erro: {e}")
        
        # 4. Aproximação Matemática
        print("\n🟣 SOLUÇÃO 4: Aproximação Matemática")
        try:
            math_result = self.math_approx.approximate_nll_length_based(test_text)
            results["mathematical"] = math_result
            
            print(f"✅ NLL Aproximado: {math_result['approximate_nll']:.4f}")
            print(f"✅ Perplexity Aproximada: {math_result['approximate_perplexity']:.4f}")
        except Exception as e:
            results["mathematical"] = {"error": str(e)}
            print(f"❌ Erro: {e}")
        
        # Resumo Final
        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL DE SOLUÇÕES NLL")
        print("=" * 60)
        
        working_solutions = []
        for method, result in results.items():
            if result.get("status") == "success":
                working_solutions.append(method)
                nll_key = "nll_value" if "nll_value" in result else "estimated_nll" if "estimated_nll" in result else "approximate_nll"
                nll_value = result.get(nll_key, "N/A")
                print(f"✅ {method.upper()}: NLL = {nll_value}")
            else:
                print(f"❌ {method.upper()}: {result.get('error', 'Erro desconhecido')}")
        
        print(f"\n🎯 {len(working_solutions)}/4 soluções funcionais")
        
        if working_solutions:
            print(f"🏆 RECOMENDAÇÃO: Use '{working_solutions[0]}' para cálculos de NLL")
        else:
            print("⚠️ Nenhuma solução funcional - verifique dependências e chaves API")
        
        # Salvar resultados
        try:
            with open("nll_comprehensive_solutions.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Resultados salvos em: nll_comprehensive_solutions.json")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
        
        return results

async def main():
    """Demonstração de todas as soluções"""
    
    # Texto de teste
    test_text = "Machine learning enables computers to learn patterns from data."
    
    suite = ComprehensiveNLLSuite()
    results = await suite.run_all_solutions(test_text)
    
    print("\n🏁 Teste de soluções NLL concluído!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure OPENAI_API_KEY para melhor precisão")
    print("2. Instale transformers/torch para modelos locais: pip install transformers torch")
    print("3. Use aproximação matemática como fallback rápido")
    print("4. Combine múltiplas estimativas para validação cruzada")

if __name__ == "__main__":
    asyncio.run(main()) 