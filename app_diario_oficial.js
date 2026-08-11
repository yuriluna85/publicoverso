/**
 * app_diario_oficial.js - Motor de busca, filtragem e renderização do Monitor do Diário Oficial
 * Portal: Publicoverso (publicoverso.com.br)
 * Desenvolvido por YLuna85 LABs
 */

document.addEventListener('DOMContentLoaded', () => {
  let todosAtos = [];
  let atosFiltrados = [];
  let tipoFiltroAtual = 'Todos';
  let termoBuscaAtual = '';

  // Elementos do DOM
  const listContainer = document.getElementById('douListContainer');
  const searchInput = document.getElementById('searchInputDOU');
  const kpiNomeacoes = document.getElementById('kpiNomeacoesCount');
  const kpiExoneracoes = document.getElementById('kpiExoneracoesCount');
  const kpiAposentadorias = document.getElementById('kpiAposentadoriasCount');
  const chipsFiltro = document.querySelectorAll('.category-chips .chip');

  // Inicialização de Acessibilidade
  initAccessibility();

  // Carregamento dos dados
  carregarDadosDOU();

  async function carregarDadosDOU() {
    try {
      const resp = await fetch('data/acervo_links_minerados.json');
      if (!resp.ok) {
        throw new Error(`Erro ao carregar dados: ${resp.status}`);
      }
      const dados = await resp.json();

      // Filtra registros que pertencem ao Diário Oficial
      todosAtos = dados.filter(item => {
        const fonte = (item.fonte || '').toLowerCase();
        const url = (item.url_original || '').toLowerCase();
        const id = (item.id || '').toLowerCase();
        return fonte.includes('diário oficial') || fonte.includes('dou') || url.includes('in.gov.br') || id.startsWith('dou-');
      });

      atualizarKPIs(todosAtos);
      aplicarFiltros();
    } catch (erro) {
      console.error('Falha no carregamento do Diário Oficial:', erro);
      if (listContainer) {
        listContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 2rem;">Não foi possível carregar os atos oficiais no momento. Tente novamente mais tarde.</p>';
      }
    }
  }

  function atualizarKPIs(lista) {
    let countNomeacoes = 0;
    let countExoneracoes = 0;
    let countAposentadorias = 0;

    lista.forEach(item => {
      const txt = `${item.titulo} ${item.resumo} ${item.categoria}`.toLowerCase();
      if (txt.includes('aposentadoria') || txt.includes('aposentar')) {
        countAposentadorias++;
      } else if (txt.includes('nomear') || txt.includes('nomeação') || txt.includes('posse')) {
        countNomeacoes++;
      } else if (txt.includes('exonerar') || txt.includes('exoneração') || txt.includes('vacância') || txt.includes('dispensar')) {
        countExoneracoes++;
      }
    });

    if (kpiNomeacoes) kpiNomeacoes.textContent = countNomeacoes;
    if (kpiExoneracoes) kpiExoneracoes.textContent = countExoneracoes;
    if (kpiAposentadorias) kpiAposentadorias.textContent = countAposentadorias;
  }

  function classificarTipoAto(item) {
    const txt = `${item.titulo} ${item.resumo} ${item.categoria}`.toLowerCase();
    if (txt.includes('aposentadoria') || txt.includes('aposentar')) return 'Aposentadoria';
    if (txt.includes('demissão') || txt.includes('demitir') || txt.includes('pad')) return 'Demissao';
    if (txt.includes('nomear') || txt.includes('nomeação') || txt.includes('posse')) return 'Nomeacao';
    if (txt.includes('exonerar') || txt.includes('exoneração') || txt.includes('vacância') || txt.includes('dispensar')) return 'Exoneracao';
    return 'Outros';
  }

  function aplicarFiltros() {
    atosFiltrados = todosAtos.filter(item => {
      const tipoAto = classificarTipoAto(item);
      const matchTipo = (tipoFiltroAtual === 'Todos') || (tipoAto === tipoFiltroAtual);

      const termo = termoBuscaAtual.toLowerCase();
      const matchBusca = !termo ||
        (item.titulo || '').toLowerCase().includes(termo) ||
        (item.resumo || '').toLowerCase().includes(termo) ||
        (item.fonte || '').toLowerCase().includes(termo);

      return matchTipo && matchBusca;
    });

    renderizarLista();
  }

  function renderizarLista() {
    if (!listContainer) return;

    if (atosFiltrados.length === 0) {
      listContainer.innerHTML = '<div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 2rem; text-align: center; color: var(--text-muted);"><p>Nenhuma portaria ou ato oficial foi encontrado para os filtros selecionados.</p></div>';
      return;
    }

    listContainer.innerHTML = atosFiltrados.map(item => {
      const tipoAto = classificarTipoAto(item);
      let badgeClass = 'badge-carreira';
      let badgeLabel = 'Ato Oficial';

      if (tipoAto === 'Aposentadoria') {
        badgeClass = 'badge-historias';
        badgeLabel = 'Aposentadoria Concedida';
      } else if (tipoAto === 'Nomeacao') {
        badgeClass = 'badge-carreira';
        badgeLabel = 'Nomeação / Posse';
      } else if (tipoAto === 'Exoneracao') {
        badgeClass = 'badge-cultura';
        badgeLabel = 'Exoneração / Vacância';
      } else if (tipoAto === 'Demissao') {
        badgeClass = 'badge-policial';
        badgeLabel = 'Demissão / Processo Disciplinar';
      }

      return `
        <article class="dou-item-card" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; transition: transform 0.2s ease, border-color 0.2s ease;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
            <span class="category-badge ${badgeClass}">${badgeLabel}</span>
            <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">${item.data || 'Data Recente'} • ${item.fonte || 'Diário Oficial da União'}</span>
          </div>
          <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin: 0; line-height: 1.4;">
            ${item.titulo}
          </h3>
          <p style="color: var(--text-primary); opacity: 0.9; font-size: 0.95rem; line-height: 1.5; margin: 0;">
            ${item.resumo}
          </p>
          <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem;">
            <a href="${item.url_original}" target="_blank" rel="noopener noreferrer" class="btn-feed-ver-todas" style="font-size: 0.85rem; padding: 0.4rem 0.9rem; text-decoration: none; border-radius: 6px; display: inline-flex; align-items: center; gap: 0.4rem;">
              Abrir Portaria Oficial no in.gov.br &rarr;
            </a>
          </div>
        </article>
      `;
    }).join('');
  }

  // Eventos de Busca
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      termoBuscaAtual = e.target.value;
      aplicarFiltros();
    });
  }

  // Eventos dos Chips de Filtro
  chipsFiltro.forEach(chip => {
    chip.addEventListener('click', () => {
      chipsFiltro.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      tipoFiltroAtual = chip.getAttribute('data-tipo') || 'Todos';
      aplicarFiltros();
    });
  });

  // Funções de Acessibilidade
  function initAccessibility() {
    const btnFontIncrease = document.getElementById('btnFontIncrease');
    const btnFontDecrease = document.getElementById('btnFontDecrease');
    const btnThemeToggle = document.getElementById('btnThemeToggle');
    const btnHighContrast = document.getElementById('btnHighContrast');

    let currentFontSize = parseInt(localStorage.getItem('pv_font_size') || '16', 10);
    document.documentElement.style.fontSize = `${currentFontSize}px`;

    if (btnFontIncrease) {
      btnFontIncrease.addEventListener('click', () => {
        if (currentFontSize < 22) {
          currentFontSize += 1;
          document.documentElement.style.fontSize = `${currentFontSize}px`;
          localStorage.setItem('pv_font_size', currentFontSize);
        }
      });
    }

    if (btnFontDecrease) {
      btnFontDecrease.addEventListener('click', () => {
        if (currentFontSize > 13) {
          currentFontSize -= 1;
          document.documentElement.style.fontSize = `${currentFontSize}px`;
          localStorage.setItem('pv_font_size', currentFontSize);
        }
      });
    }

    const savedTheme = localStorage.getItem('pv_theme') || 'light';
    if (savedTheme === 'dark') {
      document.body.classList.add('theme-dark');
      if (btnThemeToggle) btnThemeToggle.textContent = 'Tema: Escuro';
    } else if (savedTheme === 'high-contrast') {
      document.body.classList.add('theme-high-contrast');
      if (btnHighContrast) btnHighContrast.classList.add('active');
    }

    if (btnThemeToggle) {
      btnThemeToggle.addEventListener('click', () => {
        document.body.classList.remove('theme-high-contrast');
        document.body.classList.toggle('theme-dark');
        const isDark = document.body.classList.contains('theme-dark');
        btnThemeToggle.textContent = isDark ? 'Tema: Escuro' : 'Tema: Claro';
        localStorage.setItem('pv_theme', isDark ? 'dark' : 'light');
      });
    }

    if (btnHighContrast) {
      btnHighContrast.addEventListener('click', () => {
        document.body.classList.remove('theme-dark');
        document.body.classList.toggle('theme-high-contrast');
        const isHC = document.body.classList.contains('theme-high-contrast');
        localStorage.setItem('pv_theme', isHC ? 'high-contrast' : 'light');
        if (btnThemeToggle) btnThemeToggle.textContent = 'Tema: Claro';
      });
    }
  }
});
