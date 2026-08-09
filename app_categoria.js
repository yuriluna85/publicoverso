/**
 * Publicoverso - app_categoria.js
 * Gerenciador de renderização para Landing Pages Dedicadas por Categoria/Editoria.
 * Filtra acervo mestre de notícias, trata paginação, busca interna e acessibilidade.
 */

(function () {
  'use strict';

  let noticiasCategoria = [];
  let categoriaAtual = '';
  let paginaAtual = 1;
  let itensPorPagina = 10;

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

  async function inicializarLandingCategoria() {
    // Identifica qual categoria esta página representa através do atributo data-categoria no main
    const mainEl = document.querySelector('main[data-categoria]');
    if (!mainEl) return;

    categoriaAtual = mainEl.getAttribute('data-categoria') || '';

    try {
      const [resNoticias, resAcervo] = await Promise.all([
        fetch('data/noticias_curadoria.json'),
        fetch('data/acervo_links_minerados.json').catch(() => null)
      ]);

      let curadas = resNoticias.ok ? await resNoticias.json() : [];
      let mineradas = (resAcervo && resAcervo.ok) ? await resAcervo.json() : [];

      const urlsVistas = new Set();
      const todas = [];

      for (const n of curadas) {
        if (!ehVeiculoNoticiosoValido(n)) continue;
        const chave = n.url_materia || n.url_original || n.id;
        urlsVistas.add(chave);
        todas.push(n);
      }

      for (const m of mineradas) {
        if (!ehVeiculoNoticiosoValido(m)) continue;
        const chave = m.url_materia || m.url_original || m.id;
        if (!urlsVistas.has(chave)) {
          urlsVistas.add(chave);
          todas.push(m);
        }
      }

      // Filtra estritamente pela categoria da página
      noticiasCategoria = todas.filter(item => item.categoria === categoriaAtual);

      configurarControles();
      renderizarDestaquesCategoria();
      renderizarListaCategoria();
      configurarAcessibilidade();
    } catch (erro) {
      console.error('[Publicoverso] Erro ao carregar categoria:', erro);
    }
  }

  function renderizarDestaquesCategoria() {
    const heroCard = document.getElementById('catHeroMain');
    const sideList = document.getElementById('catHeroSide');

    if (!noticiasCategoria || noticiasCategoria.length === 0) {
      if (heroCard) {
        heroCard.innerHTML = `<p style="color: var(--text-muted); padding: 1.5rem;">Nenhuma matéria em destaque cadastrada para esta categoria no momento.</p>`;
      }
      return;
    }

    // Item Principal
    const principal = noticiasCategoria[0];
    if (heroCard && principal) {
      const urlDestino = principal.url_materia || principal.url_original || '#';
      const targetAttr = !principal.url_materia && principal.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';

      heroCard.innerHTML = `
        <span class="hat-badge badge-carreira">${escapar(principal.categoria)}</span>
        <h2 class="main-title" style="font-size: 1.8rem; margin: 0.75rem 0;">
          <a href="${escapar(urlDestino)}" ${targetAttr} style="color: var(--text-primary); text-decoration: none;">${escapar(principal.titulo)}</a>
        </h2>
        <p class="line-fine" style="color: var(--text-muted); font-size: 1rem; line-height: 1.5;">${escapar(principal.resumo)}</p>
        <footer class="hero-meta-footer" style="margin-top: 1rem;">
          <span style="font-size: 0.85rem; color: var(--text-muted);">${escapar(principal.fonte)} &bull; ${escapar(principal.data)}</span>
          <a href="${escapar(urlDestino)}" class="btn-curate" ${targetAttr}>
            ${principal.url_materia ? 'Ler matéria completa &rarr;' : 'Ver no veículo original &rarr;'}
          </a>
        </footer>
      `;
    }

    // Itens Secundários (Próximos 3)
    if (sideList) {
      const secundarias = noticiasCategoria.slice(1, 4);
      if (secundarias.length === 0) {
        sideList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">Mais histórias desta editoria em breve.</p>`;
        return;
      }

      sideList.innerHTML = secundarias.map(sec => {
        const urlDestino = sec.url_materia || sec.url_original || '#';
        const targetAttr = !sec.url_materia && sec.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';
        return `
          <article style="border-bottom: 1px dashed var(--border-color); padding-bottom: 0.75rem;">
            <h3 style="font-family: 'Inter', sans-serif; font-size: 1rem; font-weight: 600; margin: 0 0 0.25rem 0;">
              <a href="${escapar(urlDestino)}" ${targetAttr} style="color: var(--text-primary); text-decoration: none;">${escapar(sec.titulo)}</a>
            </h3>
            <span style="font-size: 0.78rem; color: var(--text-muted);">${escapar(sec.fonte)} &bull; ${escapar(sec.data)}</span>
          </article>
        `;
      }).join('');
    }
  }

  function renderizarListaCategoria() {
    const tbody = document.getElementById('catTbody');
    const statsEl = document.getElementById('catStats');
    const inputBusca = document.getElementById('catSearchInput');

    if (!tbody) return;

    let listaFiltrada = [...noticiasCategoria];
    const termo = inputBusca ? inputBusca.value.toLowerCase().trim() : '';

    if (termo) {
      listaFiltrada = listaFiltrada.filter(item =>
        (item.titulo || '').toLowerCase().includes(termo) ||
        (item.resumo || '').toLowerCase().includes(termo) ||
        (item.fonte || '').toLowerCase().includes(termo)
      );
    }

    const total = listaFiltrada.length;
    if (statsEl) {
      statsEl.textContent = `Exibindo ${total} ${total === 1 ? 'matéria encontrada' : 'matérias encontradas'} na categoria "${categoriaAtual}".`;
    }

    if (total === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-muted);">
            Nenhuma matéria encontrada para a busca realizada.
          </td>
        </tr>
      `;
      atualizarPaginacao(0);
      return;
    }

    const totalPaginas = Math.ceil(total / itensPorPagina);
    if (paginaAtual > totalPaginas) paginaAtual = totalPaginas;

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const paginados = listaFiltrada.slice(inicio, inicio + itensPorPagina);

    tbody.innerHTML = paginados.map(item => {
      const urlDestino = item.url_materia || item.url_original || '#';
      const targetAttr = !item.url_materia && item.url_original ? 'target="_blank" rel="noopener noreferrer"' : '';
      return `
        <tr>
          <td style="font-size: 0.85rem; color: var(--text-muted); white-space: nowrap;">${escapar(item.data)}</td>
          <td>
            <strong style="display: block; font-size: 1rem; color: var(--text-primary); font-family: 'Inter', sans-serif;">
              <a href="${escapar(urlDestino)}" ${targetAttr} style="color: inherit; text-decoration: none;">${escapar(item.titulo)}</a>
            </strong>
            <p style="margin: 0.25rem 0 0 0; font-size: 0.88rem; color: var(--text-muted); line-height: 1.4;">${escapar(item.resumo)}</p>
          </td>
          <td style="font-size: 0.85rem; color: var(--text-muted);">${escapar(item.fonte)}</td>
          <td style="text-align: center;">
            <a href="${escapar(urlDestino)}" ${targetAttr} class="btn-curate btn-curate-sm" style="display: inline-block;">
              ${item.url_materia ? 'Ler' : 'Acessar'}
            </a>
          </td>
        </tr>
      `;
    }).join('');

    atualizarPaginacao(totalPaginas);
  }

  function atualizarPaginacao(totalPaginas) {
    const infoPagina = document.getElementById('catInfoPagina');
    const btnAnterior = document.getElementById('catBtnPagAnterior');
    const btnProxima = document.getElementById('catBtnPagProxima');

    if (infoPagina) {
      infoPagina.textContent = `Página ${paginaAtual} de ${totalPaginas || 1}`;
    }

    if (btnAnterior) {
      btnAnterior.disabled = (paginaAtual <= 1);
    }

    if (btnProxima) {
      btnProxima.disabled = (paginaAtual >= totalPaginas || totalPaginas === 0);
    }
  }

  function configurarControles() {
    const inputBusca = document.getElementById('catSearchInput');
    const selectLinhas = document.getElementById('catSelectLinhas');
    const btnAnterior = document.getElementById('catBtnPagAnterior');
    const btnProxima = document.getElementById('catBtnPagProxima');

    if (inputBusca) {
      inputBusca.addEventListener('input', () => {
        paginaAtual = 1;
        renderizarListaCategoria();
      });
    }

    if (selectLinhas) {
      selectLinhas.addEventListener('change', (e) => {
        itensPorPagina = parseInt(e.target.value, 10) || 10;
        paginaAtual = 1;
        renderizarListaCategoria();
      });
    }

    if (btnAnterior) {
      btnAnterior.addEventListener('click', () => {
        if (paginaAtual > 1) {
          paginaAtual--;
          renderizarListaCategoria();
        }
      });
    }

    if (btnProxima) {
      btnProxima.addEventListener('click', () => {
        paginaAtual++;
        renderizarListaCategoria();
      });
    }
  }

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
        if (btnTemaToggle) btnTemaToggle.textContent = 'Tema: Claro';
        if (btnContraste) btnContraste.classList.remove('active');
      }
      localStorage.setItem('publicoverso-tema-v3', tema);
    }

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

  function escapar(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarLandingCategoria);
  } else {
    inicializarLandingCategoria();
  }
})();
