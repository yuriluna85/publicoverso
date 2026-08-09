#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_materias.py - Pipeline de conversao de materias autorais para HTML
Portal: Publicoverso (publicoverso.com.br)
Laboratorio: YLuna85 LABs

Funcao:
  Le arquivos .txt ou .docx da pasta /materias/conteúdo/
  Gera páginas HTML individuais em /materias/páginas/
  Cada página gerada contem navegação de retorno ao portal principal,
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
    autor = metadados.get('autor', 'Redação Publicoverso')
    categoria = metadados.get('categoria', 'Carreira e Conquistas')
    data = metadados.get('data', datetime.today().strftime('%d/%m/%Y'))
    fonte = metadados.get('fonte', 'Publicoverso')
    url_original = metadados.get('url_original', '').strip()

    mapa_badges = {
        'Artes e Literatura': 'badge-artes',
        'Esportes e Aventura': 'badge-esportes',
        'Ciência e Tecnologia': 'badge-ciencia',
        'Ciencia e Tecnologia': 'badge-ciencia',
        'Cultura Pop e Gastronomia': 'badge-culturapop',
        'Solidariedade e Comunidade': 'badge-solidariedade',
        'Histórias e Superação': 'badge-histórias',
        'Histórias e Superacao': 'badge-histórias',
        'Carreira e Conquistas': 'badge-carreira',
    }
    badge_class = mapa_badges.get(categoria, 'badge-default')

    box_fonte_html = ''
    if url_original:
        box_fonte_html = f'''
      <aside class="box-fonte-original" aria-label="Atribuição de Fonte Original">
        <span class="box-fonte-label">Fonte da Notícia Original</span>
        <p class="box-fonte-texto">
          Matéria produzida com base em reportagem publicada por <strong>{fonte}</strong>.
        </p>
        <a href="{url_original}" target="_blank" rel="noopener noreferrer" class="box-fonte-link">
          Acessar matéria original em {fonte} &rarr;
        </a>
        <p class="box-fonte-disclaimer">
          O Publicoverso referencia e valoriza o jornalismo profissional. Esta publicação é um resumo curado com link verificado para a fonte primária da informação.
        </p>
      </aside>'''

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
  <link rel="icon" type="image/x-icon" href="../../favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="../../favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="../../favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="../../apple-touch-icon.png">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="stylesheet" href="../../index.css">
  <link rel="stylesheet" href="../materia.css">
  <script type="application/ld+json">
{json_ld}
  </script>
