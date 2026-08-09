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
      const [resNoticias, resAcervo] = await Promise.all([
        fetch('data/noticias_curadoria.json'),
        fetch('data/acervo_links_minerados.json').catch(() => null)
      ]);

      if (!resNoticias.ok) throw new Error('Falha ao carregar noticias_curadoria.json.');

      noticiasMestre = await resNoticias.json();
      let acervoLinks = (resAcervo && resAcervo.ok) ? await resAcervo.json() : noticiasMestre;

      renderizarHeroGrid(noticiasMestre, acervoLinks);
      renderizarBentoGrid(noticiasMestre);
      configurarFiltros();
      configurarBusca();
      configurarAcessibilidade();
    } catch (erro) {
      console.error('[Publicoverso] Erro ao inicializar:', erro);
    }
  }

  // --- Renderização do Hero Grid (G1 + Jornal da USP) ---
  function renderizarHeroGrid(noticiasCuradas, acervoLinks) {
    const mainCol = document.getElementById('heroMainCard');
    const secondaryCol = document.getElementById('heroSecondaryCards');
    const feedCol = document.getElementById('heroFeedList');

    const aprovadas = noticiasCuradas.filter(n => n.status === 'Aprovada');
    if (aprovadas.length === 0) return;

    // 1. Super Manchete (Item 0)
    const principal = aprovadas[0];
    if (mainCol && principal) {
      const badgeClass = categoriaBadgeClass(principal.categoria);
      const urlMateria = principal.url_materia || '#';
      mainCol.innerHTML = `
        <div>
          <span class="hat-badge ${badgeClass}">${escapar(principal.categoria)}</span>
          <h2 class="main-title">
            <a href="${escapar(urlMateria)}">${escapar(principal.titulo)}</a>
          </h2>
          <p class="line-fine">${escapar(principal.resumo)}</p>
        </div>
        <footer class="hero-meta-footer">
          <span>${escapar(principal.fonte)} &bull; ${escapar(principal.data)}</span>
          ${principal.url_materia ? `<a href="${escapar(urlMateria)}" class="btn-curate" aria-label="Ler matéria: ${escapar(principal.titulo)}">Ler matéria completa &rarr;</a>` : ''}
        </footer>
      `;
    }

    // 2. Destaques Secundários (Itens 1 e 2)
    if (secondaryCol) {
      const secundarias = aprovadas.slice(1, 3);
      secondaryCol.innerHTML = secundarias.map(sec => {
        const badgeClass = categoriaBadgeClass(sec.categoria);
        const urlMateria = sec.url_materia || '#';
        return `
          <article class="secondary-card">
            <div>
              <span class="hat-badge ${badgeClass}" style="font-size:0.72rem;">${escapar(sec.categoria)}</span>
              <h3 class="secondary-title">
                <a href="${escapar(urlMateria)}">${escapar(sec.titulo)}</a>
              </h3>
              <p class="secondary-excerpt">${escapar(sec.resumo)}</p>
            </div>
            <footer class="hero-meta-footer" style="padding-top:0.6rem;">
              <span>${escapar(sec.fonte)} &bull; ${escapar(sec.data)}</span>
              ${sec.url_materia ? `<a href="${escapar(urlMateria)}" class="btn-curate btn-curate-sm">Ler</a>` : ''}
            </footer>
          </article>
        `;
      }).join('');
    }

    // 3. Feed "Últimas do Serviço Público" (Estilo G1)
    if (feedCol) {
      const ultimas = (acervoLinks && acervoLinks.length ? acervoLinks : aprovadas).slice(0, 5);
      feedCol.innerHTML = ultimas.map(item => {
        const urlDestino = item.url_materia || item.url_original || '#';
        const targetAttr = !item.url_materia && item.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';
        return `
          <div class="feed-item-mini">
            <span class="feed-meta-time">${escapar(item.data)} &bull; ${escapar(item.categoria || 'Geral')}</span>
            <h4 class="feed-item-title">
              <a href="${escapar(urlDestino)}" ${targetAttr}>${escapar(item.titulo)}</a>
            </h4>
          </div>
        `;
      }).join('');
    }
  }

  // --- Renderização do Bento Grid Geral ---
  function renderizarBentoGrid(noticias) {
    const grid = document.getElementById('bentoGrid');
    if (!grid) return;

    let aprovadas = noticias.filter(n => n.status === 'Aprovada');

    if (categoriaAtiva !== 'Todas') {
      aprovadas = aprovadas.filter(n => n.categoria === categoriaAtiva);
    }

    // Pula os primeiros 3 itens no modo "Todas" pois já estão em destaque no Hero Grid
    const paraGrid = (categoriaAtiva === 'Todas' && aprovadas.length > 3) ? aprovadas.slice(3) : aprovadas;

    if (paraGrid.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-muted); padding: 2rem; text-align: center; width: 100%;">Nenhuma notícia adicional nesta editoria no momento.</p>';
      return;
    }

    grid.innerHTML = paraGrid.map((noticia) => {
      const categoriaBadge = categoriaBadgeClass(noticia.categoria);
      const urlMateria = noticia.url_materia ? `href="${noticia.url_materia}"` : '#';

      return `
        <article class="card-news" data-categoria="${escapar(noticia.categoria)}">
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

    renderizarBentoGrid(filtradas);
  }

  // --- Acessibilidade: Fonte e Sistema Triplo de Temas ---
  function configurarAcessibilidade() {
    let tamanhoFonte = 100;

    const btnMais = document.getElementById('btnFontIncrease');
    const btnMenos = document.getElementById('btnFontDecrease');
    const btnTemaToggle = document.getElementById('btnThemeToggle');
    const btnContraste = document.getElementById('btnHighContrast');

    function aplicarTema(tema) {
      document.body.classList.remove('theme-dark', 'theme-high-contrast');

      if (tema === 'escuro') {
        document.body.classList.add('theme-dark');
        if (btnTemaToggle) btnTemaToggle.textContent = 'Tema: Escuro';
        if (btnContraste) btnContraste.classList.remove('active');
      } else if (tema === 'alto-contraste') {
        document.body.classList.add('theme-high-contrast');
        if (btnTemaToggle) btnTemaToggle.textContent = 'Tema: Claro';
        if (btnContraste) btnContraste.classList.add('active');
      } else {
        // Claro (Padrão)
        if (btnTemaToggle) btnTemaToggle.textContent = 'Tema: Claro';
        if (btnContraste) btnContraste.classList.remove('active');
      }

      localStorage.setItem('publicoverso-tema-v3', tema);
    }

    // Restaura preferência de tema salva no navegador (Padrão: 'claro')
    const temaSalvo = localStorage.getItem('publicoverso-tema-v3') || 'claro';
    aplicarTema(temaSalvo);

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

    if (btnTemaToggle) {
      btnTemaToggle.addEventListener('click', () => {
        const temaAtual = localStorage.getItem('publicoverso-tema-v3') || 'claro';
        const novoTema = (temaAtual === 'escuro') ? 'claro' : 'escuro';
        aplicarTema(novoTema);
      });
    }

    if (btnContraste) {
      btnContraste.addEventListener('click', () => {
        const temaAtual = localStorage.getItem('publicoverso-tema-v3') || 'claro';
        const novoTema = (temaAtual === 'alto-contraste') ? 'claro' : 'alto-contraste';
        aplicarTema(novoTema);
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
