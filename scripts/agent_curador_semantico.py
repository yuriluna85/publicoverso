#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_curador_semantico.py - Agente Curador e Classificador Semântico Fino de Notícias
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Módulo autônomo responsável pela triagem, validação de vínculo funcional público,
expurgo político-eleitoral, desambiguação semântica fina por árvore determinística de 9 níveis
e normalização de editorias do acervo minerado.

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

# --- 1. Gatekeeper: Lista Obrigatória de Vínculo Funcional Público ---
TERMOS_VINCULO_PUBLICO_OBRIGATORIO = [
    'servidor público', 'servidora pública', 'servidor publico', 'servidora publica',
    'funcionário público', 'funcionária pública', 'funcionario publico', 'funcionaria publica',
    'servidor federal', 'servidora federal', 'servidor estadual', 'servidora estadual',
    'servidor municipal', 'servidora municipal', 'servidor concursado', 'servidora concursada',
    'servidor estatutário', 'servidora estatutária', 'servidor da união', 'servidor do estado',
    'policial civil', 'policial militar', 'policial federal', 'policial rodoviário', 'policial rodoviario',
    'delegado de polícia', 'delegada de polícia', 'delegado de policia', 'delegada de policia',
    'perito criminal', 'perita criminal', 'agente penitenciário', 'agente penitenciario',
    'policial penal', 'guarda municipal', 'guarda civil', 'bombeiro militar', 'bombeira militar',
    'médico do sus', 'médica do sus', 'enfermeiro do sus', 'enfermeira do sus',
    'professor da rede pública', 'professora da rede pública', 'professor universitário', 'professora universitária',
    'técnico judiciário', 'analista judiciário', 'auditor fiscal', 'auditora fiscal',
    'defensor público', 'defensora pública', 'promotor de justiça', 'promotora de justiça',
    'juiz de direito', 'juíza de direito', 'magistrado', 'magistrada', 'desembargador', 'desembargadora',
    'gari concursado', 'serviço público', 'servico publico', 'funcionalismo público', 'funcionalismo publico'
]

# --- 2. Gatekeeper: Expurgo Político-Eleitoral e Campanhas ---
TERMOS_EXPURGO_POLITICO_ELEITORAL = [
    'disputam o governo', 'disputa o governo', 'candidatos a governador', 'candidato a governador',
    'candidata a governadora', 'candidato a prefeito', 'candidata a prefeita', 'disputa a prefeitura',
    'candidato a deputado', 'candidata a deputada', 'candidato a senador', 'candidata a senadora',
    'convenção partidária', 'convencao partidaria', 'convenções partidárias', 'chapa eleitoral',
    'coligação partidária', 'partido político oficializa', 'horário eleitoral', 'campanha eleitoral',
    'pesquisa eleitoral aponta', 'corrida eleitoral', 'palanque eleitoral'
]

# --- 3. Matriz de Expurgo de Lixo, Jurisprudência Seca e Propagandas ---
PADROES_URL_EXCLUIDOS = [
    '@@download.pdf', '/download.pdf', '/contato', '/fale-conosco', '/ouvidoria',
    '/jurisprudencia/', '/inteiro-teor/', '/processo-consulta/',
    'droliveira.adv.br', 'apostilaopcao.com.br', 'jusbrasil.com.br/jurisprudencia',
    'instagram.com', 'facebook.com', 'fb.watch', 'linkedin.com', 'tiktok.com',
    'reddit.com', 'twitter.com', 'x.com', 't.co', 'threads.net', 'pinterest.com', 'kwai.com'
]

FONTES_REDES_BANIDAS = [
    'instagram', 'facebook', 'linkedin', 'tiktok', 'reddit', 'twitter', 'x', 'threads', 'pinterest', 'kwai'
]

TERMOS_TITULO_EXCLUIDOS = [
    'agravo interno nos embargos', 'recurso em mandado de segurança', 'habeas corpus nº',
    'recurso especial nº', 'agravo em recurso especial', 'apelação cível nº',
    'sindicância contra você', 'defesa técnica agora', 'contrate um advogado',
    'advocacia especializada', 'escritório de advocacia', 'apostila opção',
    'compre a apostila', 'curso preparatório', 'universidade federal do espírito santo (ufes)',
    'sei/ifmg', 'edital de convocação do ibge n 2', 'tabela de cargos', 'quadro de pessoal',
    'proposta de emenda à constituição 19/1993', 'data de publicação 02/10/1993'
]

DOMINIOS_ESTRANGEIROS = [
    '.pt', '.ao', '.mz', '.cv', 'publico.pt', 'dn.pt', 'jn.pt', 'cmjornal.pt',
    'rtp.pt', 'sapo.pt', 'tsf.pt'
]

