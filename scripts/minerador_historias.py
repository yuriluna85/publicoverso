#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minerador_historias.py - Mineracao de histórias e conquistas de servidores públicos
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Fluxo:
  1. Consulta a Serper API (Google News) com os Dorks pre-configurados em config.py
  2. Para cada resultado relevante, raspa o conteúdo limpo via Scraper API
  3. Verifica deduplicacao contra noticias_curadoria.json
  4. Gera rascunho estruturado em materias/conteúdo/ (status: Pendente)
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
from minerador_protagonistas import classificar_editoria

try:
    import requests
except ImportError:
    print('[ERRO] Biblioteca requests não encontrada. Execute: pip install requests')
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
        config.registrar_log('[AVISO] SERPER_API_KEY não configurada. Abortando busca.')
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
    """Raspa o conteúdo de uma URL via Scraper API e retorna o texto limpo."""
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
    """Verifica se o resultado e relevante e não esta na lista de exclusao."""
    texto_verificar = (titulo + ' ' + (resumo or '')).lower()
    for termo in TERMOS_EXCLUSAO:
        if termo.lower() in texto_verificar:
            return False
    return True


def e_dominio_prioritario(url):
    """Verifica se a URL pertence a um dominio de alta autoridade."""
    dominio = urlparse(url).netloc.lower()
    return any(d in dominio for d in DOMINIOS_PRIORITARIOS)


# --- Geração de ID Unico ---
def gerar_id(url):
    """Gera um ID curto unico baseado na URL."""
    return 'auto-' + hashlib.md5(url.encode()).hexdigest()[:10]


# --- Verificacao de Deduplicacao ---
def carregar_ids_existentes():
    """Carrega os IDs e URLs já registradas em noticias_curadoria.json e historico_mineracao.json."""
    ids = set()
    urls = set()

    # 1. noticias_curadoria.json
    if config.ARQUIVO_NOTICIAS.exists():
        try:
            with open(config.ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                notícias = json.load(f)
            for n in notícias:
                if n.get('id'):
                    ids.add(n.get('id'))
                if n.get('url_materia'):
                    urls.add(n.get('url_materia'))
                if n.get('url_original'):
                    urls.add(n.get('url_original'))
        except Exception:
            pass

    # 2. historico_mineracao.json
    if config.ARQUIVO_HISTORICO.exists():
        try:
            with open(config.ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                historico = json.load(f)
            for item in historico:
                if item.get('id_mineracao'):
                    ids.add(item.get('id_mineracao'))
                if item.get('url'):
                    urls.add(item.get('url'))
        except Exception:
            pass

    return ids, urls


# --- Registro de Historico de Mineracao ---
def registrar_historico_mineracao(id_mineracao, url, titulo, categoria):
    """Registra a URL minerada em data/historico_mineracao.json."""
    historico = []
    if config.ARQUIVO_HISTORICO.exists():
        try:
            with open(config.ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        except Exception:
            historico = []

    historico.append({
        'id_mineracao': id_mineracao,
        'url': url,
        'titulo': titulo,
        'categoria': categoria,
        'data_mineracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

    config.ARQUIVO_HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    with open(config.ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


# --- Geração de Rascunho .txt em pre_curadoria/AAAA/MM/DD/ ---
def gerar_rascunho_txt(resultado, categoria, conteudo_raspado):
    """Gera um arquivo .txt de rascunho em pre_curadoria/AAAA/MM/DD/slug.txt."""
    titulo = resultado.get('title', 'Titulo não disponivel')
    resumo = resultado.get('snippet', '')
    fonte = resultado.get('source', 'Fonte desconhecida')
    agora = datetime.now()
    data_str = agora.strftime('%d/%m/%Y')
    url_original = resultado.get('link', '')
    id_mineracao = gerar_id(url_original)

    # Diretorio pre_curadoria/AAAA/MM/DD
    ano = agora.strftime('%Y')
    mes = agora.strftime('%m')
    dia = agora.strftime('%d')
    diretorio_destino = config.DIRETORIO_PRE_CURADORIA / ano / mes / dia
    diretorio_destino.mkdir(parents=True, exist_ok=True)

    # Gera slug para o nome do arquivo
    slug = re.sub(r'[^\w\s-]', '', titulo.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:60]
    if not slug:
        slug = id_mineracao

    nome_arquivo = f'{slug}.txt'
    caminho = diretorio_destino / nome_arquivo
    if caminho.exists():
        nome_arquivo = f'{slug}-{id_mineracao[:6]}.txt'
        caminho = diretorio_destino / nome_arquivo

    # Corpo: usa raspagem se disponivel, senao usa o snippet
    corpo = conteudo_raspado if conteudo_raspado else resumo
    corpo += f'\n\nFonte original: {url_original}'

    conteúdo = f'---\n'
    conteúdo += f'id_mineracao: {id_mineracao}\n'
    conteúdo += f'titulo: {titulo}\n'
    conteúdo += f'resumo: {resumo[:200]}\n'
    conteúdo += f'autor: Curadoria Publicoverso\n'
    conteúdo += f'categoria: {categoria}\n'
    conteúdo += f'data: {data_str}\n'
    conteúdo += f'fonte: {fonte}\n'
    conteúdo += f'status: Pendente\n'
    conteúdo += f'status_triagem: Pendente\n'
    conteúdo += f'url_original: {url_original}\n'
    conteúdo += f'---\n\n'
    conteúdo += corpo

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteúdo)

    return caminho, id_mineracao


# --- Ponto de Entrada ---
def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Minerador de histórias de servidores públicos.'
    )
    parser.add_argument('--dias', type=int, default=config.DIAS_RETROATIVOS_HISTORIAS,
                        help='Janela de busca em dias (padrao: 7)')
    parser.add_argument('--categoria', type=str, default=None,
                        help='Filtrar por categoria especifica')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando mineracao de histórias ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')
        config.registrar_log('[INFO] Execute em modo de simulação: a Serper API não sera chamada.')

    ids_existentes, urls_existentes = carregar_ids_existentes()
    config.registrar_log(f'Registros existentes no JSON / Historico: {len(ids_existentes)}')

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

            # Classificacao automatica inteligente por palavras-chave (7 Editorias)
            cat_classificada = config.classificar_categoria(titulo, resumo, conteudo_raspado, categoria_padrao=categoria)

            # Salva rascunho .txt em pre_curadoria/AAAA/MM/DD/slug.txt
            caminho_rascunho, id_mineracao = gerar_rascunho_txt(res, cat_classificada, conteudo_raspado)
            config.registrar_log(f'  [RASCUNHO] {caminho_rascunho} (Editoria: {cat_classificada})')

            # Registra no historico de mineracao
            registrar_historico_mineracao(id_mineracao, url, titulo, cat_classificada)

            ids_existentes.add(id_mineracao)
            urls_existentes.add(url)
            total_inseridos += 1

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Mineracao concluida. {total_inseridos} novos rascunhos salvos em pre_curadoria/. ===')
    config.registrar_log('Utilize scripts/promover_materia.py para aprovar e publicar as materias.')


if __name__ == '__main__':
    main()

