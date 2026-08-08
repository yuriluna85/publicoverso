/**
 * Publicoverso - app.js
 * Motor de renderização, busca por categoria, curadoria e acessibilidade.
 * Sistema Design: Dark Tech / Bento Grid / Glassmorphism
 */

(function () {
  'use strict';

  // --- Estado Global ---
  let noticiasMestre = [];
  let artigosMestre = [];
  let categoriaAtiva = 'Todas';

  // --- Carregamento de Dados ---
  async function inicializar() {
    try {
      const resNoticias = await fetch('data/noticias_curadoria.json');
      if (!resNoticias.ok) throw new Error('Falha ao carregar noticias_curadoria.json.');

      noticiasMestre = await resNoticias.json();

      renderizarNoticias(noticiasMestre);
      configurarFiltros();
      configurarBusca();
      configurarAcessibilidade();
    } catch (erro) {
      console.error('[Publicoverso] Erro ao inicializar:', erro);
    }
  }

  // --- Renderização de Notícias ---
  function renderizarNoticias(noticias) {
    const grid = document.getElementById('bentoGrid');
    if (!grid) return;

    const aprovadas = noticias.filter(n => n.status === 'Aprovada');

    if (aprovadas.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-muted); padding: 2rem;">Nenhuma notícia disponível no momento.</p>';
      return;
    }

    grid.innerHTML = aprovadas.map((noticia, idx) => {
      const classeDestaque = (noticia.destaque && idx === 0) ? ' featured' : '';
      const categoriaBadge = categoriaBadgeClass(noticia.categoria);
      const urlMateria = noticia.url_materia ? `href="${noticia.url_materia}"` : '#';

      return `
        <article class="card-news${classeDestaque}" data-categoria="${escapar(noticia.categoria)}">
          <header>
            <span class="news-badge ${categoriaBadge}" aria-label="Categoria: ${escapar(noticia.categoria)}">${escapar(noticia.categoria)}</span>
            <h3 class="news-title">${escapar(noticia.titulo)}</h3>
          </header>
          <p class="news-summary">${escapar(noticia.resumo)}</p>
          <footer class="news-meta">
            <span>${escapar(noticia.fonte)} &mdash; ${escapar(noticia.data)}</span>
            <div class="news-actions">
              ${noticia.url_materia ? `<a href="${escapar(noticia.url_materia)}" class="btn-curate" aria-label="Ler matéria completa: ${escapar(noticia.titulo)}">Ler mais</a>` : ''}
            </div>
          </footer>
        </article>
      `;
    }).join('');
  }

  // --- Renderizacao de Artigos Autorais (Desativado) ---
  /*
  function renderizarArtigos(artigos) {
    const grid = document.getElementById('authorsGrid');
    if (!grid) return;

    grid.innerHTML = artigos.map(artigo => `
      <article class="card-author">
        <p class="author-name">${escapar(artigo.autor)}</p>
        <p class="author-role">${escapar(artigo.persona)} &bull; ${escapar(artigo.data)}</p>
        <h3 class="article-title">${escapar(artigo.titulo)}</h3>
        <p class="article-excerpt">${escapar(artigo.resumo)}</p>
      </article>
    `).join('');
  }
  */

  // --- Mapeamento de Categoria para Classe de Badge ---
  function categoriaBadgeClass(categoria) {
    const mapa = {
      'Artes e Literatura': 'badge-artes',
      'Esportes e Aventura': 'badge-esportes',
      'Ciência e Tecnologia': 'badge-ciencia',
      'Ciencia e Tecnologia': 'badge-ciencia',
      'Cultura Pop e Gastronomia': 'badge-culturapop',
      'Solidariedade e Comunidade': 'badge-solidariedade',
      'Histórias e Superação': 'badge-historias',
      'Historias e Superacao': 'badge-historias',
      'Carreira e Conquistas': 'badge-carreira',
    };
    return mapa[categoria] || 'badge-default';
  }

  // --- Filtros de Categoria ---
  function configurarFiltros() {
    const chips = document.querySelectorAll('.chip[data-category]');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        categoriaAtiva = chip.dataset.category;
        aplicarFiltros();
      });
    });
  }

  // --- Busca por Texto ---
  function configurarBusca() {
    const input = document.getElementById('searchInput');
    if (!input) return;
    input.addEventListener('input', aplicarFiltros);
  }

  function aplicarFiltros() {
    const input = document.getElementById('searchInput');
    const termo = input ? input.value.toLowerCase().trim() : '';

    let filtradas = [...noticiasMestre].filter(n => n.status === 'Aprovada');

    if (categoriaAtiva !== 'Todas') {
      filtradas = filtradas.filter(n => n.categoria === categoriaAtiva);
    }

    if (termo) {
      filtradas = filtradas.filter(n =>
        (n.titulo || '').toLowerCase().includes(termo) ||
        (n.resumo || '').toLowerCase().includes(termo) ||
        (n.categoria || '').toLowerCase().includes(termo)
      );
    }

    renderizarNoticias(filtradas);
  }

  // --- Acessibilidade: Fonte e Alto Contraste ---
  function configurarAcessibilidade() {
    let tamanhoFonte = 100;

    const btnMais = document.getElementById('btnFontIncrease');
    const btnMenos = document.getElementById('btnFontDecrease');
    const btnContraste = document.getElementById('btnHighContrast');

    if (btnMais) {
      btnMais.addEventListener('click', () => {
        tamanhoFonte = Math.min(tamanhoFonte + 10, 140);
        document.documentElement.style.fontSize = tamanhoFonte + '%';
      });
    }

    if (btnMenos) {
      btnMenos.addEventListener('click', () => {
        tamanhoFonte = Math.max(tamanhoFonte - 10, 80);
        document.documentElement.style.fontSize = tamanhoFonte + '%';
      });
    }

    if (btnContraste) {
      btnContraste.addEventListener('click', () => {
        document.body.classList.toggle('high-contrast');
      });
    }
  }

  // --- Utilitário: Escape de HTML ---
  function escapar(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // --- Inicialização segura ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }

})();
