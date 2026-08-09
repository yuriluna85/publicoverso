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
|- servicos.html            Página de serviços e utilitários
|- robots.txt               Diretrizes de rastreamento
|- sitemap.xml              Mapa de URLs para indexacao
|- ads.txt                  Autorização para Google AdSense
|- build_materias.py        Pipeline de conversao de materias para HTML
|- classificador_noticias.py Agente classificador policial de notícias
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

### 09/08/2026 (Sessão 11 - Correções Finas de Layout CSS, Convite Institucional Autoral e Reclassificação de Temas do STF e Histórias de Superação)
- **Correção do Layout CSS de `.news-row-item` (`index.css`):** Ajuste da propriedade de largura para 100%, eliminando a restrição de dimensão anterior que ocasionava o esmagamento dos títulos das notícias a 140px.
- **Esvaziamento e Atualização da Seção de Artigos Autorais:** Reinicialização da base de dados `data/artigos_autorais.json` (`[]`) e substituição da seção no portal por um convite institucional para submissão de colunas autorais.
- **Reclassificação Temática de Decisões do STF e Legislação de C&T:** Reagrupamento dos conteúdos referentes aos Temas de Repercussão Geral do STF (1019, 1061 e 1261) e da legislação aplicável a Ciência e Tecnologia para a categoria "Jurídico e PAD".
- **Reclassificação de Depoimentos de Redes Sociais:** Readequação editorial dos depoimentos sobre convocação e aprovação em concursos públicos coletados em redes sociais, realocando-os para a editoria "Histórias e Superação".

### 09/08/2026 (Sessão 10 - Seção Nobre de Desinformação, Landing Pages de Categoria, Verificador Semântico Inteligente e Expansão do Robô do DOU/DOEs)
- **Implementação do Filtro Estrito Anti-Anúncios Comerciais e de Captação Advocatícia:** Adição de camada de triagem e bloqueio automatizado nos scripts `verificador_semantico_noticias.py` e `radar_movimentacao_servidores.py` para descarte imediato de conteúdos promocionais, materiais publicitários e ofertas de captação de clientes (como defesa técnica em Processo Administrativo Disciplinar - PAD, serviços de assessoria jurídica privada e cursos pagos).
- **Desenvolvimento da Seção Nobre Mitos e Fatos (`desinformacao.html`):** Criação da página institucional destinada ao combate à desinformação sobre o serviço público brasileiro, com a apresentação de dados oficiais, esclarecimentos jurídicos e estatísticas auditadas contra mitos recorrentes do funcionalismo.
- **Implementação das Landing Pages Exclusivas por Categoria:** Construção de 8 páginas tematizadas (`categoria-policial.html`, `categoria-esportes.html`, `categoria-saude.html`, `categoria-educacao.html`, `categoria-cultura.html`, `categoria-inovacao.html`, `categoria-carreira.html` e `categoria-premiacoes.html`) para indexação segmentada e otimização de navegação por editoria.
- **Desenvolvimento do Verificador Semântico Inteligente (`scripts/verificador_semantico_noticias.py`):** Modulagem de motor analítico avançado com desambiguação fina de contexto textual, responsável pela validação semântica e filtragem de ruídos antes do processamento de matérias.
- **Expansão do Robô de Monitoramento de Atos Oficiais (`scripts/radar_movimentacao_servidores.py`):** Ampliação da capacidade de varredura do robô para rastreamento automatizado de portarias de atos funcionais publicados no Diário Oficial da União (DOU) e Diários Oficiais dos Estados (DOEs), abrangendo admissões, exonerações e demissões decorrentes de Processos Administrativos Disciplinares (PAD).
- **Expurgo Total e Limpeza da Base de Curadoria:** Sanitização integral e reinicialização da base `data/noticias_curadoria.json` (`[]`), garantindo a exclusão de conteúdos legados e preparando a infraestrutura para inserção de novos registros validados.

