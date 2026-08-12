#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
capturar_url_direta.py - Utilitário de Ingestão e Captura Direta de Notícias por URL
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Uso:
  python scripts/capturar_url_direta.py "https://www.correio24horas.com.br/brasil/tres-pms-sao-presos-apos-emprestar-viatura-para-pegadinha-de-carlinhos-maia-0826"
"""

import sys
import os
import json
import csv
import re
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, unquote

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
import config
import agent_curador_semantico

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print('[ERRO] Bibliotecas requests e beautifulsoup4 necessárias. Execute: pip install requests beautifulsoup4')
    sys.exit(1)

RAIZ = Path(__file__).parent.parent
DATA_DIR = RAIZ / 'data'
ARQUIVO_ACERVO_JSON = DATA_DIR / 'acervo_links_minerados.json'
ARQUIVO_ACERVO_CSV = DATA_DIR / 'acervo_links_minerados.csv'


def sanitizar_url_direta(url):
    """Purga rastreadores (fbclid, utm_*) e desembrulha a URL."""
    if not url:
        return ""
    u = agent_curador_semantico.desembrulhar_url_direta(url.strip())
    try:
        parsed = urlparse(u)
        params = parse_qs(parsed.query)
        params_filtrados = {k: v for k, v in params.items() if not k.startswith('utm_') and k not in ['fbclid', 'gclid', 'ref', 'amp']}
        nova_query = urlencode(params_filtrados, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, nova_query, ''))
    except Exception:
        return u


def extrair_dados_pagina_web(url):
    """Baixa o HTML e extrai metadados OpenGraph / Schema.org."""
    url_limpa = sanitizar_url_direta(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        resp = requests.get(url_limpa, headers=headers, timeout=10)
        resp.raise_for_status()
        if resp.encoding is None or resp.encoding.lower() == 'iso-8859-1':
            resp.encoding = resp.apparent_encoding or 'utf-8'
        html = resp.text
    except Exception as e:
        print(f"[ERRO] Falha ao acessar URL {url_limpa}: {e}")
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # 1. Extração do Título
    og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'twitter:title'})
    titulo = og_title['content'].strip() if og_title and og_title.get('content') else (soup.title.string.strip() if soup.title else '')
    titulo = re.sub(r'[\s\-\|::]+(correio\s*24\s*horas|correio|g1|extra|uol|folha|estadão|r7|ebc).*$', '', titulo, flags=re.IGNORECASE).strip()

    # 2. Extração do Resumo
    og_desc = soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'name': 'twitter:description'})
    resumo = og_desc['content'].strip() if og_desc and og_desc.get('content') else ''

    if not resumo:
        paragrafos = [p.get_text().strip() for p in soup.find_all('p') if len(p.get_text().strip()) > 40]
        resumo = paragrafos[0][:250] + '...' if paragrafos else ''

    # 3. Extração do Nome do Veículo/Fonte
    og_site = soup.find('meta', property='og:site_name')
    if og_site and og_site.get('content'):
        fonte = og_site['content'].strip()
    else:
        netloc = urlparse(url_limpa).netloc.replace('www.', '')
        fonte = 'Correio 24 Horas' if 'correio24horas' in netloc else netloc.title()

    # 4. Extração da Data Original
    og_time = soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'name': 'publication_date'}) or soup.find('meta', attrs={'name': 'date'})
    data_iso = "2026-08-12"
    if og_time and og_time.get('content'):
        val_time = og_time['content'].strip()
        match_iso = re.search(r'(\d{4})-(\d{2})-(\d{2})', val_time)
        if match_iso:
            data_iso = match_iso.group(0)

    p_data = data_iso.split('-')
    data_br = f"{p_data[2]}/{p_data[1]}/{p_data[0]}"

    return {
        'id': f"manual-{hashlib.md5(url_limpa.encode('utf-8')).hexdigest()[:10]}",
        'data': data_br,
        'data_iso': data_iso,
        'categoria': 'Policial e Segurança Pública',
        'titulo': titulo,
        'resumo': resumo,
        'fonte': fonte,
        'url_original': url_limpa,
        'status_curadoria': 'Aprovado'
    }


def ingerir_url(url):
    print("=" * 65)
    print(f"INGESTÃO DIRETA DE NOTÍCIA VIA URL")
    print(f"URL Alvo: {url}")
    print("=" * 65)

    item = extrair_dados_pagina_web(url)
    if not item:
        print("[FALHA] Não foi possível extrair dados da página.")
        return False

    # Valida com o curador semântico
    lixo, motivo = agent_curador_semantico.eh_lixo_digital_ou_mock(
        item['titulo'], item['resumo'], item['url_original'], item['fonte'], item['id']
    )

    if lixo and "Sem vínculo" not in motivo:
        print(f"[REJEITADO PELO CURADOR] Motivo: {motivo}")
        return False

    # Classifica a editoria adequada
    cat_nova = agent_curador_semantico.classificar_semantica_fina(item['titulo'], item['resumo'])
    item['categoria'] = cat_nova

    # Carrega acervo atual
    itens_acervo = []
    if ARQUIVO_ACERVO_JSON.exists():
        try:
            with open(ARQUIVO_ACERVO_JSON, 'r', encoding='utf-8') as f:
                itens_acervo = json.load(f)
        except Exception:
            itens_acervo = []

    # Checa duplicata por URL ou Slug
    slug_novo = agent_curador_semantico.normalizar_titulo_para_slug(item['titulo'])
    url_canon_nova = agent_curador_semantico.normalizar_url_para_deduplicacao(item['url_original'])

    for exist in itens_acervo:
        slug_exist = agent_curador_semantico.normalizar_titulo_para_slug(exist.get('titulo', ''))
        url_exist = agent_curador_semantico.normalizar_url_para_deduplicacao(exist.get('url_original', ''))
        if (slug_novo and slug_novo == slug_exist) or (url_canon_nova and url_canon_nova == url_exist):
            print(f"[DUPLICATA IDENTIFICADA] A notícia já existe no acervo: {exist.get('titulo')}")
            return True

    # Injeta no início da lista
    itens_acervo.insert(0, item)

    with open(ARQUIVO_ACERVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(itens_acervo, f, ensure_ascii=False, indent=2)

    with open(ARQUIVO_ACERVO_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'data', 'data_iso', 'categoria', 'titulo', 'resumo', 'fonte', 'url_original', 'status_curadoria'])
        writer.writeheader()
        for i in itens_acervo:
            writer.writerow({
                'id': i.get('id', ''),
                'data': i.get('data', ''),
                'data_iso': i.get('data_iso', ''),
                'categoria': i.get('categoria', ''),
                'titulo': i.get('titulo', ''),
                'resumo': i.get('resumo', ''),
                'fonte': i.get('fonte', ''),
                'url_original': i.get('url_original', ''),
                'status_curadoria': i.get('status_curadoria', 'Aprovado')
            })

    print(f"[SUCESSO] Notícia adicionada ao acervo:")
    print(f"  - Título: {item['titulo']}")
    print(f"  - Categoria: {item['categoria']}")
    print(f"  - Fonte: {item['fonte']}")
    print(f"  - Data: {item['data']} (ISO: {item['data_iso']})")
    print("=" * 65)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Publicoverso - Ingestão Direta de Notícias por URL")
    parser.add_argument('url', type=str, help="URL da notícia a ser capturada e adicionada ao acervo")
    args = parser.parse_args()

    ingerir_url(args.url)
