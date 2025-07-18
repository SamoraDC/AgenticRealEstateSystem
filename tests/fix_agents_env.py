#!/usr/bin/env python3
"""
Script para corrigir carregamentos de .env nos agentes.
Remove carregamentos duplicados e centraliza configuração.
"""

import re
from pathlib import Path

def fix_agent_file(file_path: Path):
    """Corrige um arquivo de agente removendo carregamentos de .env."""
    
    print(f"🔧 Corrigindo {file_path}...")
    
    # Ler conteúdo
    content = file_path.read_text(encoding='utf-8')
    
    # Padrões para remover
    patterns_to_remove = [
        r'from dotenv import load_dotenv\n',
        r'from pathlib import Path\n',
        r'import os\n',
        r'\s*# Carregar \.env.*?\n',
        r'\s*current_dir = Path.*?\n',
        r'\s*root_dir = current_dir.*?\n', 
        r'\s*env_path = root_dir.*?\n',
        r'\s*load_dotenv\(env_path\)\n',
        r'\s*# Tentar várias formas.*?\n',
        r'\s*openrouter_key = \(\s*os\.getenv.*?\s*\)\n',
        r'\s*self\.logger\.info\(f"🔑.*?\n'
    ]
    
    # Aplicar remoções
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Substituir linha de obtenção da chave
    content = re.sub(
        r'openrouter_key = \(\s*os\.getenv.*?\)',
        'openrouter_key = self.settings.apis.openrouter_key or ""',
        content,
        flags=re.MULTILINE | re.DOTALL
    )
    
    # Limpar linhas vazias excessivas
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Escrever conteúdo corrigido
    file_path.write_text(content, encoding='utf-8')
    print(f"✅ {file_path} corrigido!")

def main():
    """Função principal."""
    
    print("🚀 Iniciando correção de carregamentos de .env nos agentes...")
    
    # Arquivos para corrigir
    agent_files = [
        Path("app/agents/search.py"),
        Path("app/agents/scheduling.py")
    ]
    
    for file_path in agent_files:
        if file_path.exists():
            fix_agent_file(file_path)
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print("✅ Correção concluída!")

if __name__ == "__main__":
    main() 