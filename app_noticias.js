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
      const [resCuradoria, resAcervo] = await Promise.all([
        fetch('data/noticias_curadoria.json').catch(() => null),
        fetch('data/acervo_links_minerados.json').catch(() => null)
      ]);

      const curadas = (resCuradoria && resCuradoria.ok) ? await resCuradoria.json() : [];
      const mineradas = (resAcervo && resAcervo.ok) ? await resAcervo.json() : [];

      // Mescla deduplicando por URL
      const urlsVistas = new Set();
      const mescla = [];

      function ehPropagandaComercial(item) {
        if (!item) return true;
        const txt = ((item.titulo || '') + ' ' + (item.resumo || '') + ' ' + (item.fonte || '')).toLowerCase();
        const termos = [
          'sindicância contra você', 'sindicancia contra voce', 'pad contra você', 'pad contra voce',
          'defesa técnica agora', 'defesa tecnica agora', 'contrate um advogado', 'advocacia especializada',
          'escritório de advocacia', 'escritorio de advocacia', 'fale conosco pelo whatsapp',
          'fale com nosso advogado', 'consulte nossos advogados', 'agende uma consulta', 'precisa de defesa',
          'defenda seu cargo', 'fale com um especialista', 'nossos serviços jurídicos',
          'nossos servicos juridicos', 'nosso escritório', 'nosso escritorio',
          'prestamos assessoria jurídica', 'prestamos assessoria juridica',
          'entre em contato conosco', 'serviços advocatícios', 'servicos advocaticios',
          'defesa em pad', 'defesa de servidores públicos', 'defesa de servidor',
          'escritório especializado', 'escritorio especializado', 'garanta seus direitos',
          'responde a processo administrativo', 'responde a pad', 'defesa técnica do servidor',
          'proteger carreira', 'proteger sua carreira', 'defesa em sindicância', 'advogado de servidor',
          'advocacia para servidores', 'fale com um advogado', 'consultoria jurídica para servidores'
        ];
        return termos.some(t => txt.includes(t));
      }

      for (const n of curadas) {
        if (ehPropagandaComercial(n)) continue;
        const chave = n.url_materia || n.url_original || n.id;
        if (chave) urlsVistas.add(chave);
        if (n.status_curadoria !== 'Rejeitada' && n.status !== 'Rejeitada') {
          mescla.push(n);
        }
      }

      for (const m of mineradas) {
        if (ehPropagandaComercial(m)) continue;
        const chave = m.url_materia || m.url_original || m.id;
        if (chave && urlsVistas.has(chave)) continue;
        if (chave) urlsVistas.add(chave);
        if (m.status_curadoria !== 'Rejeitada' && m.status !== 'Rejeitada') {
          mescla.push(m);
        }
      }

      if (mescla.length === 0) throw new Error('Nenhuma notícia disponível no acervo.');

      noticiasMestre = mescla;

      // Ordena da mais recente para a mais antiga (DD/MM/AAAA)
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
      const urlDestino = noticia.url_materia || noticia.url_original || '#';
      const ehLinkExterno = !noticia.url_materia && noticia.url_original;
      const targetAttr = ehLinkExterno ? 'target="_blank" rel="noopener noreferrer"' : '';
      const statusBadge = noticia.status_curadoria === 'Aprovada' ? '<span style="font-size:0.75rem; color:var(--color-brand-turquoise); font-weight:600; margin-left:0.5rem;">[Curada]</span>' : '';

      return `
        <tr class="tr-noticia">
          <td class="td-data">${escapar(noticia.data)}</td>
          <td class="td-categoria">
            <span class="news-badge ${badgeClass}">${escapar(noticia.categoria)}</span>
          </td>
          <td class="td-conteudo">
            <h3 class="noticia-list-titulo">
              <a href="${escapar(urlDestino)}" ${targetAttr}>
                ${escapar(noticia.titulo)} ${statusBadge}
              </a>
            </h3>
            <p class="noticia-list-resumo">${escapar(noticia.resumo)}</p>
          </td>
          <td class="td-fonte">${escapar(noticia.fonte)}</td>
          <td class="td-acao" style="text-align: center;">
            <a href="${escapar(urlDestino)}" ${targetAttr} class="btn-curate btn-curate-sm" aria-label="Abrir notícia: ${escapar(noticia.titulo)}">
              ${ehLinkExterno ? 'Acessar Fonte' : 'Ler Matéria'}
            </a>
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
