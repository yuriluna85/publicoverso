#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_curador_semantico.py - Agente Curador e Classificador Semântico de Notícias
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Módulo autônomo responsável pela triagem, limpeza de não-notícias (garbage collector),
desambiguação semântica fina e normalização de editorias do acervo minerado.

Uso:
  python scripts/agent_curador_semantico.py
  python scripts/agent_curador_semantico.py --reclassificar-tudo
"""

import sys
import os
import json
import csv
import re
import argparse
from pathlib import Path
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    pass

RAIZ = Path(__file__).parent.parent
DATA_DIR = RAIZ / 'data'
ARQUIVO_ACERVO_JSON = DATA_DIR / 'acervo_links_minerados.json'
ARQUIVO_ACERVO_CSV = DATA_DIR / 'acervo_links_minerados.csv'
LOG_FILE = RAIZ / 'scripts' / 'log_mineracao.txt'

# --- 1. Matriz de Expurgo Anti-Lixo, Anti-Jurisprudência e Anti-Propaganda ---

PADROES_URL_EXCLUIDOS = [
    '@@download.pdf', '/download.pdf', '/contato', '/fale-conosco', '/ouvidoria',
    '/jurisprudencia/', '/inteiro-teor/', '/processo-consulta/',
    'droliveira.adv.br', 'apostilaopcao.com.br', 'jusbrasil.com.br/jurisprudencia'
]

TERMOS_TITULO_EXCLUIDOS = [
    'agravo interno nos embargos', 'recurso em mandado de segurança', 'habeas corpus nº',
    'recurso especial nº', 'agravo em recurso especial', 'apelação cível nº',
    'sindicância contra você', 'defesa técnica agora', 'contrate um advogado',
    'advocacia especializada', 'escritório de advocacia', 'apostila opção',
    'compre a apostila', 'curso preparatório', 'universidade federal do espírito santo (ufes)',
    'sei/ifmg', 'edital de convocação do ibge n 2', 'tabela de cargos', 'quadro de pessoal'
]

DOMINIOS_ESTRANGEIROS = [
    '.pt', '.ao', '.mz', '.cv', 'publico.pt', 'dn.pt', 'jn.pt', 'cmjornal.pt',
    'rtp.pt', 'sapo.pt', 'tsf.pt'
]

TERMOS_ESTRANGEIROS = [
    'portugal', 'lisboa', 'porto', 'coimbra', 'castro daire', 'viseu', 'braga',
    'angola', 'luanda', 'moçambique', 'maputo'
]

# --- 2. Matriz de Palavras-Chave e Contra-Indicações por Nível de Precedência ---

# Nível 1: Jurídico e PAD
KEYWORDS_JURIDICO_PAD = [
    'processo administrativo disciplinar', 'pad', 'demissão a bem do serviço público',
    'demissao a bem do servico publico', 'exoneração a pedido', 'exoneracao a pedido',
    'pena de demissão', 'pena de demissao', 'demitido a bem', 'sindicância punitiva',
    'sindicancia punitiva', 'improbidade administrativa', 'lei 8.112', 'lei 8112',
    'cassação de aposentadoria', 'cassacao de aposentadoria', 'recurso administrativo',
    'perda de cargo público', 'perda de cargo publico', 'cassação de mandato'
]

# Nível 2: Policial e Segurança Pública
KEYWORDS_POLICIAL = [
    'operação policial', 'operacao policial', 'investigação criminal', 'investigacao criminal',
    'prisão em flagrante', 'prisao em flagrante', 'mandado de prisão', 'mandado de busca',
    'apreensão de drogas', 'apreensao de drogas', 'apreensão de armas', 'combate ao crime',
    'homicídio', 'homicidio', 'assalto', 'furto', 'roubo', 'facção criminosa', 'faccao criminosa',
    'crime organizado', 'perícia criminal', 'pericia criminal', 'confronto armado', 'esfaqueado',
    'morto a tiros', 'assassinado', 'morto ao tentar apartar'
]

# Nível 3: Esportes e Aventura
KEYWORDS_ESPORTES = [
    'maratona', 'maratonista', 'corrida de rua', 'campeonato', 'torneio', 'medalha de ouro',
    'medalha de prata', 'medalha de bronze', 'pódio', 'podio', 'atleta', 'futebol',
    'jiu-jitsu', 'jiujitsu', 'judô', 'judo', 'karatê', 'karate', 'natação', 'natacao',
    'ciclismo', 'triathlon', 'triatlo', 'ironman', 'venceu competição', 'venceu competicao',
    'campeão', 'campeao', 'campeã', 'campea', 'jogos universitários', 'olimpíadas', 'paralimpíadas'
]

# Nível 4: Artes e Literatura
KEYWORDS_ARTES = [
    'lança livro', 'lanca livro', 'publicou livro', 'obra literária', 'obra literaria',
    'romance', 'poesia', 'poema', 'exposição de arte', 'exposicao de arte', 'escritor',
    'escritora', 'artista plástico', 'artista plastico', 'escultura', 'pintura',
    'teatro', 'peça teatral', 'peca teatral', 'documentário', 'documentario', 'filme',
    'álbum musical', 'album musical', 'música', 'musica', 'canção', 'sarau'
]

# Nível 5: Ciência e Tecnologia
KEYWORDS_CIENCIA = [
    'descoberta científica', 'descoberta cientifica', 'pesquisa científica', 'pesquisa cientifica',
    'patente registrada', 'artigo científico', 'artigo cientifico', 'desenvolveu aplicativo',
    'criou app', 'software livre', 'inteligência artificial', 'inovação tecnológica',
    'inovacao tecnologica', 'fiocruz', 'embrapa', 'inpe', 'cnpq', 'finep', 'prêmio científico'
]

# Nível 6: Cultura Pop e Gastronomia
KEYWORDS_CULTURA = [
    'bbb', 'big brother', 'masterchef', 'the voice', 'reality', 'reality show',
    'culinária', 'culinaria', 'cozinha', 'gastronomia', 'receita', 'chef',
    'bake off', 'no limite', 'humorista', 'stand-up', 'youtube'
]

# Nível 7: Solidariedade e Comunidade
KEYWORDS_SOLIDARIEDADE = [
    'doação de sangue', 'doacao de sangue', 'doador de sangue', 'ação solidária',
    'acao solidaria', 'trabalho voluntário', 'trabalho voluntario', 'voluntariado',
    'campanha do agasalho', 'arrecadação de alimentos', 'arrecadacao de alimentos',
    'caridade', 'projeto social', 'ajuda humanitária', 'ajuda humanitaria',
    'resgate de animais', 'sopão comunitário', 'sopao comunitario'
]

# Nível 8: Histórias e Superação
KEYWORDS_HISTORIAS = [
    'trajetória inspiradora', 'trajetoria inspiradora', 'história de vida',
    'de gari a', 'de vigilante a', 'de merendeira a', 'de estagiário a',
    'superou câncer', 'superou doença', 'pcd', 'inclusão', 'inspiração',
    'superação', 'superacao', 'legado de vida', 'história exemplar'
]

# Nível 9: Carreira e Conquistas
KEYWORDS_CARREIRA = [
    'concurso', 'aprovado', 'aprovada', 'aprovação', 'aprovacao', 'toma posse',
    'tomam posse', 'nomeação', 'nomeacao', 'convocação', 'convocacao', 'carreira',
    'promoção', 'progressão', 'pcctae', 'rsc', 'reajuste', 'salário', 'licença capacitação',
    'aposentadoria voluntária', 'concessão de aposentadoria', 'oficializa aposentadoria',
    'desembargadora', 'desembargador', 'promotora de justiça', 'promotor de justiça'
]


def eh_lixo_digital(titulo, resumo, url, fonte):
    """Valida se o item deve ser sumariamente descartado."""
    texto_total = f"{titulo} {resumo} {url} {fonte}".lower()

    # 1. Checagem de tamanho mínimo de título
    if len(titulo.strip()) < 20:
        return True, "Título muito curto (< 20 caracteres)"

    # 2. Checagem de padrões de URL excluídos
    for padrao in PADROES_URL_EXCLUIDOS:
        if padrao in url.lower() or padrao in texto_total:
            return True, f"Padrão de URL/Texto banido ({padrao})"

    # 3. Checagem de títulos de não-notícias ou jurisprudência
    for termo in TERMOS_TITULO_EXCLUIDOS:
        if termo in texto_total:
            return True, f"Termo excluído detectado ({termo})"

    # 4. Checagem de contextos internacionais
    parsed_url = urlparse(url)
    dominio = parsed_url.netloc.lower()
    for dom in DOMINIOS_ESTRANGEIROS:
        if dominio.endswith(dom) or dom in dominio:
            return True, f"Domínio internacional ({dom})"

    for term_est in TERMOS_ESTRANGEIROS:
        if f" {term_est} " in f" {texto_total} ":
            return True, f"Termo de contexto internacional ({term_est})"

    return False, ""


def enriquecer_resumo_se_necessario(url, resumo_atual):
    """Raspa levemente meta descriptions se o resumo atual for nulo ou vago."""
    if resumo_atual and len(resumo_atual.strip()) > 40:
        return resumo_atual

    if 'requests' not in sys.modules or 'BeautifulSoup' not in sys.modules:
        return resumo_atual

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
            if meta_desc and meta_desc.get('content'):
                return meta_desc.get('content').strip()
            paragrafos = soup.find_all('p')
            for p in paragrafos:
                txt = p.get_text().strip()
                if len(txt) > 50:
                    return txt[:250] + '...'
    except Exception:
        pass

    return resumo_atual


def classificar_semantica_fina(titulo, resumo, categoria_atual=""):
    """
    Aplica a matriz de prevalência hierárquica e contra-indicações estritas.
    """
    texto = f"{titulo} {resumo}".lower()

    # 1. Jurídico e PAD (Processo Disciplinar, Demissão a bem do serviço público)
    if any(kw in texto for kw in KEYWORDS_JURIDICO_PAD):
        if not any(term in texto for term in ['toma posse', 'nomeação', 'convocação', 'concurso público']):
            return 'Jurídico e PAD'

    # 2. Policial e Segurança Pública (Operações, crimes, homicídios, esfaqueamento)
    is_policial = any(kw in texto for kw in KEYWORDS_POLICIAL)
    if is_policial:
        # Se for um crime/homicídio, NÃO PODE cair em Artes ou Esportes mesmo que tenha a palavra 'show' ou 'jiu-jitsu'
        if any(term in texto for term in ['morto', 'homicídio', 'esfaqueado', 'assassinado', 'prisão', 'operação', 'criminoso']):
            return 'Policial e Segurança Pública'

    # 3. Esportes e Aventura (Competições, atletas, maratonas, medalhas)
    if any(kw in texto for kw in KEYWORDS_ESPORTES):
        if not any(term in texto for term in ['morto a tiros', 'assassinado', 'preso em flagrante', 'operação policial']):
            if any(term in texto for term in ['venceu', 'maratona', 'pódio', 'podio', 'atleta', 'campeão', 'campeao', 'campeã', 'campea', 'medalha', 'torneio', 'jiu-jitsu', 'judô', 'natação']):
                return 'Esportes e Aventura'

    # 4. Artes e Literatura (Livros, peças, música, exposições)
    if any(kw in texto for kw in KEYWORDS_ARTES):
        if not any(term in texto for term in ['morto ao tentar', 'apartar briga', 'esfaqueado', 'homicídio', 'assassinado']):
            if any(term in texto for term in ['livro', 'romance', 'poesia', 'exposição', 'exposicao', 'escritor', 'escritora', 'artista', 'álbum', 'album', 'música', 'musica', 'teatro']):
                return 'Artes e Literatura'

    # 5. Ciência e Tecnologia (Inovações, patentes, artigos científicos)
    if any(kw in texto for kw in KEYWORDS_CIENCIA):
        if not any(term in texto for term in ['oficializa aposentadoria', 'portaria de aposentadoria', 'toma posse', 'nomeação']):
            return 'Ciência e Tecnologia'

    # 6. Cultura Pop e Gastronomia
    if any(kw in texto for kw in KEYWORDS_CULTURA):
        return 'Cultura Pop e Gastronomia'

    # 7. Solidariedade e Comunidade
    if any(kw in texto for kw in KEYWORDS_SOLIDARIEDADE):
        if not any(term in texto for term in ['operação policial', 'investigação criminal', 'prisão em flagrante']):
            return 'Solidariedade e Comunidade'

    # 8. Histórias e Superação
    if any(kw in texto for kw in KEYWORDS_HISTORIAS):
        return 'Histórias e Superação'

    # 9. Policial Fallback (Se tiver marca policial clara)
    if is_policial:
        return 'Policial e Segurança Pública'

    # 10. Carreira e Conquistas (Posse, nomeação, aposentadoria, concursos)
    if any(kw in texto for kw in KEYWORDS_CARREIRA):
        return 'Carreira e Conquistas'

    categorias_validas = [
        'Artes e Literatura', 'Esportes e Aventura', 'Ciência e Tecnologia',
        'Cultura Pop e Gastronomia', 'Solidariedade e Comunidade',
        'Histórias e Superação', 'Carreira e Conquistas', 'Jurídico e PAD',
        'Policial e Segurança Pública'
    ]

    if categoria_atual in categorias_validas:
        return categoria_atual

    return 'Carreira e Conquistas'


def processar_curadoria(reclassificar_tudo=False):
    """Executa o pipeline completo de curadoria e sanitização semântica."""
    if not ARQUIVO_ACERVO_JSON.exists():
        print(f"[AVISO] Arquivo {ARQUIVO_ACERVO_JSON} não encontrado.")
        return

    try:
        with open(ARQUIVO_ACERVO_JSON, 'r', encoding='utf-8') as f:
            itens = json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar JSON: {e}")
        return

    print("=" * 65)
    print("AGENTE CURADOR E CLASSIFICADOR SEMÂNTICO DO PUBLICOVERSO")
    print(f"Total de itens para análise: {len(itens)}")
    print("=" * 65)

    descartados = 0
    reclassificados = 0
    acervo_sanitizado = []
    urls_vistas = set()

    for item in itens:
        titulo = item.get('titulo', '').strip()
        resumo = item.get('resumo', '').strip()
        url = item.get('url_original', '').strip()
        fonte = item.get('fonte', '').strip()
        cat_original = item.get('categoria', '').strip()

        # Deduplicação por URL
        if url in urls_vistas:
            descartados += 1
            print(f"[DESCARTE DUPLICADO] {titulo[:50]}...")
            continue
        urls_vistas.add(url)

        # 1. Filtro Anti-Lixo e Anti-Propaganda
        lixo, motivo = eh_lixo_digital(titulo, resumo, url, fonte)
        if lixo:
            descartados += 1
            print(f"[DESCARTE LIXO] Motivo: {motivo} | {titulo[:60]}")
            continue

        # 2. Enriquecimento textual condicional
        if not resumo or len(resumo) < 30:
            resumo = enriquecer_resumo_se_necessario(url, resumo)
            item['resumo'] = resumo

        # 3. Classificação semântica fina
        cat_nova = classificar_semantica_fina(titulo, resumo, cat_original)

        if cat_nova != cat_original:
            item['categoria'] = cat_nova
            reclassificados += 1
            print(f"[RECLASSIFICADO] {cat_original} -> {cat_nova} | {titulo[:60]}")

        acervo_sanitizado.append(item)

    # 4. Salvar base JSON e CSV sincronizados
    with open(ARQUIVO_ACERVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(acervo_sanitizado, f, ensure_ascii=False, indent=2)

    with open(ARQUIVO_ACERVO_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'data', 'categoria', 'titulo', 'resumo', 'fonte', 'url_original', 'status_curadoria'])
        writer.writeheader()
        for i in acervo_sanitizado:
            writer.writerow({
                'id': i.get('id', ''),
                'data': i.get('data', ''),
                'categoria': i.get('categoria', ''),
                'titulo': i.get('titulo', ''),
                'resumo': i.get('resumo', ''),
                'fonte': i.get('fonte', ''),
                'url_original': i.get('url_original', ''),
                'status_curadoria': i.get('status_curadoria', 'Aprovado')
            })

    print("-" * 65)
    print(f"SANITIÇÃO CONCLUÍDA:")
    print(f"  - Itens mantidos no acervo: {len(acervo_sanitizado)}")
    print(f"  - Itens descartados (Lixo/Duplicados): {descartados}")
    print(f"  - Itens reclassificados semanticamente: {reclassificados}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Publicoverso - Agente Curador e Classificador Semântico")
    parser.add_argument('--reclassificar-tudo', action='store_true', help="Reprocessa todo o acervo histórico de notícias")
    args = parser.parse_args()

    processar_curadoria(reclassificar_tudo=args.reclassificar_tudo)


if __name__ == '__main__':
    main()