</head>
<body>

  <header class="navbar">
    <div class="navbar-container">
      <a href="../../index.html" class="brand-logo" aria-label="Voltar para a página inicial do Publicoverso">
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
          <span>A rede do serviço público</span>
        </div>
      </a>
      <nav class="navbar-links" aria-label="Navegação principal">
        <a href="../../index.html" class="nav-link">Início</a>
        <a href="../../noticias.html" class="nav-link">Notícias</a>
        <a href="../../concursos.html" class="nav-link">Radar de Concursos</a>
        <a href="../../sobre.html" class="nav-link">Sobre</a>
        <a href="../../contato.html" class="nav-link">Contato</a>
      </nav>

      <!-- Controles de Acessibilidade e Tema -->
      <div class="controls-bar" aria-label="Controles de Acessibilidade e Tema">
        <button id="btnFontDecrease" class="btn-a11y" aria-label="Diminuir tamanho do texto">A-</button>
        <button id="btnFontIncrease" class="btn-a11y" aria-label="Aumentar tamanho do texto">A+</button>
        <button id="btnThemeToggle" class="btn-a11y" aria-label="Alternar entre Modo Claro e Escuro">Tema: Claro</button>
        <button id="btnHighContrast" class="btn-a11y" aria-label="Alternar Modo Alto Contraste para baixa visão">Alto Contraste</button>
      </div>
    </div>
  </header>

  <main class="main-wrapper">
    <article class="materia-completa" aria-labelledby="materia-titulo">

      <nav class="breadcrumb" aria-label="Localizacao na página">
        <a href="../../index.html">Início</a> &rsaquo;
        <span>{categoria}</span>
      </nav>

      <header class="materia-header">
        <span class="news-badge {badge_class}" aria-label="Categoria: {categoria}">{categoria}</span>
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

      {box_fonte_html}

      <!-- Publicidade (AdSense) -->
      <aside class="adsense-block" aria-label="Publicidade">
        <p class="adsense-label">Publicidade</p>
      </aside>

      <footer class="materia-footer">
        <a href="../../index.html" class="btn-voltar" aria-label="Voltar para o portal principal do Publicoverso">
          &larr; Voltar ao Publicoverso
        </a>
        <div class="ferramentas-uteis">
          <p>Ferramentas para servidores públicos:</p>
          <a href="https://taes-federal.com.br/" target="_blank" rel="noopener noreferrer" class="link-accent">Calculadora TAE Federal</a>
        </div>
      </footer>

    </article>
  </main>

  <!-- Mega-Rodapé Editorial Institucional -->
  <footer class="footer-mega" aria-label="Rodapé institucional e navegacional do Publicoverso">
    <div class="footer-mega-container">
      
      <div class="footer-col footer-col-brand">
        <div class="footer-brand-header">
          <div class="pv-logo-hexagon" aria-hidden="true">
            <svg width="32" height="32" viewBox="0 0 40 40" fill="none">
              <polygon points="20,2 35,10 35,30 20,38 5,30 5,10" stroke="url(#hexGradFooter)" stroke-width="2.5" fill="rgba(0, 210, 200, 0.08)"/>
              <circle cx="20" cy="20" r="3.5" fill="#00D2C8"/>
              <circle cx="20" cy="8" r="2.5" fill="#00D2C8"/>
              <circle cx="31" cy="15" r="2.5" fill="#9146FF"/>
              <circle cx="31" cy="27" r="2.5" fill="#00D2C8"/>
              <circle cx="20" cy="33" r="2.5" fill="#9146FF"/>
              <circle cx="9" cy="27" r="2.5" fill="#00D2C8"/>
              <circle cx="9" cy="15" r="2.5" fill="#9146FF"/>
              <defs>
                <linearGradient id="hexGradFooter" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                  <stop stop-color="#00D2C8"/>
                  <stop offset="1" stop-color="#9146FF"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <span class="footer-brand-title">Publicoverso</span>
        </div>
        <p class="footer-brand-desc">
          O portal comunitário de notícias, conquistas e histórias inspiradoras de quem faz o serviço público acontecer no Brasil.
        </p>
        <div class="curatorial-badge">
          <span class="curatorial-icon" aria-hidden="true">✍️</span>
          <span>Curadoria Editorial: <strong>Cristina Mascarenhas</strong></span>
        </div>
      </div>

      <div class="footer-col">
        <h3 class="footer-col-title">Editorias</h3>
        <ul class="footer-col-list">
          <li><a href="../../noticias.html?cat=Artes%20e%20Literatura">Artes &amp; Literatura</a></li>
          <li><a href="../../noticias.html?cat=Esportes%20e%20Aventura">Esportes &amp; Aventura</a></li>
          <li><a href="../../noticias.html?cat=Ci%C3%AAncia%20e%20Tecnologia">Ciência &amp; Tecnologia</a></li>
          <li><a href="../../noticias.html?cat=Cultura%20Pop%20e%20Gastronomia">Cultura Pop &amp; Gastronomia</a></li>
          <li><a href="../../noticias.html?cat=Solidariedade%20e%20Comunidade">Solidariedade &amp; Comunidade</a></li>
          <li><a href="../../noticias.html?cat=Policial%20e%20Seguran%C3%A7a%20P%C3%BAblica">Policial &amp; Segurança Pública</a></li>
          <li><a href="../../noticias.html?cat=Carreira%20e%20Conquistas">Carreira &amp; Conquistas</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h3 class="footer-col-title">Utilitários &amp; Serviços</h3>
        <ul class="footer-col-list">
          <li><a href="../../servicos.html">Contrate Nossos Serviços</a></li>
          <li><a href="https://taes-federal.com.br/" target="_blank" rel="noopener noreferrer">Calculadora TAE Federal</a></li>
          <li><a href="../../simulador-diárias.html">Simulador de Diárias</a></li>
          <li><a href="../../concursos.html">Radar de Editais</a></li>
          <li><a href="../../sobre.html">Sobre a Equipe</a></li>
          <li><a href="../../contato.html">Canal de Sugestões</a></li>
        </ul>
      </div>

      <div class="footer-col">
        <h3 class="footer-col-title">Governança &amp; Privacidade</h3>
        <ul class="footer-col-list">
          <li><a href="../../privacidade.html">Política de Privacidade (LGPD)</a></li>
          <li><a href="../../termos.html">Termos e Condições de Uso</a></li>
          <li><a href="mailto:publicoverso@gmail.com">Redação (publicoverso@gmail.com)</a></li>
          <li><a href="../../contato.html#dpo">Contato Encarregado (DPO)</a></li>
        </ul>
      </div>

    </div>

    <div class="footer-bottom">
      <div class="footer-bottom-container">
        <p class="footer-legal-disclaimer">
          Portal comunitário independente, sem vínculo oficial com órgãos governamentais. Conteúdos curados sob a Lei nº 13.709/2018 (LGPD).
        </p>
        <p class="footer-copyright">
          &copy; 2026 Publicoverso. Todos os direitos reservados. Desenvolvimento e Tecnologia: YLuna85 LABs.
        </p>
      </div>
    </div>
  </footer>
  <script>
    (function() {{
      var btnMais = document.getElementById('btnFontIncrease');
      var btnMenos = document.getElementById('btnFontDecrease');
      var btnTema = document.getElementById('btnThemeToggle');
      var btnAlto = document.getElementById('btnHighContrast');
      var tamanho = 100;

      function aplicar(tema) {{
        document.body.classList.remove('theme-dark', 'theme-high-contrast');
        if (tema === 'escuro') {{
          document.body.classList.add('theme-dark');
          if (btnTema) btnTema.textContent = 'Tema: Escuro';
        }} else if (tema === 'alto-contraste') {{
          document.body.classList.add('theme-high-contrast');
          if (btnTema) btnTema.textContent = 'Tema: Claro';
        }} else {{
          if (btnTema) btnTema.textContent = 'Tema: Claro';
        }}
        localStorage.setItem('publicoverso-tema-v3', tema);
      }}

      var salvo = localStorage.getItem('publicoverso-tema-v3') || 'claro';
      aplicar(salvo);

      if (btnMais) btnMais.addEventListener('click', function() {{ tamanho = Math.min(tamanho + 10, 140); document.documentElement.style.fontSize = tamanho + '%'; }});
      if (btnMenos) btnMenos.addEventListener('click', function() {{ tamanho = Math.max(tamanho - 10, 80); document.documentElement.style.fontSize = tamanho + '%'; }});
      if (btnTema) btnTema.addEventListener('click', function() {{
        var t = localStorage.getItem('publicoverso-tema-v3') || 'claro';
        aplicar(t === 'escuro' ? 'claro' : 'escuro');
      }});
      if (btnAlto) btnAlto.addEventListener('click', function() {{
        var t = localStorage.getItem('publicoverso-tema-v3') || 'claro';
        aplicar(t === 'alto-contraste' ? 'claro' : 'alto-contraste');
      }});
    }})();
  </script>
