#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Carregamento centralizado de chaves de API e configuracoes globais
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Instrucoes:
  1. Crie um arquivo .env na raiz do repositorio com o conteudo:
       SERPER_API_KEY=sua_chave_aqui
       SCRAPER_API_KEY=sua_chave_aqui
  2. Importe este modulo nos scripts de mineracao.
"""

import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# --- Raiz do Projeto ---
RAIZ_PROJETO = Path(__file__).parent.parent

# --- Caminhos de Dados ---
ARQUIVO_NOTICIAS = RAIZ_PROJETO / 'data' / 'noticias_curadoria.json'
ARQUIVO_CONCURSOS = RAIZ_PROJETO / 'data' / 'concursos_radar.json'
ARQUIVO_ARTIGOS = RAIZ_PROJETO / 'data' / 'artigos_autorais.json'
ARQUIVO_HISTORICO = RAIZ_PROJETO / 'data' / 'historico_mineracao.json'
DIRETORIO_RASCUNHOS = RAIZ_PROJETO / 'materias' / 'conteudo'
DIRETORIO_PRE_CURADORIA = RAIZ_PROJETO / 'pre_curadoria'
DIRETORIO_PAGINAS = RAIZ_PROJETO / 'materias' / 'paginas'
ARQUIVO_LOG = RAIZ_PROJETO / 'scripts' / 'log_mineracao.txt'

# --- Carregamento de Variaveis de Ambiente ---
def _carregar_dotenv():
    """Le o arquivo .env da raiz e injeta as variaveis no ambiente."""
    caminho_env = RAIZ_PROJETO / '.env'
    if not caminho_env.exists():
        return
    with open(caminho_env, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#') or '=' not in linha:
                continue
            chave, _, valor = linha.partition('=')
            os.environ.setdefault(chave.strip(), valor.strip())

_carregar_dotenv()

# --- Chaves de API ---
SERPER_API_KEY = os.environ.get('SERPER_API_KEY', '')
SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY', '')

# --- Endpoints ---
SERPER_NEWS_URL = 'https://google.serper.dev/news'
SERPER_SEARCH_URL = 'https://google.serper.dev/search'
SCRAPER_API_URL = 'https://api.scraperapi.com/'

# --- Configuracoes de Mineracao ---
DIAS_RETROATIVOS_HISTORIAS = 7      # Janela de busca de noticias (dias)
DIAS_RETROATIVOS_CONCURSOS = 30     # Janela de busca de editais (dias)
MAX_RESULTADOS_POR_DORK = 10        # Limite de resultados por consulta
PAUSA_ENTRE_REQUISICOES = 2.5       # Segundos entre chamadas de API

# --- Categorias Validas do Portal ---
CATEGORIAS_VALIDAS = [
    'Gente e Cultura',
    'Conquistas e Premiacoes',
    'Carreira e Legislacao',
    'Inovacao e Boas Praticas',
]

# --- Dorks de Busca: Historias Humanas ---
DORKS_HISTORIAS = [
    # Categoria: Gente e Cultura
    {
        'categoria': 'Gente e Cultura',
        'query': '("servidor público" OR "servidora pública" OR "policial federal" OR "policial civil" OR "policial militar" OR "professor universitário" OR "médico do SUS" OR "analista judiciário" OR "técnico administrativo" OR "auditor fiscal") AND ("BBB" OR "Big Brother" OR "MasterChef" OR "The Voice" OR "reality show" OR "atleta" OR "campeão" OR "maratona" OR "jiu-jitsu" OR "natação" OR "corrida")',
    },
    {
        'categoria': 'Gente e Cultura',
        'query': '("servidor público" OR "funcionário público" OR "servidora pública") AND ("lança livro" OR "publicou livro" OR "autor de livro" OR "exposição de arte" OR "artista plástico" OR "músico" OR "cantor" OR "ator" OR "bailarino" OR "fotógrafo")',
    },

    # Categoria: Conquistas e Premiacoes
    {
        'categoria': 'Conquistas e Premiacoes',
        'query': '("servidor público" OR "professora da rede" OR "pesquisador" OR "médica" OR "enfermeira" OR "delegada") AND ("prêmio internacional" OR "vence prêmio" OR "reconhecimento internacional" OR "representará o Brasil" OR "patente registrada" OR "descoberta científica")',
    },
    {
        'categoria': 'Conquistas e Premiacoes',
        'query': '("servidor do IF" OR "servidor da UFBA" OR "servidor da UFRJ" OR "servidor da Fiocruz" OR "servidor da Embrapa" OR "servidor do INPE" OR "pesquisador federal") AND ("descoberta" OR "prêmio" OR "artigo publicado" OR "conquista" OR "condecoração")',
    },

    # Categoria: Inovacao e Boas Praticas
    {
        'categoria': 'Inovacao e Boas Praticas',
        'query': '("servidor público" OR "funcionário público" OR "agente público") AND ("criou aplicativo" OR "desenvolveu sistema" OR "app" OR "inovação" OR "tecnologia" OR "ato de bravura" OR "salvou vidas" OR "heroísmo" OR "projeto social")',
    },
    {
        'categoria': 'Inovacao e Boas Praticas',
        'query': '("prefeitura" OR "governo estadual" OR "governo federal" OR "órgão público") AND ("boas práticas" OR "case de sucesso" OR "melhoria" OR "premiação de gestão" OR "eficiência" OR "economizou" OR "reduziu desperdício")',
    },

    # Categoria: Carreira e Legislacao
    {
        'categoria': 'Carreira e Legislacao',
        'query': '("servidor público" OR "serviço público") AND ("trajetória inspiradora" OR "de gari a" OR "aprovado em concurso" OR "aposentadoria" OR "30 anos de serviço" OR "progressão na carreira" OR "virou médico" OR "virou juiz")',
    },
    {
        'categoria': 'Carreira e Legislacao',
        'query': '(PCCTAE OR "plano de carreira" OR "reajuste salarial" OR "revisão geral anual" OR "licença capacitação" OR "afastamento para mestrado" OR "afastamento para doutorado") AND ("servidor público" OR "funcional")',
    },
]

# --- Dorks de Busca: Editais de Concursos ---
DORKS_CONCURSOS = [
    '"inscrições abertas" ("concurso público" OR "processo seletivo") ("federal" OR "tribunal" OR "universidade federal" OR "instituto federal") 2026',
    '"edital publicado" "concurso público" ("DOU" OR "Diário Oficial") "vagas" 2026',
    'site:cebraspe.org.br "inscrições" 2026',
    'site:conhecimento.fgv.br "concurso" "inscrições" 2026',
    'site:institutoaocp.org.br "edital" "inscrições abertas" 2026',
    '"concurso público" ("Receita Federal" OR "Banco Central" OR "Senado" OR "Câmara dos Deputados" OR "TCU" OR "STJ" OR "STF") "vagas" 2026',
    '"concurso público" ("policial federal" OR "agente federal" OR "delegado" OR "perito federal") "vagas" 2026',
    '"concurso público" ("Anatel" OR "ANAC" OR "ANVISA" OR "IBGE" OR "IPEA" OR "Bacen") "vagas" 2026',
]


def verificar_chaves():
    """Verifica se as chaves de API estao configuradas."""
    erros = []
    if not SERPER_API_KEY:
        erros.append('SERPER_API_KEY nao configurada no arquivo .env')
    if not SCRAPER_API_KEY:
        erros.append('SCRAPER_API_KEY nao configurada no arquivo .env')
    return erros


def registrar_log(mensagem):
    """Registra uma mensagem no log de mineracao."""
    from datetime import datetime
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    linha = f'{timestamp} {mensagem}\n'
    try:
        ARQUIVO_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
            f.write(linha)
    except Exception:
        pass
    print(linha.strip())


if __name__ == '__main__':
    erros = verificar_chaves()
    if erros:
        print('[ATENCAO] Chaves de API ausentes:')
        for e in erros:
            print(f'  - {e}')
        print('\nCrie um arquivo .env na raiz do projeto com:')
        print('  SERPER_API_KEY=sua_chave_aqui')
        print('  SCRAPER_API_KEY=sua_chave_aqui')
    else:
        print('[OK] Todas as chaves de API estao configuradas.')
        print(f'Raiz do projeto: {RAIZ_PROJETO}')