TERMOS_ESTRANGEIROS = [
    'portugal', 'lisboa', 'porto', 'coimbra', 'castro daire', 'viseu', 'braga',
    'angola', 'luanda', 'moçambique', 'maputo'
]

# --- 4. Palavras-Chave para a Árvore Determinística de 9 Níveis ---

TERMOS_POLICIAL_CRIMES = [
    'homicídio', 'homicidio', 'assassinado', 'assassinada', 'assaltado', 'assaltada',
    'assalto', 'roubo', 'furto', 'esfaqueado', 'esfaqueada', 'morto a tiros', 'morta a tiros',
    'morto ao tentar', 'morta ao tentar', 'morre após moto', 'morre e neto', 'acidente fatal',
    'operação policial', 'operacao policial', 'investigação criminal', 'investigacao criminal',
    'prisão em flagrante', 'prisao em flagrante', 'mandado de prisão', 'apreensão de drogas',
    'facção criminosa', 'crime organizado', 'perícia criminal', 'confronto armado'
]

TERMOS_JURIDICO_STF_PAD = [
    'tema 1019', 'stf', 'stj', 'trânsito em julgado', 'transito em julgado', 'conflito de interesses',
    'fachin', 'ministro fachin', 'regras para participação', 'processo administrativo disciplinar',
    'pad', 'demissão a bem do serviço público', 'demissao a bem', 'exoneração punitiva',
    'pena de demissão', 'improbidade administrativa', 'lei 8.112', 'lei 8112',
    'cassação de aposentadoria', 'recurso administrativo', 'perda de cargo público'
]

TERMOS_ESPORTES_LUCIDOS = [
    'maratona', 'maratonista', 'corrida de rua', 'campeonato', 'torneio', 'medalha de ouro',
    'medalha de prata', 'medalha de bronze', 'pódio', 'podio', 'atleta', 'futebol',
    'jiu-jitsu', 'jiujitsu', 'judô', 'judo', 'karatê', 'karate', 'natação', 'natacao',
    'ciclismo', 'triathlon', 'triatlo', 'ironman', 'venceu competição', 'campeão', 'campeã'
]

TERMOS_ARTES_LIVROS = [
    'lança livro', 'lanca livro', 'lançou livro', 'publicou livro', 'obra literária',
    'romance', 'poesia', 'poema', 'exposição de arte', 'escritor', 'escritora',
    'artista plástico', 'escultura', 'pintura', 'peça teatral', 'álbum musical', 'música', 'sarau'
]

TERMOS_CIENCIA_PESQUISA = [
    'descoberta científica', 'pesquisa científica', 'patente registrada', 'artigo científico',
    'artigo publicado em revista', 'desenvolveu aplicativo', 'software livre',
    'inteligência artificial', 'inovação tecnológica', 'fiocruz', 'embrapa', 'inpe', 'cnpq'
]

TERMOS_CULTURA_POP = [
    'bbb', 'big brother', 'masterchef', 'the voice', 'reality show', 'culinária',
    'gastronomia', 'receita', 'chef', 'bake off', 'no limite', 'humorista', 'stand-up'
]

TERMOS_SOLIDARIEDADE = [
    'doação de sangue', 'doador de sangue', 'ação solidária', 'trabalho voluntário',
    'voluntariado', 'campanha do agasalho', 'arrecadação de alimentos', 'projeto social',
    'ajuda humanitária', 'resgate de animais', 'sopão comunitário'
]

TERMOS_HISTORIAS = [
    'trajetória inspiradora', 'de gari a', 'de vigilante a', 'de merendeira a', 'de estagiário a',
    'superou câncer', 'superou doença grave', 'pcd', 'inclusão', 'inspiração', 'superação', 'legado de vida'
]

TERMOS_CARREIRA = [
    'concurso', 'aprovado', 'aprovada', 'aprovação', 'toma posse', 'tomam posse', 'nomeação',
    'convocação', 'carreira', 'promoção', 'progressão', 'pcctae', 'rsc', 'reajuste', 'salário',
    'licença capacitação', 'aposentadoria voluntária', 'concessão de aposentadoria', 'oficializa aposentadoria',
    'desembargadora', 'desembargador', 'promotora de justiça', 'promotor de justiça', 'proposta de emenda'
]