### 09/08/2026 (Sessão 9 - Expurgo de Arquivos de Teste/Template e Trava de Segurança no Pipeline de Materias)
- **Expurgo Definitivo de Conteúdos de Teste e Templates:** Remoção completa dos arquivos de matérias de teste e modelos de rascunho dos diretórios `materias/conteudo/` e `materias/paginas/`, bem como a limpeza integral dos registros correspondentes na base de dados `data/noticias_curadoria.json`.
- **Implementação de Trava de Segurança em `build_materias.py`:** Inclusão de filtro rígido de validação de arquivos no pipeline de compilação de matérias. O script foi atualizado para ignorar expressamente arquivos de modelo (`_TEMPLATE_MATERIA.txt`), rascunhos de homologação e artefatos de testes unitários ou de integração durante o processo de geração das páginas HTML e atualização da base JSON.

### 09/08/2026 (Sessão 8 - Correções Finais e Consolidação do Portal)
- **Corrigido bug crítico em `app.js`:** Adicionada a função `categoriaBadgeClass()` que estava sendo chamada nas três colunas do hero grid e no bento grid mas não estava definida, causando falha silenciosa na renderização de todos os badges de editoria.
- **Corrigido carregamento das Google Fonts em `index.html`:** Adicionado o link `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800">` que estava ausente, fazendo o portal usar tipografia de fallback do sistema.
- **Atualizado `app_noticias.js`:** A página `noticias.html` agora mescla `noticias_curadoria.json` e `acervo_links_minerados.json` em paralelo com deduplicação por URL, exibindo o acervo completo (curadoria + mineração) em ordem cronológica.
- **Adicionado alias `.badge-cultura` em `index.css`:** Corrigida incompatibilidade entre o nome de classe retornado por `categoriaBadgeClass()` (`badge-cultura`) e os seletores existentes no CSS (`badge-culturapop`). Badges de "Histórias e Superação" também foram padronizados removendo o seletor com acento (`.badge-histórias`) em favor do seletor ASCII-safe (`.badge-historias`).

### 09/08/2026 (Sessão 7 - Arquitetura Editorial G1, Colunas de Opinião, Perfis Lattes, Agente Classificador Policial, Cron 05h e Serviços)
- **Criação da Página de Serviços (`servicos.html`):** Desenvolvimento de interface centralizada para consulta de utilitários, simuladores e ferramentas voltadas aos servidores públicos.
- **Implementação do Agente Classificador (`classificador_noticias.py`):** Módulo automatizado para classificação, categorização e triagem de notícias com inteligência aplicada ao segmento policial e de segurança pública.
- **Ajuste da Cron no GitHub Actions (`.github/workflows/`):** Atualização do agendamento automatizado de execução das rotinas de mineração e publicação no GitHub Actions para às 05h.
- **Integração dos Perfis Lattes da Curadoria:** Adição dos links e metadados dos currículos Lattes de Cristina Mascarenhas (com foto de perfil oficial) e Yuri Almeida na seção institucional (`sobre.html`).
- **Expurgo Integral de Mocks:** Remoção completa de dados fictícios, estruturas mockadas e registros temporários das bases de dados JSON, garantindo 100% de conteúdos autênticos.

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

### 09/08/2026 (Sessao 6 - Servidor Local .bat, HTTPS Estrito e Novo E-mail de Contato)
- Criado o mini servidor local Python nativo `server.py` na porta 8088 com suporte a MIME types UTF-8, no-cache em desenvolvimento e logs limpos.
- Criado o executável Windows `iniciar_servidor_local.bat` para disparo automatizado com 1 clique e abertura direta do navegador em `http://localhost:8088`.
- Inserido o e-mail de contato e curadoria direta `publicoverso@gmail.com` em todas as páginas (`contato.html`, `sobre.html`, `privacidade.html`, `termos.html`, `build_materias.py` e Mega-Rodapé Editorial).
### 09/08/2026 (Sessao 14 - Calibragem Semântica Fina & Gatekeeper de Vínculo Público)
- Implementada a validação factual de vínculo funcional público obrigatório no Gatekeeper de triagem (`TERMOS_VINCULO_PUBLICO_OBRIGATORIO`). Notícias genéricas sem menção a servidores públicos (ex.: maratonista Daniel Ferreira) são sumariamente descartadas.
- Implementado o filtro estrito anti-eleitoral e político-partidário (`TERMOS_EXPURGO_POLITICO_ELEITORAL`), eliminando candidaturas ao governo/prefeitura e convenções partidárias (ex.: candidatos ao governo de Roraima).
- Implementado o expurgo de documentos legislativos arcaicos (ex.: PEC de 1993).
- Refatorada a matriz determinística de 9 editorias:
  - Fatos criminais, assaltos e acidentes com servidores redirecionados para **Policial e Segurança Pública** (corrigindo desvios em Artes).
  - Temas do STF (Tema 1019) e conflitos de interesses/regras de conduta (Fachin) redirecionados para **Jurídico e PAD** (corrigindo desvios em Ciência).
  - Livros e romances reais de servidores mantidos em **Artes e Literatura**.
