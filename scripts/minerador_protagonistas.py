#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minerador_protagonistas.py - Mineracao especializada em histórias humanas de servidores públicos
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Foco Estrito:
  - Vida alem do trabalho: Literatura, Artes, Esportes, Cultura Pop/Realities, Voluntariado e Superacao.
  - Expurgo total de atos institucionais, burocracia e rotinas de órgãos/prefeituras.
  - Verificacao ativa de liveness (HTTP 200), resolucao de redirects (URLs canonicas) e limpeza de UTMs.
  - Atribuição obrigatoria do veiculo original e link verificado.

Uso:
  python scripts/minerador_protagonistas.py
  python scripts/minerador_protagonistas.py --dias 15
  python scripts/minerador_protagonistas.py --eixo "Literatura"
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
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
import config

try:
    import requests
except ImportError:
    print('[ERRO] Biblioteca requests não encontrada. Execute: pip install requests')
    sys.exit(1)


# --- Dorks Especializadas nos 5 Eixos Humanos ---
DORKS_PROTAGONISTAS = [
    # Eixo 1: Literatura, Artes e Expressao Cultural
    {
        'eixo': 'Literatura e Artes',
        'categoria': 'Artes e Literatura',
        'query': '("servidor público" OR "servidora pública" OR "policial" OR "professor" OR "médico" OR "analista" OR "técnico judiciário" OR "auditor" OR "gari") AND ("lança livro" OR "pública romance" OR "escreve poesia" OR "autor do livro" OR "autora do livro" OR "ilustrador" OR "quadrinista" OR "lançou HQ")',
    },
    {
        'eixo': 'Literatura e Artes',
        'categoria': 'Artes e Literatura',
        'query': '("servidor público" OR "servidora pública") AND ("exposição fotográfica" OR "artista plástico" OR "escultor" OR "pintura em tela" OR "gravou álbum" OR "lançou single" OR "vocalista da banda" OR "toca violino" OR "peça de teatro")',
    },

    # Eixo 2: Esportes, Desafios Fisicos e Superacao Atletica
    {
        'eixo': 'Esportes e Desafios',
        'categoria': 'Esportes e Aventura',
        'query': '("servidor público" OR "servidora pública" OR "agente penitenciário" OR "guarda municipal" OR "policial militar" OR "bombeiro militar" OR "enfermeira") AND ("campeão de jiu-jitsu" OR "faixa preta" OR "maratonista" OR "completou maratona" OR "ironman" OR "triatlo" OR "atleta amador" OR "travessia a nado" OR "campeonato de fisiculturismo")',
    },
    {
        'eixo': 'Esportes e Desafios',
        'categoria': 'Esportes e Aventura',
        'query': '("servidor" OR "servidora") AND ("olimpíadas" OR "paralimpíadas" OR "jogos pan-americanos" OR "representa o Brasil no exterior" OR "campeão sul-americano" OR "campeã mundial")',
    },

    # Eixo 3: Cultura Pop, Gastronomia e Entretenimento
    {
        'eixo': 'Entretenimento e Cultura Pop',
        'categoria': 'Cultura Pop e Gastronomia',
        'query': '("servidor público" OR "servidora pública" OR "policial federal" OR "médica do SUS" OR "professor universitário") AND ("participa do BBB" OR "participante do BBB" OR "Big Brother Brasil" OR "MasterChef Brasil" OR "The Voice Brasil" OR "Bake Off" OR "No Limite" OR "reality show")',
    },
    {
        'eixo': 'Entretenimento e Cultura Pop',
        'categoria': 'Cultura Pop e Gastronomia',
        'query': '("servidor público" OR "servidora pública") AND ("stand-up comedy" OR "humorista" OR "canal de culinária" OR "influenciador digital" OR "canal no YouTube de música")',
    },

    # Eixo 4: Iniciativas Sociais, Voluntariado e Heroismo Pessoal
    {
        'eixo': 'Voluntariado e Causa Social',
        'categoria': 'Solidariedade e Comunidade',
        'query': '("servidor público" OR "servidora pública") AND ("criou ONG" OR "projeto social independente" OR "fora do horário de trabalho" OR "resgate de animais" OR "sopão comunitário" OR "ensina crianças carentes" OR "reforma de casas voluntária")',
    },
    {
        'eixo': 'Voluntariado e Causa Social',
        'categoria': 'Solidariedade e Comunidade',
        'query': '("servidor público" OR "servidora pública") AND ("fora de serviço salva" OR "estava de folga e salvou" OR "herói anônimo" OR "ato de coragem fora do expediente")',
    },

    # Eixo 5: Trajetorias Extraordinarias e Superacao Pessoal
    {
        'eixo': 'Trajetoria e Superacao',
        'categoria': 'Histórias e Superação',
        'query': '("de gari a" OR "de vigilante a" OR "de merendeira a" OR "de estagiário a") AND ("passou em concurso" OR "formou-se em" OR "doutorado" OR "conquistou o sonho")',
    },
    {
        'eixo': 'Trajetoria e Superacao',
        'categoria': 'Histórias e Superação',
        'query': '("aposentou-se aos" OR "servidor com 90 anos" OR "servidora centenária" OR "40 anos dedicados") AND ("história de vida" OR "legado de vida")',
    },
]

