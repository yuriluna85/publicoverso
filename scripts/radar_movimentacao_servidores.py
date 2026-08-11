#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
radar_movimentacao_servidores.py - Robô de monitoramento de vida funcional de servidores públicos
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Foco:
  - Minerador Nativo do Diário Oficial da União (in.gov.br): Exonerações a pedido, Demissões, Nomeações, Vacâncias e Aposentadorias.
  - Posse e nomeação de aprovados em concursos públicos.
  - Aposentadorias, homenagens de despedida e histórias de legado funcional (30+ anos de serviço).
  - Vacâncias e transições de carreira de servidores públicos do Brasil.
  - Expurgo absoluto de políticos com mandato, candidatos e anúncios comerciais/advocacia.

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
    from bs4 import BeautifulSoup
except ImportError:
    print('[ERRO] Bibliotecas requests ou bs4 não encontradas. Execute: pip install requests beautifulsoup4')
    sys.exit(1)


# --- Dorks Nativas do Diário Oficial da União (in.gov.br) ---
QUERIES_DOU_DIRETO = [
    {
        'tipo': 'Exoneração a Pedido (DOU)',
        'categoria': 'Carreira e Conquistas',
        'query': '"exonerar a pedido"'
    },
    {
        'tipo': 'Demissão a Bem do Serviço Público (DOU)',
        'categoria': 'Jurídico e PAD',
        'query': '"demissão"'
    },
    {
        'tipo': 'Portaria de Nomeação (DOU)',
        'categoria': 'Carreira e Conquistas',
        'query': '"nomear"'
    },
    {
        'tipo': 'Vacância de Cargo (DOU)',
        'categoria': 'Carreira e Conquistas',
        'query': '"conceder vacância"'
    },
    {
        'tipo': 'Aposentadoria Voluntária (DOU)',
        'categoria': 'Histórias e Superação',
        'query': '"conceder aposentadoria"'
    }
]

