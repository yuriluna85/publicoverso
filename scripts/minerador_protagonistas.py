#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minerador_protagonistas.py - Mineração especializada em histórias humanas de servidores públicos
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Foco Estrito:
  - Vida além do trabalho: Literatura, Artes, Esportes, Cultura Pop/Realities, Voluntariado e Superação.
  - Expurgo total de atos institucionais, burocracia, memoriais RSC e rotinas de órgãos/prefeituras.
  - Deduplicação Tripla: URL Canônica Normalizada + Slug/Hash de Título + Similaridade Semântica (>= 80%).
  - Classificação Semântica com Matriz de Pesos (Ação Humana Soberana).
  - Verificação ativa de liveness (HTTP 200), resolução de redirects e limpeza de UTMs.
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

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
import config
from classificador_noticias import classificar_materia, e_documento_burocratico, CATEGORIAS_OFICIAIS

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
        'query': '("servidor público" OR "servidora pública" OR "policial" OR "professor" OR "médico" OR "analista" OR "técnico judiciário" OR "auditor" OR "gari") AND ("lança livro" OR "publica romance" OR "escreve poesia" OR "autor do livro" OR "autora do livro" OR "ilustrador" OR "quadrinista" OR "lançou HQ")',
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

    # Eixo 6: Virais e Inusitados
    {
        'eixo': 'Virais e Inusitados',
        'categoria': 'Policial e Segurança Pública',
        'query': '("PMs" OR "PM" OR "policial militar" OR "policiais" OR "guarda municipal" OR "servidor público") AND ("pegadinha" OR "influenciador" OR "viralizou" OR "vídeo viral" OR "fato inusitado")',
    },
]


MAPA_EIXOS_EDITORIAS = {
    'Literatura e Artes': 'Artes e Literatura',
    'Esportes e Desafios': 'Esportes e Aventura',
    'Entretenimento e Cultura Pop': 'Cultura Pop e Gastronomia',
    'Voluntariado e Causa Social': 'Solidariedade e Comunidade',
    'Trajetoria e Superacao': 'Histórias e Superação',
    'Virais e Inusitados': 'Cultura Pop e Gastronomia',
}


# --- Termos de Expurgo Burocratico e Institucional ---
TERMOS_EXPURGO_INSTITUCIONAL = [
    'nota oficial', 'portaria n', 'diário oficial', 'comunicado oficial',
    'expediente administrativo', 'recesso forense', 'ponto facultativo',
    'cronograma de pagamentos', 'tabela salarial', 'recadastramento obrigatório',
    'prova de vida', 'censo funcional', 'comissão de licitação', 'pregão eletrônico',
    'edital de credenciamento', 'termo de cooperação', 'contrato administrativo',
    'prestação de contas', 'auditoria do tcu', 'relatório de gestão',
    'resolução n', 'decreto estadual', 'decreto municipal', 'projeto de lei n',
    'memorial descritivo', 'banca de rsc', 'rsc pcctae'
]


# --- Parametros de URL para Limpeza ---
PARAMETROS_RASTREAMENTO = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'gclsrc', 'dclid', 'zanpid', 'msclkid',
    '_ga', '_gl', 'mc_cid', 'mc_eid', 'ref', 'source', 'origin',
    'outputType', 'amp', 'utm_name', 'igshid'
}


def limpar_parametros_url(url_bruta):
    """Remove parametros de rastreamento UTM, fragmentos e normaliza a URL."""
    try:
        parsed = urlparse(url_bruta)
        params = parse_qs(parsed.query, keep_blank_values=False)
        params_limpos = {k: v for k, v in params.items() if k.lower() not in PARAMETROS_RASTREAMENTO}
        query_limpa = urlencode(params_limpos, doseq=True)

        scheme = 'https' if parsed.scheme in ('http', 'https') else parsed.scheme
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
            
        path = parsed.path.rstrip('/')

        url_limpa = urlunparse((
            scheme,
            netloc,
            path,
            '',
            query_limpa,
            ''
        ))
        return url_limpa
    except Exception:
        return url_bruta


