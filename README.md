# Publicoverso

Portal editorial de curadoria independente dedicado a indexar e celebrar as histórias, conquistas e trajetorias das pessoas que atuam no serviço público brasileiro.

**Site:** publicoverso.com.br
**Curadoria editorial:** Cristina Mascarenhas

---

## Estrutura do repositorio

```
portal-servidores-públicos/
|- index.html               Página principal do portal
|- index.css                Design System - tokens, componentes e layout
|- app.js                   Motor de renderizacao, filtros e acessibilidade
|- sobre.html               Página institucional - Sobre e curadoria
|- contato.html             Página de contato editorial
|- privacidade.html         Política de privacidade (LGPD + AdSense)
|- termos.html              Termos de uso
|- robots.txt               Diretrizes de rastreamento
|- sitemap.xml              Mapa de URLs para indexacao
|- ads.txt                  Autorização para Google AdSense
|- build_materias.py        Pipeline de conversao de materias para HTML
|- data/
|  |- noticias_curadoria.json   Base de notícias e materias curadas
|  |- artigos_autorais.json     Base de colunas autorais
|- materias/
|  |- conteúdo/             Depositar arquivos .txt ou .docx das materias aqui
|  |  |- _TEMPLATE_MATERIA.txt  Modelo de arquivo de materia
|  |- páginas/              HTML gerado pelo pipeline (build_materias.py)
|  |- materia.css           Estilos de páginas de materias e páginas inst.
```

---

## Pipeline de Materias Autorais

Para publicar uma nova materia no portal:

1. Copie o arquivo `materias/conteúdo/_TEMPLATE_MATERIA.txt` e renomeie com o slug da materia (ex: `professora-ganha-premio-internacional.txt`).
2. Edite o cabeçalho e o corpo conforme o modelo.
3. Execute o pipeline:

```bash
# Processar todos os arquivos novos
python build_materias.py

# Processar um arquivo especifico
python build_materias.py --arquivo professora-ganha-premio-internacional.txt
```

O script gera o HTML em `materias/páginas/` e atualiza automaticamente `data/noticias_curadoria.json`.

**Requisito para arquivos .docx:** `pip install python-docx`

---

## Categorias de conteúdo

- Gente e Cultura
- Conquistas e Premiações
- Carreira e Legislação
- Inovação e Boas Práticas

---

## Integracao com ferramentas externas