# --- Dorks de Vida Funcional via Serper News (Notícias de Imprensa) ---
DORKS_MOVIMENTACAO = [
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
    {
        'tipo': 'Aposentadoria e Legado',
        'categoria': 'Histórias e Superação',
        'query': '("aposenta-se" OR "concede aposentadoria" OR "homenagem de aposentadoria" OR "despedida do serviço público") AND ("servidor público" OR "professora" OR "médico" OR "policial" OR "analista") AND ("anos de dedicação" OR "anos de história" OR "legado") -site:*.pt -Portugal -vereador -prefeito -deputado',
    },
    {
        'tipo': 'Demissão a Bem do Serviço Público e PAD',
        'categoria': 'Jurídico e PAD',
        'query': '("demissão a bem do serviço público" OR "aplicação da pena de demissão" OR "demitir o servidor" OR "portaria de demissão") AND ("Processo Administrativo Disciplinar" OR "PAD" OR "Lei 8.112" OR "Lei 8112") AND ("Diário Oficial" OR "DOU" OR "servidor público") -site:*.pt -Portugal -vereador -prefeito -deputado',
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
    """Registra URL processada no arquivo de histórico."""
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


def registrar_no_acervo(id_mov, data_pub, cat_mapeada, titulo, resumo, fonte, url_bruta):
    """Grava nova matéria minerada no acervo (CSV + JSON)."""
    resumo_limpo = (resumo[:200] if resumo else titulo).replace('\n', ' ').replace('"', '""')

    # Append ao CSV
    arquivo_csv = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.csv'
    if arquivo_csv.exists():
        try:
            with open(arquivo_csv, 'a', encoding='utf-8') as f:
                f.write(f'\n{id_mov},{data_pub},{cat_mapeada},"{titulo}","{resumo_limpo}",{fonte},{url_bruta},Pendente')
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
                "data": data_pub,
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


def minerar_dou_oficial_direto(termo_busca, exact_date="dia", max_paginas=2):
    """
    Mineração nativa direta na busca pública do Diário Oficial da União (in.gov.br).
    Extrai atos oficiais diretamente dos metadados Liferay embutidos com suporte a paginação.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    resultados = []
    urls_vistas = set()

    for pagina in range(1, max_paginas + 1):
        url = f'https://www.in.gov.br/consulta/-/buscar/dou?q={requests.utils.quote(termo_busca)}&s=todos&exactDate={exact_date}&sortType=0&page={pagina}'
        try:
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, 'html.parser')
            elem_params = soup.find(id=re.compile(r'.*BuscaDouPortlet_params'))
            if not elem_params:
                break

            dados = json.loads(elem_params.string or elem_params.text)
            hits = dados.get('jsonArray', [])
            if not hits:
                break
            
            for h in hits:
                url_titulo = h.get('urlTitle', '')
                link_completo = f"https://www.in.gov.br/web/dou/-/{url_titulo}" if url_titulo else ""
                titulo = h.get('title', '')
                pub_date = h.get('pubDate', '')
                secao = h.get('pubName', 'DO2')
                snippet_html = h.get('content', '')
                snippet_limpo = BeautifulSoup(snippet_html, 'html.parser').get_text()

                if link_completo and titulo and link_completo not in urls_vistas:
                    urls_vistas.add(link_completo)
                    resultados.append({
                        'titulo': titulo,
                        'data': pub_date or datetime.now().strftime('%d/%m/%Y'),
                        'secao': secao,
                        'link': link_completo,
                        'resumo': snippet_limpo,
                        'fonte': f'Diário Oficial da União ({secao})'
                    })
        except Exception as e:
            config.registrar_log(f'  [ERRO MINERAÇÃO NATIVA DOU PAG {pagina}] {e}')
            break

    return resultados



def main():
    parser = argparse.ArgumentParser(description='Publicoverso - Robô de Movimentação Funcional de Servidores.')
    parser.add_argument('--dias', type=int, default=15, help='Janela de busca em dias (padrao: 15)')
    parser.add_argument('--dry-run', action='store_true', help='Executa busca sem alterar arquivos de dados no disco')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando Robô de Movimentação Funcional (Portal Publicoverso + DOU Oficial Direct) ===')
    if args.dry_run:
        config.registrar_log('[MODO DRY-RUN ATIVADO: Nenhum arquivo de dados será alterado no disco]')

    urls_conhecidas = carregar_historico_urls()
    config.registrar_log(f'URLs de movimentação no historico: {len(urls_conhecidas)}')

    total_novas = 0

    # CAMADA 1: Mineração Direta no Diário Oficial da União (in.gov.br) para o dia de hoje
    config.registrar_log('--- [CAMADA 1] Minerando atos oficiais diretamente do in.gov.br (DOU) ---')
    for q_dou in QUERIES_DOU_DIRETO:
        tipo = q_dou['tipo']
        query_str = q_dou['query']
        categoria = q_dou['categoria']
        config.registrar_log(f'Buscando DOU Nativo: [{tipo}] ({query_str})...')

        atos_dou = minerar_dou_oficial_direto(query_str, exact_date="dia")
        config.registrar_log(f'  Encontrados {len(atos_dou)} atos no DOU hoje.')

        for ato in atos_dou:
            url_bruta = ato['link']
            titulo = ato['titulo']
            resumo = ato['resumo']
            fonte = ato['fonte']
            data_pub = ato['data']

            if not url_bruta or url_bruta in urls_conhecidas:
                continue

            if not args.dry_run:
                salvar_historico_url(url_bruta)
                urls_conhecidas.add(url_bruta)

                id_mov = 'dou-' + hashlib.md5(url_bruta.encode()).hexdigest()[:10]
                registrar_no_acervo(id_mov, data_pub, categoria, titulo, resumo, fonte, url_bruta)
                config.registrar_log(f'  [ATO DOU REGISTRADO] {titulo[:60]}... ({data_pub})')
            else:
                config.registrar_log(f'  [DRY-RUN - ATO DOU ENCONTRADO] {titulo[:60]}... ({data_pub})')

            total_novas += 1

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    # CAMADA 2: Mineração Complementar via Serper News
    config.registrar_log('--- [CAMADA 2] Minerando notícias e imprensa funcional via Serper News ---')
    for item in DORKS_MOVIMENTACAO:
        tipo = item['tipo']
        config.registrar_log(f'Buscando imprensa funcional: [{tipo}] ...')

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

            # Validação Factual em 4 Camadas + Filtro Anti-Anúncio Comercial
            if not config.validar_servidor_publico_brasileiro(titulo, resumo, url_bruta):
                continue

            # Expurgo de anúncios comerciais e advocacia privada
            texto_chk = f"{titulo} {resumo} {url_bruta} {fonte}".lower()
            if any(kw in texto_chk for kw in ['sindicância contra você', 'sindicancia contra voce', 'pad contra você', 'defesa técnica agora', 'contrate um advogado', 'advocacia especializada', 'escritório de advocacia', 'fale conosco pelo whatsapp', 'fale com nosso advogado', 'consulte nossos advogados', 'agende uma consulta', 'precisa de defesa', 'defenda seu cargo', 'fale com um especialista', 'nossos serviços jurídicos', 'nossos servicos juridicos', 'nosso escritório', 'prestamos assessoria jurídica', 'entre em contato conosco', 'serviços advocatícios', 'defesa em pad', 'defesa de servidores públicos', 'escritório especializado', 'garanta seus direitos', 'responde a processo administrativo', 'responde a pad', 'defesa técnica do servidor', 'proteger carreira', 'proteger sua carreira', 'defesa em sindicância', 'advogado de servidor', 'advocacia para servidores', 'fale com um advogado', 'consultoria jurídica para servidores']):
                config.registrar_log(f'  [DESCARTADO ANÚNCIO/PROPAGANDA] {titulo}')
                if not args.dry_run:
                    salvar_historico_url(url_bruta)
                continue

            if not args.dry_run:
                salvar_historico_url(url_bruta)
                urls_conhecidas.add(url_bruta)

                id_mov = 'mov-' + hashlib.md5(url_bruta.encode()).hexdigest()[:10]
                data_hoje = datetime.now().strftime('%d/%m/%Y')
                cat_mapeada = item.get('categoria', 'Carreira e Conquistas')
                registrar_no_acervo(id_mov, data_hoje, cat_mapeada, titulo, resumo, fonte, url_bruta)
                config.registrar_log(f'  [MOVIMENTAÇÃO REGISTRADA] {titulo[:60]}... (Fonte: {fonte})')
            else:
                config.registrar_log(f'  [DRY-RUN - MOVIMENTAÇÃO ENCONTRADA] {titulo[:60]}... (Fonte: {fonte})')

            total_novas += 1
            time.sleep(config.PAUSA_ENTRE_REQUISICOES)

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Robô de Movimentação Funcional concluído. {total_novas} novos registros adicionados. ===')


if __name__ == '__main__':
    main()
