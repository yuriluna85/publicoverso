/**
 * app_concursos.js - Motor de renderizacao e filtragem do Radar de Concursos
 * Portal: Publicoverso (publicoverso.com.br)
 */

(function () {
  'use strict';

  let concursosMestre = [];
  let filtroEscolaridade = 'Todos';
  let filtroEsfera = 'Todas';

  // --- Carregamento de Dados ---
  async function inicializar() {
    try {
      const resp = await fetch('data/concursos_radar.json');
      if (!resp.ok) throw new Error('Falha ao carregar concursos_radar.json');
      concursosMestre = await resp.json();
      renderizarConcursos(concursosMestre);
      configurarFiltros();
      configurarBusca();
    } catch (erro) {
      console.error('[Publicoverso - Concursos] Erro:', erro);
      const grid = document.getElementById('gridConcursos');
      if (grid) {
        grid.innerHTML = '<p style="color: var(--text-muted); padding: 2rem;">Não foi possivel carregar o radar de concursos. Tente novamente em instantes.</p>';
      }
    }
  }

  // --- Renderizacao dos Cards de Concursos ---
  function renderizarConcursos(lista) {
    const grid = document.getElementById('gridConcursos');
    const semResultados = document.getElementById('semResultados');
    if (!grid) return;

    if (lista.length === 0) {
      grid.innerHTML = '';
      if (semResultados) semResultados.style.display = 'block';
      return;
    }

    if (semResultados) semResultados.style.display = 'none';

    grid.innerHTML = lista.map(concurso => {
      const classeDestaque = concurso.destaque ? ' featured' : '';
      const badgeStatus = badgeStatusClass(concurso.status);
      const vagasTexto = concurso.vagas > 0 ? `${concurso.vagas} vagas` : 'Consultar edital';

      return `
        <article class="card-news card-concurso${classeDestaque}" data-escolaridade="${escapar(concurso.escolaridade)}" data-esfera="${escapar(concurso.esfera)}">
          <header>
            <div class="concurso-badges">
              <span class="news-badge ${badgeStatus}" aria-label="Status: ${escapar(concurso.status)}">${escapar(concurso.status)}</span>
              <span class="concurso-esfera">${escapar(concurso.esfera)}</span>
            </div>
            <h3 class="news-title">${escapar(concurso.órgão)}</h3>
          </header>

          <div class="concurso-detalhes">
            <div class="concurso-detalhe">
              <span class="detalhe-label">Cargos</span>
              <span class="detalhe-valor">${escapar(concurso.cargos)}</span>
            </div>
            <div class="concurso-detalhe">
              <span class="detalhe-label">Vagas</span>
              <span class="detalhe-valor">${escapar(vagasTexto)}</span>
            </div>
            <div class="concurso-detalhe">
              <span class="detalhe-label">Escolaridade</span>
              <span class="detalhe-valor">${escapar(concurso.escolaridade)}</span>
            </div>
            <div class="concurso-detalhe">
              <span class="detalhe-label">Remuneracao maxima</span>
              <span class="detalhe-valor concurso-remuneracao">${escapar(concurso.remuneracao_max)}</span>
            </div>
            <div class="concurso-detalhe">
              <span class="detalhe-label">Inscrições</span>
              <span class="detalhe-valor">${escapar(concurso.periodo_inscricao)}</span>
            </div>
            <div class="concurso-detalhe">
              <span class="detalhe-label">Banca organizadora</span>
              <span class="detalhe-valor">${escapar(concurso.banca)}</span>
            </div>
          </div>

          <footer class="news-meta">
            <span>Atualizado: ${escapar(concurso.data_atualizacao)}</span>
            <a href="${escapar(concurso.link_edital)}" class="btn-curate" target="_blank" rel="noopener noreferrer" aria-label="Acessar edital oficial de ${escapar(concurso.órgão)}">
              Ver edital oficial
            </a>
          </footer>
        </article>
      `;
    }).join('');
  }

  // --- Classe do Badge de Status ---
  function badgeStatusClass(status) {
    const mapa = {
      'Inscrições Abertas': 'badge-inscrições-abertas',
      'Edital Publicado': 'badge-estadual',
      'Publicacoes Continuas': 'badge-federal',
      'Previsto 2026': 'badge-previsto',
      'Em Analise': 'badge-municipal',
    };
    return mapa[status] || 'badge-default';
  }

  // --- Filtros de Escolaridade e Esfera ---
  function configurarFiltros() {
    const chipsEscolaridade = document.querySelectorAll('[data-filtro-escolaridade]');
    const chipsEsfera = document.querySelectorAll('[data-filtro-esfera]');

    chipsEscolaridade.forEach(chip => {
      chip.addEventListener('click', () => {
        chipsEscolaridade.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        filtroEscolaridade = chip.dataset.filtroEscolaridade;
        aplicarFiltros();
      });
    });

    chipsEsfera.forEach(chip => {
      chip.addEventListener('click', () => {
        chipsEsfera.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        filtroEsfera = chip.dataset.filtroEsfera;
        aplicarFiltros();
      });
    });
  }

  // --- Busca Textual ---
  function configurarBusca() {
    const input = document.getElementById('searchConcurso');
    if (!input) return;
    input.addEventListener('input', aplicarFiltros);
  }

  function aplicarFiltros() {
    const input = document.getElementById('searchConcurso');
    const termo = input ? input.value.toLowerCase().trim() : '';

    let filtrados = [...concursosMestre];

    if (filtroEscolaridade !== 'Todos') {
      filtrados = filtrados.filter(c =>
        (c.escolaridade || '').includes(filtroEscolaridade)
      );
    }

    if (filtroEsfera !== 'Todas') {
      filtrados = filtrados.filter(c => c.esfera === filtroEsfera);
    }

    if (termo) {
      filtrados = filtrados.filter(c =>
        (c.órgão || '').toLowerCase().includes(termo) ||
        (c.cargos || '').toLowerCase().includes(termo) ||
        (c.banca || '').toLowerCase().includes(termo) ||
        (c.sigla || '').toLowerCase().includes(termo)
      );
    }

    renderizarConcursos(filtrados);
  }

  // --- Escape de HTML ---
  function escapar(str) {
    if (!str && str !== 0) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // --- Init ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }

})();