- **Calculadora TAE Federal:** [taes-federal.com.br](https://taes-federal.com.br) - Simulação de salários, RSC e PCCTAE para servidores Técnico-Administrativos em Educacao.
- **Simulador de Diárias:** /simulador-diárias.html (em desenvolvimento)

---

## Conformidade Google AdSense

Antes de solicitar aprovacao do AdSense:
- Substituir `pub-XXXXXXXXXXXXXXXX` em `ads.txt` pelo ID real do AdSense.
- Adicionar o codigo de anuncio no bloco `.adsense-block` nas páginas.
- Verificar que `sobre.html`, `privacidade.html`, `contato.html` e `termos.html` estao acessiveis.
- Submeter `sitemap.xml` no Google Search Console.

---

## Log de Atualizações (Changelog)

### 09/08/2026 (Sessão 8 - Correções Finais e Consolidação do Portal)
- **Corrigido bug crítico em `app.js`:** Adicionada a função `categoriaBadgeClass()` que estava sendo chamada nas três colunas do hero grid e no bento grid mas não estava definida, causando falha silenciosa na renderização de todos os badges de editoria.
- **Corrigido carregamento das Google Fonts em `index.html`:** Adicionado o link `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800">` que estava ausente, fazendo o portal usar tipografia de fallback do sistema.
- **Atualizado `app_noticias.js`:** A página `noticias.html` agora mescla `noticias_curadoria.json` e `acervo_links_minerados.json` em paralelo com deduplicação por URL, exibindo o acervo completo (curadoria + mineração) em ordem cronológica.
- **Adicionado alias `.badge-cultura` em `index.css`:** Corrigida incompatibilidade entre o nome de classe retornado por `categoriaBadgeClass()` (`badge-cultura`) e os seletores existentes no CSS (`badge-culturapop`). Badges de "Histórias e Superação" também foram padronizados removendo o seletor com acento (`.badge-histórias`) em favor do seletor ASCII-safe (`.badge-historias`).

### 08/08/2026 (Sessão 8 - Exibição Direta das Notícias Mineradas na Capa Principal)
- **Integração Imediata do Acervo na Capa (`index.html` e `app.js`):**
  - O motor de renderização `app.js` unifica `noticias_curadoria.json` e `acervo_links_minerados.json`.
  - Exibe todas as notícias mineradas pelos robôs em tempo real na capa do portal (Super Manchete, Destaques Secundários e Bento Grid), direcionando o leitor para o veículo original (`target="_blank"`) no caso de matérias sem página interna autoral gerada.

### 08/08/2026 (Sessão 7 - Validação Factual em 4 Camadas, Expurgo Político e Robô de Movimentação Funcional)
- **Filtro de Blindagem Anti-Político e Anti-Eleitoral:**
  - Expurgo automático de qualquer conteúdo sobre mandatos eletivos (vereadores, prefeitos, deputados, senadores, governadores, presidente) e disputas partidárias/eleitorais.
- **Validação Factual Estrita de Servidores Públicos do Brasil (`validar_servidor_publico_brasileiro`):**
  - **Camada 1 (Dorks Estritos):** Exclusão ativa de domínios internacionais (`-site:*.pt -site:*.ao -site:*.mz -Portugal`).
  - **Camada 2 (Expurgo Geográfico Internacional):** Bloqueio automático de domínios estrangeiros e cidades de fora do país (ex: `diarioviseu.pt`, `Castro Daire`, `Lisboa`).
  - **Camada 3 (Expurgo Político):** Rejeição sumária de políticos e candidatos.
  - **Camada 4 (Prova Factual de Vínculo):** Exigência de âncora textual comprovatória de vínculo com o serviço público brasileiro (`servidor público`, `estatutário`, `concursado`, `SUS`, `instituto federal`, `universidade federal`, `polícia`, `tribunal`, `DOU`).
- **Novo Robô de Movimentação Funcional (`scripts/radar_movimentacao_servidores.py`):**
  - Rastreamento exclusivo de posses, nomeações de aprovados em concursos, aposentadorias e trajetórias de legado funcional nos Diários Oficiais e na imprensa.
  - Integrado ao `pipeline_completo.py` e ao workflow agendado do GitHub Actions (`.github/workflows/atualizacao_publicoverso.yml`).

### 08/08/2026 (Sessao 6 - Novo Layout Editorial Fusão G1 + Jornal da USP)
- **Reestruturação Completa da Capa (`index.html`):**
  - **Grid Editorial Hero em 3 Colunas:**
    1. **Coluna 1 (Super Manchete - 50% Desktop):** Manchete de grande impacto com chapéu de editoria, título em `Outfit` 800, linha-fina contextual e rodapé com meta-informações.
    2. **Coluna 2 (Destaques Secundários - 25% Desktop):** Dois cartões médios verticais empilhados com resumo objetivo e acabamento nobre.
    3. **Coluna 3 (Feed "Últimas do Serviço Público" - 25% Desktop):** Feed dinâmico ao vivo com os últimos 5 links minerados da web, indicador pulsante e atalho para o acervo completo (`noticias.html`).
  - **Estética Editorial Inspirada no Jornal da USP:** Inclusão de cabeçalhos de seção com linhas divisórias de gradiente suave (`.section-line-usp`), tipografia hierárquica e espaçamento proporcional.
  - **Preservação de Identidade & A11y:** Manutenção da paleta de cores (Azul Petróleo, Turquesa Neon e Roxo Luna), botões balão arredondados no cabeçalho e suporte total aos 3 temas (Claro, Escuro e Alto Contraste AAA).

### 08/08/2026 (Sessao 4 - Minerador de Protagonistas e Atribuição de Fonte)
- Criado o robô `scripts/minerador_protagonistas.py` dedicado a minerar histórias humanas de servidores e servidoras pública fora da reparticao (Literatura, Esportes, Cultura Pop/Realities, Voluntariado e Superacao Pessoal).
- Implementado motor de verificacao ativa de liveness (HTTP status 200), resolucao de redirecionamentos (URLs canonicas), remocao de parametros de rastreamento (UTMs) e expurgo total de pautas burocraticas/institucionais.
- Adicionado o `.box-fonte-original` no `build_materias.py` e `materias/materia.css` para exibir obrigatoriamente a fonte original e o link direto verificado da notícia.
- Integrado o novo minerador ao `scripts/pipeline_completo.py` e ao GitHub Actions em `.github/workflows/atualizacao_publicoverso.yml`.

### 08/08/2026 (Sessao 3 - Esteira de Pre-Curadoria e Remocao de Colunas)
- Corrigidos todos os links internos e favicons das páginas (`index.html`, `sobre.html`, `contato.html`, `privacidade.html`, `termos.html`, `concursos.html` e `build_materias.py`) de caminhos absolutos (`/sobre.html`) para caminhos relativos funcionais (`sobre.html` / `../../sobre.html`), garantindo navegação 100% perfeita tanto no GitHub Pages quanto em preview local.
- Criado o script `generate_favicons.py` que gera a suite completa de favicons com base no logo hexagonal/constelacao: `favicon.ico` (16, 32, 48px), `favicon.svg`, `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png` e `apple-touch-icon.png` (180x180).
- Adicionadas as tags de favicon no `<head>` de todas as páginas (`index.html`, `sobre.html`, `contato.html`, `privacidade.html`, `termos.html`, `concursos.html` e `build_materias.py`).
- Implementada esteira de triagem e historico temporal:
  - Os robos de mineracao gravam os rascunhos em `pre_curadoria/AAAA/MM/DD/slug.txt` com base na data atual.
  - Criado o utilitário CLI `scripts/promover_materia.py` para validar e mover materias selecionadas da pre-curadoria para `materias/conteúdo/`.
  - Criado `requirements.txt` e o workflow do GitHub Actions em `.github/workflows/atualizacao_publicoverso.yml`.
- Refatorado `index.html`: removida a secao de Colunas Autorais, mantendo o nome e curadoria editorial de Cristina Mascarenhas no Hero e Rodapé.
- Atualizado `app.js`: desativado o carregamento de colunas para otimizacao do feed principal.

### 08/08/2026 (Sessao 2 - Mineracao e Radar de Concursos)
- Implementado modulo de scripts de mineracao em `scripts/`:
  - `config.py`: configuracoes globais, Dorks pre-configurados por categoria editorial e variaveis de ambiente.
  - `minerador_historias.py`: busca via Serper API (Google News), raspagem via Scraper API, filtragem de relevancia e geração de rascunhos em `materias/conteúdo/`.
  - `radar_concursos.py`: busca de editais de concursos via Serper API, extracao de metadados estruturados e atualização de `data/concursos_radar.json`.
  - `pipeline_completo.py`: orquestrador que executa todos os scripts em sequencia com um unico comando.
- Criada base inicial `data/concursos_radar.json` com 5 editais de alta relevancia (PF, RFB, BCB, CNJ, TAE/UF).
- Criada página `concursos.html` com grid interativo de editais, filtros por escolaridade e esfera, busca textual e aviso anti-fraude.
- Criado `app_concursos.js` com motor de renderizacao e filtragem do Radar de Concursos.
- Adicionados estilos dos cards de concurso em `index.css` (badges de status, grid de detalhes, aviso anti-fraude).
- Atualizado `index.html` com link `Radar de Concursos` no menu e terceiro card de utilitários.
- Atualizado `sitemap.xml` com a URL de `concursos.html`.

### 08/08/2026
- Implementacao completa do portal Publicoverso.
- Logo SVG hexagonal/constelacao com tokens #00D2C8 e #9146FF.
- Refatoracao total de `index.html` com novo conceito editorial (indexador de histórias humanas do serviço público, sem filtro de esfera).
- Criacao de `app.js` com motor de renderizacao via JSON, filtros de categoria e acessibilidade (A+/A-, Alto Contraste).
- Criacao das páginas institucionais: `sobre.html` (perfil da curadora Cristina Mascarenhas), `contato.html`, `privacidade.html` (LGPD + AdSense) e `termos.html`.
- Pipeline `build_materias.py`: converte .txt/.docx em HTML com JSON-LD NewsArticle e atualiza `noticias_curadoria.json`.
- Criacao de `materia.css` para estilos de páginas de materias e páginas institucionais.
- Adicionados `robots.txt`, `sitemap.xml` e `ads.txt` para conformidade SEO e AdSense.
- Base de dados `noticias_curadoria.json` atualizada com 7 materias curadas no novo formato (sem campo `esfera`).
- Template de materia em `materias/conteúdo/_TEMPLATE_MATERIA.txt`.
