#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
promover_materia.py - Promocao de materias da pre-curadoria para producao
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Fluxo:
  1. Recebe um arquivo da pasta pre_curadoria/AAAA/MM/DD/slug.txt
  2. Altera o metadado 'status:' no cabecalho para 'Aprovada'
  3. Copia o arquivo atualizado para materias/conteudo/
  4. Executa build_materias.py para compilar o HTML e atualizar noticias_curadoria.json

Uso:
  python scripts/promover_materia.py --arquivo pre_curadoria/2026/08/08/exemplo-materia.txt
"""

import sys
import os
import re
import argparse
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Ajuste de path para importacao do config.py
sys.path.insert(0, str(Path(__file__).parent))
import config


def promover_materia(caminho_arquivo_str):
    caminho_origem = Path(caminho_arquivo_str)

    if not caminho_origem.is_absolute():
        caminho_origem = config.RAIZ_PROJETO / caminho_origem

    if not caminho_origem.exists() or not caminho_origem.is_file():
        print(f'[ERRO] Arquivo nao encontrado: {caminho_origem}')
        sys.exit(1)

    conteudo = caminho_origem.read_text(encoding='utf-8')

    # Atualizacao do metadado status no cabecalho YAML
    if conteudo.startswith('---'):
        partes = conteudo.split('---', 2)
        if len(partes) >= 3:
            bloco_meta = partes[1]
            linhas_meta = []
            tem_status = False
            for linha in bloco_meta.splitlines():
                if linha.startswith('status:'):
                    linhas_meta.append('status: Aprovada')
                    tem_status = True
                elif linha.startswith('status_triagem:'):
                    linhas_meta.append('status_triagem: Aprovada')
                else:
                    linhas_meta.append(linha)
            if not tem_status:
                linhas_meta.append('status: Aprovada')
            partes[1] = '\n' + '\n'.join(linhas_meta) + '\n'
            conteudo_atualizado = '---'.join(partes)
        else:
            conteudo_atualizado = conteudo
    else:
        conteudo_atualizado = f'---\nstatus: Aprovada\n---\n\n' + conteudo

    # Destino em materias/conteudo/
    config.DIRETORIO_RASCUNHOS.mkdir(parents=True, exist_ok=True)
    caminho_destino = config.DIRETORIO_RASCUNHOS / caminho_origem.name
    caminho_destino.write_text(conteudo_atualizado, encoding='utf-8')

    print(f'[OK] Arquivo promovido e salvo em: {caminho_destino}')

    # Execucao do pipeline build_materias.py
    script_build = config.RAIZ_PROJETO / 'build_materias.py'
    if not script_build.exists():
        print(f'[ERRO] Script build_materias.py nao encontrado em: {script_build}')
        sys.exit(1)

    cmd = [sys.executable, str(script_build), '--arquivo', caminho_destino.name]
    print(f'[INFO] Executando build_materias.py para {caminho_destino.name}...')

    resultado = subprocess.run(cmd, cwd=str(config.RAIZ_PROJETO), capture_output=True, text=True, encoding='utf-8')

    if resultado.returncode == 0:
        print(resultado.stdout)
        print('[SUCESSO] Materia promovida, HTML gerado e noticias_curadoria.json atualizado.')
    else:
        print(f'[ERRO] Falha ao executar build_materias.py:')
        print(resultado.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Promover materia da pre-curadoria para producao.'
    )
    parser.add_argument(
        '--arquivo',
        type=str,
        required=True,
        help='Caminho relativo ou absoluto para o arquivo em pre_curadoria/ (ex: pre_curadoria/2026/08/08/slug.txt)'
    )
    args = parser.parse_args()

    promover_materia(args.arquivo)


if __name__ == '__main__':
    main()