</body>
</html>
"""


# --- Parser de Arquivo .txt com Cabeçalho Estruturado ---
def parsear_txt(caminho_arquivo):
    """
    Le um .txt com cabeçalho YAML simplificado delimitado por '---'.
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
    conteúdo = caminho_arquivo.read_text(encoding='utf-8')
    metadados = {}
    corpo = conteúdo

    if conteúdo.startswith('---'):
        partes = conteúdo.split('---', 2)
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
        print('[ERRO] Biblioteca python-docx não encontrada. Execute: pip install python-docx')
        sys.exit(1)

    doc = Document(str(caminho_arquivo))
    paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # O primeiro paragrafo e tratado como titulo se não houver cabeçalho
    metadados = {
        'titulo': paragrafos[0] if paragrafos else 'Materia sem titulo',
        'resumo': paragrafos[1] if len(paragrafos) > 1 else '',
        'autor': 'Redação Publicoverso',
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


# --- Atualizar JSON de Notícias ---
def atualizar_json_noticias(metadados, slug_html):
    """Registra a nova materia no arquivo noticias_curadoria.json."""
    if not ARQUIVO_JSON_NOTICIAS.exists():
        notícias = []
    else:
        with open(ARQUIVO_JSON_NOTICIAS, 'r', encoding='utf-8') as f:
            notícias = json.load(f)

    novo_id = metadados.get('id_mineracao') or f"autoral-{slug_html[:30]}"
    url_materia = f"materias/páginas/{slug_html}.html"

    # Verificar se já existe
    ids_existentes = {n.get('id') for n in notícias}
    if novo_id in ids_existentes:
        print(f'[AVISO] Materia já registrada no JSON: {novo_id}')
        return

    item_noticia = {
        "id": novo_id,
        "titulo": metadados.get('titulo', ''),
        "resumo": metadados.get('resumo', ''),
        "conteudo_completo": metadados.get('resumo', ''),
        "categoria": metadados.get('categoria', 'Gente e Cultura'),
        "fonte": metadados.get('fonte') or metadados.get('autor') or 'Redação Publicoverso',
        "data": metadados.get('data', datetime.today().strftime('%d/%m/%Y')),
        "status": metadados.get('status', 'Aprovada'),
        "destaque": False,
        "url_materia": url_materia
    }

    if metadados.get('url_original'):
        item_noticia['url_original'] = metadados.get('url_original')

    notícias.insert(0, item_noticia)

    with open(ARQUIVO_JSON_NOTICIAS, 'w', encoding='utf-8') as f:
        json.dump(notícias, f, ensure_ascii=False, indent=2)

    print(f'[OK] JSON atualizado: {url_materia}')


# --- Processar um Arquivo ---
def processar_arquivo(caminho_arquivo):
    sufixo = caminho_arquivo.suffix.lower()

    if sufixo == '.txt':
        metadados, corpo_html = parsear_txt(caminho_arquivo)
    elif sufixo == '.docx':
        metadados, corpo_html = parsear_docx(caminho_arquivo)
    else:
        print(f'[IGNORADO] Formato não suportado: {caminho_arquivo.name}')
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
        help='Nome do arquivo especifico em materias/conteúdo/ a processar (ex: minha-materia.txt)',
        default=None
    )
    args = parser.parse_args()

    if not DIRETORIO_CONTEUDO.exists():
        print(f'[ERRO] Diretorio de conteúdo não encontrado: {DIRETORIO_CONTEUDO}')
        sys.exit(1)

    if args.arquivo:
        caminho = DIRETORIO_CONTEUDO / args.arquivo
        if not caminho.exists():
            print(f'[ERRO] Arquivo não encontrado: {caminho}')
            sys.exit(1)
        processar_arquivo(caminho)
    else:
        arquivos = list(DIRETORIO_CONTEUDO.glob('*.txt')) + list(DIRETORIO_CONTEUDO.glob('*.docx'))
        if not arquivos:
            print('[AVISO] Nenhum arquivo .txt ou .docx encontrado em materias/conteúdo/')
            return
        for arq in sorted(arquivos):
            processar_arquivo(arq)

    print('\nPipeline concluído.')


if __name__ == '__main__':
    main()
