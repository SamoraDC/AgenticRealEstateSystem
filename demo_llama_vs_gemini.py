#!/usr/bin/env python3
"""
DEMONSTRAÇÃO FINAL: llama-3.1-8b-instant (Groq) vs Google Gemini para NLL

RESULTADO ESPERADO:
- llama-3.1-8b-instant: ✅ Texto básico, ❌ Sem logprobs/NLL
- Google Gemini: ✅ Texto + ✅ NLL via sampling

DEMONSTRAÇÃO: Comparação lado a lado das capacidades
"""

import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class LlamaVsGeminiComparator:
    """Comparador final: llama-3.1-8b-instant vs Google Gemini"""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Texto de teste
        self.test_text = "Artificial intelligence revolutionizes how we process information and make decisions."
        
        self.setup_clients()
    
    def setup_clients(self):
        """Configurar clientes"""
        
        # Google Gemini
        if self.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_api_key)
                self.google_model = genai.GenerativeModel('gemini-2.0-flash-lite')
                print("✅ Google Gemini configurado")
            except ImportError:
                print("❌ Google Generative AI não disponível")
                self.google_model = None
        else:
            self.google_model = None
        
        # Groq llama-3.1-8b-instant
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                print("✅ Groq llama-3.1-8b-instant configurado")
            except ImportError:
                print("❌ Groq não disponível")
                self.groq_client = None
        else:
            self.groq_client = None
    
    def print_section(self, title: str):
        """Imprimir seção formatada"""
        print(f"\n{'='*70}")
        print(f" {title}")
        print(f"{'='*70}")
    
    async def test_llama_instant(self) -> Dict[str, Any]:
        """Testar llama-3.1-8b-instant"""
        
        print("🟢 TESTANDO: llama-3.1-8b-instant (Groq)")
        print("-" * 50)
        
        if not self.groq_client:
            return {"error": "Groq não disponível"}
        
        result = {
            "model": "llama-3.1-8b-instant",
            "provider": "Groq",
            "basic_functionality": False,
            "logprobs_available": False,
            "nll_calculable": False
        }
        
        # Teste 1: Funcionalidade básica
        print(f"📝 Texto: {self.test_text}")
        print("🔍 Testando funcionalidade básica...")
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": f"Analise este texto: {self.test_text}"}],
                temperature=0.3,
                max_tokens=100
            )
            
            response_text = response.choices[0].message.content
            print(f"✅ Resposta básica recebida ({len(response_text)} chars)")
            print(f"📤 Resposta: {response_text[:120]}...")
            
            result.update({
                "basic_functionality": True,
                "response_text": response_text,
                "response_length": len(response_text)
            })
            
        except Exception as e:
            print(f"❌ Erro básico: {e}")
            result["basic_error"] = str(e)
            return result
        
        # Teste 2: Logprobs
        print("\n🔍 Testando logprobs...")
        
        try:
            logprobs_response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": self.test_text}],
                temperature=0.1,
                max_tokens=50,
                logprobs=True,
                top_logprobs=5
            )
            
            print("✅ Logprobs suportados! (surpresa)")
            result["logprobs_available"] = True
            # Aqui poderia analisar os logprobs...
            
        except Exception as e:
            print(f"❌ Logprobs rejeitados: {e}")
            result["logprobs_error"] = str(e)
        
        print("\n📊 RESULTADO llama-3.1-8b-instant:")
        print(f"   ✅ Funcionalidade básica: {'SIM' if result['basic_functionality'] else 'NÃO'}")
        print(f"   📊 Logprobs: {'SIM' if result['logprobs_available'] else 'NÃO'}")
        print(f"   🎯 NLL: {'SIM' if result['nll_calculable'] else 'NÃO'}")
        
        return result
    
    async def test_google_gemini(self) -> Dict[str, Any]:
        """Testar Google Gemini"""
        
        print("\n🔵 TESTANDO: Google Gemini 2.0 Flash Lite")
        print("-" * 50)
        
        if not self.google_model:
            return {"error": "Google Gemini não disponível"}
        
        result = {
            "model": "gemini-2.0-flash-lite",
            "provider": "Google",
            "basic_functionality": False,
            "nll_calculable": False
        }
        
        # Teste 1: Funcionalidade básica
        print(f"📝 Texto: {self.test_text}")
        print("🔍 Testando funcionalidade básica...")
        
        try:
            basic_response = self.google_model.generate_content(
                f"Analise este texto: {self.test_text}",
                generation_config={"temperature": 0.3, "max_output_tokens": 100}
            )
            
            response_text = basic_response.text
            print(f"✅ Resposta básica recebida ({len(response_text)} chars)")
            print(f"📤 Resposta: {response_text[:120]}...")
            
            result.update({
                "basic_functionality": True,
                "response_text": response_text,
                "response_length": len(response_text)
            })
            
        except Exception as e:
            print(f"❌ Erro básico: {e}")
            result["basic_error"] = str(e)
            return result
        
        # Teste 2: NLL via sampling
        print("\n🔍 Testando NLL via sampling...")
        
        try:
            # Usar calculadora já implementada
            from nll_calculator_final import calculate_nll
            
            nll_value = await calculate_nll(self.test_text)
            
            print(f"✅ NLL calculado via sampling: {nll_value:.4f}")
            
            result.update({
                "nll_calculable": True,
                "nll_value": nll_value,
                "nll_method": "sampling_estimation"
            })
            
        except Exception as e:
            print(f"❌ Erro NLL: {e}")
            result["nll_error"] = str(e)
        
        print("\n📊 RESULTADO Google Gemini:")
        print(f"   ✅ Funcionalidade básica: {'SIM' if result['basic_functionality'] else 'NÃO'}")
        print(f"   📊 Logprobs: ⚠️ Parcial (via sampling)")
        print(f"   🎯 NLL: {'SIM' if result['nll_calculable'] else 'NÃO'}")
        if result.get('nll_calculable'):
            print(f"   📈 NLL obtido: {result['nll_value']:.4f}")
        
        return result
    
    def generate_final_comparison(self, llama_result: Dict, gemini_result: Dict):
        """Gerar comparação final detalhada"""
        
        self.print_section("COMPARAÇÃO FINAL: llama-3.1-8b-instant vs Google Gemini")
        
        print(f"🎯 OBJETIVO: Calcular NLL para texto de teste")
        print(f"📝 Texto analisado: '{self.test_text}'")
        
        # Tabela de comparação
        print(f"\n📋 TABELA COMPARATIVA:")
        print("-" * 70)
        print(f"{'Aspecto':<20} {'llama-3.1-8b':<20} {'Google Gemini':<25}")
        print("-" * 70)
        
        # Funcionalidade básica
        llama_basic = "✅ SIM" if llama_result.get("basic_functionality") else "❌ NÃO"
        gemini_basic = "✅ SIM" if gemini_result.get("basic_functionality") else "❌ NÃO"
        print(f"{'Funcionalidade':<20} {llama_basic:<20} {gemini_basic:<25}")
        
        # Logprobs
        llama_logprobs = "✅ SIM" if llama_result.get("logprobs_available") else "❌ NÃO"
        gemini_logprobs = "⚠️ Parcial"
        print(f"{'Logprobs':<20} {llama_logprobs:<20} {gemini_logprobs:<25}")
        
        # NLL
        llama_nll = "✅ SIM" if llama_result.get("nll_calculable") else "❌ NÃO"
        gemini_nll = "✅ SIM" if gemini_result.get("nll_calculable") else "❌ NÃO"
        print(f"{'NLL Calculável':<20} {llama_nll:<20} {gemini_nll:<25}")
        
        # Valor NLL
        llama_nll_val = f"{llama_result.get('nll_value', 0):.4f}" if llama_result.get("nll_calculable") else "N/A"
        gemini_nll_val = f"{gemini_result.get('nll_value', 0):.4f}" if gemini_result.get("nll_calculable") else "N/A"
        print(f"{'Valor NLL':<20} {llama_nll_val:<20} {gemini_nll_val:<25}")
        
        print("-" * 70)
        
        # Análise detalhada
        print(f"\n🔍 ANÁLISE DETALHADA:")
        
        print(f"\n🟢 llama-3.1-8b-instant (Groq):")
        if llama_result.get("basic_functionality"):
            print(f"   ✅ Gera texto de qualidade")
            print(f"   📝 Resposta: {len(llama_result.get('response_text', ''))} caracteres")
        
        if not llama_result.get("logprobs_available"):
            error = llama_result.get("logprobs_error", "Erro desconhecido")
            print(f"   ❌ Logprobs: {error}")
            print(f"   ❌ Consequência: Impossível calcular NLL diretamente")
        
        print(f"\n🔵 Google Gemini 2.0 Flash Lite:")
        if gemini_result.get("basic_functionality"):
            print(f"   ✅ Gera texto de qualidade")
            print(f"   📝 Resposta: {len(gemini_result.get('response_text', ''))} caracteres")
        
        if gemini_result.get("nll_calculable"):
            print(f"   ✅ NLL via sampling: {gemini_result['nll_value']:.4f}")
            print(f"   ✅ Método: Estimação por amostragem múltipla")
        else:
            print(f"   ❌ NLL falhou: {gemini_result.get('nll_error', 'Erro desconhecido')}")
        
        # Conclusão e recomendações
        print(f"\n🎯 CONCLUSÃO:")
        
        if gemini_result.get("nll_calculable") and not llama_result.get("nll_calculable"):
            print(f"🏆 VENCEDOR PARA NLL: Google Gemini")
            print(f"   📈 NLL obtido: {gemini_result['nll_value']:.4f}")
            print(f"   💡 Recomendação: Use Google Gemini para cálculos de NLL")
        
        elif llama_result.get("nll_calculable") and not gemini_result.get("nll_calculable"):
            print(f"🏆 VENCEDOR PARA NLL: llama-3.1-8b-instant")
            print(f"   📈 NLL obtido: {llama_result['nll_value']:.4f}")
            print(f"   💡 Recomendação: Use llama-3.1-8b-instant para NLL")
        
        elif not llama_result.get("nll_calculable") and not gemini_result.get("nll_calculable"):
            print(f"❌ NENHUM MODELO CALCULOU NLL")
            print(f"   💡 Recomendação: Considere OpenAI ou modelos locais")
        
        else:
            print(f"🤝 AMBOS CALCULARAM NLL")
            print(f"   📊 llama-3.1-8b: {llama_result.get('nll_value', 0):.4f}")
            print(f"   📊 Google Gemini: {gemini_result.get('nll_value', 0):.4f}")
        
        print(f"\n🔧 PARA USO GERAL:")
        if llama_result.get("basic_functionality"):
            print(f"   ✅ llama-3.1-8b-instant: Excelente para geração de texto")
        if gemini_result.get("basic_functionality"):
            print(f"   ✅ Google Gemini: Excelente para texto + análises")

async def main():
    """Função principal da demonstração"""
    
    print("🔬 DEMONSTRAÇÃO: llama-3.1-8b-instant vs Google Gemini")
    print("=" * 70)
    print("Comparando capacidades para cálculo de NLL")
    
    comparator = LlamaVsGeminiComparator()
    
    # Testar ambos os modelos
    llama_result = await comparator.test_llama_instant()
    gemini_result = await comparator.test_google_gemini()
    
    # Gerar comparação final
    comparator.generate_final_comparison(llama_result, gemini_result)
    
    print(f"\n🏁 Demonstração concluída!")
    print(f"💡 Use o modelo que melhor atende suas necessidades de NLL.")

if __name__ == "__main__":
    asyncio.run(main()) 