MAPA_EIXOS_EDITORIAS = {
    'Literatura e Artes': 'Artes e Literatura',
    'Esportes e Desafios': 'Esportes e Aventura',
    'Entretenimento e Cultura Pop': 'Cultura Pop e Gastronomia',
    'Voluntariado e Causa Social': 'Solidariedade e Comunidade',
    'Trajetoria e Superacao': 'Histórias e Superação',
}


def classificar_editoria(titulo, resumo, categoria_fallback='Carreira e Conquistas'):
    """Classifica automaticamente a notícia em uma das 7 editorias jornalisticas."""
    return config.classificar_categoria(titulo, resumo, categoria_padrao=categoria_fallback)


# --- Filtros de Exclusao (Anti-Burocracia / Anti-Órgãos) ---
TERMOS_EXPURGO_INSTITUCIONAL = [
    'prefeitura abre licitação', 'prefeitura inaugura', 'secretaria municipal de',
    'gabinete do prefeito', 'câmara municipal aprova', 'governador anuncia',
    'corte de despesas', 'greve dos servidores', 'sindicato cobra', 'assembleia da categoria',
    'reajuste salarial', 'teto remuneratório', 'improbidade administrativa',
    'inquérito civil', 'denúncia do ministério público', 'audiência pública sobre orçamento',
    'plano plurianual', 'decreto municipal', 'boletim oficial',
]


# --- Módulo de Liveness, Redirects e Limpeza de URLs ---
def limpar_parametros_url(url):
    """Remove parametros de rastreamento (utm_*, gclid, fbclid) mantendo a URL limpa."""
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        params_limpos = {
            k: v for k, v in query_params.items()
            if not (k.startswith('utm_') or k in ('gclid', 'fbclid', 'ref', 'source'))
        }
        nova_query = urlencode(params_limpos, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, nova_query, parsed.fragment))
    except Exception:
        return url


def identificar_veiculo(url):
    """Identifica o nome amigavel do veiculo de imprensa a partir do dominio."""
    dominio = urlparse(url).netloc.lower()

    mapa_dominios = {
        'g1.globo.com': 'G1',
        'oglobo.globo.com': 'O Globo',
        'uol.com.br': 'UOL',
        'folha.uol.com.br': 'Folha de S.Paulo',
        'estadao.com.br': 'Estadão',
        'correiobraziliense.com.br': 'Correio Braziliense',
        'agenciabrasil.ebc.com.br': 'Agência Brasil',
        'bbc.com': 'BBC News Brasil',
        'carta.capital.com.br': 'CartaCapital',
        'veja.abril.com.br': 'Veja',
        'istoe.com.br': 'IstoÉ',
        'metropoles.com': 'Metrópoles',
        'cnnbrasil.com.br': 'CNN Brasil',
        'terra.com.br': 'Terra',
        'r7.com': 'R7',
    }

    for d, nome in mapa_dominios.items():
        if d in dominio:
            return nome

    # Fallback: extrai nome limpo do dominio (ex: news.yahoo.com -> Yahoo)
    partes = dominio.replace('www.', '').split('.')
    return partes[0].capitalize() if partes else 'Imprensa'


