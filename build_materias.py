#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_materias.py - Pipeline de conversao de materias autorais para HTML
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Funcao:
  Le arquivos .txt ou .docx da pasta /materias/conteudo/
  Gera paginas HTML individuais em /materias/paginas/
  Cada pagina gerada contem navegacao de retorno ao portal principal,
  JSON-LD NewsArticle e estrutura semantica conforme o System Design.

Uso:
  python build_materias.py
  python build_materias.py --arquivo nome-do-arquivo.txt
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# --- Configuracao de Caminhos ---
DIRETORIO_BASE = Path(__file__).parent
DIRETORIO_CONTEUDO = DIRETORIO_BASE / 'materias' / 'conteudo'
DIRETORIO_PAGINAS = DIRETORIO_BASE / 'materias' / 'paginas'
ARQUIVO_JSON_NOTICIAS = DIRETORIO_BASE / 'data' / 'noticias_curadoria.json'


# --- Template HTML ---
def gerar_html(metadados, corpo_html):
    """Monta o HTML completo da materia com System Design do Publicoverso."""
    titulo = metadados.get('titulo', 'Materia sem titulo')
    resumo = metadados.get('resumo', '')
    autor = metadados.get('autor', 'Redacao Publicoverso')
    categoria = metadados.get('categoria', 'Gente e Cultura')
    data = metadados.get('data', datetime.today().strftime('%d/%m/%Y'))
    fonte = metadados.get('fonte', 'Publicoverso')

    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": titulo,
        "description": resumo,
        "datePublished": datetime.today().strftime('%Y-%m-%d'),
        "author": {
            "@type": "Person",
            "name": autor
        },
        "publisher": {
            "@type": "Organization",
            "name": "Publicoverso",
            "url": "https://publicoverso.com.br"
        },
        "articleSection": categoria,
        "inLanguage": "pt-BR"
    }, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{resumo}">
  <meta name="robots" content="index, follow">
  <meta property="og:title" content="{titulo} | Publicoverso">
  <meta property="og:description" content="{resumo}">
  <meta property="og:type" content="article">
  <title>{titulo} | Publicoverso</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../../index.css">
  <link rel="stylesheet" href="../materia.css">
  <script type="application/ld+json">
{json_ld}
  </script>