def eh_lixo_digital(titulo, resumo, url, fonte):
    """Valida se o item deve ser descartado (Gatekeeper)."""
    texto_total = f"{titulo} {resumo} {url} {fonte}".lower()
    fonte_lower = (fonte or '').strip().lower()

    # 1. Checagem de tamanho mínimo de título
    if len(titulo.strip()) < 20:
        return True, "Título muito curto (< 20 caracteres)"

    # 2. Validação OBRIGATÓRIA de Vínculo Funcional Público
    tem_vinculo = any(term in texto_total for term in TERMOS_VINCULO_PUBLICO_OBRIGATORIO)
    if not tem_vinculo:
        return True, "Sem vínculo funcional público comprovado no texto"

    # 3. Expurgo Político-Eleitoral e Campanhas
    for t_pol in TERMOS_EXPURGO_POLITICO_ELEITORAL:
        if t_pol in texto_total:
            return True, f"Notícia sobre disputa político-eleitoral ({t_pol})"

    # 4. Checagem de fontes de redes sociais
    for f_banida in FONTES_REDES_BANIDAS:
        if f_banida == fonte_lower or f_banida in fonte_lower:
            return True, f"Fonte de rede social banida ({fonte})"

    # 5. Checagem de padrões de URL excluídos
    for padrao in PADROES_URL_EXCLUIDOS:
        if padrao in url.lower() or padrao in texto_total:
            return True, f"Padrão de URL/Texto banido ({padrao})"

    # 6. Checagem de títulos de não-notícias ou jurisprudência
    for termo in TERMOS_TITULO_EXCLUIDOS:
        if termo in texto_total:
            return True, f"Termo excluído detectado ({termo})"

    # 7. Checagem de contextos internacionais
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
    Árvore determinística de 9 níveis com contra-indicações estritas.
    """
    texto = f"{titulo} {resumo}".lower()

    # NÍVEL 1: Policial e Segurança Pública (Crimes, assaltos, homicídios, mortes violentas e acidentes)
    if any(kw in texto for kw in TERMOS_POLICIAL_CRIMES):
        return 'Policial e Segurança Pública'

    # NÍVEL 2: Jurídico e PAD (Decisões do STF, STJ, Temas, Conflito de Interesses, PADs)
    if any(kw in texto for kw in TERMOS_JURIDICO_STF_PAD):
        return 'Jurídico e PAD'

    # NÍVEL 3: Artes e Literatura (Produção autoral concreta de servidores)
    if any(kw in texto for kw in TERMOS_ARTES_LIVROS):
        return 'Artes e Literatura'

    # NÍVEL 4: Esportes e Aventura (Atletas e competições de servidores)
    if any(kw in texto for kw in TERMOS_ESPORTES_LUCIDOS):
        return 'Esportes e Aventura'

    # NÍVEL 5: Ciência e Tecnologia (Inovações e pesquisas científicas reais)
    if any(kw in texto for kw in TERMOS_CIENCIA_PESQUISA):
        return 'Ciência e Tecnologia'

    # NÍVEL 6: Cultura Pop e Gastronomia (Realities, culinária, humor)
    if any(kw in texto for kw in TERMOS_CULTURA_POP):
        return 'Cultura Pop e Gastronomia'

    # NÍVEL 7: Solidariedade e Comunidade (Voluntariado, doações, resgates)
    if any(kw in texto for kw in TERMOS_SOLIDARIEDADE):
        return 'Solidariedade e Comunidade'

    # NÍVEL 8: Histórias e Superação (Trajetórias inspiradoras de vida)
    if any(kw in texto for kw in TERMOS_HISTORIAS):
        return 'Histórias e Superação'

    # NÍVEL 9: Carreira e Conquistas (Vida funcional, posses, concursos, reajustes, aposentadorias)
    if any(kw in texto for kw in TERMOS_CARREIRA):
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

        # 1. Gatekeeper Anti-Lixo, Anti-Político e Validação de Vínculo Público
        lixo, motivo = eh_lixo_digital(titulo, resumo, url, fonte)
        if lixo:
            descartados += 1
            print(f"[DESCARTE GATEKEEPER] Motivo: {motivo} | {titulo[:60]}")
            continue

        # 2. Enriquecimento textual condicional
        if not resumo or len(resumo) < 30:
            resumo = enriquecer_resumo_se_necessario(url, resumo)
            item['resumo'] = resumo

        # 3. Classificação semântica fina determinística
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
    print(f"  - Itens descartados (Lixo/Política/Sem Vínculo): {descartados}")
    print(f"  - Itens reclassificados semanticamente: {reclassificados}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Publicoverso - Agente Curador e Classificador Semântico Fino")
    parser.add_argument('--reclassificar-tudo', action='store_true', help="Reprocessa todo o acervo histórico de notícias")
    args = parser.parse_args()

    processar_curadoria(reclassificar_tudo=args.reclassificar_tudo)


if __name__ == '__main__':
    main()
