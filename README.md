# Publicoverso

Portal editorial de curadoria independente dedicado a indexar e celebrar as historias, conquistas e trajetorias das pessoas que atuam no servico publico brasileiro.

**Site:** publicoverso.com.br
**Curadoria editorial:** Cristina Mascarenhas

---

## Estrutura do repositorio

```
portal-servidores-publicos/
|- index.html               Pagina principal do portal
|- index.css                Design System - tokens, componentes e layout
|- app.js                   Motor de renderizacao, filtros e acessibilidade
|- sobre.html               Pagina institucional - Sobre e curadoria
|- contato.html             Pagina de contato editorial
|- privacidade.html         Politica de privacidade (LGPD + AdSense)
|- termos.html              Termos de uso
|- robots.txt               Diretrizes de rastreamento
|- sitemap.xml              Mapa de URLs para indexacao
|- ads.txt                  Autorizacao para Google AdSense
|- build_materias.py        Pipeline de conversao de materias para HTML
|- data/
|  |- noticias_curadoria.json   Base de noticias e materias curadas
|  |- artigos_autorais.json     Base de colunas autorais
|- materias/
|  |- conteudo/             Depositar arquivos .txt ou .docx das materias aqui
|  |  |- _TEMPLATE_MATERIA.txt  Modelo de arquivo de materia
|  |- paginas/              HTML gerado pelo pipeline (build_materias.py)
|  |- materia.css           Estilos de paginas de materias e paginas inst.
```

---

## Pipeline de Materias Autorais

Para publicar uma nova materia no portal:

1. Copie o arquivo `materias/conteudo/_TEMPLATE_MATERIA.txt` e renomeie com o slug da materia (ex: `professora-ganha-premio-internacional.txt`).
2. Edite o cabecalho e o corpo conforme o modelo.
3. Execute o pipeline:

```bash
# Processar todos os arquivos novos
python build_materias.py

# Processar um arquivo especifico
python build_materias.py --arquivo professora-ganha-premio-internacional.txt
```

O script gera o HTML em `materias/paginas/` e atualiza automaticamente `data/noticias_curadoria.json`.

**Requisito para arquivos .docx:** `pip install python-docx`

---

## Categorias de conteudo

- Gente e Cultura
- Conquistas e Premiacoes
- Carreira e Legislacao
- Inovacao e Boas Praticas

---

## Integracao com ferramentas externas

