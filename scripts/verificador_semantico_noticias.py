#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verificador_semantico_noticias.py - Matriz Fina de Desambiguacao Semantica para Noticias
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Objetivo:
  Classificar e desambiguar rigorosamente o acervo de noticias mineradas entre
  as editorias:
  1. Policial e Segurança Pública (operacoes, prisões, crimes, investigacoes)
  2. Esportes e Aventura (maratonas, torneios, titulos esportivos de servidores)
  3. Jurídico e PAD (processos disciplinares, demissoes a bem do serviço publico, Lei 8.112, decisoes judiciais)
  4. Artes e Literatura (livros, exibiçoes, teatro, musica, artes plasticas)
  5. Ciência e Tecnologia (pesquisas, patentes, inovacao, softwares, artigos cientificos)
  6. Solidariedade e Comunidade (doaçoes, trabalho voluntario, proj sociais, resgates)
  7. Carreira e Conquistas / Histórias e Superação (posse, nomeacao, aposentadoria, trajetorias)

Regra de Prioridade:
  Atividades culturais, esportivas, cientificas e juridico-disciplinares prevalecem sobre
  a simples funcao do servidor (ex.: policial que publica livro -> Artes e Literatura;
  policial que vence maratona -> Esportes e Aventura; policial respondendo a PAD -> Jurídico e PAD).

Uso:
  python scripts/verificador_semantico_noticias.py
