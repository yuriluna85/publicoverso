#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
radar_concursos.py - Radar de editais de concursos públicos em aberto
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Fluxo:
  1. Consulta a Serper API (Google Search) com dorks de concursos
  2. Extrai metadados estruturados de cada edital encontrado
  3. Verifica deduplicacao contra concursos_radar.json
  4. Insere novos editais com status 'Em Analise' para revisao manual
  5. Remove automaticamente editais com inscrições encerradas

Uso:
  python scripts/radar_concursos.py
  python scripts/radar_concursos.py --forcar-atualização
"""

import sys
import os
import json
import time
import re
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
import config

try:
    import requests
except ImportError:
    print('[ERRO] Biblioteca requests não encontrada. Execute: pip install requests')
    sys.exit(1)


# --- Bancas Organizadoras Reconhecidas ---
BANCAS_RECONHECIDAS = [
    'Cebraspe', 'FGV', 'FCC', 'Instituto AOCP', 'Vunesp',
    'IBFC', 'Fundatec', 'Avança SP', 'IADES', 'Idecan',
    'FUMARC', 'CESPE', 'CONSULPLAN', 'FUNDEP',
]

# --- Órgãos de Alta Relevancia (Prioridade de Destaque) ---
ORGAOS_DESTAQUE = [
    'Receita Federal', 'Banco Central', 'Senado Federal',
    'Câmara dos Deputados', 'TCU', 'CGU', 'STJ', 'STF', 'TST', 'TSE',
    'TRF', 'TRT', 'Policia Federal', 'Policia Rodoviária Federal',
    'Anatel', 'ANAC', 'ANVISA', 'IBGE', 'INPE', 'Capes',
    'Universidade Federal', 'Instituto Federal',
]


# --- Busca de Concursos via Serper API ---
def buscar_concursos_serper(dork):
    """Consulta a Serper API Google Search e retorna resultados de editais."""
    if not config.SERPER_API_KEY:
        config.registrar_log('[AVISO] SERPER_API_KEY não configurada.')
        return []

    headers = {
        'X-API-KEY': config.SERPER_API_KEY,
        'Content-Type': 'application/json',
    }
    payload = {
        'q': dork,
        'gl': 'br',
        'hl': 'pt-br',
        'num': config.MAX_RESULTADOS_POR_DORK,
    }

    try:
        resp = requests.post(config.SERPER_SEARCH_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        return dados.get('organic', [])
    except requests.RequestException as e:
        config.registrar_log(f'[ERRO] Serper (concursos): {e}')
        return []


# --- Extracao de Metadados do Edital ---
def extrair_metadados_edital(resultado):
    """
    Tenta extrair campos estruturados do titulo e snippet do resultado.
    Retorna um dict com os campos do concurso ou None se irrelevante.
    """
    titulo = resultado.get('title', '')
    snippet = resultado.get('snippet', '')
    url = resultado.get('link', '')
    texto = titulo + ' ' + snippet

    # Descarta resultados sem mencao a concurso ou processo seletivo
    if not re.search(r'concurso\s+p.blico|processo\s+seletivo|edital', texto, re.IGNORECASE):
        return None

    # Detecta esfera
    esfera = 'Federal'
    if re.search(r'municipal|prefeitura|câmara municipal', texto, re.IGNORECASE):
        esfera = 'Municipal'
    elif re.search(r'estadual|governo do estado|assembleia legislativa|tribunal de justiça', texto, re.IGNORECASE):
        esfera = 'Estadual'

    # Detecta banca
    banca = 'Não identificada'
    for b in BANCAS_RECONHECIDAS:
        if b.lower() in texto.lower():
            banca = b
            break

    # Detecta destaque
    e_destaque = any(org.lower() in texto.lower() for org in ORGAOS_DESTAQUE)

    # Tenta extrair numero de vagas
    vagas_match = re.search(r'(\d+)\s*vagas?', texto, re.IGNORECASE)
    vagas = int(vagas_match.group(1)) if vagas_match else 0

    # Tenta extrair remuneracao
    remuneracao_match = re.search(r'R\$\s*([\d.]+,?\d*)', texto)
    remuneracao = f'R$ {remuneracao_match.group(1)}' if remuneracao_match else 'Consultar edital'

    # Tenta identificar escolaridade
    escolaridade = 'Consultar edital'
    if re.search(r'ensino m.dio|n.vel m.dio', texto, re.IGNORECASE):
        escolaridade = 'Ensino Médio'
    elif re.search(r'ensino superior|n.vel superior|superior completo', texto, re.IGNORECASE):
        escolaridade = 'Ensino Superior'
    elif re.search(r'ensino fundamental|n.vel fundamental', texto, re.IGNORECASE):
        escolaridade = 'Ensino Fundamental'

    return {
        'id': 'concurso-' + hashlib.md5(url.encode()).hexdigest()[:8],
        'órgão': titulo.split('|')[0].strip()[:80],
        'sigla': '',
        'esfera': esfera,
        'cargos': 'Consultar edital',
        'vagas': vagas,
        'escolaridade': escolaridade,
        'remuneracao_max': remuneracao,
        'periodo_inscricao': 'Consultar edital',
        'banca': banca,
        'link_edital': url,
        'status': 'Em Analise',
        'destaque': e_destaque,
        'data_atualizacao': datetime.now().strftime('%d/%m/%Y'),
    }


# --- Carregamento e Salvamento do JSON de Concursos ---
def carregar_concursos():
    if not config.ARQUIVO_CONCURSOS.exists():
        return []
    with open(config.ARQUIVO_CONCURSOS, 'r', encoding='utf-8') as f:
        return json.load(f)


def salvar_concursos(concursos):
    config.ARQUIVO_CONCURSOS.parent.mkdir(parents=True, exist_ok=True)
    with open(config.ARQUIVO_CONCURSOS, 'w', encoding='utf-8') as f:
        json.dump(concursos, f, ensure_ascii=False, indent=2)


# --- Ponto de Entrada ---
def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Radar de concursos públicos.'
    )
    parser.add_argument('--forcar-atualizacao', '--forcar-atualização', dest='forcar_atualizacao',
                        action='store_true', help='Remove e reprocessa todos os editais existentes')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando Radar de Concursos ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')

    concursos_existentes = [] if args.forcar_atualizacao else carregar_concursos()
    ids_existentes = {c['id'] for c in concursos_existentes}
    config.registrar_log(f'Editais existentes no radar: {len(concursos_existentes)}')

    novos = []

    for dork in config.DORKS_CONCURSOS:
        config.registrar_log(f'Buscando concursos: {dork[:70]}...')
        resultados = buscar_concursos_serper(dork)
        config.registrar_log(f'  Resultados: {len(resultados)}')

        for res in resultados:
            metadados = extrair_metadados_edital(res)
            if not metadados:
                continue
            if metadados['id'] in ids_existentes:
                continue

            novos.append(metadados)
            ids_existentes.add(metadados['id'])
            config.registrar_log(f'  [NOVO EDITAL] {metadados["órgão"][:60]}')

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    todos = novos + concursos_existentes
    # Destaque primeiro, depois por data de atualização
    todos.sort(key=lambda x: (not x.get('destaque', False), x.get('data_atualizacao', '')))
    salvar_concursos(todos)

    config.registrar_log(f'=== Radar concluído. {len(novos)} novos editais adicionados. Total: {len(todos)}. ===')
    config.registrar_log('Revise os editais com status "Em Analise" e altere para "Inscrições Abertas" apos verificacao manual.')


if __name__ == '__main__':
    main()
