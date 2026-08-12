#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
desembrulhar_e_sanitizar_urls.py - Saneamento e Resolução Ativa de Links GUID Google News
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs
"""

import os
import sys
import json
import csv
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

sys.stdout.reconfigure(encoding='utf-8')

RAIZ = Path(__file__).parent.parent
DATA_DIR = RAIZ / 'data'
ARQUIVO_ACERVO_JSON = DATA_DIR / 'acervo_links_minerados.json'
ARQUIVO_ACERVO_CSV = DATA_DIR / 'acervo_links_minerados.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def resolver_url_google_guid(guid_ou_url):
    """Converte identificadores GUID CAES... ou links intermediários do Google News na URL HTTP final."""
    if not guid_ou_url:
        return ""
    
    u = str(guid_ou_url).strip()
    
    # Se for um GUID puro iniciando em CAES
    if u.startswith('CAES'):
        u = f"https://news.google.com/rss/articles/{u}"
    
    # Se não tem esquema HTTP
    if not u.startswith('http://') and not u.startswith('https://'):
        return ""

    # Se é um link do news.google.com ou google.com/goto
    if 'news.google.com' in u or 'google.com/goto' in u:
        try:
            resp = requests.head(u, headers=HEADERS, allow_redirects=True, timeout=8)
            url_final = resp.url
            if url_final and ('http://' in url_final or 'https://' in url_final) and 'news.google.com' not in url_final:
                return url_final
        except Exception:
            pass

        try:
            resp = requests.get(u, headers=HEADERS, allow_redirects=True, timeout=8)
            url_final = resp.url
            if url_final and ('http://' in url_final or 'https://' in url_final) and 'news.google.com' not in url_final:
                return url_final
        except Exception:
            pass

    return u

def sanitizar_parametros_url(url):
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        return ""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params_filtrados = {k: v for k, v in params.items() if not k.startswith('utm_') and k not in ['fbclid', 'gclid', 'ref', 'amp']}
        nova_query = urlencode(params_filtrados, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, nova_query, ''))
    except Exception:
        return url

def sanitizar_todo_acervo():
    print("=" * 70)
    print("RESOLVEDOR E SANITIZADOR DE LINKS QUEBRADOS - PUBLICOVERSO")
    print("=" * 70)

    if not ARQUIVO_ACERVO_JSON.exists():
        print("[ERRO] Arquivo acervo_links_minerados.json não encontrado.")
        return

    with open(ARQUIVO_ACERVO_JSON, 'r', encoding='utf-8') as f:
        acervo = json.load(f)

    acervo_limpo = []
    corrigidos = 0
    removidos = 0

    for item in acervo:
        url_orig = item.get('url_original', '').strip()
        titulo = item.get('titulo', '')[:50]

        # Se for GUID ou Google News, resolve ativamente
        if url_orig.startswith('CAES') or 'news.google.com' in url_orig or 'google.com/goto' in url_orig or not url_orig.startswith('http'):
            print(f"[RESOLVENDO GUID/URL] {titulo}...")
            url_resolvida = resolver_url_google_guid(url_orig)
            
            if url_resolvida and (url_resolvida.startswith('http://') or url_resolvida.startswith('https://')) and not url_resolvida.startswith('CAES'):
                url_limpa = sanitizar_parametros_url(url_resolvida)
                item['url_original'] = url_limpa
                print(f"  -> RESOLVIDO COM SUCESSO: {url_limpa[:70]}")
                corrigidos += 1
                acervo_limpo.append(item)
            else:
                print(f"  -> [REMOVIDO] Não foi possível resolver URL válida para: {titulo}")
                removidos += 1
        else:
            url_limpa = sanitizar_parametros_url(url_orig)
            item['url_original'] = url_limpa
            acervo_limpo.append(item)

    # Persiste no JSON e CSV
    with open(ARQUIVO_ACERVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(acervo_limpo, f, ensure_ascii=False, indent=2)

    with open(ARQUIVO_ACERVO_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'data', 'data_iso', 'categoria', 'titulo', 'resumo', 'fonte', 'url_original', 'status_curadoria'])
        writer.writeheader()
        for i in acervo_limpo:
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

    print("=" * 70)
    print(f"SANETIZAÇÃO CONCLUÍDA:")
    print(f"  - Total no acervo saneado: {len(acervo_limpo)}")
    print(f"  - Links GUID corrigidos para URLs HTTP: {corrigidos}")
    print(f"  - Links irrecuperáveis removidos: {removidos}")
    print("=" * 70)

if __name__ == '__main__':
    sanitizar_todo_acervo()
