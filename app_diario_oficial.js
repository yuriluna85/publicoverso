/**
 * Publicoverso - app_diario_oficial.js
 * Controlador do Monitor de Movimentações do Diário Oficial (DOU / DOE)
 * Suporte a busca em tempo real, partição de arquivos por Ano/Mês, KPIs e Tema Triplo
 */

(function () {
  'use strict';

  // --- Estado Global ---
  let atosMestre = [];
  let atosFiltrados = [];
  let tipoAtoAtivo = 'Todas';
  let paginaAtual = 1;
  let itensPorPagina = 10;
  let termoBusca = '';

  // --- Inicialização ---
  async function inicializar() {
    configurarTema();
    configurarEventos();

    try {
      // Carrega o índice de meses e os atos recentes
      const [resRecentes, resIndice] = await Promise.all([
        fetch('data/diario_oficial/movimentacoes_recentes.json').catch(() => null),
        fetch('data/diario_oficial/indice_meses_disponiveis.json').catch(() => null)
      ]);

      if (resRecentes && resRecentes.ok) {
        atosMestre = await resRecentes.json();
      }

      if (resIndice && resIndice.ok) {
        const indice = await resIndice.json();
        populareSeletorMeses(indice);
      }

      aplicarFiltrosEProcessar();
    } catch (e) {
      console.warn('Erro ao inicializar Diário Oficial:', e);
      exibirMensagemSemDados();
    }
  }

  // --- Configuração dos Eventos da Interface ---
  function configurarEventos() {
    // Chips de Filtro por Tipo de Ato
    const containerChips = document.getElementById('doChipsContainer');
    if (containerChips) {
      containerChips.addEventListener('click', function (e) {
        const btn = e.target.closest('.chip-btn');
        if (!btn) return;

        containerChips.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        tipoAtoAtivo = btn.getAttribute('data-tipo') || 'Todas';
        paginaAtual = 1;
        aplicarFiltrosEProcessar();
      });
    }

    // Busca Rápida com Debounce
    const inputBusca = document.getElementById('doSearchInput');
    if (inputBusca) {
      let timer = null;
      inputBusca.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          termoBusca = inputBusca.value.trim().toLowerCase();
          paginaAtual = 1;
          aplicarFiltrosEProcessar();
        }, 300);
      });
    }

    // Seletor de Linhas por Página
    const selectLinhas = document.getElementById('doSelectLinhas');
    if (selectLinhas) {
      selectLinhas.addEventListener('change', function () {
        itensPorPagina = parseInt(selectLinhas.value, 10) || 10;
        paginaAtual = 1;
        aplicarFiltrosEProcessar();
      });
    }

    // Seletor de Período Histórico (Mês/Ano)
    const selectMesAno = document.getElementById('doSelectMesAno');
    if (selectMesAno) {
      selectMesAno.addEventListener('change', async function () {
        const caminhoCsv = selectMesAno.value;
        if (caminhoCsv === 'recentes') {
          inicializar();
        } else {
          await carregarCsvHistorico(caminhoCsv);
        }
      });
    }

    // Botões de Paginação
    const btnAnt = document.getElementById('doBtnPagAnterior');
    const btnProx = document.getElementById('doBtnPagProxima');

    if (btnAnt) {
      btnAnt.addEventListener('click', function () {
        if (paginaAtual > 1) {
          paginaAtual--;
          renderizarTabelaEPaginacao();
        }
      });
    }

    if (btnProx) {
      btnProx.addEventListener('click', function () {
        const totalPaginas = Math.ceil(atosFiltrados.length / itensPorPagina) || 1;
        if (paginaAtual < totalPaginas) {
          paginaAtual++;
          renderizarTabelaEPaginacao();
        }
      });
    }

    // Botão de Download do CSV do Mês
    const btnDownload = document.getElementById('btnDownloadCSV');
    if (btnDownload) {
      btnDownload.addEventListener('click', function () {
        const selectMes = document.getElementById('doSelectMesAno');
        const caminhoCsv = (selectMes && selectMes.value !== 'recentes') ? selectMes.value : 'data/diario_oficial/2026/08/movimentacoes_2026_08.csv';
        window.open(caminhoCsv, '_blank');
      });
    }
  }

  // --- Carregamento de CSV Histórico ---
  async function carregarCsvHistorico(caminhoCsv) {
    try {
      const resp = await fetch(caminhoCsv);
      if (!resp.ok) throw new Error('Não foi possível carregar o CSV');
      const textoCsv = await resp.text();

      atosMestre = converterCsvParaObjetos(textoCsv);
      paginaAtual = 1;
      aplicarFiltrosEProcessar();
    } catch (err) {
      console.warn('Erro ao carregar CSV:', err);
      exibirMensagemSemDados();
    }
  }

  function converterCsvParaObjetos(csvTexto) {
    const linhas = csvTexto.split('\n').filter(l => l.strip ? l.strip() : l.trim());
    if (linhas.length <= 1) return [];

    const cabecalhos = linhas[0].split(',').map(c => c.replace(/"/g, '').trim());
    const resultado = [];

    for (let i = 1; i < linhas.length; i++) {
      const colunas = linhas[i].match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g) || linhas[i].split(',');
      if (!colunas || colunas.length < 3) continue;

      const item = {};
      cabecalhos.forEach((col, idx) => {
        let val = colunas[idx] || '';
        val = val.replace(/^"|"$/g, '').trim();
        item[col] = val;
      });
      resultado.push(item);
    }
    return resultado;
  }

  // --- Processamento de Filtros e KPIs ---
  function aplicarFiltrosEProcessar() {
    atosFiltrados = atosMestre.filter(item => {
      // Filtro por Tipo de Ato
      if (tipoAtoAtivo !== 'Todas') {
        const tipoItem = (item.tipo_ato || '').toLowerCase();
        const tipoAlvo = tipoAtoAtivo.toLowerCase();
        if (!tipoItem.includes(tipoAlvo.split(' ')[0])) {
          return false;
        }
      }

      // Filtro por Busca Textual (Nome, Órgão, Portaria, Resumo)
      if (termoBusca) {
        const textoTotal = `${item.servidor_nome} ${item.orgao} ${item.numero_portaria} ${item.resumo_portaria} ${item.tipo_ato}`.toLowerCase();
        if (!textoTotal.includes(termoBusca)) {
          return false;
        }
      }

      return true;
    });

    renderizarKPIs();
    renderizarTabelaEPaginacao();
  }

  // --- Renderização dos Bento KPI Cards ---
  function renderizarKPIs() {
    const total = atosMestre.length;
    let nomeacoes = 0;
    let convocacoes = 0;
    let exoneracoes = 0;
    let aposentadorias = 0;

    for (const a of atosMestre) {
      const tipo = (a.tipo_ato || '').toLowerCase();
      if (tipo.includes('admiss') || tipo.includes('nomea')) nomeacoes++;
      else if (tipo.includes('convoca')) convocacoes++;
      else if (tipo.includes('exoner') || tipo.includes('dispen')) exoneracoes++;
      else if (tipo.includes('aposent')) aposentadorias++;
    }

    const elTotal = document.getElementById('kpiTotalAtos');
    const elNom = document.getElementById('kpiNomeacoes');
    const elConv = document.getElementById('kpiConvocacoes');
    const elExo = document.getElementById('kpiExoneracoes');
    const elApo = document.getElementById('kpiAposentadorias');

    if (elTotal) elTotal.textContent = total;
    if (elNom) elNom.textContent = nomeacoes;
    if (elConv) elConv.textContent = convocacoes;
    if (elExo) elExo.textContent = exoneracoes;
    if (elApo) elApo.textContent = aposentadorias;
  }

  // --- Renderização da Tabela Responsiva e Paginação ---
  function renderizarTabelaEPaginacao() {
    const tbody = document.getElementById('doTbody');
    const elStats = document.getElementById('doStats');
    const elInfoPag = document.getElementById('doInfoPagina');
    const btnAnt = document.getElementById('doBtnPagAnterior');
    const btnProx = document.getElementById('doBtnPagProxima');

    if (!tbody) return;

    if (atosFiltrados.length === 0) {
      exibirMensagemSemDados();
      return;
    }

    const totalPaginas = Math.ceil(atosFiltrados.length / itensPorPagina) || 1;
    if (paginaAtual > totalPaginas) paginaAtual = totalPaginas;

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const paginaItens = atosFiltrados.slice(inicio, fim);

    if (elStats) {
      elStats.textContent = `Exibindo ${inicio + 1} - ${Math.min(fim, atosFiltrados.length)} de ${atosFiltrados.length} publicações oficiais encontradas.`;
    }

    if (elInfoPag) {
      elInfoPag.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
    }

    if (btnAnt) btnAnt.disabled = (paginaAtual === 1);
    if (btnProx) btnProx.disabled = (paginaAtual === totalPaginas);

    tbody.innerHTML = paginaItens.map(item => `
      <tr>
        <td>
          <strong style="color: var(--text-primary); font-size: 0.9rem;">${escapar(item.data_publicacao || '09/08/2026')}</strong>
          <span style="display: block; font-size: 0.75rem; color: var(--text-muted);">${escapar(item.secao_diario || 'Seção 2 - DOU')}</span>
        </td>
        <td>
          ${gerarBadgeTipoAto(item.tipo_ato)}
        </td>
        <td>
          <strong style="color: var(--text-primary); font-size: 0.95rem;">${escapar(item.servidor_nome || 'Servidor Público Nominado')}</strong>
          <span style="display: block; font-size: 0.8rem; color: #00D2C8; font-weight: 600;">${escapar(item.numero_portaria || item.cargo_funcao || 'Portaria Oficial')}</span>
        </td>
        <td>
          <span style="font-weight: 700; color: var(--text-primary); font-size: 0.88rem; display: block; margin-bottom: 0.2rem;">${escapar(item.orgao || 'Administração Pública')}</span>
          <p style="margin: 0; font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">${escapar(item.resumo_portaria || 'Publicação oficial do Diário Oficial.')}</p>
        </td>
        <td style="text-align: center;">
          <a href="${escapar(item.url_portaria || 'https://www.in.gov.br')}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background: rgba(0, 210, 200, 0.12); color: #00D2C8; border: 1px solid rgba(0, 210, 200, 0.3); font-size: 0.78rem; font-weight: 700; padding: 0.4rem 0.75rem; border-radius: 6px; text-decoration: none;">
            Abrir Portaria &rarr;
          </a>
        </td>
      </tr>
    `).join('');
  }

  function gerarBadgeTipoAto(tipo) {
    const t = (tipo || '').toLowerCase();
    let corBg = 'rgba(0, 210, 200, 0.12)';
    let corTexto = '#00D2C8';

    if (t.includes('admiss') || t.includes('nomea')) {
      corBg = 'rgba(16, 185, 129, 0.15)';
      corTexto = '#10B981';
    } else if (t.includes('convoca')) {
      corBg = 'rgba(145, 70, 255, 0.15)';
      corTexto = '#9146FF';
    } else if (t.includes('exoner') || t.includes('dispen')) {
      corBg = 'rgba(245, 158, 11, 0.15)';
      corTexto = '#F59E0B';
    } else if (t.includes('aposent')) {
      corBg = 'rgba(59, 130, 246, 0.15)';
      corTexto = '#3B82F6';
    } else if (t.includes('demiss') || t.includes('pad')) {
      corBg = 'rgba(239, 68, 68, 0.15)';
      corTexto = '#EF4444';
    }

    return `<span class="hat-badge" style="background: ${corBg}; color: ${corTexto}; border: 1px solid ${corTexto}44;">${escapar(tipo || 'Ato Oficial')}</span>`;
  }

  function populareSeletorMeses(indice) {
    const select = document.getElementById('doSelectMesAno');
    if (!select || !indice || indice.length === 0) return;

    select.innerHTML = '<option value="recentes">Últimos Atos (Recentes)</option>';
    for (const item of indice) {
      const opt = document.createElement('option');
      opt.value = item.caminho_csv;
      opt.textContent = `${item.label} (CSV Oficial)`;
      select.appendChild(opt);
    }
  }

  function exibirMensagemSemDados() {
    const tbody = document.getElementById('doTbody');
    const elStats = document.getElementById('doStats');

    if (elStats) elStats.textContent = 'Nenhuma publicação oficial encontrada para os filtros aplicados.';
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 3rem 1rem;">
            <h4 style="font-family: 'Outfit', sans-serif; color: var(--text-primary); margin: 0 0 0.5rem 0;">Nenhuma publicação oficial localizada</h4>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin: 0;">Tente selecionar outro período histórico ou limpar os termos de busca.</p>
          </td>
        </tr>
      `;
    }
  }

  function escapar(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --- Gerenciamento do Tema Triplo ---
  function configurarTema() {
    const temaSalvo = localStorage.getItem('publicoverso_theme') || 'dark';
    aplicarTema(temaSalvo);

    const bDark = document.getElementById('btnThemeDark');
    const bLight = document.getElementById('btnThemeLight');
    const bContrast = document.getElementById('btnThemeContrast');

    if (bDark) bDark.addEventListener('click', () => aplicarTema('dark'));
    if (bLight) bLight.addEventListener('click', () => aplicarTema('light'));
    if (bContrast) bContrast.addEventListener('click', () => aplicarTema('contrast'));
  }

  function aplicarTema(tema) {
    document.documentElement.setAttribute('data-theme', tema);
    localStorage.setItem('publicoverso_theme', tema);

    const btnDark = document.getElementById('btnThemeDark');
    const btnLight = document.getElementById('btnThemeLight');
    const btnContrast = document.getElementById('btnThemeContrast');

    if (btnDark) btnDark.setAttribute('aria-checked', tema === 'dark' ? 'true' : 'false');
    if (btnLight) btnLight.setAttribute('aria-checked', tema === 'light' ? 'true' : 'false');
    if (btnContrast) btnContrast.setAttribute('aria-checked', tema === 'contrast' ? 'true' : 'false');
  }

  // --- Disparo ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }
})();
