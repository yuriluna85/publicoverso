/**
 * Publicoverso - app_noticias.js
 * Gerenciador do Índice Geral de Notícias (Lista Cronológica, Filtros, Busca e Paginação)
 * Suporte total ao Sistema Triplo de Temas (Claro, Escuro e Alto Contraste AAA)
 */

(function () {
  'use strict';

  // --- Estado Global ---
  let noticiasMestre = [];
  let noticiasFiltradas = [];
  let paginaAtual = 1;
  let itensPorPagina = 10;
  let editoriaAtiva = 'Todas';
  let termoBusca = '';

  // --- Inicialização ---
  async function inicializar() {
    try {
      const res = await fetch('data/noticias_curadoria.json');
      if (!res.ok) throw new Error('Falha ao carregar noticias_curadoria.json.');

      const dados = await res.json();
      noticiasMestre = dados.filter(n => n.status === 'Aprovada');

      // Ordena da notícia mais recente para a mais antiga (DD/MM/AAAA)
      noticiasMestre.sort((a, b) => converterData(b.data) - converterData(a.data));

      configurarEventos();
      configurarAcessibilidade();
      aplicarFiltrosEPaginacao();
    } catch (erro) {
      console.error('[Publicoverso] Erro ao carregar acervo de notícias:', erro);
      const tbody = document.getElementById('noticiasTbody');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">Erro ao carregar acervo de notícias.</td></tr>';
      }
    }
  }

  // --- Converte DD/MM/AAAA para Timestamp ---
  function converterData(stringData) {
    if (!stringData) return 0;
    const partes = stringData.split('/');
    if (partes.length === 3) {
      return new Date(partes[2], partes[1] - 1, partes[0]).getTime();
    }
    return 0;
  }

  // --- Configuração de Eventos UI ---
  function configurarEventos() {
    const selectCategoria = document.getElementById('selectCategoria');
    const selectLinhas = document.getElementById('selectLinhas');
    const inputBusca = document.getElementById('inputBuscaNoticias');
    const btnAnterior = document.getElementById('btnPagAnterior');
    const btnProxima = document.getElementById('btnPagProxima');

    if (selectCategoria) {
      selectCategoria.addEventListener('change', (e) => {
        editoriaAtiva = e.target.value;
        paginaAtual = 1;
        aplicarFiltrosEPaginacao();
      });
    }

    if (selectLinhas) {
      selectLinhas.addEventListener('change', (e) => {
        itensPorPagina = parseInt(e.target.value, 10) || 10;
        paginaAtual = 1;
        aplicarFiltrosEPaginacao();
      });
    }

    if (inputBusca) {
      inputBusca.addEventListener('input', (e) => {
        termoBusca = e.target.value.toLowerCase().trim();
        paginaAtual = 1;
        aplicarFiltrosEPaginacao();
      });
    }

    if (btnAnterior) {
      btnAnterior.addEventListener('click', () => {
        if (paginaAtual > 1) {
          paginaAtual--;
          aplicarFiltrosEPaginacao();
          rolarParaTopoLista();
        }
      });
    }

    if (btnProxima) {
      btnProxima.addEventListener('click', () => {
        const totalPaginas = Math.ceil(noticiasFiltradas.length / itensPorPagina) || 1;
        if (paginaAtual < totalPaginas) {
          paginaAtual++;
          aplicarFiltrosEPaginacao();
          rolarParaTopoLista();
        }
      });
    }
  }

  // --- Aplicação de Filtros e Renderização com Paginação ---
  function aplicarFiltrosEPaginacao() {
    let resultado = [...noticiasMestre];

    // Filtro por Editoria
    if (editoriaAtiva !== 'Todas') {
      resultado = resultado.filter(n => n.categoria === editoriaAtiva);
    }

    // Filtro por Busca Textual
    if (termoBusca) {
      resultado = resultado.filter(n =>
        (n.titulo || '').toLowerCase().includes(termoBusca) ||
        (n.resumo || '').toLowerCase().includes(termoBusca) ||
        (n.fonte || '').toLowerCase().includes(termoBusca) ||
        (n.categoria || '').toLowerCase().includes(termoBusca)
      );
    }

    noticiasFiltradas = resultado;

    const totalItens = noticiasFiltradas.length;
    const totalPaginas = Math.ceil(totalItens / itensPorPagina) || 1;
    if (paginaAtual > totalPaginas) paginaAtual = totalPaginas;

    const inicioIndex = (paginaAtual - 1) * itensPorPagina;
    const fimIndex = inicioIndex + itensPorPagina;
    const paginaItens = noticiasFiltradas.slice(inicioIndex, fimIndex);

    renderizarTabela(paginaItens);
    renderizarEstatisticas(totalItens, inicioIndex, Math.min(fimIndex, totalItens));
    renderizarControlesPaginação(totalPaginas);
  }

  // --- Renderização da Tabela de Notícias ---
  function renderizarTabela(itens) {
    const tbody = document.getElementById('noticiasTbody');
    if (!tbody) return;

    if (itens.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="sem-resultados">
            Nenhuma notícia encontrada com os filtros selecionados.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = itens.map(noticia => {
      const badgeClass = categoriaBadgeClass(noticia.categoria);
      const urlMateria = noticia.url_materia || '#';
      const temLink = noticia.url_materia ? true : false;

      return `
        <tr class="tr-noticia">
          <td class="td-data">${escapar(noticia.data)}</td>
          <td class="td-categoria">
            <span class="news-badge ${badgeClass}">${escapar(noticia.categoria)}</span>
          </td>
          <td class="td-conteudo">
            <h3 class="noticia-list-titulo">
              ${temLink ? `<a href="${escapar(urlMateria)}">${escapar(noticia.titulo)}</a>` : escapar(noticia.titulo)}
            </h3>
            <p class="noticia-list-resumo">${escapar(noticia.resumo)}</p>
          </td>
          <td class="td-fonte">${escapar(noticia.fonte)}</td>
          <td class="td-acao" style="text-align: center;">
            ${temLink ? `<a href="${escapar(urlMateria)}" class="btn-curate btn-curate-sm" aria-label="Ler notícia completa: ${escapar(noticia.titulo)}">Ler</a>` : '<span class="text-muted" style="font-size:0.78rem;">Em breve</span>'}
          </td>
        </tr>
      `;
    }).join('');
  }

  // --- Renderiza Estatísticas e Resumo de Itens ---
  function renderizarEstatisticas(total, inicio, fim) {
    const stats = document.getElementById('noticiasStats');
    if (!stats) return;

    if (total === 0) {
      stats.textContent = 'Nenhum resultado encontrado.';
    } else {
      stats.textContent = `Exibindo ${inicio + 1} a ${fim} de ${total} notícias cadastradas no acervo.`;
    }
  }

  // --- Controles de Paginação ---
  function renderizarControlesPaginação(totalPaginas) {
    const info = document.getElementById('infoPagina');
    const btnAnterior = document.getElementById('btnPagAnterior');
    const btnProxima = document.getElementById('btnPagProxima');

    if (info) {
      info.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
    }

    if (btnAnterior) {
      btnAnterior.disabled = (paginaAtual <= 1);
    }

    if (btnProxima) {
      btnProxima.disabled = (paginaAtual >= totalPaginas);
    }
  }

  function rolarParaTopoLista() {
    const topo = document.getElementById('noticias-titulo');
    if (topo) topo.scrollIntoView({ behavior: 'smooth' });
  }

  // --- Mapeamento de Categoria para Classe de Badge ---
  function categoriaBadgeClass(categoria) {
    const mapa = {
      'Artes e Literatura': 'badge-artes',
      'Esportes e Aventura': 'badge-esportes',
      'Ciência e Tecnologia': 'badge-ciencia',
      'Cultura Pop e Gastronomia': 'badge-culturapop',
      'Solidariedade e Comunidade': 'badge-solidariedade',
      'Histórias e Superação': 'badge-histórias',
      'Carreira e Conquistas': 'badge-carreira',
    };
    return mapa[categoria] || 'badge-default';
  }

  // --- Acessibilidade e Sistema Triplo de Temas ---
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

  // --- Inicialização Automática ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }

})();
