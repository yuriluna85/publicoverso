/**
 * Publicoverso - apps/radar-concursos/app.js
 * Controlador da Aplicação Radar de Concursos Públicos
 */

(function () {
  'use strict';

  let concursosMestre = [];

  async function inicializar() {
    configurarTema();

    try {
      const resp = await fetch('../../data/acervo_links_minerados.json');
      if (resp.ok) {
        const dados = await resp.json();
        concursosMestre = dados.filter(item => item.categoria_slug === 'carreira' || (item.editoria || '').toLowerCase().includes('concurso'));
      }
      renderizarConcursos(concursosMestre);

      const inputBusca = document.getElementById('inputBuscaConcurso');
      if (inputBusca) {
        inputBusca.addEventListener('input', function () {
          const termo = inputBusca.value.trim().toLowerCase();
          const filtrados = concursosMestre.filter(c => 
            `${c.titulo} ${c.resumo} ${c.veiculo}`.toLowerCase().includes(termo)
          );
          renderizarConcursos(filtrados);
        });
      }
    } catch (e) {
      console.warn('Erro ao carregar radar de concursos:', e);
    }
  }

  function renderizarConcursos(lista) {
    const grid = document.getElementById('gridConcursos');
    const stats = document.getElementById('statsConcursos');

    if (!grid) return;

    if (stats) {
      stats.textContent = `${lista.length} oportunidades e editais monitorados no momento.`;
    }

    if (lista.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center; padding: 2rem;">Nenhum edital encontrado para os termos pesquisados.</p>';
      return;
    }

    grid.innerHTML = lista.map(c => `
      <article style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <span class="hat-badge" style="background: rgba(0, 210, 200, 0.12); color: #00D2C8; border: 1px solid rgba(0, 210, 200, 0.3); font-size: 0.75rem; margin-bottom: 0.5rem; display: inline-block;">
            ${escapar(c.veiculo || 'Edital Oficial')}
          </span>
          <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; color: var(--text-primary); margin: 0.4rem 0 0.6rem 0; line-height: 1.3;">
            ${escapar(c.titulo)}
          </h3>
          <p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.4; margin: 0 0 1rem 0;">
            ${escapar(c.resumo)}
          </p>
        </div>
        <a href="${escapar(c.url)}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background: rgba(0, 210, 200, 0.12); color: #00D2C8; border: 1px solid rgba(0, 210, 200, 0.3); font-size: 0.85rem; font-weight: 700; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; text-align: center;">
          Acessar Edital / Notícia &rarr;
        </a>
      </article>
    `).join('');
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

  function configurarTema() {
    const temaSalvo = localStorage.getItem('publicoverso_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', temaSalvo);

    const bToggle = document.getElementById('btnThemeToggle');
    const bHighContrast = document.getElementById('btnHighContrast');

    if (bToggle) {
      bToggle.addEventListener('click', () => {
        const atual = document.documentElement.getAttribute('data-theme') || 'dark';
        const novo = atual === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', novo);
        localStorage.setItem('publicoverso_theme', novo);
      });
    }

    if (bHighContrast) {
      bHighContrast.addEventListener('click', () => {
        const atual = document.documentElement.getAttribute('data-theme') || 'dark';
        const novo = atual === 'contrast' ? 'dark' : 'contrast';
        document.documentElement.setAttribute('data-theme', novo);
        localStorage.setItem('publicoverso_theme', novo);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }
})();
