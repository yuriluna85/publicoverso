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

  // Trava de Segurança Defensiva Anti-Redes Sociais
  const REDES_BANIDAS = ['instagram.com', 'facebook.com', 'linkedin.com', 'tiktok.com', 'reddit.com', 'twitter.com', 'x.com', 'threads.net', 'youtube.com', 'pinterest.com', 'kwai.com'];

  function ehVeiculoNoticiosoValido(item) {
    if (!item) return false;
    const url = (item.url_original || item.url_materia || '').toLowerCase();
    const fonte = (item.fonte || '').toLowerCase();
    for (const r of REDES_BANIDAS) {
      if (url.includes(r) || fonte.includes(r.split('.')[0])) {
        return false;
      }
    }
    return true;
  }

  // --- Carregamento de Dados ---
  async function inicializar() {
    try {
      const [resNoticias, resAcervo, resArtigos] = await Promise.all([
        fetch('data/noticias_curadoria.json'),
        fetch('data/acervo_links_minerados.json').catch(() => null),
        fetch('data/artigos_autorais.json').catch(() => null)
      ]);

      let curadas = resNoticias.ok ? await resNoticias.json() : [];
      let mineradas = (resAcervo && resAcervo.ok) ? await resAcervo.json() : [];
      artigosMestre = (resArtigos && resArtigos.ok) ? await resArtigos.json() : [];

      // Unifica curadas e mineradas em uma lista mestre para a capa
      const urlsVistas = new Set();
      noticiasMestre = [];

      // Adiciona primeiro as curadas válidas
      for (const n of curadas) {
        if (!ehVeiculoNoticiosoValido(n)) continue;
        const chave = n.url_materia || n.url_original || n.id;
        urlsVistas.add(chave);
        noticiasMestre.push(n);
      }

      // Em seguida, adiciona as mineradas encontradas pelos robôs (apenas veículos noticiosos válidos)
      for (const m of mineradas) {
        if (!ehVeiculoNoticiosoValido(m)) continue;
        const chave = m.url_materia || m.url_original || m.id;
        if (!urlsVistas.has(chave)) {
          urlsVistas.add(chave);
          noticiasMestre.push(m);
        }
      }

      renderizarHeroGrid(noticiasMestre);
      renderizarColunasOpiniao(artigosMestre);
      renderizarListasEditoriais(noticiasMestre);
      configurarFiltros();
      configurarBusca();
      configurarAcessibilidade();
      configurarBannerLGPD();
    } catch (erro) {
      console.error('[Publicoverso] Erro ao inicializar:', erro);
    }
  }

  // --- Gestão de Cookies e Consentimento LGPD (Lei 13.709/2018) ---
  function configurarBannerLGPD() {
    const consentimento = localStorage.getItem('publicoverso_cookie_consent');
    if (consentimento) return; // Usuário já respondeu anteriormente

    const bannerHTML = `
      <div id="lgpdBanner" class="lgpd-banner" role="dialog" aria-live="polite" aria-label="Consentimento de Cookies e Privacidade">
        <div class="lgpd-content">
          <p class="lgpd-text">
            <strong>Privacidade e Transparência:</strong> Utilizamos cookies e tecnologias semelhantes para aprimorar a sua experiência de navegação, analisar o tráfego do portal e personalizar conteúdos, em estrita conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018 - LGPD). Ao continuar, você concorda com a nossa <a href="privacidade.html" class="lgpd-link">Política de Privacidade</a>.
          </p>
          <div class="lgpd-actions">
            <button id="btnLgpdAceitar" class="btn-lgpd btn-lgpd-primary">Aceitar Todos</button>
            <button id="btnLgpdRecusar" class="btn-lgpd btn-lgpd-secondary">Apenas Necessários</button>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', bannerHTML);

    const btnAceitar = document.getElementById('btnLgpdAceitar');
    const btnRecusar = document.getElementById('btnLgpdRecusar');
    const banner = document.getElementById('lgpdBanner');

    if (btnAceitar) {
      btnAceitar.addEventListener('click', function () {
        localStorage.setItem('publicoverso_cookie_consent', 'todos');
        if (banner) banner.remove();
      });
    }

    if (btnRecusar) {
      btnRecusar.addEventListener('click', function () {
        localStorage.setItem('publicoverso_cookie_consent', 'necessarios');
        if (banner) banner.remove();
      });
    }
  }

  // --- Renderização das Colunas de Opinião (Cristina Mascarenhas) ---
  function renderizarColunasOpiniao(artigos) {
    const container = document.getElementById('opinionArticlesList');
    if (!container) return;

    if (!artigos || artigos.length === 0) {
      container.innerHTML = `
        <div style="background: var(--bg-card); border: 1px dashed var(--border-color); border-radius: 8px; padding: 1.25rem; text-align: center;">
          <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.5rem 0;">Espaço Aberto para Artigos e Reflexões</h4>
          <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.4; margin: 0 0 0.8rem 0;">Temas sobre a práxis docente, tecnologia na gestão e valorização do servidorismo público.</p>
          <a href="contato.html" style="display: inline-block; background: var(--color-brand-purple); color: #FFF; font-size: 0.8rem; font-weight: 700; padding: 0.4rem 0.9rem; border-radius: 4px; text-decoration: none;">Envie sua sugestão de pauta &rarr;</a>
        </div>
      `;
      return;
    }

    container.innerHTML = artigos.map(artigo => `
      <article style="border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem;">
        <span style="font-size: 0.75rem; color: #00D2C8; font-weight: 700; text-transform: uppercase;">Opinião &bull; ${escapar(artigo.data || '2026')}</span>
        <h4 style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0.3rem 0;">
          <a href="${escapar(artigo.url_materia || artigo.url || 'sobre.html')}" style="color: inherit; text-decoration: none;">${escapar(artigo.titulo)}</a>
        </h4>
        <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; margin: 0;">${escapar(artigo.resumo)}</p>
      </article>
    `).join('');
  }

  // --- Renderização do Hero Grid (G1) ---
  function renderizarHeroGrid(noticias) {
    const mainCol = document.getElementById('heroMainCard');
    const secondaryCol = document.getElementById('heroSecondaryCards');
    const feedCol = document.getElementById('heroFeedList');

    if (!noticias || noticias.length === 0) return;

    // 1. Super Manchete (Item 0)
    const principal = noticias[0];
    if (mainCol && principal) {
      const badgeClass = categoriaBadgeClass(principal.categoria);
      const urlDestino = principal.url_materia || principal.url_original || '#';
      const targetAttr = !principal.url_materia && principal.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';

      mainCol.innerHTML = `
        <div>
          <span class="hat-badge ${badgeClass}">${escapar(principal.categoria || 'Serviço Público')}</span>
          <h2 class="main-title">
            <a href="${escapar(urlDestino)}" ${targetAttr}>${escapar(principal.titulo)}</a>
          </h2>
          <p class="line-fine">${escapar(principal.resumo)}</p>
        </div>
        <footer class="hero-meta-footer">
          <span>${escapar(principal.fonte)} &bull; ${escapar(principal.data)}</span>
          <a href="${escapar(urlDestino)}" class="btn-curate" ${targetAttr} aria-label="Ler matéria: ${escapar(principal.titulo)}">
            ${principal.url_materia ? 'Ler matéria completa &rarr;' : 'Ver no veículo original &rarr;'}
          </a>
        </footer>
      `;
    }

    // 2. Destaques Secundários (Itens 1 e 2)
    if (secondaryCol) {
      const secundarias = noticias.slice(1, 3);
      secondaryCol.innerHTML = secundarias.map(sec => {
        const badgeClass = categoriaBadgeClass(sec.categoria);
        const urlDestino = sec.url_materia || sec.url_original || '#';
        const targetAttr = !sec.url_materia && sec.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';

        return `
          <article class="secondary-card">
            <div>
              <span class="hat-badge ${badgeClass}" style="font-size:0.72rem;">${escapar(sec.categoria || 'Geral')}</span>
              <h3 class="secondary-title">
                <a href="${escapar(urlDestino)}" ${targetAttr}>${escapar(sec.titulo)}</a>
              </h3>
              <p class="secondary-excerpt">${escapar(sec.resumo)}</p>
            </div>
            <footer class="hero-meta-footer" style="padding-top:0.6rem;">
              <span>${escapar(sec.fonte)} &bull; ${escapar(sec.data)}</span>
              <a href="${escapar(urlDestino)}" class="btn-curate btn-curate-sm" ${targetAttr}>
                ${sec.url_materia ? 'Ler' : 'Ver'}
              </a>
            </footer>
          </article>
        `;
      }).join('');
    }

    // 3. Feed "Últimas do Serviço Público" (Estilo G1)
    if (feedCol) {
      const ultimas = noticias.slice(0, 5);
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

  // --- Renderização de Listas Discretas de Notícias em Linhas por Editoria (Padrão G1/R7) ---
  function renderizarListasEditoriais(noticias) {
    const container = document.getElementById('editorialListsContainer');
    if (!container) return;

    let lista = [...noticias];

    if (categoriaAtiva !== 'Todas') {
      lista = lista.filter(n => n.categoria === categoriaAtiva);
    } else if (lista.length > 3) {
      lista = lista.slice(3); // Pula os 3 destaques do Hero
    }

    if (lista.length === 0) {
      container.innerHTML = '<p style="color: var(--text-muted); padding: 2rem; text-align: center; width: 100%;">Nenhuma notícia encontrada nesta editoria.</p>';
      return;
    }

    // Mapeamento de categorias para arquivos .html dedicados
    const arquivosCategoria = {
      'Policial e Segurança Pública': 'categoria-policial.html',
      'Esportes e Aventura': 'categoria-esportes.html',
      'Artes e Literatura': 'categoria-artes.html',
      'Ciência e Tecnologia': 'categoria-ciencia.html',
      'Cultura Pop e Gastronomia': 'categoria-cultura.html',
      'Solidariedade e Comunidade': 'categoria-solidariedade.html',
      'Carreira e Conquistas': 'categoria-carreira.html',
      'Histórias e Superação': 'categoria-historias.html'
    };

    // Agrupa notícias por categoria
    const categoriasMap = {};
    lista.forEach(item => {
      const cat = item.categoria || 'Geral';
      if (!categoriasMap[cat]) categoriasMap[cat] = [];
      categoriasMap[cat].push(item);
    });

    container.innerHTML = Object.keys(categoriasMap).map(catName => {
      const itensCat = categoriasMap[catName];
      const linkCategoria = arquivosCategoria[catName] || `noticias.html?cat=${encodeURIComponent(catName)}`;

      return `
        <div class="editorial-block" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem; margin-bottom: 1rem;">
            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin: 0;">${escapar(catName)}</h3>
            <a href="${linkCategoria}" style="color: #00D2C8; font-size: 0.88rem; font-weight: 700; text-decoration: none;">Leia mais dessa categoria &rarr;</a>
          </div>
          <div class="news-list-rows" style="display: grid; gap: 1rem;">
            ${itensCat.slice(0, 3).map(item => {
              const urlDestino = item.url_materia || item.url_original || '#';
              const targetAttr = !item.url_materia && item.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';
              return `
                <article class="news-row-item" style="border-bottom: 1px dashed var(--border-color); padding-bottom: 0.75rem;">
                  <h4 style="font-family: 'Inter', sans-serif; font-size: 1.05rem; font-weight: 600; margin: 0 0 0.25rem 0;">
                    <a href="${escapar(urlDestino)}" ${targetAttr} style="color: var(--text-primary); text-decoration: none;">${escapar(item.titulo)}</a>
                  </h4>
                  <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.4; margin: 0 0 0.4rem 0;">${escapar(item.resumo)}</p>
                  <span style="font-size: 0.75rem; color: var(--text-muted);">${escapar(item.fonte)} &bull; ${escapar(item.data)}</span>
                </article>
              `;
            }).join('')}
          </div>
          <div style="margin-top: 1rem; text-align: right;">
            <a href="${linkCategoria}" class="btn-curate btn-curate-sm" style="display: inline-block;">Leia mais dessa categoria &rarr;</a>
          </div>
        </div>
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

    let filtradas = [...noticiasMestre];

    if (categoriaAtiva !== 'Todas') {
      filtradas = filtradas.filter(n => n.categoria === categoriaAtiva);
    }

    if (termo) {
      filtradas = filtradas.filter(n =>
        (n.titulo || '').toLowerCase().includes(termo) ||
        (n.resumo || '').toLowerCase().includes(termo) ||
        (n.categoria || '').toLowerCase().includes(termo) ||
        (n.fonte || '').toLowerCase().includes(termo)
      );
    }

    renderizarListasEditoriais(filtradas);
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

  // --- Utilitário: Mapeamento de Badge de Categoria ---
  function categoriaBadgeClass(categoria) {
    const mapa = {
      'Artes e Literatura':         'badge-artes',
      'Esportes e Aventura':        'badge-esportes',
      'Ciência e Tecnologia':       'badge-ciencia',
      'Cultura Pop e Gastronomia':  'badge-cultura',
      'Solidariedade e Comunidade': 'badge-solidariedade',
      'Histórias e Superação':      'badge-historias',
      'Carreira e Conquistas':      'badge-carreira',
    };
    return mapa[categoria] || 'badge-carreira';
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