</head>
<body>

  <header class="navbar">
    <div class="navbar-container">
      <a href="/" class="brand-logo" aria-label="Voltar para a pagina inicial do Publicoverso">
        <svg class="logo-hex" width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <polygon points="20,2 35,10 35,30 20,38 5,30 5,10" stroke="url(#hexGradMateria)" stroke-width="2" fill="rgba(0,210,200,0.06)"/>
          <circle cx="20" cy="8" r="2.5" fill="#00D2C8"/><circle cx="31" cy="15" r="2.5" fill="#9146FF"/>
          <circle cx="31" cy="27" r="2.5" fill="#00D2C8"/><circle cx="20" cy="33" r="2.5" fill="#9146FF"/>
          <circle cx="9" cy="27" r="2.5" fill="#00D2C8"/><circle cx="9" cy="15" r="2.5" fill="#9146FF"/>
          <circle cx="20" cy="20" r="3.5" fill="#00D2C8"/>
          <line x1="20" y1="20" x2="20" y2="8" stroke="#00D2C8" stroke-width="1.2" opacity="0.7"/>
          <line x1="20" y1="20" x2="31" y2="15" stroke="#9146FF" stroke-width="1.2" opacity="0.7"/>
          <line x1="20" y1="20" x2="9" y2="15" stroke="#9146FF" stroke-width="1.2" opacity="0.7"/>
          <defs>
            <linearGradient id="hexGradMateria" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
              <stop stop-color="#00D2C8"/><stop offset="1" stop-color="#9146FF"/>
            </linearGradient>
          </defs>
        </svg>
        <div class="brand-text">
          <h1>Publicoverso</h1>
          <span>A rede do servico publico</span>
        </div>
      </a>
      <nav class="navbar-links" aria-label="Navegacao principal">
        <a href="/" class="nav-link">Inicio</a>
        <a href="/sobre.html" class="nav-link">Sobre</a>
        <a href="/contato.html" class="nav-link">Contato</a>
      </nav>
    </div>
  </header>

  <main class="main-wrapper">
    <article class="materia-completa" aria-labelledby="materia-titulo">

      <nav class="breadcrumb" aria-label="Localizacao na pagina">
        <a href="/">Inicio</a> &rsaquo;
        <a href="/index.html">Noticias</a> &rsaquo;
        <span>{categoria}</span>
      </nav>

      <header class="materia-header">
        <span class="news-badge badge-default" aria-label="Categoria: {categoria}">{categoria}</span>
        <h2 id="materia-titulo" class="materia-titulo">{titulo}</h2>
        <p class="materia-resumo">{resumo}</p>
        <div class="materia-meta">
          <span>Por <strong>{autor}</strong></span>
          <span>{data}</span>
          <span>Fonte: {fonte}</span>
        </div>
      </header>

      <div class="materia-corpo">
        {corpo_html}
      </div>

      <!-- Publicidade (AdSense) -->
      <aside class="adsense-block" aria-label="Publicidade">
        <p class="adsense-label">Publicidade</p>
      </aside>

      <footer class="materia-footer">
        <a href="/" class="btn-voltar" aria-label="Voltar para o portal principal do Publicoverso">
          &larr; Voltar ao Publicoverso
        </a>
        <div class="ferramentas-uteis">
          <p>Ferramentas para servidores publicos:</p>
          <a href="https://taes-federal.com.br/" target="_blank" rel="noopener noreferrer" class="link-accent">Calculadora TAE Federal</a>
        </div>
      </footer>

    </article>
  </main>

  <footer class="footer">
    <p class="footer-brand">Publicoverso</p>
    <nav class="footer-links" aria-label="Links institucionais do rodape">
      <a href="/">Inicio</a>
      <a href="/sobre.html">Sobre</a>
      <a href="/contato.html">Contato</a>
      <a href="/privacidade.html">Privacidade</a>
      <a href="/termos.html">Termos de Uso</a>
    </nav>
    <p class="footer-disclaimer">Portal independente, sem vinculo oficial com orgaos governamentais. Curadoria editorial: Cristina Mascarenhas.</p>
    <p>&copy; 2026 Publicoverso. Todos os direitos reservados.</p>
  </footer>

