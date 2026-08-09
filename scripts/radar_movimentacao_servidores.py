#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
radar_movimentacao_servidores.py - Robô de monitoramento de vida funcional de servidores públicos
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Foco:
  - Posse e nomeação de aprovados em concursos públicos.
  - Aposentadorias, homenagens de despedida e histórias de legado funcional (30+ anos de serviço).
  - Vacâncias e transições de carreira de servidores públicos do Brasil.
  - Expurgo absoluto de políticos com mandato e candidatos.

Uso:
  python scripts/radar_movimentacao_servidores.py
  python scripts/radar_movimentacao_servidores.py --dias 15
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
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
import config

try:
    import requests
except ImportError:
    print('[ERRO] Biblioteca requests não encontrada. Execute: pip install requests')
    sys.exit(1)


# --- Dorks de Vida Funcional e Movimentação ---
DORKS_MOVIMENTACAO = [
    # Eixo 1: Posse e Novos Concursados
    {
        'tipo': 'Posse e Nomeação',
        'categoria': 'Carreira e Conquistas',
        'query': '("toma posse" OR "tomam posse" OR "cerimônia de posse" OR "novos servidores empossados" OR "nomeação de servidores" OR "convocação de aprovados") AND ("concurso público" OR "universidade federal" OR "instituto federal" OR "tribunal" OR "prefeitura" OR "governo do estado") -site:*.pt -Portugal -vereador -prefeito -deputado',
    },
    {
        'tipo': 'Posse e Nomeação',
        'categoria': 'Histórias e Superação',
        'query': '("após anos de estudo" OR "estudou com livros doados" OR "filho de agricultores" OR "primeiro da família") AND ("toma posse como servidor" OR "nomeado servidor público" OR "conquista cargo público") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Eixo 2: Aposentadoria e Legado Funcional
    {
        'tipo': 'Aposentadoria e Legado',
        'categoria': 'Histórias e Superação',
        'query': '("aposenta-se" OR "concede aposentadoria" OR "homenagem de aposentadoria" OR "despedida do serviço público") AND ("servidor público" OR "professora" OR "médico" OR "policial" OR "analista") AND ("anos de dedicação" OR "anos de história" OR "legado") -site:*.pt -Portugal -vereador -prefeito -deputado',
    },
    {
        'tipo': 'Aposentadoria e Legado',
        'categoria': 'Carreira e Conquistas',
        'query': '("portaria de aposentadoria" OR "aposentadoria voluntária por tempo de contribuição") AND ("DOU" OR "Diário Oficial") ("servidor público federal" OR "servidor estadual") -cassado -improbidade -site:*.pt -Portugal -vereador -prefeito',
    }
]


def carregar_historico_urls():
    """Carrega URLs conhecidas para evitar duplicidade."""
    arquivo_hist = config.RAIZ_PROJETO / 'data' / 'historico_movimentacao.json'
    urls = set()

    if arquivo_hist.exists():
        try:
            with open(arquivo_hist, 'r', encoding='utf-8') as f:
                hist = json.load(f)
            for item in hist:
                if isinstance(item, str):
                    urls.add(item)
                elif isinstance(item, dict) and item.get('url'):
                    urls.add(item.get('url'))
        except Exception:
            pass

    return urls


def salvar_historico_url(url):
    """Registra URL processada no arquivo de historico."""
    arquivo_hist = config.RAIZ_PROJETO / 'data' / 'historico_movimentacao.json'
    hist = []
    if arquivo_hist.exists():
        try:
            with open(arquivo_hist, 'r', encoding='utf-8') as f:
                hist = json.load(f)
        except Exception:
            hist = []

    urls_salvas = set()
    for item in hist:
        if isinstance(item, str):
            urls_salvas.add(item)
        elif isinstance(item, dict) and item.get('url'):
            urls_salvas.add(item.get('url'))

    if url not in urls_salvas:
        hist.append({
            'url': url,
            'data_mineracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        arquivo_hist.parent.mkdir(parents=True, exist_ok=True)
        with open(arquivo_hist, 'w', encoding='utf-8') as f:
            json.dump(hist, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Publicoverso - Robô de Movimentação Funcional de Servidores.')
    parser.add_argument('--dias', type=int, default=15, help='Janela de busca em dias (padrao: 15)')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando Robô de Movimentação Funcional (Posse, Nomeação & Aposentadoria) ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')

    urls_conhecidas = carregar_historico_urls()
    config.registrar_log(f'URLs de movimentação no historico: {len(urls_conhecidas)}')

    total_novas = 0

    for item in DORKS_MOVIMENTACAO:
        tipo = item['tipo']
        config.registrar_log(f'Buscando movimentação funcional: [{tipo}] ...')

        headers = {'X-API-KEY': config.SERPER_API_KEY, 'Content-Type': 'application/json'}
        payload = {'q': item['query'], 'gl': 'br', 'hl': 'pt-br', 'num': config.MAX_RESULTADOS_POR_DORK, 'tbs': f'qdr:d{args.dias}'}

        try:
            resp = requests.post(config.SERPER_NEWS_URL, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            resultados = resp.json().get('news', [])
        except Exception as e:
            config.registrar_log(f'  [ERRO] Serper API: {e}')
            continue

        config.registrar_log(f'  Resultados brutos: {len(resultados)}')

        for res in resultados:
            url_bruta = res.get('link', '')
            titulo = res.get('title', '')
            resumo = res.get('snippet', '')
            fonte = res.get('source', 'Imprensa / Diário Oficial')

            if not url_bruta or url_bruta in urls_conhecidas:
                continue

            # Validação Factual em 4 Camadas
            if not config.validar_servidor_publico_brasileiro(titulo, resumo, url_bruta):
                continue

            salvar_historico_url(url_bruta)
            urls_conhecidas.add(url_bruta)

            # Grava no Acervo Geral de Links Minerados (CSV + JSON)
            cat_mapeada = item.get('categoria', 'Carreira e Conquistas')
            id_mov = 'mov-' + hashlib.md5(url_bruta.encode()).hexdigest()[:10]
            data_hoje = datetime.now().strftime('%d/%m/%Y')
            resumo_limpo = (resumo[:200] if resumo else titulo).replace('\n', ' ').replace(',', ';')

            # Append ao CSV
            arquivo_csv = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.csv'
            if arquivo_csv.exists():
                try:
                    with open(arquivo_csv, 'a', encoding='utf-8') as f:
                        f.write(f'\n{id_mov},{data_hoje},{cat_mapeada},"{titulo}","{resumo_limpo}",{fonte},{url_bruta},Pendente')
                except Exception as e:
                    config.registrar_log(f'  [AVISO CSV] {e}')

            # Append ao JSON
            arquivo_json = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.json'
            if arquivo_json.exists():
                try:
                    with open(arquivo_json, 'r', encoding='utf-8') as f:
                        lista_acervo = json.load(f)
                    lista_acervo.insert(0, {
                        "id": id_mov,
                        "data": data_hoje,
                        "categoria": cat_mapeada,
                        "titulo": titulo,
                        "resumo": resumo[:200],
                        "fonte": fonte,
                        "url_original": url_bruta,
                        "status_curadoria": "Pendente"
                    })
                    with open(arquivo_json, 'w', encoding='utf-8') as f:
                        json.dump(lista_acervo, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    config.registrar_log(f'  [AVISO JSON] {e}')

            total_novas += 1
            config.registrar_log(f'  [MOVIMENTAÇÃO REGISTRADA] {titulo[:60]}... (Fonte: {fonte})')
            time.sleep(config.PAUSA_ENTRE_REQUISICOES)

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Robô de Movimentação Funcional concluído. {total_novas} novos registros adicionados. ===')


if __name__ == '__main__':
    main()
