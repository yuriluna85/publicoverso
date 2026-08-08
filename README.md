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