</body>
</html>
"""


# --- Parser de Arquivo .txt com Cabecalho Estruturado ---
def parsear_txt(caminho_arquivo):
    """
    Le um .txt com cabecalho YAML simplificado delimitado por '---'.
    Formato esperado:
      ---
      titulo: Titulo da materia
      resumo: Resumo de uma linha
      autor: Nome do autor
      categoria: Gente e Cultura
      data: 08/08/2026
      fonte: Curadoria Publicoverso
      ---
      Corpo da materia em texto corrido.
      Paragrafos separados por linha em branco.
    """
    conteudo = caminho_arquivo.read_text(encoding='utf-8')
    metadados = {}
    corpo = conteudo

    if conteudo.startswith('---'):
        partes = conteudo.split('---', 2)
        if len(partes) >= 3:
            bloco_meta = partes[1].strip()
            corpo = partes[2].strip()
            for linha in bloco_meta.splitlines():
                if ':' in linha:
                    chave, _, valor = linha.partition(':')
                    metadados[chave.strip()] = valor.strip()

    # Converter paragrafos em <p>
    paragrafos = [p.strip() for p in corpo.split('\n\n') if p.strip()]
    corpo_html = '\n'.join(f'<p>{p}</p>' for p in paragrafos)

    return metadados, corpo_html


# --- Parser de Arquivo .docx ---
def parsear_docx(caminho_arquivo):
    """Le um .docx usando python-docx. Requer: pip install python-docx"""
    try:
        from docx import Document
    except ImportError:
        print('[ERRO] Biblioteca python-docx nao encontrada. Execute: pip install python-docx')
        sys.exit(1)

    doc = Document(str(caminho_arquivo))
    paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # O primeiro paragrafo e tratado como titulo se nao houver cabecalho
    metadados = {
        'titulo': paragrafos[0] if paragrafos else 'Materia sem titulo',
        'resumo': paragrafos[1] if len(paragrafos) > 1 else '',
        'autor': 'Redacao Publicoverso',
        'categoria': 'Gente e Cultura',
        'data': datetime.today().strftime('%d/%m/%Y'),
        'fonte': 'Publicoverso',
    }

    corpo_paragrafos = paragrafos[2:] if len(paragrafos) > 2 else paragrafos
    corpo_html = '\n'.join(f'<p>{p}</p>' for p in corpo_paragrafos)

    return metadados, corpo_html


# --- Gerar Slug para Nome de Arquivo HTML ---
def gerar_slug(titulo):
    slug = titulo.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:80]


# --- Atualizar JSON de Noticias ---
def atualizar_json_noticias(metadados, slug_html):
    """Registra a nova materia no arquivo noticias_curadoria.json."""
    if not ARQUIVO_JSON_NOTICIAS.exists():
        noticias = []
    else:
        with open(ARQUIVO_JSON_NOTICIAS, 'r', encoding='utf-8') as f:
            noticias = json.load(f)

    novo_id = f"autoral-{slug_html[:30]}"
    url_materia = f"/materias/paginas/{slug_html}.html"

    # Verificar se ja existe
    ids_existentes = {n.get('id') for n in noticias}
    if novo_id in ids_existentes:
        print(f'[AVISO] Materia ja registrada no JSON: {novo_id}')
        return

    noticias.insert(0, {
        "id": novo_id,
        "titulo": metadados.get('titulo', ''),
        "resumo": metadados.get('resumo', ''),
        "conteudo_completo": metadados.get('resumo', ''),
        "categoria": metadados.get('categoria', 'Gente e Cultura'),
        "fonte": metadados.get('autor', 'Redacao Publicoverso'),
        "data": metadados.get('data', datetime.today().strftime('%d/%m/%Y')),
        "status": "Aprovada",
        "destaque": False,
        "url_materia": url_materia
    })

    with open(ARQUIVO_JSON_NOTICIAS, 'w', encoding='utf-8') as f:
        json.dump(noticias, f, ensure_ascii=False, indent=2)

    print(f'[OK] JSON atualizado: {url_materia}')


# --- Processar um Arquivo ---
def processar_arquivo(caminho_arquivo):
    sufixo = caminho_arquivo.suffix.lower()

    if sufixo == '.txt':
        metadados, corpo_html = parsear_txt(caminho_arquivo)
    elif sufixo == '.docx':
        metadados, corpo_html = parsear_docx(caminho_arquivo)
    else:
        print(f'[IGNORADO] Formato nao suportado: {caminho_arquivo.name}')
        return

    titulo = metadados.get('titulo', caminho_arquivo.stem)
    slug = gerar_slug(titulo)
    arquivo_saida = DIRETORIO_PAGINAS / f'{slug}.html'

    DIRETORIO_PAGINAS.mkdir(parents=True, exist_ok=True)

    html = gerar_html(metadados, corpo_html)
    arquivo_saida.write_text(html, encoding='utf-8')

    print(f'[OK] Gerado: {arquivo_saida.name}')

    atualizar_json_noticias(metadados, slug)


# --- Ponto de Entrada ---
def main():
    parser = argparse.ArgumentParser(
        description='Publicoverso - Pipeline de conversao de materias autorais para HTML.'
    )
    parser.add_argument(
        '--arquivo',
        type=str,
        help='Nome do arquivo especifico em materias/conteudo/ a processar (ex: minha-materia.txt)',
        default=None
    )
    args = parser.parse_args()

    if not DIRETORIO_CONTEUDO.exists():
        print(f'[ERRO] Diretorio de conteudo nao encontrado: {DIRETORIO_CONTEUDO}')
        sys.exit(1)

    if args.arquivo:
        caminho = DIRETORIO_CONTEUDO / args.arquivo
        if not caminho.exists():
            print(f'[ERRO] Arquivo nao encontrado: {caminho}')
            sys.exit(1)
        processar_arquivo(caminho)
    else:
        arquivos = list(DIRETORIO_CONTEUDO.glob('*.txt')) + list(DIRETORIO_CONTEUDO.glob('*.docx'))
        if not arquivos:
            print('[AVISO] Nenhum arquivo .txt ou .docx encontrado em materias/conteudo/')
            return
        for arq in sorted(arquivos):
            processar_arquivo(arq)

    print('\nPipeline concluido.')


if __name__ == '__main__':
    main()