- Executada a sanitização retroativa: 35 matérias 100% legítimas mantidas com categorização impecável.

### 09/08/2026 (Sessao 13 - Mineração Aberta da Vida Além do Trabalho & Expurgo Total de Redes Sociais)
- Reformulada a engenharia de busca do Publicoverso: mineração aberta em toda a internet (sem cercadinho de domínios), cobrindo portais de sindicatos (SINPF, FASUBRA, SINASEFE, ANDES, SINDIFISCO), associações de classe (ADPESP, delegados.com.br), portais regionais/locais e imprensa nacional.
- Implementadas Dorks de cauda longa focadas no protagonismo humano da "Vida dos Servidores Para Além do Trabalho" (livros, romances, poesia, maratonas, jiu-jitsu, MasterChef, BBB, programas de TV, voluntariado, ONGs e superação).
- Implementada a blindagem quádrupla anti-redes sociais (Instagram, Facebook, LinkedIn, TikTok, Reddit, X/Twitter, Threads, YouTube, Pinterest, Kwai) nas Dorks, no `agent_curador_semantico.py` e nas travas defensivas do frontend JavaScript (`app.js`, `app_noticias.js`, `app_categoria.js`).
- Executada a curadoria retroativa, eliminando 100% dos posts de redes sociais e mantendo 75 notícias puras de veículos noticiosos e comunicados institucionais de imprensa.

### 09/08/2026 (Sessao 12 - Agente Curador e Classificador Semântico de Notícias)
- Criado o módulo autônomo `scripts/agent_curador_semantico.py` para sanitização semântica, desambiguação e descarte de não-notícias do Publicoverso.
- Implementado o pipeline de 4 camadas: (1) Garbage Collector para expurgo de PDFs estáticos de órgãos (`@@download.pdf`), acórdãos forenses do STJ/Jusbrasil, propagandas de escritórios advocatícios/apostilas e ruído social; (2) Enriquecedor textual leve via raspagem de meta description e parágrafos iniciais; (3) Matriz hierárquica de 9 níveis com contra-indicações estritas para eliminar falsos cognatos (ex.: "show" em homicídio -> Policial; "aposentadoria" em Física -> Carreira); (4) Normalização para as 8 landing pages.
- Integrado o novo agente ao `scripts/pipeline_completo.py` e ao agendamento do GitHub Actions em `.github/workflows/atualizacao_publicoverso.yml`.
- Executada a higienização retroativa completa no acervo (`data/acervo_links_minerados.json`), descartando 10 itens de lixo/duplicatas e reclassificando 8 matérias com alta precisão factual.

### 09/08/2026 (Sessao 5 - Reestruturacao Editorial, Mega-Roda-pe e Banner LGPD)
- Reestruturado o System Design de Cores (`SYSTEM_DESIGN_PUBLICOVERSO.md`) calibrando a luminosidade dos tokens de leitura para garantir contraste estrito WCAG 2.1 AA/AAA em todos os 3 modos de cor.
- Implementado o componente de **Consentimento de Cookies e Privacidade (LGPD Lei nº 13.709/2018 / GDPR)** em `app.js` e `index.css`, com mensagem clara em Linguagem Simples, botões de ação e persistência de escolha do usuário via `localStorage` (`publicoverso_cookie_consent`).
- Substituído o rodapé simples anterior pelo novo **Mega-Rodapé Editorial em 4 Colunas** em `index.html` (Marca/Curadoria, Editorias, Utilitários e Governança/LGPD/DPO).
- Adicionadas regras no `index.css` para layout responsivo do rodapé (4 colunas no desktop, 2 colunas em tablet e 1 coluna em mobile) e contraste elevado em links e legendas.

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
