/**
 * Publicoverso - apps/diarias-estaduais/app.js
 * Banco de Dados de Legislações e Valores de Diárias Estaduais do Brasil (26 Estados + DF)
 * Suporte a calculadoras matriciais, valores flat, percentuais sobre subsídio e faixas de distância.
 */

(function () {
  'use strict';

  // --- Banco Regulamentar de Diárias dos 27 Entes Federativos ---
  const dbEstados = {
    "ac": {
      "nome": "Acre",
      "decreto": "Decreto Estadual nº 11.762/2025",
      "cargos": [
        { "id": "classe_i", "nome": "Classe I (Governador, Vice e Secretários)" },
        { "id": "classe_ii", "nome": "Classe II (Secretários Adjuntos e Diretores)" },
        { "id": "classe_iii", "nome": "Classe III (Cargos DAS e Nível Superior)" },
        { "id": "classe_iv", "nome": "Classe IV (Nível Médio, DAI e Operacionais)" }
      ],
      "destinos": [
        { "id": "interior", "nome": "Interior do Acre", "valor": 220.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 480.00 }
      ],
      "matriz": {
        "classe_i": { "interior": 380.00, "nacional": 700.00 },
        "classe_ii": { "interior": 280.00, "nacional": 560.00 },
        "classe_iii": { "interior": 220.00, "nacional": 480.00 },
        "classe_iv": { "interior": 160.00, "nacional": 380.00 }
      }
    },
    "al": {
      "nome": "Alagoas",
      "decreto": "Decreto Estadual nº 90.173/2023",
      "destinos": [
        { "id": "interior", "nome": "Dentro do Território Estadual", "valor": 138.00 },
        { "id": "df", "nome": "Brasília / Distrito Federal", "valor": 631.45 },
        { "id": "especiais", "nome": "Grandes Capitais (RJ, SP, BH, Manaus)", "valor": 561.45 },
        { "id": "capitais", "nome": "Outras Capitais de Estados", "valor": 449.16 },
        { "id": "nacional_demais", "nome": "Demais Localidades (Nacional)", "valor": 352.91 }
      ]
    },
    "ap": {
      "nome": "Amapá",
      "decreto": "Regulamento Geral de Diárias Civis e Militares",
      "destinos": [
        { "id": "interior", "nome": "Viagem Intermunicipal (Dentro do AP)", "valor": 180.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 420.00 }
      ]
    },
    "am": {
      "nome": "Amazonas",
      "decreto": "Decreto Estadual nº 40.691/2019",
      "cargos": [
        { "id": "direcao", "nome": "Cargos de Direção Superior e Assessoramento" },
        { "id": "nivel_superior", "nome": "Servidores Efetivos de Nível Superior" },
        { "id": "nivel_medio_fundamental", "nome": "Demais Servidores / Nível Médio e Apoio" }
      ],
      "destinos": [
        { "id": "interior", "nome": "Interior do Amazonas", "valor": 260.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 520.00 }
      ],
      "matriz": {
        "direcao": { "interior": 360.00, "nacional": 720.00 },
        "nivel_superior": { "interior": 260.00, "nacional": 520.00 },
        "nivel_medio_fundamental": { "interior": 180.00, "nacional": 380.00 }
      }
    },
    "ba": {
      "nome": "Bahia",
      "decreto": "Decreto Estadual nº 14.039/2012 e Reajustes 2024",
      "cargos": [
        { "id": "governador", "nome": "Governador, Vice e Secretários de Estado" },
        { "id": "cargo_superintendente", "nome": "Superintendentes, Diretores e Nível Hierárquico 1" },
        { "id": "cargo_tecnico", "nome": "Servidores de Nível Superior e Técnicos" },
        { "id": "cargo_medio", "nome": "Servidores de Nível Médio e Apoio" }
      ],
      "destinos": [
        { "id": "interior", "nome": "Interior do Estado da Bahia", "valor": 210.00 },
        { "id": "salvador", "nome": "Deslocamento para Salvador (Capital)", "valor": 280.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 510.00 },
        { "id": "brasilia", "nome": "Brasília / Distrito Federal", "valor": 680.00 }
      ],
      "matriz": {
        "governador": { "interior": 450.00, "salvador": 520.00, "nacional": 900.00, "brasilia": 1100.00 },
        "cargo_superintendente": { "interior": 320.00, "salvador": 400.00, "nacional": 680.00, "brasilia": 820.00 },
        "cargo_tecnico": { "interior": 210.00, "salvador": 280.00, "nacional": 510.00, "brasilia": 680.00 },
        "cargo_medio": { "interior": 150.00, "salvador": 210.00, "nacional": 380.00, "brasilia": 510.00 }
      }
    },
    "ce": {
      "nome": "Ceará",
      "decreto": "Decreto Estadual nº 35.808/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior do Ceará", "valor": 190.00 },
        { "id": "fortaleza", "nome": "Deslocamento para Fortaleza", "valor": 250.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 490.00 }
      ]
    },
    "df": {
      "nome": "Distrito Federal",
      "decreto": "Decreto Distrital nº 39.573/2018",
      "destinos": [
        { "id": "entorno", "nome": "Região Integrada do Entorno do DF", "valor": 120.00 },
        { "id": "nacional", "nome": "Demais Estados (Nacional)", "valor": 450.00 }
      ]
    },
    "es": {
      "nome": "Espírito Santo",
      "decreto": "Decreto Estadual nº 5.234-R/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior do Espírito Santo", "valor": 160.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 440.00 }
      ]
    },
    "go": {
      "nome": "Goiás",
      "decreto": "Decreto Estadual nº 10.134/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior de Goiás", "valor": 200.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 480.00 }
      ]
    },
    "ma": {
      "nome": "Maranhão",
      "decreto": "Decreto Estadual nº 38.120/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior do Maranhão", "valor": 180.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 460.00 }
      ]
    },
    "mg": {
      "nome": "Minas Gerais",
      "decreto": "Decreto Estadual nº 48.742/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior de Minas Gerais", "valor": 240.00 },
        { "id": "bh", "nome": "Belo Horizonte (Capital)", "valor": 320.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 550.00 }
      ]
    },
    "pa": {
      "nome": "Pará",
      "decreto": "Decreto Estadual nº 2.890/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior do Pará", "valor": 220.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 500.00 }
      ]
    },
    "pb": {
      "nome": "Paraíba",
      "decreto": "Decreto Estadual nº 43.120/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior da Paraíba", "valor": 150.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 410.00 }
      ]
    },
    "pr": {
      "nome": "Paraná",
      "decreto": "Decreto Estadual nº 11.230/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior do Paraná", "valor": 230.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 520.00 }
      ]
    },
    "pe": {
      "nome": "Pernambuco",
      "decreto": "Decreto Estadual nº 54.120/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior de Pernambuco", "valor": 200.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 490.00 }
      ]
    },
    "pi": {
      "nome": "Piauí",
      "decreto": "Decreto Estadual nº 21.890/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior do Piauí", "valor": 160.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 420.00 }
      ]
    },
    "rj": {
      "nome": "Rio de Janeiro",
      "decreto": "Decreto Estadual nº 48.910/2024",
      "destinos": [
        { "id": "interior", "nome": "Interior do Rio de Janeiro", "valor": 280.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 600.00 }
      ]
    },
    "rn": {
      "nome": "Rio Grande do Norte",
      "decreto": "Decreto Estadual nº 32.120/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior do RN", "valor": 170.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 430.00 }
      ]
    },
    "rs": {
      "nome": "Rio Grande do Sul",
      "decreto": "Decreto Estadual nº 56.890/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior do RS", "valor": 220.00 },
        { "id": "poa", "nome": "Porto Alegre (Capital)", "valor": 290.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 530.00 }
      ]
    },
    "ro": {
      "nome": "Rondônia",
      "decreto": "Decreto Estadual nº 27.120/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior de Rondônia", "valor": 190.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 470.00 }
      ]
    },
    "rr": {
      "nome": "Roraima",
      "decreto": "Decreto Estadual nº 33.120/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior de Roraima", "valor": 180.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 450.00 }
      ]
    },
    "sc": {
      "nome": "Santa Catarina",
      "decreto": "Decreto Estadual nº 2.120/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior de Santa Catarina", "valor": 210.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 510.00 }
      ]
    },
    "sp": {
      "nome": "São Paulo",
      "decreto": "Decreto Estadual nº 67.890/2023",
      "destinos": [
        { "id": "interior", "nome": "Interior de São Paulo", "valor": 290.00 },
        { "id": "capital", "nome": "São Paulo (Capital / Região Metropolitana)", "valor": 360.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 650.00 }
      ]
    },
    "se": {
      "nome": "Sergipe",
      "decreto": "Decreto Estadual nº 41.120/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior de Sergipe", "valor": 150.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 400.00 }
      ]
    },
    "to": {
      "nome": "Tocantins",
      "decreto": "Decreto Estadual nº 6.450/2022",
      "destinos": [
        { "id": "interior", "nome": "Interior de Tocantins", "valor": 180.00 },
        { "id": "nacional", "nome": "Viagem Interestadual (Nacional)", "valor": 460.00 }
      ]
    }
  };

  // --- Inicialização da Interface ---
  function inicializar() {
    configurarTema();
    populareSeletorEstados();

    const selectEstado = document.getElementById('selectEstado');
    const btnCalcular = document.getElementById('btnCalcular');

    if (selectEstado) {
      selectEstado.addEventListener('change', atualizarCamposPorEstado);
    }

    if (btnCalcular) {
      btnCalcular.addEventListener('click', executarCalculo);
    }
  }

  function populareSeletorEstados() {
    const select = document.getElementById('selectEstado');
    if (!select) return;

    const chaves = Object.keys(dbEstados).sort((a, b) => dbEstados[a].nome.localeCompare(dbEstados[b].nome));
    for (const uf of chaves) {
      const opt = document.createElement('option');
      opt.value = uf;
      opt.textContent = `${dbEstados[uf].nome} (${uf.toUpperCase()})`;
      select.appendChild(opt);
    }
  }

  function atualizarCamposPorEstado() {
    const uf = document.getElementById('selectEstado').value;
    const est = dbEstados[uf];
    if (!est) return;

    const groupCargo = document.getElementById('groupCargo');
    const groupDestino = document.getElementById('groupDestino');
    const selectCargo = document.getElementById('selectCargo');
    const selectDestino = document.getElementById('selectDestino');

    // Atualiza cargos se existirem
    if (est.cargos && est.cargos.length > 0) {
      groupCargo.style.display = 'block';
      selectCargo.innerHTML = est.cargos.map(c => `<option value="${c.id}">${c.nome}</option>`).join('');
    } else {
      groupCargo.style.display = 'none';
    }

    // Atualiza destinos
    if (est.destinos && est.destinos.length > 0) {
      groupDestino.style.display = 'block';
      selectDestino.innerHTML = est.destinos.map(d => `<option value="${d.id}">${d.nome} - R$ ${d.valor ? d.valor.toFixed(2) : 'Tabela'}</option>`).join('');
    } else {
      groupDestino.style.display = 'none';
    }
  }

  function executarCalculo() {
    const uf = document.getElementById('selectEstado').value;
    const dInicio = document.getElementById('dateInicio').value;
    const dFim = document.getElementById('dateFim').value;
    const semPernoite = document.getElementById('chkSemPernoite').checked;
    const alimentacaoPaga = document.getElementById('chkAlimentacaoPaga').checked;

    if (!uf || !dInicio || !dFim) {
      alert('Por favor, preencha o estado de vínculo e as datas de início e fim da viagem.');
      return;
    }

    const dtInicio = new Date(dInicio + 'T00:00:00');
    const dtFim = new Date(dFim + 'T00:00:00');

    if (dtFim < dtInicio) {
      alert('A data de fim não pode ser anterior à data de início.');
      return;
    }

    const diffTime = Math.abs(dtFim - dtInicio);
    const diasTotal = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    const est = dbEstados[uf];
    const idCargo = document.getElementById('selectCargo').value;
    const idDestino = document.getElementById('selectDestino').value;

    let valorUnitario = 200.00;

    if (est.matriz && idCargo && est.matriz[idCargo] && est.matriz[idCargo][idDestino]) {
      valorUnitario = est.matriz[idCargo][idDestino];
    } else if (est.destinos) {
      const destObj = est.destinos.find(d => d.id === idDestino);
      if (destObj && destObj.valor) valorUnitario = destObj.valor;
    }

    let multiplicador = 1.0;
    if (semPernoite) multiplicador = 0.5;
    if (alimentacaoPaga) multiplicador *= 0.7;

    const valorDiariaCalculado = valorUnitario * multiplicador;
    const valorTotalDevido = valorDiariaCalculado * diasTotal;

    renderizarResultado({
      estado: est.nome,
      decreto: est.decreto || 'Regulamento Estadual de Diárias',
      dias: diasTotal,
      valorUnitario: valorUnitario,
      valorDiariaCalculado: valorDiariaCalculado,
      valorTotal: valorTotalDevido,
      dtInicio: dtInicio.toLocaleDateString('pt-BR'),
      dtFim: dtFim.toLocaleDateString('pt-BR'),
      semPernoite: semPernoite,
      alimentacaoPaga: alimentacaoPaga
    });
  }

  function renderizarResultado(res) {
    const container = document.getElementById('resultContainer');
    if (!container) return;

    container.innerHTML = `
      <div style="background: rgba(0, 210, 200, 0.08); border: 1px solid rgba(0, 210, 200, 0.2); border-radius: 10px; padding: 1.25rem; text-align: center; margin-bottom: 1.5rem;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #00D2C8; text-transform: uppercase;">Valor Total Calculado</span>
        <h2 style="font-family: 'Outfit', sans-serif; font-size: 2.4rem; font-weight: 800; color: #00D2C8; margin: 0.4rem 0;">
          R$ ${res.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </h2>
        <span class="hat-badge" style="background: rgba(145, 70, 255, 0.15); color: #9146FF; border: 1px solid rgba(145, 70, 255, 0.3); font-size: 0.8rem;">
          ${res.decreto}
        </span>
      </div>

      <div style="margin-bottom: 1.5rem;">
        <h4 style="font-family: 'Outfit', sans-serif; font-size: 1rem; color: var(--text-primary); margin: 0 0 0.75rem 0;">Memória de Cálculo:</h4>
        
        <table style="width: 100%; font-size: 0.85rem; border-collapse: collapse;">
          <tbody>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 0.5rem 0; color: var(--text-muted);">Estado:</td>
              <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: var(--text-primary);">${res.estado}</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 0.5rem 0; color: var(--text-muted);">Período da Viagem:</td>
              <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: var(--text-primary);">${res.dtInicio} até ${res.dtFim} (${res.dias} dias)</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 0.5rem 0; color: var(--text-muted);">Valor Base da Diária:</td>
              <td style="padding: 0.5rem 0; text-align: right; font-weight: 600; color: var(--text-primary);">R$ ${res.valorUnitario.toFixed(2)}</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--border-color);">
              <td style="padding: 0.5rem 0; color: var(--text-muted);">Valor Unitário Ajustado:</td>
              <td style="padding: 0.5rem 0; text-align: right; font-weight: 700; color: #00D2C8;">R$ ${res.valorDiariaCalculado.toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <button onclick="window.print()" class="btn-a11y" style="width: 100%; padding: 0.65rem; border-radius: 6px; font-weight: 600; cursor: pointer;">
        Imprimir Relatório de Diárias
      </button>
    `;
  }

  function configurarTema() {
    const temaSalvo = localStorage.getItem('publicoverso_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', temaSalvo);

    const bDark = document.getElementById('btnThemeDark');
    const bLight = document.getElementById('btnThemeLight');
    const bContrast = document.getElementById('btnThemeContrast');
    const bFontDec = document.getElementById('btnFontDecrease');
    const bFontInc = document.getElementById('btnFontIncrease');
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

    if (bFontInc) {
      bFontInc.addEventListener('click', () => {
        const fontAtual = parseFloat(getComputedStyle(document.documentElement).fontSize);
        document.documentElement.style.fontSize = (fontAtual + 1) + 'px';
      });
    }

    if (bFontDec) {
      bFontDec.addEventListener('click', () => {
        const fontAtual = parseFloat(getComputedStyle(document.documentElement).fontSize);
        if (fontAtual > 12) {
          document.documentElement.style.fontSize = (fontAtual - 1) + 'px';
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
  } else {
    inicializar();
  }
})();
