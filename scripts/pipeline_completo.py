#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_completo.py - Orquestrador do pipeline completo do Publicoverso
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Executa em sequencia:
  1. minerador_historias.py  - Minera novas historias de servidores
  2. radar_concursos.py      - Atualiza o radar de editais de concursos
  3. build_materias.py       - Gera as paginas HTML dos rascunhos aprovados

Uso:
  python scripts/pipeline_completo.py
  python scripts/pipeline_completo.py --apenas-mineracao
  python scripts/pipeline_completo.py --apenas-build
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).parent.parent
SCRIPT_MINERADOR = RAIZ / 'scripts' / 'minerador_historias.py'
SCRIPT_RADAR = RAIZ / 'scripts' / 'radar_concursos.py'
SCRIPT_BUILD = RAIZ / 'build_materias.py'


def executar(script, descricao):
    """Executa um script Python e exibe o resultado."""
    print(f'\n[INICIANDO] {descricao}')
    print(f'  Script: {script}')
    inicio = datetime.now()
    resultado = subprocess.run(
        [sys.executable, str(script)],
        capture_output=False,
        text=True,
        encoding='utf-8',
    )
    duracao = (datetime.now() - inicio).seconds
    status = '[OK]' if resultado.returncode == 0 else '[ERRO]'
    print(f'{status} {descricao} concluido em {duracao}s (codigo: {resultado.returncode})')
    return resultado.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Orquestrador do pipeline completo.'
    )
    parser.add_argument('--apenas-mineracao', action='store_true',
                        help='Executa apenas a mineracao de historias e concursos')
    parser.add_argument('--apenas-build', action='store_true',
                        help='Executa apenas o build das paginas HTML')
    args = parser.parse_args()

    print('=' * 60)
    print('PUBLICOVERSO - Pipeline Completo')
    print(f'Inicio: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    print('=' * 60)

    sucesso_total = True

    if not args.apenas_build:
        ok1 = executar(SCRIPT_MINERADOR, 'Minerador de Historias de Servidores')
        ok2 = executar(SCRIPT_RADAR, 'Radar de Editais de Concursos')
        sucesso_total = ok1 and ok2

    if not args.apenas_mineracao:
        ok3 = executar(SCRIPT_BUILD, 'Build das Paginas HTML')
        sucesso_total = sucesso_total and ok3

    print('\n' + '=' * 60)
    status_final = 'CONCLUIDO COM SUCESSO' if sucesso_total else 'CONCLUIDO COM ERROS'
    print(f'PUBLICOVERSO - {status_final}')
    print(f'Fim: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    print('=' * 60)


if __name__ == '__main__':
    main()
