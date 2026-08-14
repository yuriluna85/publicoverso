#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/sanitizar_duplicatas_precuradoria.py
-------------------------------------------
Utilitário de Higienização e Eliminação de Duplicatas na pasta `pre_curadoria/`.
Detecta arquivos com sufixos redundantes (-auto-*.txt) e slugs idênticos,
preservando apenas a versão canônica mais limpa.

Uso:
  python scripts/sanitizar_duplicatas_precuradoria.py --dry-run
  python scripts/sanitizar_duplicatas_precuradoria.py --executar
"""

import os
import sys
import re
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).parent.parent
DIR_PRE = RAIZ / 'pre_curadoria'

def sanitizar_precuradoria(executar=False):
    print("="*60)
    print("🧹 HIGIENIZAÇÃO DE DUPLICATAS - PRE_CURADORIA (PUBLICOVERSO)")
    print("="*60)
    
    if not DIR_PRE.exists():
        print(f"[ERRO] Pasta {DIR_PRE} não encontrada.")
        return

    arquivos_por_pasta = {}
    for root, dirs, files in os.walk(DIR_PRE):
        txts = [f for f in files if f.endswith('.txt') and f != 'desktop.ini']
        if txts:
            arquivos_por_pasta[root] = txts

    total_analisados = 0
    duplicatas_encontradas = []

    for pasta, arquivos in arquivos_por_pasta.items():
        vistos = {}
        for arq in sorted(arquivos):
            total_analisados += 1
            caminho_completo = Path(pasta) / arq
            
            # Normaliza o slug removendo sufixos -auto-*
            slug_limpo = re.sub(r'-auto-[a-zA-Z0-9]+\.txt$', '.txt', arq)
            slug_base = re.sub(r'\.txt$', '', slug_limpo)
            
            if slug_base in vistos:
                duplicatas_encontradas.append({
                    'duplicata': caminho_completo,
                    'original': vistos[slug_base],
                    'motivo': f'Sufixo redundante ou slug idêntico a {vistos[slug_base].name}'
                })
            else:
                vistos[slug_base] = caminho_completo

    print(f"📊 Total de Arquivos Analisados em pre_curadoria/: {total_analisados}")
    print(f"⚠️  Duplicatas Identificadas: {len(duplicatas_encontradas)}\n")

    for idx, d in enumerate(duplicatas_encontradas, 1):
        print(f"[{idx}] ❌ Duplicata: {d['duplicata'].name}")
        print(f"     📁 Pasta: {d['duplicata'].parent.relative_to(RAIZ)}")
        print(f"     ✅ Canônico Mantido: {d['original'].name}")
        print(f"     📝 Motivo: {d['motivo']}\n")

    if duplicatas_encontradas:
        if executar:
            print("🚀 Removendo arquivos duplicados...")
            removidos = 0
            for d in duplicatas_encontradas:
                try:
                    d['duplicata'].unlink()
                    removidos += 1
                except Exception as e:
                    print(f"Erro ao remover {d['duplicata']}: {e}")
            print(f"✅ {removidos} arquivos duplicados removidos com sucesso!")
        else:
            print("🔍 [MODO SEGURO - DRY RUN] Nenhum arquivo foi excluído.")
            print("Para executar a limpeza definitiva, rode: python scripts/sanitizar_duplicatas_precuradoria.py --executar")
    else:
        print("🎉 Nenhuma duplicata encontrada na pasta pre_curadoria/!")

    print("="*60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Higienizador de Duplicatas em pre_curadoria/")
    parser.add_argument("--executar", action="store_true", help="Executa a remoção dos arquivos duplicados")
    parser.add_argument("--dry-run", action="store_true", help="Modo simulação")
    args = parser.parse_args()

    sanitizar_precuradoria(executar=args.executar)
