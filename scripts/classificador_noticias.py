#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/classificador_noticias.py
---------------------------------
Classificador Semântico com Matriz de Pesos para o Portal Publicoverso.
Portal: Publicoverso (publicoverso.com.br)
Laboratório: YLuna85 LABs

Princípio Fundamental:
  Soberania da Ação Humana: As ações concretas (vencer maratona, publicar livro,
  doar sangue, inventar patente, salvar vidas) possuem peso 3x maior do que o cargo,
  órgão ou corporação do servidor, assegurando que um policial escritor vá para
  'Artes e Literatura' e um médico triatleta vá para 'Esportes e Aventura'.
"""

import os
import sys
import json
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# --- 9 Categorias Oficiais do Portal Publicoverso ---
CATEGORIAS_OFICIAIS = [
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

# --- Dicionários de Pesos Semânticos (Ações: 3 pts, Contexto: 1 pt) ---
DICIONARIO_SEMANTICO = {
    'Artes e Literatura': {
        'acoes_fortes': [
            'lança livro', 'lançou livro', 'publica romance', 'publicou romance', 'escreve poesia',
            'lançou hq', 'quadrinista', 'ilustrador', 'ilustradora', 'artista plástico', 'pintura em tela',
            'exposição de arte', 'exposição fotográfica', 'lançou single', 'gravou álbum', 'vocalista da banda',
            'peça de teatro', 'escreveu livro', 'sarau', 'poeta', 'poetisa', 'escritor', 'escritora'
        ],
        'termos_apoio': [
            'livro', 'romance', 'poesia', 'obra literária', 'fotografia', 'escultura', 'música', 'teatro',
            'literatura', 'artístico', 'artística', 'cultura', 'bienal'
        ]
    },
    'Esportes e Aventura': {
        'acoes_fortes': [
            'venceu maratona', 'completou maratona', 'campeão de jiu-jitsu', 'campeã de jiu-jitsu',
            'faixa preta', 'ironman', 'triatlo', 'travessia a nado', 'campeonato de fisiculturismo',
            'subiu ao pódio', 'medalha de ouro', 'medalha de prata', 'medalha de bronze', 'venceu torneio',
            'atleta amador', 'corrida rústica', 'corrida de rua', 'jogos pan-americanos', 'paralimpíadas'
        ],
        'termos_apoio': [
            'maratona', 'corrida', 'atleta', 'campeonato', 'torneio', 'pódio', 'futebol', 'natação',
            'ciclismo', 'judô', 'karatê', 'jiu-jitsu', 'voleibol', 'basquete', 'ultramaratona'
        ]
    },
    'Ciência e Tecnologia': {
        'acoes_fortes': [
            'registrou patente', 'desenvolveu aplicativo', 'criou software', 'descobriu espécie',
            'artigo publicado em revista internacional', 'pesquisa científica inovadora', 'prêmio de inovação',
            'inteligência artificial', 'invenção premiada'
        ],
        'termos_apoio': [
            'ciência', 'tecnologia', 'inovação', 'patente', 'pesquisa', 'software', 'aplicativo', 'laboratório',
            'pesquisador', 'pesquisadora', 'cientista', 'doutorado', 'artigo científico'
        ]
    },
    'Cultura Pop e Gastronomia': {
        'acoes_fortes': [
            'participa do bbb', 'participou do bbb', 'masterchef', 'the voice brasil', 'bake off brasil',
            'reality show', 'canal de culinária', 'humorista', 'stand-up comedy', 'canal no youtube',
            'influenciador digital', 'influenciadora digital', 'receita premiada', 'viralizou com comida'
        ],
        'termos_apoio': [
            'gastronomia', 'culinária', 'cultura pop', 'reality', 'humor', 'comédia', 'meme', 'viralizou',
            'chef', 'cozinha', 'entretenimento'
        ]
    },
    'Solidariedade e Comunidade': {
        'acoes_fortes': [
            'salvou vida fora do expediente', 'salvou criança', 'salvou animal', 'criou ong',
            'projeto social independente', 'resgate de animais', 'sopão comunitário', 'doação de sangue',
            'ensina crianças carentes', 'reforma voluntária', 'herói anônimo', 'ato de bravura de folga'
        ],
        'termos_apoio': [
            'voluntário', 'voluntária', 'voluntariado', 'solidariedade', 'doação', 'ajuda comunitária',
            'projeto social', 'ação social', 'resgate', 'bravura'
        ]
    },
    'Histórias e Superação': {
        'acoes_fortes': [
            'de gari a', 'de vigilante a', 'de merendeira a', 'de estagiário a', 'superou doença rara',
            'primeiro da família com diploma', '40 anos dedicados ao serviço', 'aposentou-se aos 90 anos',
            'história de vida emocionante', 'trajetória inspiradora'
        ],
        'termos_apoio': [
            'superação', 'trajetória', 'história de vida', 'legado', 'dedicação', 'aposentadoria histórica',
            'inspiração', 'exemplo de vida'
        ]
    },
    'Carreira e Conquistas': {
        'acoes_fortes': [
            'aprovado em 1º lugar', 'aprovada em 1º lugar', 'passou em concurso concorrido',
            'defendeu tese de doutorado', 'recebeu comenda oficial', 'homenagem por mérito',
            'assumiu cargo de destaque', 'conquista profissional'
        ],
        'termos_apoio': [
            'concurso público', 'aprovação', 'conquista', 'mérito', 'homenagem', 'carreira', 'posse',
            'capacitação', 'formação'
        ]
    },
    'Jurídico e PAD': {
        'acoes_fortes': [
            'decisão judicial anula demissão', 'stf garante direito', 'stj fixa tese',
            'reintegração de servidor', 'absolvido em pad', 'direito a licença-prêmio',
            'isonomia salarial reconhecida'
        ],
        'termos_apoio': [
            'pad', 'processo administrativo', 'stf', 'stj', 'tribunal', 'decisão judicial', 'liminar',
            'direito do servidor', 'estabilidade', 'reintegração', 'sindicato'
        ]
    },
    'Policial e Segurança Pública': {
        'acoes_fortes': [
            'operação policial desarticula', 'apreensão recorde de drogas', 'prisão de foragido',
            'desmantelou quadrilha', 'perícia desvenda crime', 'resgate em cativeiro'
        ],
        'termos_apoio': [
            'operação policial', 'polícia civil', 'polícia militar', 'polícia federal', 'guarda municipal',
            'segurança pública', 'prisão', 'apreensão', 'investigação', 'mandado'
        ]
    }
}

# --- Termos de Expurgo Burocrático Rígido ---
TERMOS_EXPURGO_BUROCRATICO = [
    'memorial descritivo', 'banca de rsc', 'rsc pcctae', 'progressão por capacitação funcional',
    'portaria de substituição de chefia', 'ata da reunião ordinária', 'aviso de licitação n',
    'pregão eletrônico n', 'termo de cooperação técnica sem', 'resultado preliminar de remoção interna'
]

def e_documento_burocratico(titulo, resumo=""):
    """Identifica se o texto é puramente burocrático e deve ser expurgado."""
    texto = f"{titulo} {resumo}".lower()
    for termo in TERMOS_EXPURGO_BUROCRATICO:
        if termo in texto:
            return True
    return False

def classificar_materia(titulo, resumo="", categoria_sugerida=""):
    """
    Classifica o texto em uma das 9 editorias aplicando a Matriz de Pesos Semânticos.
    Retorna (categoria_vencedora, pontuacoes).
    """
    texto = f"{titulo} {resumo}".lower()
    pontuacoes = {cat: 0 for cat in CATEGORIAS_OFICIAIS}
    
    # 1. Avalia ações fortes (peso 3) e termos de apoio (peso 1)
    for cat, regras in DICIONARIO_SEMANTICO.items():
        for acao in regras['acoes_fortes']:
            if acao in texto:
                pontuacoes[cat] += 3.5
        for termo in regras['termos_apoio']:
            if termo in texto:
                pontuacoes[cat] += 1.0

    # 2. Desambiguação Crítica: Ações Artísticas/Esportivas superam ocorrências policiais
    if pontuacoes['Artes e Literatura'] >= 3.0:
        pontuacoes['Policial e Segurança Pública'] = max(0, pontuacoes['Policial e Segurança Pública'] - 3.0)
        
    if pontuacoes['Esportes e Aventura'] >= 3.0:
        pontuacoes['Policial e Segurança Pública'] = max(0, pontuacoes['Policial e Segurança Pública'] - 3.0)

    # 3. Escolha da Categoria Vencedora
    categoria_max = max(pontuacoes, key=pontuacoes.get)
    maior_pontuacao = pontuacoes[categoria_max]

    if maior_pontuacao > 0:
        return categoria_max, pontuacoes
        
    # Se não atingiu pontuação mínima, utiliza a sugerida ou fallback seguro
    if categoria_sugerida in CATEGORIAS_OFICIAIS:
        return categoria_sugerida, pontuacoes
        
    return 'Histórias e Superação', pontuacoes

def reclassificar_acervo_json(caminho_json=None, dry_run=False):
    """Reclassifica o JSON de notícias aplicando o novo motor semântico."""
    if caminho_json is None:
        raiz = Path(__file__).parent.parent
        caminho_json = raiz / 'data' / 'noticias_curadoria.json'
        
    if not os.path.exists(caminho_json):
        print(f"[AVISO] Arquivo {caminho_json} não encontrado.")
        return
        
    with open(caminho_json, 'r', encoding='utf-8') as f:
        noticias = json.load(f)
        
    modificados = 0
    reclassificadas = []
    
    for item in noticias:
        cat_anterior = item.get('categoria', '')
        titulo = item.get('titulo', '')
        resumo = item.get('resumo', '')
        
        cat_nova, _ = classificar_materia(titulo, resumo, cat_anterior)
        
        if cat_nova != cat_anterior:
            modificados += 1
            item['categoria'] = cat_nova
            
        reclassificadas.append(item)
        
    print(f"📊 Total de Matérias Analisadas: {len(noticias)}")
    print(f"🔄 Matérias Reclassificadas: {modificados}")
    
    if not dry_run:
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(reclassificadas, f, ensure_ascii=False, indent=2)
        print(f"✅ Arquivo {caminho_json} atualizado com sucesso!")
    else:
        print("🔍 [DRY-RUN] Nenhuma alteração foi gravada em disco.")

if __name__ == "__main__":
    dry_run_mode = '--dry-run' in sys.argv
    reclassificar_acervo_json(dry_run=dry_run_mode)
