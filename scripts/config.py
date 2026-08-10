#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py - Carregamento centralizado de chaves de API e configuracoes globais
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Instrucoes:
  1. Crie um arquivo .env na raiz do repositorio com o conteúdo:
       SERPER_API_KEY=sua_chave_aqui
       SCRAPER_API_KEY=sua_chave_aqui
  2. Importe este modulo nos scripts de mineracao.
"""

import sys
import os
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# --- Raiz do Projeto ---
RAIZ_PROJETO = Path(__file__).parent.parent

# --- Caminhos de Dados ---
ARQUIVO_NOTICIAS = RAIZ_PROJETO / 'data' / 'noticias_curadoria.json'
ARQUIVO_CONCURSOS = RAIZ_PROJETO / 'data' / 'concursos_radar.json'
ARQUIVO_ARTIGOS = RAIZ_PROJETO / 'data' / 'artigos_autorais.json'
ARQUIVO_HISTORICO = RAIZ_PROJETO / 'data' / 'historico_mineracao.json'
DIRETORIO_RASCUNHOS = RAIZ_PROJETO / 'materias' / 'conteúdo'
DIRETORIO_PRE_CURADORIA = RAIZ_PROJETO / 'pre_curadoria'
DIRETORIO_PAGINAS = RAIZ_PROJETO / 'materias' / 'páginas'
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
DIAS_RETROATIVOS_HISTORIAS = 7      # Janela de busca de notícias (dias)
DIAS_RETROATIVOS_CONCURSOS = 30     # Janela de busca de editais (dias)
MAX_RESULTADOS_POR_DORK = 10        # Limite de resultados por consulta
PAUSA_ENTRE_REQUISICOES = 2.5       # Segundos entre chamadas de API

# --- Categorias Validas do Portal (9 Editorias Jornalisticas) ---
CATEGORIAS_VALIDAS = [
    'Artes e Literatura',
    'Esportes e Aventura',
    'Ciência e Tecnologia',
    'Cultura Pop e Gastronomia',
    'Solidariedade e Comunidade',
    'Histórias e Superação',
    'Carreira e Conquistas',
    'Jurídico e PAD',
    'Policial e Segurança Pública'
]

# --- Matrizes de Validação Factual e Expurgo ---
DOMINIOS_INTERNACIONAIS_EXCLUIDOS = [
    '.pt', '.ao', '.mz', '.cv', 'diarioviseu.pt', 'publico.pt', 'dn.pt', 'jn.pt',
    'cmjornal.pt', 'record.pt', 'abola.pt', 'rtp.pt', 'sapo.pt', 'tsf.pt'
]

TERMOS_GEOGRAFICOS_ESTRANGEIROS = [
    'portugal', 'lisboa', 'porto', 'coimbra', 'castro daire', 'viseu', 'braga',
    'aveiro', 'leiria', 'algarve', 'funchal', 'angola', 'luanda', 'moçambique', 'maputo'
]

TERMOS_EXPURGO_POLITICO = [
    'vereador', 'vereadora', 'prefeito', 'prefeita', 'deputado', 'deputada',
    'senador', 'senadora', 'governador', 'governadora', 'presidente da república',
    'ministro de estado', 'secretário municipal de governo', 'secretário estadual',
    'candidato', 'candidata', 'eleições', 'campanha eleitoral', 'horário eleitoral',
    'partido político', 'coligação', 'palanque', 'votos', 'disputa eleitoral',
    'reeleição', 'comício', 'pesquisa eleitoral', 'câmara de vereadores',
    'plenário da câmara', 'assembleia legislativa'
]

ANCORAS_VINCULO_PUBLICO_BR = [
    'servidor público', 'servidora pública', 'funcionário público', 'funcionária pública',
    'servidor federal', 'servidora federal', 'servidor estadual', 'servidora estadual',
    'servidor municipal', 'servidora municipal', 'servidor concursado', 'servidora concursada',
    'servidor estatutário', 'cargo público', 'função pública', 'órgão público',
    'rede pública municipal', 'rede pública estadual', 'escola pública', 'colégio público',
    'universidade federal', 'instituto federal', 'ifba', 'ufba', 'ufrj', 'usp', 'unicamp',
    'unidade básica de saúde', 'posto de saúde', 'sus', 'hospital público', 'samu',
    'polícia federal', 'polícia civil', 'polícia militar', 'polícia rodoviária federal',
    'guarda municipal', 'guarda civil', 'bombeiro militar', 'perito criminal',
    'tribunal de justiça', 'tribunal regional', 'ministério público', 'defensoria pública',
    'receita federal', 'inss', 'ibama', 'icmbio', 'dnit', 'anvisa', 'anatel', 'fiocruz',
    'embrapa', 'diário oficial da união', 'diário oficial do estado', 'dou'
]

# --- Dorks de Busca: Histórias Humanas ---
DORKS_HISTORIAS = [
    # Categoria: Cultura Pop e Gastronomia
    {
        'categoria': 'Cultura Pop e Gastronomia',
        'query': '("servidor público" OR "servidora pública" OR "policial federal" OR "policial civil" OR "policial militar" OR "professor universitário" OR "médica do SUS" OR "analista judiciário" OR "auditor fiscal") AND ("BBB" OR "Big Brother" OR "MasterChef" OR "The Voice" OR "reality show" OR "gastronomia" OR "culinária") -site:*.pt -Portugal -vereador -prefeito -deputado',
    },
    # Categoria: Artes e Literatura
    {
        'categoria': 'Artes e Literatura',
        'query': '("servidor público" OR "funcionário público" OR "servidora pública") AND ("lança livro" OR "publicou livro" OR "autor de livro" OR "exposição de arte" OR "artista plástico" OR "músico" OR "cantor" OR "ator" OR "bailarino" OR "fotógrafo" OR "poesia") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Categoria: Esportes e Aventura
    {
        'categoria': 'Esportes e Aventura',
        'query': '("servidor público" OR "servidora pública" OR "policial militar" OR "bombeiro militar" OR "guarda municipal concursado") AND ("atleta" OR "campeão" OR "maratona" OR "jiu-jitsu" OR "natação" OR "corrida" OR "triatlo" OR "ironman" OR "olimpíadas") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Categoria: Ciência e Tecnologia
    {
        'categoria': 'Ciência e Tecnologia',
        'query': '("servidor público" OR "professora da rede pública" OR "pesquisador federal" OR "médica do SUS") AND ("prêmio internacional" OR "vence prêmio" OR "reconhecimento internacional" OR "patente registrada" OR "descoberta científica" OR "criou aplicativo" OR "desenvolveu sistema" OR "inovação") -site:*.pt -Portugal -vereador -prefeito',
    },
    {
        'categoria': 'Ciência e Tecnologia',
        'query': '("servidor do IF" OR "servidor da UFBA" OR "servidor da UFRJ" OR "servidor da Fiocruz" OR "servidor da Embrapa" OR "servidor do INPE" OR "pesquisador federal") AND ("descoberta" OR "prêmio" OR "artigo publicado" OR "conquista" OR "tecnologia") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Categoria: Solidariedade e Comunidade
    {
        'categoria': 'Solidariedade e Comunidade',
        'query': '("servidor público" OR "funcionário público" OR "agente público estatutário") AND ("projeto social" OR "ong" OR "voluntariado" OR "ato de bravura" OR "salvou vidas" OR "heroísmo" OR "ação comunitária") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Categoria: Histórias e Superação
    {
        'categoria': 'Histórias e Superação',
        'query': '("servidor público" OR "servidora pública") AND ("trajetória inspiradora" OR "de gari a" OR "superação" OR "aprovado em concurso" OR "aposentadoria" OR "30 anos de serviço" OR "virou médico" OR "virou juiz") -site:*.pt -Portugal -vereador -prefeito',
    },
    # Categoria: Carreira e Conquistas
    {
        'categoria': 'Carreira e Conquistas',
        'query': '("servidor público federal" OR "servidor estadual" OR "servidor municipal") AND ("progressão de carreira" OR "reestruturação de carreira" OR "RSC" OR "capacitação" OR "conquista de direitos") -site:*.pt -Portugal -vereador -prefeito',
    },
    {
        'categoria': 'Carreira e Conquistas',
        'query': '(PCCTAE OR "plano de carreira" OR "reajuste salarial" OR "revisão geral anual" OR "licença capacitação" OR "afastamento para mestrado" OR "afastamento para doutorado") AND ("servidor público" OR "funcional") -site:*.pt -Portugal -vereador -prefeito',
    }
]

# --- Classificador Inteligente por Palavras-Chave (7 Editorias) ---
PALAVRAS_CHAVE_EDITORIAS = {
    'Artes e Literatura': [
        'livro', 'livros', 'romance', 'poesia', 'poema', 'poemas', 'escritor', 'escritora',
        'autor', 'autora', 'literatura', 'literário', 'literária', 'quadrinista', 'hq',
        'gibi', 'ilustrador', 'ilustradora', 'arte', 'artes', 'artista', 'escultor',
        'escultora', 'pintura', 'quadro', 'exposição', 'teatro', 'peça', 'música',
        'músico', 'musico', 'cantor', 'cantora', 'violino', 'banda', 'álbum', 'album',
        'single', 'fotografia', 'fotógrafo', 'fotografa'
    ],
    'Esportes e Aventura': [
        'esporte', 'esportes', 'atleta', 'campeão', 'campeã', 'campeonato', 'maratona',
        'maratonista', 'triatlo', 'ironman', 'jiu-jitsu', 'jiujitsu', 'faixa preta',
        'judô', 'judo', 'karatê', 'karate', 'natação', 'natacao', 'nado', 'corrida',
        'ciclismo', 'bicicleta', 'futebol', 'basquete', 'vôlei', 'volei', 'olimpíadas',
        'olimpiadas', 'paralimpíadas', 'paralimpiadas', 'pan-americano', 'aventura',
        'escalada', 'travessia', 'fisiculturismo'
    ],
    'Ciência e Tecnologia': [
        'ciência', 'ciencia', 'científico', 'cientifico', 'científica', 'científica',
        'tecnologia', 'aplicativo', 'app', 'software', 'sistema', 'inovação', 'inovação',
        'descoberta', 'pesquisa', 'pesquisador', 'pesquisadora', 'artigo científico',
        'patente', 'inteligência artificial', 'ia', 'ti', 'dados', 'automação',
        'automacao', 'laboratório', 'laboratorio', 'fiocruz', 'embrapa', 'inpe'
    ],
    'Cultura Pop e Gastronomia': [
        'bbb', 'big brother', 'masterchef', 'the voice', 'reality', 'reality show',
        'culinária', 'culinaria', 'cozinha', 'gastronomia', 'receita', 'chef',
        'bake off', 'no limite', 'entretenimento', 'humorista', 'stand-up', 'youtube',
        'influenciador', 'influenciadora', 'tiktok'
    ],
    'Solidariedade e Comunidade': [
        'voluntariado', 'voluntário', 'voluntario', 'voluntária', 'voluntaria', 'ong',
        'projeto social', 'doação', 'doacao', 'doar', 'comunitário', 'comunitario',
        'comunitária', 'comunitaria', 'ação social', 'ação social', 'resgate',
        'causa social', 'crianças carentes', 'sopão', 'sopao', 'animais',
        'solidariedade', 'ajuda humanitária'
    ],
    'Histórias e Superação': [
        'superação', 'superacao', 'trajetória', 'trajetoria', 'história de vida',
        'historica', 'venceu', 'vencer', 'superou', 'desafio', 'de gari a',
        'de vigilante a', 'de merendeira a', 'de estagiário a', 'de estagiario a',
        'superou câncer', 'superou cancer', 'superou doença', 'deficiência',
        'deficiencia', 'pcd', 'inclusão', 'inclusao', 'inspiração', 'inspiracao',
        'inspiradora', 'lição de vida', 'licao de vida', 'aposentadoria',
        'centenário', 'centenario', 'legado'
    ],
    'Carreira e Conquistas': [
        'concurso', 'aprovado', 'aprovada', 'aprovação', 'aprovacao', 'posse',
        'carreira', 'promoção', 'promoção', 'progressão', 'progressao', 'pcctae',
        'rsc', 'reajuste', 'salário', 'salário', 'licença', 'licença', 'capacitação',
        'capacitação', 'prêmio', 'premio', 'premiação', 'premiação', 'reconhecimento',
        'conquista', 'gestão pública', 'gestao pública', 'eficiência', 'eficiencia',
        'mérito', 'merito', 'legislação', 'legislação', 'edital'
    ]
}


def classificar_categoria(titulo, resumo='', texto_completo=None, categoria_padrao=None):
    """
    Classifica automaticamente o conteúdo em uma das 7 Editorias Jornalisticas
    com base em contagem ponderada de palavras-chave.
    Ponderacao: Titulo tem peso 2, Resumo/Texto tem peso 1.
    """
    if not categoria_padrao or categoria_padrao not in CATEGORIAS_VALIDAS:
        categoria_padrao = 'Carreira e Conquistas'

    titulo_lower = (titulo or '').lower()
    corpo_lower = ((resumo or '') + ' ' + (texto_completo or '')).lower()

    pontuacao = {cat: 0 for cat in CATEGORIAS_VALIDAS}

    for cat, kw_list in PALAVRAS_CHAVE_EDITORIAS.items():
        for kw in kw_list:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, titulo_lower):
                pontuacao[cat] += 2
            if re.search(pattern, corpo_lower):
                pontuacao[cat] += 1

    melhor_categoria = max(pontuacao, key=pontuacao.get)
    if pontuacao[melhor_categoria] > 0:
        return melhor_categoria

    return categoria_padrao


def validar_servidor_publico_brasileiro(titulo, resumo='', url='', corpo=''):
    """
    Validador Factual em 4 Camadas para Garantir Exclusividade de Servidores Públicos do Brasil:
    1. Rejeita domínios internacionais (.pt, .ao, etc.)
    2. Rejeita termos geográficos de Portugal e outros países sem menção ao Brasil
    3. Rejeita mandatários políticos e termos eleitorais
    4. Exige ao menos UMA âncora textual confirmando vínculo com o serviço público brasileiro
    """
    url_lower = (url or '').lower()
    for dom in DOMINIOS_INTERNACIONAIS_EXCLUIDOS:
        if dom in url_lower:
            registrar_log(f'  [EXPURGADO INTERNACIONAL] Domínio excluído: {url}')
            return False

    texto_completo = ((titulo or '') + ' ' + (resumo or '') + ' ' + (corpo or '')).lower()

    # Expurgo Geográfico Estrangeiro
    for termo_geo in TERMOS_GEOGRAFICOS_ESTRANGEIROS:
        if termo_geo in texto_completo and 'brasil' not in texto_completo and 'brasileir' not in texto_completo:
            registrar_log(f'  [EXPURGADO ESTRANGEIRO] Menciona "{termo_geo}" sem vínculo com o Brasil.')
            return False

    # Expurgo Anti-Político
    for termo_pol in TERMOS_EXPURGO_POLITICO:
        if termo_pol in texto_completo:
            registrar_log(f'  [EXPURGADO POLÍTICO] Contém termo político: "{termo_pol}".')
            return False

    # Confirmação de Vínculo com Serviço Público Brasileiro
    tem_ancora = any(ancora in texto_completo for ancora in ANCORAS_VINCULO_PUBLICO_BR)
    if not tem_ancora:
        registrar_log(f'  [EXPURGADO SEM VÍNCULO] Não encontrada âncora comprovatória de serviço público BR.')
        return False

    return True

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
        erros.append('SERPER_API_KEY não configurada no arquivo .env')
    if not SCRAPER_API_KEY:
        erros.append('SCRAPER_API_KEY não configurada no arquivo .env')
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