- **Calculadora TAE Federal:** [taes-federal.com.br](https://taes-federal.com.br) - Simulacao de salarios, RSC e PCCTAE para servidores Tecnico-Administrativos em Educacao.
- **Simulador de Diarias:** /simulador-diarias.html (em desenvolvimento)

---

## Conformidade Google AdSense

Antes de solicitar aprovacao do AdSense:
- Substituir `pub-XXXXXXXXXXXXXXXX` em `ads.txt` pelo ID real do AdSense.
- Adicionar o codigo de anuncio no bloco `.adsense-block` nas paginas.
- Verificar que `sobre.html`, `privacidade.html`, `contato.html` e `termos.html` estao acessiveis.
- Submeter `sitemap.xml` no Google Search Console.

---

## Log de Atualizacoes (Changelog)

### 08/08/2026 (Sessao 5 - Taxonomia das 7 Editorias Jornalisticas)
- Implementada a arquitetura editorial estilo "G1 dos Servidores Publicos" com 7 grandes editorias: Artes & Literatura, Esportes & Aventura, Ciencia & Tecnologia, Cultura Pop & Gastronomia, Solidariedade & Comunidade, Historias & Superacao e Carreira & Conquistas.
- Atualizado o Design System em `index.css` com 7 badges coloridos exclusivos (`.badge-artes`, `.badge-esportes`, `.badge-ciencia`, `.badge-pop`, `.badge-social`, `.badge-superacao`, `.badge-carreira`).
- Atualizados os chips de navegacao em `index.html` e a filtragem dinamica em `app.js`.
- Criado o algoritmo `classificar_editoria()` em `scripts/minerador_protagonistas.py` e `scripts/minerador_historias.py` para categorizacao automatica das materias mineradas.
- Reclassificada toda a base inicial em `data/noticias_curadoria.json`.

### 08/08/2026 (Sessao 4 - Minerador de Protagonistas e Atribuicao de Fonte)
- Criado o robô `scripts/minerador_protagonistas.py` dedicado a minerar historias humanas de servidores e servidoras publica fora da reparticao (Literatura, Esportes, Cultura Pop/Realities, Voluntariado e Superacao Pessoal).
- Implementado motor de verificacao ativa de liveness (HTTP status 200), resolucao de redirecionamentos (URLs canonicas), remocao de parametros de rastreamento (UTMs) e expurgo total de pautas burocraticas/institucionais.
- Adicionado o `.box-fonte-original` no `build_materias.py` e `materias/materia.css` para exibir obrigatoriamente a fonte original e o link direto verificado da noticia.
- Integrado o novo minerador ao `scripts/pipeline_completo.py` e ao GitHub Actions em `.github/workflows/atualizacao_publicoverso.yml`.

### 08/08/2026 (Sessao 3 - Esteira de Pre-Curadoria e Remocao de Colunas)
- Corrigidos todos os links internos e favicons das paginas (`index.html`, `sobre.html`, `contato.html`, `privacidade.html`, `termos.html`, `concursos.html` e `build_materias.py`) de caminhos absolutos (`/sobre.html`) para caminhos relativos funcionais (`sobre.html` / `../../sobre.html`), garantindo navegacao 100% perfeita tanto no GitHub Pages quanto em preview local.
- Criado o script `generate_favicons.py` que gera a suite completa de favicons com base no logo hexagonal/constelacao: `favicon.ico` (16, 32, 48px), `favicon.svg`, `favicon-16x16.png`, `favicon-32x32.png`, `favicon-48x48.png` e `apple-touch-icon.png` (180x180).
- Adicionadas as tags de favicon no `<head>` de todas as paginas (`index.html`, `sobre.html`, `contato.html`, `privacidade.html`, `termos.html`, `concursos.html` e `build_materias.py`).
- Implementada esteira de triagem e historico temporal:
  - Os robos de mineracao gravam os rascunhos em `pre_curadoria/AAAA/MM/DD/slug.txt` com base na data atual.
  - Criado o utilitario CLI `scripts/promover_materia.py` para validar e mover materias selecionadas da pre-curadoria para `materias/conteudo/`.
  - Criado `requirements.txt` e o workflow do GitHub Actions em `.github/workflows/atualizacao_publicoverso.yml`.
- Refatorado `index.html`: removida a secao de Colunas Autorais, mantendo o nome e curadoria editorial de Cristina Mascarenhas no Hero e Rodape.
- Atualizado `app.js`: desativado o carregamento de colunas para otimizacao do feed principal.

### 08/08/2026 (Sessao 2 - Mineracao e Radar de Concursos)
- Implementado modulo de scripts de mineracao em `scripts/`:
  - `config.py`: configuracoes globais, Dorks pre-configurados por categoria editorial e variaveis de ambiente.
  - `minerador_historias.py`: busca via Serper API (Google News), raspagem via Scraper API, filtragem de relevancia e geracao de rascunhos em `materias/conteudo/`.
  - `radar_concursos.py`: busca de editais de concursos via Serper API, extracao de metadados estruturados e atualizacao de `data/concursos_radar.json`.
  - `pipeline_completo.py`: orquestrador que executa todos os scripts em sequencia com um unico comando.
- Criada base inicial `data/concursos_radar.json` com 5 editais de alta relevancia (PF, RFB, BCB, CNJ, TAE/UF).
- Criada pagina `concursos.html` com grid interativo de editais, filtros por escolaridade e esfera, busca textual e aviso anti-fraude.
- Criado `app_concursos.js` com motor de renderizacao e filtragem do Radar de Concursos.
- Adicionados estilos dos cards de concurso em `index.css` (badges de status, grid de detalhes, aviso anti-fraude).
- Atualizado `index.html` com link `Radar de Concursos` no menu e terceiro card de utilitarios.
- Atualizado `sitemap.xml` com a URL de `concursos.html`.

### 08/08/2026
- Implementacao completa do portal Publicoverso.
- Logo SVG hexagonal/constelacao com tokens #00D2C8 e #9146FF.
- Refatoracao total de `index.html` com novo conceito editorial (indexador de historias humanas do servico publico, sem filtro de esfera).
- Criacao de `app.js` com motor de renderizacao via JSON, filtros de categoria e acessibilidade (A+/A-, Alto Contraste).
- Criacao das paginas institucionais: `sobre.html` (perfil da curadora Cristina Mascarenhas), `contato.html`, `privacidade.html` (LGPD + AdSense) e `termos.html`.
- Pipeline `build_materias.py`: converte .txt/.docx em HTML com JSON-LD NewsArticle e atualiza `noticias_curadoria.json`.
- Criacao de `materia.css` para estilos de paginas de materias e paginas institucionais.
- Adicionados `robots.txt`, `sitemap.xml` e `ads.txt` para conformidade SEO e AdSense.
- Base de dados `noticias_curadoria.json` atualizada com 7 materias curadas no novo formato (sem campo `esfera`).
- Template de materia em `materias/conteudo/_TEMPLATE_MATERIA.txt`.
