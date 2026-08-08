#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minerador_historias.py - Mineracao de historias e conquistas de servidores publicos
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Fluxo:
  1. Consulta a Serper API (Google News) com os Dorks pre-configurados em config.py
  2. Para cada resultado relevante, raspa o conteudo limpo via Scraper API
  3. Verifica deduplicacao contra noticias_curadoria.json
  4. Gera rascunho estruturado em materias/conteudo/ (status: Pendente)
  5. Insere entrada pendente em noticias_curadoria.json para revisao da curadoria

Uso:
  python scripts/minerador_historias.py
  python scripts/minerador_historias.py --dias 3
  python scripts/minerador_historias.py --categoria "Gente e Cultura"
"""

import sys
import os
import json
import time
import re
import argparse
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus, urlparse

sys.stdout.reconfigure(encoding='utf-8')

# Ajuste do path para importar config.py do mesmo diretorio
sys.path.insert(0, str(Path(__file__).parent))
import config

try:
    import requests
except ImportError:
    print('[ERRO] Biblioteca requests nao encontrada. Execute: pip install requests')
    sys.exit(1)


# --- Dominios de Alta Autoridade para Priorizacao ---
DOMINIOS_PRIORITARIOS = [
    'g1.globo.com', 'uol.com.br', 'folha.uol.com.br', 'estadao.com.br',
    'correiobraziliense.com.br', 'agenciabrasil.ebc.com.br', 'gov.br',
    'senado.leg.br', 'bbc.com/portuguese', 'carta.capital.com.br',
    'oglobo.globo.com', 'veja.abril.com.br', 'istoe.com.br',
]

# --- Palavras-Chave de Exclusao (Descarta automaticamente) ---
TERMOS_EXCLUSAO = [
    'greve', 'salário mínimo', 'escândalo', 'corrupção', 'improbidade',
    'afastado', 'preso', 'indiciado', 'investigado', 'denunciado',
    'demissão em massa', 'corte de gastos', 'teto de gastos',
]


# --- Requisicao Serper API ---
def buscar_noticias_serper(dork, dias=7):
    """Consulta a Serper API Google News e retorna lista de resultados."""
    if not config.SERPER_API_KEY:
        config.registrar_log('[AVISO] SERPER_API_KEY nao configurada. Abortando busca.')
        return []

    headers = {
        'X-API-KEY': config.SERPER_API_KEY,
        'Content-Type': 'application/json',
    }
    payload = {
        'q': dork['query'],
        'gl': 'br',
        'hl': 'pt-br',
        'num': config.MAX_RESULTADOS_POR_DORK,
        'tbs': f'qdr:d{dias}',
    }

    try:
        resp = requests.post(config.SERPER_NEWS_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        return dados.get('news', [])
    except requests.RequestException as e:
        config.registrar_log(f'[ERRO] Serper API: {e}')
        return []


# --- Extracao de Texto Limpo via Scraper API ---
def raspar_conteudo(url):
    """Raspa o conteudo de uma URL via Scraper API e retorna o texto limpo."""
    if not config.SCRAPER_API_KEY:
        return None

    params = {
        'api_key': config.SCRAPER_API_KEY,
        'url': url,
        'render': 'false',
    }

    try:
        resp = requests.get(config.SCRAPER_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        html = resp.text
        return extrair_texto_limpo(html)
    except requests.RequestException as e:
        config.registrar_log(f'[AVISO] Scraper API falhou para {url}: {e}')
        return None


def extrair_texto_limpo(html):
    """Extrai paragrafos de texto limpo de um HTML bruto sem dependencias externas."""
    # Remove tags de script e style
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags HTML
    texto = re.sub(r'<[^>]+>', ' ', html)
    # Normaliza espacos e quebras
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    # Filtra linhas muito curtas (menus, botoes)
    paragrafos = [l for l in linhas if len(l) > 80]
    return '\n\n'.join(paragrafos[:20])  # Limita a 20 paragrafos


# --- Verificacao de Relevancia ---
def e_relevante(titulo, resumo):
    """Verifica se o resultado e relevante e nao esta na lista de exclusao."""
    texto_verificar = (titulo + ' ' + (resumo or '')).lower()
    for termo in TERMOS_EXCLUSAO:
        if termo.lower() in texto_verificar:
            return False
    return True


def e_dominio_prioritario(url):
    """Verifica se a URL pertence a um dominio de alta autoridade."""
    dominio = urlparse(url).netloc.lower()
    return any(d in dominio for d in DOMINIOS_PRIORITARIOS)


# --- Geracao de ID Unico ---
def gerar_id(url):
    """Gera um ID curto unico baseado na URL."""
    return 'auto-' + hashlib.md5(url.encode()).hexdigest()[:10]


# --- Verificacao de Deduplicacao ---
def carregar_ids_existentes():
    """Carrega os IDs e URLs ja registradas em noticias_curadoria.json."""
    if not config.ARQUIVO_NOTICIAS.exists():
        return set(), set()
    with open(config.ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
        noticias = json.load(f)
    ids = {n.get('id') for n in noticias}
    urls = {n.get('url_materia') for n in noticias if n.get('url_materia')}
    return ids, urls


# --- Geracao de Rascunho .txt ---
def gerar_rascunho_txt(resultado, categoria, conteudo_raspado):
    """Gera um arquivo .txt de rascunho no padrao do pipeline build_materias.py."""
    titulo = resultado.get('title', 'Titulo nao disponivel')
    resumo = resultado.get('snippet', '')
    fonte = resultado.get('source', 'Fonte desconhecida')
    data = datetime.now().strftime('%d/%m/%Y')
    url_original = resultado.get('link', '')

    # Gera slug para o nome do arquivo
    slug = re.sub(r'[^\w\s-]', '', titulo.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:60]
    nome_arquivo = f'_pendente_{slug}.txt'
    caminho = config.DIRETORIO_RASCUNHOS / nome_arquivo

    # Corpo: usa raspagem se disponivel, senao usa o snippet
    corpo = conteudo_raspado if conteudo_raspado else resumo
    corpo += f'\n\nFonte original: {url_original}'

    conteudo = f'---\n'
    conteudo += f'titulo: {titulo}\n'
    conteudo += f'resumo: {resumo[:200]}\n'
    conteudo += f'autor: Curadoria Publicoverso\n'
    conteudo += f'categoria: {categoria}\n'
    conteudo += f'data: {data}\n'
    conteudo += f'fonte: {fonte}\n'
    conteudo += f'status: Pendente\n'
    conteudo += f'url_original: {url_original}\n'
    conteudo += f'---\n\n'
    conteudo += corpo

    config.DIRETORIO_RASCUNHOS.mkdir(parents=True, exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    return caminho


# --- Insercao no JSON como Pendente ---
def inserir_no_json(resultado, categoria, url_original):
    """Insere a noticia como entrada pendente em noticias_curadoria.json."""
    titulo = resultado.get('title', '')
    resumo = resultado.get('snippet', '')
    fonte = resultado.get('source', 'Curadoria Publicoverso')
    data = datetime.now().strftime('%d/%m/%Y')
    novo_id = gerar_id(url_original)

    nova_entrada = {
        'id': novo_id,
        'titulo': titulo,
        'resumo': resumo,
        'conteudo_completo': resumo,
        'categoria': categoria,
        'fonte': fonte,
        'data': data,
        'status': 'Pendente',
        'destaque': False,
        'url_materia': url_original,
    }

    noticias = []
    if config.ARQUIVO_NOTICIAS.exists():
        with open(config.ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
            noticias = json.load(f)

    noticias.insert(0, nova_entrada)

    with open(config.ARQUIVO_NOTICIAS, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)

    return novo_id


# --- Ponto de Entrada ---
def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Minerador de historias de servidores publicos.'
    )
    parser.add_argument('--dias', type=int, default=config.DIAS_RETROATIVOS_HISTORIAS,
                        help='Janela de busca em dias (padrao: 7)')
    parser.add_argument('--categoria', type=str, default=None,
                        help='Filtrar por categoria especifica')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando mineracao de historias ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')
        config.registrar_log('[INFO] Execute em modo de simulacao: a Serper API nao sera chamada.')

    ids_existentes, urls_existentes = carregar_ids_existentes()
    config.registrar_log(f'Registros existentes no JSON: {len(ids_existentes)}')

    dorks = config.DORKS_HISTORIAS
    if args.categoria:
        dorks = [d for d in dorks if d['categoria'] == args.categoria]
        if not dorks:
            config.registrar_log(f'[AVISO] Nenhum dork encontrado para a categoria: {args.categoria}')
            return

    total_inseridos = 0

    for dork in dorks:
        categoria = dork['categoria']
        config.registrar_log(f'Buscando: [{categoria}] ...')

        resultados = buscar_noticias_serper(dork, dias=args.dias)
        config.registrar_log(f'  Resultados retornados: {len(resultados)}')

        for res in resultados:
            url = res.get('link', '')
            titulo = res.get('title', '')
            resumo = res.get('snippet', '')

            if not url or url in urls_existentes:
                continue

            if not e_relevante(titulo, resumo):
                config.registrar_log(f'  [EXCLUIDO] {titulo[:60]}...')
                continue

            novo_id = gerar_id(url)
            if novo_id in ids_existentes:
                continue

            # Raspagem via Scraper API
            conteudo_raspado = None
            if config.SCRAPER_API_KEY:
                conteudo_raspado = raspar_conteudo(url)
                time.sleep(config.PAUSA_ENTRE_REQUISICOES)

            # Salva rascunho .txt
            caminho_rascunho = gerar_rascunho_txt(res, categoria, conteudo_raspado)
            config.registrar_log(f'  [RASCUNHO] {caminho_rascunho.name}')

            # Insere no JSON como Pendente
            inserir_no_json(res, categoria, url)
            ids_existentes.add(novo_id)
            urls_existentes.add(url)
            total_inseridos += 1

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Mineracao concluida. {total_inseridos} novos registros inseridos (status: Pendente). ===')
    config.registrar_log('Revise os rascunhos em materias/conteudo/ e altere o status para "Aprovada" em noticias_curadoria.json para publicar.')


if __name__ == '__main__':
    main()