def extrair_slug_titulo(titulo):
    """Gera um slug canônico normalizado a partir do título."""
    slug = re.sub(r'[^\w\s-]', '', titulo.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    return slug[:60]


def calcular_similaridade_jaccard(str1, str2):
    """Calcula similaridade de palavras entre dois títulos."""
    w1 = set(re.findall(r'\w{3,}', str1.lower()))
    w2 = set(re.findall(r'\w{3,}', str2.lower()))
    if not w1 or not w2:
        return 0.0
    inter = len(w1.intersection(w2))
    union = len(w1.union(w2))
    return inter / union if union > 0 else 0.0


def identificar_veiculo(url):
    """Identifica o nome do veiculo a partir do dominio da URL."""
    try:
        dominio = urlparse(url).netloc.lower()
        if dominio.startswith('www.'):
            dominio = dominio[4:]

        mapa_veiculos = {
            'g1.globo.com': 'G1',
            'globo.com': 'Globo',
            'uol.com.br': 'UOL',
            'folha.uol.com.br': 'Folha de S.Paulo',
            'estadao.com.br': 'Estadão',
            'correiobraziliense.com.br': 'Correio Braziliense',
            'agenciabrasil.ebc.com.br': 'Agência Brasil',
            'gov.br': 'Portal Gov.br',
            'senado.leg.br': 'Agência Senado',
            'camara.leg.br': 'Agência Câmara',
            'bbc.com': 'BBC News Brasil',
            'metropoles.com': 'Metrópoles',
            'terra.com.br': 'Terra',
            'oglobo.globo.com': 'O Globo',
            'veja.abril.com.br': 'Veja',
            'istoe.com.br': 'IstoÉ',
            'cnnbrasil.com.br': 'CNN Brasil',
            'gazetadopovo.com.br': 'Gazeta do Povo',
            'diariodepernambuco.com.br': 'Diário de Pernambuco',
            'correiodopovo.com.br': 'Correio do Povo',
            'atarde.com.br': 'A Tarde',
            'ibahia.com': 'iBahia',
            'bahianoticias.com.br': 'Bahia Notícias',
        }

        for dom, nome in mapa_veiculos.items():
            if dom in dominio:
                return nome

        partes = dominio.split('.')
        if len(partes) >= 2:
            return partes[0].capitalize()
        return dominio
    except Exception:
        return 'Veículo Regional'


def verificar_liveness_e_canonizar(url_bruta, timeout=12):
    """Verifica liveness (HTTP 200), resolve redirecionamentos e limpa a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        resp = requests.get(url_bruta, headers=headers, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            config.registrar_log(f'  [LINK MORTO] HTTP {resp.status_code}: {url_bruta}')
            return None, None, False

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


def e_materia_humanizada(titulo, resumo):
    """Retorna True apenas se não contiver termos burocraticos de descarte."""
    texto = (titulo + ' ' + (resumo or '')).lower()
    if e_documento_burocratico(titulo, resumo):
        return False
    for termo in TERMOS_EXPURGO_INSTITUCIONAL:
        if termo in texto:
            return False
    return True


# --- Deduplicação Tripla (URL + Slug + Similaridade) ---
def carregar_base_deduplicacao():
    """Carrega URLs, slugs e títulos para checagem de duplicidade tripla."""
    urls = set()
    slugs = set()
    titulos = []

    # 1. noticias_curadoria.json
    if config.ARQUIVO_NOTICIAS.exists():
        try:
            with open(config.ARQUIVO_NOTICIAS, 'r', encoding='utf-8') as f:
                noticias = json.load(f)
            for n in noticias:
                if isinstance(n, dict):
                    if n.get('url_materia'):
                        urls.add(limpar_parametros_url(n['url_materia']))
                    if n.get('url_original'):
                        urls.add(limpar_parametros_url(n['url_original']))
                    t = n.get('titulo', '')
                    if t:
                        slugs.add(extrair_slug_titulo(t))
                        titulos.append(t)
        except Exception:
            pass

    # 2. acervo_links_minerados.json
    arquivo_acervo = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.json'
    if arquivo_acervo.exists():
        try:
            with open(arquivo_acervo, 'r', encoding='utf-8') as f:
                acervo = json.load(f)
            for item in acervo:
                if isinstance(item, dict):
                    if item.get('url_original'):
                        urls.add(limpar_parametros_url(item['url_original']))
                    t = item.get('titulo', '')
                    if t:
                        slugs.add(extrair_slug_titulo(t))
                        titulos.append(t)
        except Exception:
            pass

    # 3. pre_curadoria/ (arquivos .txt existentes)
    pasta_pre = config.RAIZ_PROJETO / 'pre_curadoria'
    if pasta_pre.exists():
        for root, dirs, files in os.walk(pasta_pre):
            for f in files:
                if f.endswith('.txt') and f != 'desktop.ini':
                    nome_base = f[:-4]
                    if nome_base.startswith('protagonista_'):
                        nome_base = nome_base[len('protagonista_'):]
                    slugs.add(nome_base[:55])

    return urls, slugs, titulos


def verificar_duplicidade_tripla(url_limpa, titulo, urls_salvas, slugs_salvos, titulos_salvos):
    """
    Executa a verificação tripla:
    1. URL canônica já salva
    2. Slug canônico já salvo
    3. Similaridade Jaccard >= 0.80 contra títulos existentes
    """
    if url_limpa in urls_salvas:
        return True, "URL idêntica já minerada"

    slug = extrair_slug_titulo(titulo)
    if slug in slugs_salvos:
        return True, f"Slug de título idêntico ({slug})"

    for t_existente in titulos_salvos:
        sim = calcular_similaridade_jaccard(titulo, t_existente)
        if sim >= 0.80:
            return True, f"Alta similaridade semântica ({int(sim*100)}%) com '{t_existente[:45]}...'"

    return False, ""


def salvar_rascunho_protagonista(resultado, item_dork, url_verificada, nome_veiculo, conteudo_raspado):
    """Salva a matéria em pre_curadoria/AAAA/MM/DD/protagonista_{slug}.txt sem criar sufixos duplicados."""
    agora = datetime.now()
    ano = agora.strftime('%Y')
    mes = agora.strftime('%m')
    dia = agora.strftime('%d')

    pasta_dia = config.RAIZ_PROJETO / 'pre_curadoria' / ano / mes / dia
    pasta_dia.mkdir(parents=True, exist_ok=True)

    titulo = resultado.get('title', 'Título não disponível')
    resumo = resultado.get('snippet', '')
    eixo = item_dork['eixo']

    # Classificação Semântica com Matriz de Pesos
    categoria, _ = classificar_materia(titulo, resumo, item_dork['categoria'])

    slug = extrair_slug_titulo(titulo)
    nome_arquivo = f'protagonista_{slug}.txt'
    caminho = pasta_dia / nome_arquivo

    corpo = conteudo_raspado if conteudo_raspado else resumo

    conteudo = f'---\n'
    conteudo += f'id_mineracao: min-protagonista-{agora.strftime("%Y%m%d%H%M%S")}\n'
    conteudo += f'titulo: {titulo}\n'
    conteudo += f'resumo: {resumo[:200]}\n'
    conteudo += f'autor: Curadoria Publicoverso\n'
    conteudo += f'categoria: {categoria}\n'
    conteudo += f'eixo_tematico: {eixo}\n'
    conteudo += f'fonte: {nome_veiculo}\n'
    conteudo += f'url_original: {url_verificada}\n'
    conteudo += f'link_status: Verificado (HTTP 200)\n'
    conteudo += f'data_verificacao: {agora.strftime("%d/%m/%Y %H:%M")}\n'
    conteudo += f'status: Pendente\n'
    conteudo += f'---\n\n'
    conteudo += corpo
    conteudo += f'\n\nFonte original: {url_verificada}'

    caminho.write_text(conteudo, encoding='utf-8')
    return caminho, categoria


def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Minerador Especialista de Protagonistas com Deduplicação Tripla.'
    )
    parser.add_argument('--dias', type=int, default=15, help='Janela de busca em dias (padrão: 15)')
    parser.add_argument('--eixo', type=str, default=None, help='Filtrar por eixo temático específico')
    parser.add_argument('--dry-run', action='store_true', help='Modo de teste sem gravar arquivos')
    args = parser.parse_args()

    config.registrar_log('=== Iniciando minerador de Protagonistas ("Vida Além do Trabalho") ===')

    erros = config.verificar_chaves()
    if erros:
        for e in erros:
            config.registrar_log(f'[ERRO] {e}')
        if not config.SERPER_API_KEY:
            print("[AVISO] SERPER_API_KEY ausente. Modo dry-run ou verificação apenas.")
            return

    urls_conhecidas, slugs_conhecidos, titulos_conhecidos = carregar_base_deduplicacao()
    config.registrar_log(f'Base anti-duplicidade: {len(urls_conhecidas)} URLs, {len(slugs_conhecidos)} slugs, {len(titulos_conhecidos)} títulos.')

    dorks = DORKS_PROTAGONISTAS
    if args.eixo:
        dorks = [d for d in dorks if d['eixo'] == args.eixo]
        if not dorks:
            config.registrar_log(f'[AVISO] Nenhum dork para o eixo: {args.eixo}')
            return

    total_novas = 0
    total_duplicadas = 0
    total_expurgadas = 0

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

        config.registrar_log(f'  Resultados brutos: {len(resultados)}')

        for res in resultados:
            url_bruta = res.get('link', '')
            titulo = res.get('title', '')
            resumo = res.get('snippet', '')

            if not url_bruta or not titulo:
                continue

            # 1. Filtro Factual de Servidor Público Brasileiro
            if not config.validar_servidor_publico_brasileiro(titulo, resumo, url_bruta):
                continue

            # 2. Filtro de expurgo institucional e burocrático
            if not e_materia_humanizada(titulo, resumo):
                total_expurgadas += 1
                config.registrar_log(f'  [EXPURGADO BUROCRÁTICO] {titulo[:60]}...')
                continue

            # 3. Verificação de Liveness e Canonização de URL
            url_limpa, veiculo, ok = verificar_liveness_e_canonizar(url_bruta)
            if not ok or not url_limpa:
                continue

            # 4. Deduplicação Tripla
            duplicado, motivo = verificar_duplicidade_tripla(url_limpa, titulo, urls_conhecidas, slugs_conhecidos, titulos_conhecidos)
            if duplicado:
                total_duplicadas += 1
                config.registrar_log(f'  [DUPLICATA IGNORADA] {motivo}')
                continue

            # 5. Raspagem de Conteúdo
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

            if args.dry_run:
                config.registrar_log(f'  [DRY-RUN NOVA MATÉRIA] {titulo[:60]} ({veiculo})')
                total_novas += 1
                continue

            caminho_rascunho, cat_final = salvar_rascunho_protagonista(res, item, url_limpa, veiculo, conteudo_raspado)
            urls_conhecidas.add(url_limpa)
            slugs_conhecidos.add(extrair_slug_titulo(titulo))
            titulos_conhecidos.append(titulo)

            # Grava no Acervo Geral de Links Minerados (CSV + JSON)
            id_prot = 'prot-' + hashlib.md5(url_limpa.encode()).hexdigest()[:10]
            data_hoje = datetime.now().strftime('%d/%m/%Y')
            resumo_limpo = (resumo[:200] if resumo else titulo).replace('\n', ' ').replace(',', ';')

            arquivo_json = config.RAIZ_PROJETO / 'data' / 'acervo_links_minerados.json'
            if arquivo_json.exists():
                try:
                    with open(arquivo_json, 'r', encoding='utf-8') as f:
                        lista_acervo = json.load(f)
                    lista_acervo.insert(0, {
                        "id": id_prot,
                        "data": data_hoje,
                        "categoria": cat_final,
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
            config.registrar_log(f'  [NOVA MATÉRIA SALVA] {caminho_rascunho.name} [{cat_final}]')
            time.sleep(config.PAUSA_ENTRE_REQUISICOES)

        time.sleep(config.PAUSA_ENTRE_REQUISICOES)

    config.registrar_log(f'=== Mineração Concluída: {total_novas} novas matérias, {total_duplicadas} duplicatas bloqueadas, {total_expurgadas} burocracias expurgadas. ===')


if __name__ == '__main__':
    main()