"""

import sys
import os
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DIRETORIO_RAIZ = Path(__file__).parent.parent
ARQUIVO_ACERVO_JSON = DIRETORIO_RAIZ / 'data' / 'acervo_links_minerados.json'
ARQUIVO_ACERVO_CSV = DIRETORIO_RAIZ / 'data' / 'acervo_links_minerados.csv'

# --- Filtro Estrito Anti-Anúncios Comerciais e Serviços Advocatícios ---
KEYWORDS_ANUNCIO_COMERCIAL = [
    'sindicância contra você', 'sindicancia contra voce', 'pad contra você', 'pad contra voce',
    'defesa técnica agora', 'defesa tecnica agora', 'contrate um advogado', 'advocacia especializada',
    'escritório de advocacia', 'escritorio de advocacia', 'fale conosco pelo whatsapp',
    'fale com nosso advogado', 'consulte nossos advogados', 'agende uma consulta', 'precisa de defesa',
    'defenda seu cargo', 'fale com um especialista', 'nossos serviços jurídicos',
    'nossos servicos juridicos', 'nosso escritório', 'nosso escritorio',
    'prestamos assessoria jurídica', 'prestamos assessoria juridica',
    'entre em contato conosco', 'serviços advocatícios', 'servicos advocaticios',
    'defesa em pad', 'defesa de servidores públicos', 'defesa de servidor',
    'escritório especializado', 'escritorio especializado', 'garanta seus direitos'
]


def eh_anuncio_comercial(titulo, resumo, url='', fonte=''):
    texto = f"{titulo} {resumo} {url} {fonte}".lower()
    for kw in KEYWORDS_ANUNCIO_COMERCIAL:
        if kw in texto:
            return True
    return False


# --- Dicionarios de Palavras-Chave para Desambiguacao Fina ---

KEYWORDS_JURIDICO_PAD = [
    'processo administrativo disciplinar', 'pad', 'demissão a bem do serviço público',
    'demissao a bem do servico publico', 'exoneração a pedido', 'exoneracao a pedido',
    'pena de demissão', 'pena de demissao', 'demitido a bem', 'sindicância punitiva',
    'sindicancia punitiva', 'improbidade administrativa', 'lei 8.112', 'lei 8112',
    'cassação de aposentadoria', 'cassacao de aposentadoria', 'mandado de segurança',
    'mandado de seguranca', 'recurso administrativo', 'decisão judicial', 'decisao judicial',
    'tribunal de contas', 'tcu', 'stf', 'stj', 'trf', 'tjsp', 'tjes', 'tjmg',
    'perda de cargo público', 'perda de cargo publico', 'cassação de mandato'
]

KEYWORDS_ESPORTES = [
    'maratona', 'maratonista', 'corrida de rua', 'campeonato', 'torneio', 'medalha de ouro',
    'medalha de prata', 'medalha de bronze', 'pódio', 'podio', 'atleta', 'futebol',
    'jiu-jitsu', 'jiujitsu', 'judô', 'judo', 'karatê', 'karate', 'natação', 'natacao',
    'ciclismo', 'triathlon', 'triatlo', 'ironman', 'venceu competição', 'venceu competicao',
    'campeão', 'campeao', 'campeã', 'campea', 'jogos universitários', 'olimpíadas', 'paralimpíadas'
]

KEYWORDS_ARTES = [
    'lança livro', 'lanca livro', 'publicou livro', 'obra literária', 'obra literaria',
    'romance', 'poesia', 'poema', 'exposição de arte', 'exposicao de arte', 'escritor',
    'escritora', 'artista plástico', 'artista plastico', 'escultura', 'pintura',
    'teatro', 'peça teatral', 'peca teatral', 'documentário', 'documentario', 'filme',
    'álbum musical', 'album musical', 'música', 'musica', 'cancao', 'canção', 'sarau'
]

KEYWORDS_CIENCIA = [
    'descoberta científica', 'descoberta cientifica', 'pesquisa científica', 'pesquisa cientifica',
    'patente registrada', 'artigo científico', 'artigo cientifico', 'desenvolveu aplicativo',
    'criou app', 'software livre', 'inteligência artificial', 'inovação tecnológica',
    'inovacao tecnologica', 'fiocruz', 'embrapa', 'inpe', 'cnpq', 'finep', 'prêmio científico'
]

KEYWORDS_SOLIDARIEDADE = [
    'doação de sangue', 'doacao de sangue', 'doador de sangue', 'ação solidária',
    'acao solidaria', 'trabalho voluntário', 'trabalho voluntario', 'voluntariado',
    'campanha do agasalho', 'arrecadação de alimentos', 'arrecadacao de alimentos',
    'caridade', 'projeto social', 'ajuda humanitária', 'ajuda humanitaria',
    'resgate de animais', 'sopão comunitário', 'sopao comunitario'
]

KEYWORDS_POLICIAL = [
    'operação policial', 'operacao policial', 'investigação criminal', 'investigacao criminal',
    'prisão em flagrante', 'prisao em flagrante', 'mandado de prisão', 'mandado de busca',
    'apreensão de drogas', 'apreensao de drogas', 'apreensão de armas', 'combate ao crime',
    'homicídio', 'homicidio', 'assalto', 'furto', 'roubo', 'facção criminosa', 'faccao criminosa',
    'crime organizado', 'perícia criminal', 'pericia criminal', 'confronto armado'
]


def desambiguar_categoria(titulo, resumo, categoria_atual=''):
    """
    Aplica a matriz de desambiguacao semantica fina baseada em contexto
    e hierarquia de prevalencia.
    """
    texto = f"{titulo} {resumo}".lower()

    # 1. Jurídico e PAD (Processo Administrativo, Demissao, Improbidade, Lei 8.112)
    for kw in KEYWORDS_JURIDICO_PAD:
        if kw in texto:
            return 'Jurídico e PAD'

    # 2. Esportes e Aventura (Prevalece sobre ocupacao policial/administrativa)
    for kw in KEYWORDS_ESPORTES:
        if kw in texto and any(term in texto for term in ['venceu', 'maratona', 'pódio', 'podio', 'atleta', 'campeão', 'campeao', 'campeã', 'campea', 'medalha', 'torneio', 'jiu-jitsu', 'judô', 'natação']):
            return 'Esportes e Aventura'

    # 3. Artes e Literatura (Prevalece sobre ocupacao policial/administrativa)
    for kw in KEYWORDS_ARTES:
        if kw in texto and any(term in texto for term in ['livro', 'romance', 'poesia', 'exposição', 'exposicao', 'escritor', 'escritora', 'artista', 'álbum', 'album', 'música', 'musica', 'teatro']):
            return 'Artes e Literatura'

    # 4. Ciência e Tecnologia
    for kw in KEYWORDS_CIENCIA:
        if kw in texto:
            return 'Ciência e Tecnologia'

    # 5. Solidariedade e Comunidade
    for kw in KEYWORDS_SOLIDARIEDADE:
        if kw in texto and not any(term in texto for term in ['operação', 'operacao', 'investigação', 'investigacao', 'prisão', 'prisao']):
            return 'Solidariedade e Comunidade'

    # 6. Policial e Segurança Pública (Estritamente acoes policiais e criminais)
    for kw in KEYWORDS_POLICIAL:
        if kw in texto:
            return 'Policial e Segurança Pública'

    # Manter categoria atual se for valida, ou fallback padrao
    categorias_validas = [
        'Artes e Literatura', 'Esportes e Aventura', 'Ciência e Tecnologia',
        'Cultura Pop e Gastronomia', 'Solidariedade e Comunidade',
        'Histórias e Superação', 'Carreira e Conquistas', 'Jurídico e PAD',
        'Policial e Segurança Pública'
    ]

    if categoria_atual in categorias_validas:
        return categoria_atual

    return 'Carreira e Conquistas'


def executar_verificacao():
    """Processa todos os itens em acervo_links_minerados.json aplicando o verificador semantico."""
    if not ARQUIVO_ACERVO_JSON.exists():
        print(f"[AVISO] Arquivo {ARQUIVO_ACERVO_JSON} nao encontrado.")
        return 0

    try:
        with open(ARQUIVO_ACERVO_JSON, 'r', encoding='utf-8') as f:
            itens = json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao ler {ARQUIVO_ACERVO_JSON}: {e}")
        return 0

    print(f"=== Executando Verificador Semântico de Notícias ({len(itens)} itens no acervo) ===")

    total_modificados = 0
    itens_filtrados = []
    estatisticas_categorias = {}

    for item in itens:
        titulo = item.get('titulo', '')
        resumo = item.get('resumo', '')
        url = item.get('url_original', '')
        fonte = item.get('fonte', '')
        cat_anterior = item.get('categoria', '')

        # Descartar anúncios comerciais e captação advocatícia
        if eh_anuncio_comercial(titulo, resumo, url, fonte):
            print(f"[REMOVIDO ANÚNCIO] {titulo} ({fonte})")
            total_modificados += 1
            continue

        cat_nova = desambiguar_categoria(titulo, resumo, cat_anterior)

        if cat_anterior != cat_nova:
            item['categoria'] = cat_nova
            total_modificados += 1

        estatisticas_categorias[cat_nova] = estatisticas_categorias.get(cat_nova, 0) + 1
        itens_filtrados.append(item)

    with open(ARQUIVO_ACERVO_JSON, 'w', encoding='utf-8') as f:
        json.dump(itens_filtrados, f, ensure_ascii=False, indent=2)

    print(f"[SUCESSO] Verificação concluída. {total_modificados} itens reclassificados.")
    print("Distribuição final por categoria:")
    for cat, qtd in sorted(estatisticas_categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {qtd}")

    return len(itens)


if __name__ == '__main__':
    executar_verificacao()