def verificar_liveness_e_canonizar(url_bruta, timeout=10):
    """
    Realiza teste de liveness (HTTP 200), segue redirecionamentos para obter
    a URL canonica final e extrai o nome do veiculo.
    Retorna: (url_limpa, nome_veiculo, status_ok)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        resp = requests.get(url_bruta, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            config.registrar_log(f'  [LINK MORTO] HTTP {resp.status_code}: {url_bruta}')
            return None, None, False

        # Verifica se retornou HTML com tamanho minimo
        if len(resp.text) < 500:
            config.registrar_log(f'  [LINK REJEITADO] Conteúdo insuficiente: {url_bruta}')
            return None, None, False

        url_final = resp.url
        url_limpa = limpar_parametros_url(url_final)
        nome_veiculo = identificar_veiculo(url_limpa)

        return url_limpa, nome_veiculo, True
    except requests.RequestException as e:
        config.registrar_log(f'  [ERRO LIVENESS] {url_bruta}: {e}')
        return None, None, False


# --- Verificacao de Expurgo Burocratico ---
def e_materia_humanizada(titulo, resumo):
    """Retorna True apenas se não contiver termos burocraticos de descarte."""
    texto = (titulo + ' ' + (resumo or '')).lower()
    for termo in TERMOS_EXPURGO_INSTITUCIONAL:
        if termo in texto:
            return False
    return True


# --- Historico e Deduplicacao ---
def carregar_historico_urls():
    """Carrega URLs do noticias_curadoria.json, acervo_links_minerados.json e historico_mineracao.json com suporte a dicts e strings."""
    urls = set()

    # 1. noticias_curadoria.json
    if config.ARQUIVO_NOTICIAS.exists():
        try:
            with open(config.ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                noticias = json.load(f)
            for n in noticias:
                if isinstance(n, dict):
                    if n.get('url_materia'):
                        urls.add(n.get('url_materia'))
                    if n.get('url_original'):
                        urls.add(n.get('url_original'))
        except Exception:
            pass

    # 2. historico_mineracao.json
    arquivo_hist = config.RAIZ_PROJETO / 'data' / 'historico_mineracao.json'
    if arquivo_hist.exists():
        try:
            with open(arquivo_hist, 'r', encoding='utf-8') as f:
                hist = json.load(f)
            for item in hist:
                if isinstance(item, str):
                    urls.add(item)
                elif isinstance(item, dict):
                    if item.get('url'):
                        urls.add(item.get('url'))
                    if item.get('url_original'):
                        urls.add(item.get('url_original'))
        except Exception:
            pass

    return urls


def salvar_historico_url(url):
    """Registra a nova URL minerada no historico permanente."""
    arquivo_hist = config.RAIZ_PROJETO / 'data' / 'historico_mineracao.json'
    hist = []
    if arquivo_hist.exists():
        try:
            with open(arquivo_hist, 'r', encoding='utf-8') as f:
                hist = json.load(f)
        except Exception:
            hist = []

    # Verifica duplicidade suportando tanto strings quanto dicts
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


# --- Salvamento do Rascunho na Estrutura Temporal ---
def salvar_rascunho_protagonista(resultado, item_dork, url_verificada, nome_veiculo, conteudo_raspado):
    """Salva a materia em pre_curadoria/AAAA/MM/DD/protagonista_{eixo}_{slug}.txt."""
    agora = datetime.now()
    ano = agora.strftime('%Y')
    mes = agora.strftime('%m')
    dia = agora.strftime('%d')

    pasta_dia = config.RAIZ_PROJETO / 'pre_curadoria' / ano / mes / dia
    pasta_dia.mkdir(parents=True, exist_ok=True)

    titulo = resultado.get('title', 'Titulo não disponivel')
    resumo = resultado.get('snippet', '')
    eixo = item_dork['eixo']
    categoria = classificar_editoria(titulo, resumo, item_dork['categoria'])

    slug = re.sub(r'[^\w\s-]', '', titulo.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:55]
    nome_arquivo = f'protagonista_{slug}.txt'
    caminho = pasta_dia / nome_arquivo

    corpo = conteudo_raspado if conteudo_raspado else resumo

    conteúdo = f'---\n'
    conteúdo += f'id_mineracao: min-protagonista-{agora.strftime("%Y%m%d%H%M%S")}\n'
    conteúdo += f'titulo: {titulo}\n'
    conteúdo += f'resumo: {resumo[:200]}\n'
    conteúdo += f'autor: Curadoria Publicoverso\n'
    conteúdo += f'categoria: {categoria}\n'
    conteúdo += f'eixo_tematico: {eixo}\n'
    conteúdo += f'fonte: {nome_veiculo}\n'
    conteúdo += f'url_original: {url_verificada}\n'
    conteúdo += f'link_status: Verificado (HTTP 200)\n'
    conteúdo += f'data_verificacao: {agora.strftime("%d/%m/%Y %H:%M")}\n'
    conteúdo += f'status: Pendente\n'
    conteúdo += f'---\n\n'
    conteúdo += corpo
    conteúdo += f'\n\nFonte original: {url_verificada}'

    caminho.write_text(conteúdo, encoding='utf-8')
    return caminho


# --- Ponto de Entrada ---
def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Minerador Especialista de Protagonistas.'
    )
    parser.add_argument('--dias', type=int, default=15, help='Janela de busca em dias (padrao: 15)')
    parser.add_argument('--eixo', type=str, default=None, help='Filtrar por eixo tematico especifico')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando minerador de Protagonistas ("Vida Alem do Trabalho") ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')

    urls_conhecidas = carregar_historico_urls()
    config.registrar_log(f'URLs conhecidas no historico: {len(urls_conhecidas)}')

    dorks = DORKS_PROTAGONISTAS
    if args.eixo:
        dorks = [d for d in dorks if d['eixo'] == args.eixo]
        if not dorks:
            config.registrar_log(f'[AVISO] Nenhum dork para o eixo: {args.eixo}')
            return

    total_novas = 0

    for item in dorks:
        eixo = item['eixo']
        config.registrar_log(f'Buscando eixo humano: [{eixo}] ...')

        headers = {'X-API-KEY': config.SERPER_API_KEY, 'Content-Type': 'application/json'}
        payload = {'q': item['query'], 'gl': 'br', 'hl': 'pt-br', 'num': config.MAX_RESULTADOS_POR_DORK, 'tbs': f'qdr:d{args.dias}'}

        try:
            resp = requests.post(config.SERPER_NEWS_URL, headers=headers, json=payload, timeout=15)
            resp.raise_for_status()
            resultados = resp.json().get('news', [])
        except Exception as e:
            config.registrar_log(f'  [ERRO] Serper API: {e}')
            continue

        blacklist_descartes = config.carregar_blacklist_descartes()

        for res in resultados:
            url_bruta = res.get('link', '')
            titulo = res.get('title', '')
            resumo = res.get('snippet', '')

            if not url_bruta or url_bruta in urls_conhecidas:
                continue

            # Despolui a URL e gera o slug do título
            url_canon = config.normalizar_url_para_deduplicacao(url_bruta)
            slug_titulo = config.normalizar_titulo_para_slug(titulo)

            # Consulta Blacklist Persistente de Descartes
            if url_canon in blacklist_descartes or slug_titulo in blacklist_descartes:
                config.registrar_log(f'  [IGNORADO BLACKLIST] {titulo[:60]}...')
                continue

            # Filtro Factual de Servidor Público Brasileiro
            if not config.validar_servidor_publico_brasileiro(titulo, resumo, url_bruta):
                continue

            # Filtro de expurgo institucional
            if not e_materia_humanizada(titulo, resumo):
                config.registrar_log(f'  [EXPURGADO INSTITUCIONAL] {titulo[:60]}...')
                continue

            # Verificacao ativa de Liveness e Resolucao de URL
            url_limpa, veiculo, ok = verificar_liveness_e_canonizar(url_bruta)
            if not ok or not url_limpa:
                continue

            if url_limpa in urls_conhecidas:
                continue

            # Raspagem limpa
            conteudo_raspado = None
            if config.SCRAPER_API_KEY:
                try:
                    p = {'api_key': config.SCRAPER_API_KEY, 'url': url_limpa, 'render': 'false'}
                    r = requests.get(config.SCRAPER_API_URL, params=p, timeout=25)
                    if r.status_code == 200:
                        from minerador_historias import extrair_texto_limpo
                        conteudo_raspado = extrair_texto_limpo(r.text)
                except Exception:
                    pass

            # Segunda verificação factual pós-raspagem
            if not config.validar_servidor_publico_brasileiro(titulo, resumo, url_limpa, conteudo_raspado):
                continue

            caminho_rascunho = salvar_rascunho_protagonista(res, item, url_limpa, veiculo, conteudo_raspado)
            salvar_historico_url(url_limpa)
            urls_conhecidas.add(url_limpa)

            # Grava no Acervo Geral de Links Minerados (CSV + JSON)
            cat_mapeada = item.get('categoria') or MAPA_EIXOS_EDITORIAS.get(item.get('eixo'), 'Histórias e Superação')
            id_prot = 'prot-' + hashlib.md5(url_limpa.encode()).hexdigest()[:10]
            data_hoje = datetime.now().strftime('%d/%m/%Y')
            resumo_limpo = (resumo[:200] if resumo else titulo).replace('\n', ' ').replace(',', ';')

            # Append ao CSV
            arquivo_csv = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.csv'
            if arquivo_csv.exists():
                try:
                    with open(arquivo_csv, 'a', encoding='utf-8') as f:
                        f.write(f'\n{id_prot},{data_hoje},{cat_mapeada},"{titulo}","{resumo_limpo}",{veiculo},{url_limpa},Pendente')
                except Exception as e:
                    config.registrar_log(f'  [AVISO CSV] {e}')

            # Append ao JSON
            arquivo_json = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.json'
            if arquivo_json.exists():
                try:
                    with open(arquivo_json, 'r', encoding='utf-8') as f:
                        lista_acervo = json.load(f)
                    lista_acervo.insert(0, {
                        "id": id_prot,
                        "data": data_hoje,
                        "categoria": cat_mapeada,
                        "titulo": titulo,
                        "resumo": resumo[:200],
                        "fonte": veiculo,
                        "url_original": url_limpa,
                        "status_curadoria": "Pendente"
                    })
                    with open(arquivo_json, 'w', encoding='utf-8') as f:
                        json.dump(lista_acervo, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    config.registrar_log(f'  [AVISO JSON] {e}')

            total_novas += 1

            config.registrar_log(f'  [RASCUNHO PROTAGONISTA] {caminho_rascunho.name} (Fonte: {veiculo})')
            time.sleep(config.PAUSA_ENTRE_REQUISICOES)

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Mineracao de Protagonistas concluida. {total_novas} novas histórias salvas em pre_curadoria/. ===')


if __name__ == '__main__':
    main()
