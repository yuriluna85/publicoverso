#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_completo.py - Orquestrador do pipeline completo do Publicoverso
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Executa em sequência:
  1. minerador_historias.py     - Minera novas histórias gerais de servidores
  2. minerador_protagonistas.py - Minera os 5 eixos temáticos de protagonistas humanos
  3. radar_concursos.py         - Atualiza o radar de editais de concursos
  4. build_materias.py          - Gera as páginas HTML dos rascunhos aprovados

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
SCRIPT_MINERADOR_HISTORIAS = RAIZ / 'scripts' / 'minerador_historias.py'
SCRIPT_MINERADOR_PROTAGONISTAS = RAIZ / 'scripts' / 'minerador_protagonistas.py'
SCRIPT_RADAR_MOVIMENTACAO = RAIZ / 'scripts' / 'radar_movimentacao_servidores.py'
SCRIPT_RADAR = RAIZ / 'scripts' / 'radar_concursos.py'
SCRIPT_CLASSIFICADOR = RAIZ / 'scripts' / 'classificador_noticias.py'
SCRIPT_BUILD = RAIZ / 'build_materias.py'


def executar(script, descrição, dry_run=False):
    """Executa um script Python e exibe o resultado."""
    print(f'\n[INICIANDO] {descrição}')
    print(f'  Script: {script}')
    cmd = [sys.executable, str(script)]
    if dry_run:
        cmd.append('--dry-run')
    início = datetime.now()
    resultado = subprocess.run(
        cmd,
        capture_output=False,
        text=True,
        encoding='utf-8',
    )
    duracao = (datetime.now() - início).seconds
    status = '[OK]' if resultado.returncode == 0 else '[ERRO]'
    print(f'{status} {descrição} concluído em {duracao}s (codigo: {resultado.returncode})')
    return resultado.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Orquestrador do pipeline completo.'
    )
    parser.add_argument('--apenas-mineracao', action='store_true',
                        help='Executa apenas a mineracao de histórias e concursos')
    parser.add_argument('--apenas-build', action='store_true',
                        help='Executa apenas o build das páginas HTML')
    parser.add_argument('--dry-run', action='store_true',
                        help='Executa o pipeline em modo teste sem alterar dados no disco')
    args = parser.parse_args()

    print('=' * 60)
    print('PUBLICOVERSO - Pipeline Completo')
    print(f'Início: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    if args.dry_run:
        print('[MODO DRY-RUN ATIVADO: Nenhum arquivo de dados será alterado no disco]')
    print('=' * 60)

    sucesso_total = True

    if not args.apenas_build:
        ok1 = executar(SCRIPT_MINERADOR_HISTORIAS, 'Minerador de Histórias Gerais de Servidores', dry_run=args.dry_run)
        ok2 = executar(SCRIPT_MINERADOR_PROTAGONISTAS, 'Minerador Especialista de Protagonistas (Vida Alem do Trabalho)', dry_run=args.dry_run)
        ok3 = executar(SCRIPT_RADAR_MOVIMENTACAO, 'Robô de Movimentação Funcional (Posse, Nomeação & Aposentadoria)', dry_run=args.dry_run)
        ok4 = executar(SCRIPT_RADAR, 'Radar de Editais de Concursos', dry_run=args.dry_run)
        ok5 = executar(SCRIPT_CLASSIFICADOR, 'Classificador Inteligente de Notícias (Policial & Segurança Pública)')
        sucesso_total = ok1 and ok2 and ok3 and ok4 and ok5

    if not args.apenas_mineracao:
        ok4 = executar(SCRIPT_BUILD, 'Build das Páginas HTML')
        sucesso_total = sucesso_total and ok4

    print('\n' + '=' * 60)
    status_final = 'CONCLUIDO COM SUCESSO' if sucesso_total else 'CONCLUIDO COM ERROS'
    print(f'PUBLICOVERSO - {status_final}')
    print(f'Fim: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
    print('=' * 60)


if __name__ == '__main__':
    main()
