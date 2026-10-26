# Issue 09 — Construir a página HTML de consulta

**Status:** parcialmente concluída em 26/10/2026 — implementação e testes
automatizados concluídos; captura visual desktop/móvel não concluída.

## Objetivo

Construir uma página estática, responsiva e acessível para apresentar a votação
de Otoniel Andrade por cidade, zona e seção. A página carregará exclusivamente o
dataset validado da Issue 08, mostrará os totais oficiais e disponibilizará a
listagem paginada; os filtros combináveis serão implementados na Issue 10.

## Direção técnica

A implementação será buildless, com HTML, CSS e JavaScript nativos, seguindo o
fluxo recomendado pela skill `sites` para páginas estáticas simples.

- Diretório publicável: `public/`.
- Framework: nenhum.
- Dependências de runtime: nenhuma.
- Fonte dos dados: `public/data/votos_otoniel_25222_TO_2026.json`.
- Comportamento: executado integralmente no navegador.
- Persistência, API e backend: não necessários.

A publicação/hosting não faz parte desta issue; o resultado ficará pronto para
ser servido como site estático e validado localmente.

## Escopo

### Incluído

- Estrutura visual completa da página.
- Carregamento e validação básica do JSON público.
- Identificação do candidato, eleição e fonte oficial.
- Cards de resumo com votos, municípios, registros e agregações.
- Tabela paginada com os 1.225 registros.
- Estados de carregamento, erro, ausência de dados e conteúdo pronto.
- Navegação acessível da paginação.
- Layout responsivo para desktop e dispositivos móveis.
- Link para download do XLSX validado da Issue 07.
- Testes das funções puras de apresentação e paginação.

### Excluído

- Filtros combináveis por cidade, zona e seção, pertencentes à Issue 10.
- Total recalculado por filtros, pertencente à Issue 10.
- Backend, autenticação, banco de dados ou painel administrativo.
- Alteração de dados eleitorais pelo navegador.
- Publicação em domínio ou mudança de audiência do site.

## Arquitetura de arquivos

```text
public/
├── index.html
├── assets/
│   └── styles.css
├── js/
│   ├── data-model.js
│   └── app.js
├── data/
│   ├── votos_otoniel_25222_TO_2026.json
│   └── votos_otoniel_25222_TO_2026.json.sha256
└── downloads/
    └── otoniel_andrade_25222_TO_2026.xlsx

tests/web/
└── data-model.test.mjs
```

`data-model.js` concentrará validação, ordenação, paginação e formatação sem
acessar o DOM. `app.js` será responsável por estado, eventos e renderização.

## Estrutura da página

### Cabeçalho

- Identificação “Otoniel Andrade — 25222”.
- Cargo “Deputado Estadual”.
- Eleições 2026, 1º turno, Tocantins.
- Selo textual “Dados oficiais do TSE”.

### Resumo

Quatro cards:

1. Total de votos: `7.180`.
2. Municípios: `89`.
3. Unidades de apuração: `1.225`.
4. Registros com seção agregada: `19`.

Os valores devem vir do JSON, nunca ser digitados diretamente no HTML.

### Contexto e proveniência

- Data de geração do dataset.
- Versão do contrato e do schema.
- Link para a URL oficial do TSE.
- Nota explicativa sobre seções agregadas.
- Link para baixar o XLSX validado.

### Tabela

| Coluna | Conteúdo |
| --- | --- |
| Cidade | Nome oficial do município |
| Zona eleitoral | Identificador textual |
| Seção | Identificador textual |
| Seções agregadas | Lista ou indicação “Não” |
| Votos | Inteiro formatado em `pt-BR` |

- Paginação padrão de 50 registros.
- Indicador “Exibindo X–Y de 1.225”.
- Botões Anterior e Próxima com estados desabilitados corretos.
- Cabeçalho da tabela permanece legível durante rolagem.
- Contêiner com rolagem horizontal em telas estreitas.

## Estados da interface

### Carregando

- Mensagem anunciada por `aria-live`.
- Estrutura principal permanece estável para evitar saltos de layout.

### Pronto

- Cards e tabela preenchidos somente após validação mínima do dataset.
- Paginação iniciada na primeira página.

### Vazio

- Mensagem clara quando `registros` for uma lista vazia.
- Tabela e paginação ocultadas.

### Erro

- Mensagem amigável sem expor stack trace.
- Orientação para tentar novamente ou verificar o arquivo de dados.
- Erro técnico preservado apenas no console do navegador.

### JavaScript desabilitado

- Elemento `noscript` explicando que a consulta interativa requer JavaScript.

## Plano de execução

- [x] Criar `public/index.html` com landmarks semânticos, metadados, skip link,
  conteúdo inicial e estados da aplicação.
- [x] Criar `public/assets/styles.css` com tokens visuais, layout responsivo,
  foco visível, contraste adequado e estilos de tabela/paginação.
- [x] Criar `public/js/data-model.js` com validação básica do documento,
  formatação `pt-BR` e paginação determinística.
- [x] Criar `public/js/app.js` com máquina de estados simples: carregando,
  pronto, vazio e erro.
- [x] Carregar o dataset com `fetch()` usando caminho relativo ao site.
- [x] Renderizar conteúdo exclusivamente com `textContent` e criação explícita
  de elementos, sem inserir dados oficiais por `innerHTML`.
- [x] Preencher os cards de resumo e a proveniência a partir do JSON.
- [x] Implementar tabela com 50 registros por página e navegação anterior/próxima.
- [x] Exibir seções agregadas sem distribuir ou duplicar seus votos.
- [x] Copiar o XLSX validado para `public/downloads/` e criar link de download.
- [x] Adicionar `tests/web/data-model.test.mjs` usando o test runner nativo do
  Node para validação, paginação, limites e formatação.
- [x] Testar falhas de HTTP, JSON inválido, schema incompatível e lista vazia.
- [x] Servir `public/` localmente por HTTP; não validar via `file://`, pois
  `fetch()` depende de origem HTTP.
- [x] Antes da prévia no navegador, ler a orientação local de preview da skill
  `sites` e seguir o fluxo indicado por ela.
- [ ] Validar visualmente desktop e viewport móvel, navegação por teclado,
  estados de foco, rolagem da tabela e ausência de overflow da página.
- [x] Executar a suíte Python existente e os novos testes JavaScript.
- [x] Atualizar esta issue marcando apenas os itens efetivamente concluídos e
  registrando limites de validação, se houver.

## Regras de segurança e integridade

1. O frontend somente lê o JSON; não recalcula nem altera dados de origem.
2. Os cards devem coincidir com o objeto `resumo` do dataset.
3. A tabela deve usar os registros na ordem publicada pela Issue 08.
4. Dados do TSE são tratados como texto não confiável para fins de renderização.
5. Links externos usam `rel="noopener noreferrer"` quando abrirem nova aba.
6. Nenhum valor eleitoral será gravado diretamente no HTML como fonte paralela.
7. O XLSX oferecido para download deve ser exatamente o artefato validado da
   Issue 07.
8. A interface deve explicar que uma linha com agregação representa uma única
   unidade de apuração.

## Acessibilidade

- [x] Documento possui idioma `pt-BR`, título descritivo e hierarquia correta de
  títulos.
- [x] Conteúdo usa `header`, `main`, `section`, `table` e `footer` semanticamente.
- [x] Tabela possui `caption`, cabeçalhos com `scope="col"` e descrição adequada.
- [x] Mudanças de carregamento e erro são anunciadas por região `aria-live`.
- [x] Paginação é operável por teclado e possui nomes acessíveis.
- [x] Foco visível não é removido pelos estilos.
- [ ] Cores mantêm contraste legível sem depender apenas de cor para significado.
- [x] Movimento e transições respeitam `prefers-reduced-motion`.

## Casos de teste

- [ ] Dataset válido preenche cabeçalho, cards e primeira página.
- [x] Primeira página contém 50 registros e a última contém o restante.
- [x] Botão Anterior inicia desabilitado e Próxima desabilita na última página.
- [x] Indicador de faixa apresenta valores corretos em todas as páginas.
- [x] Votos usam separador de milhar `pt-BR`.
- [x] Seção agregada é apresentada sem duplicação de linha ou voto.
- [x] Lista vazia produz estado vazio sem paginação.
- [x] JSON inválido ou HTTP com erro produz estado de erro.
- [x] Versão de schema incompatível é rejeitada com mensagem clara.
- [x] Textos semelhantes a HTML são apresentados literalmente.
- [x] Link do TSE e download do XLSX apontam para os recursos corretos.
- [ ] A página permanece utilizável em viewport móvel.

## Critérios de aceite

- [ ] A página apresenta Otoniel Andrade, cargo e eleição corretamente.
- [ ] Os cards exibem 7.180 votos, 89 municípios, 1.225 registros e 19
  agregações, todos lidos do JSON.
- [ ] A tabela permite navegar pelos 1.225 registros sem travamento perceptível.
- [ ] Cidade, zona, seção, agregações e votos são exibidos corretamente.
- [ ] Estados de carregamento, vazio e erro são compreensíveis.
- [ ] A página funciona em desktop e tela móvel.
- [ ] A navegação essencial funciona por teclado.
- [ ] XLSX validado está disponível para download.
- [x] Testes Python e JavaScript estão aprovados.
- [x] Nenhum dado eleitoral é duplicado ou inserido manualmente no HTML.

## Riscos e decisões

- O navegador não deve abrir `index.html` diretamente pelo sistema de arquivos;
  a documentação indicará um servidor HTTP local.
- A paginação será usada em vez de virtualização porque 1.225 registros formam
  um conjunto pequeno e a solução é mais acessível e simples.
- Os filtros serão adicionados apenas na Issue 10 para manter esta entrega
  focada em carregamento, apresentação e navegação.
- O site não dependerá de CDN, fontes externas ou bibliotecas JavaScript.
- Não serão usadas imagens decorativas: a prioridade é legibilidade e consulta
  de dados, evitando peso visual sem função.

## Dependências

- **Pré-requisitos:** Issue 08 concluída e dataset/checksum validados.
- **Artefato relacionado:** XLSX da Issue 07 para download.
- **Desbloqueia:** Issue 10 — filtros e total dinâmico.

## Validação executada

- 42 testes Python aprovados.
- 9 testes JavaScript aprovados.
- HTML semântico validado: idioma `pt-BR`, landmarks, 31 IDs e cinco cabeçalhos
  de coluna com `scope="col"`.
- Página, JSON, CSS, JavaScript e XLSX responderam HTTP 200 em localhost.
- Carregamento JavaScript real via HTTP confirmou 1.225 registros e 25 registros
  na última página.
- O XLSX publicado para download é idêntico ao artefato validado da Issue 07.
- Duas tentativas de captura por Firefox headless não produziram imagens; a
  segunda confirmou falha do compositor `RenderCompositorSWGL`. Por isso, os
  itens de validação visual permanecem pendentes.

## Entregas realizadas

- [x] `public/index.html`
- [x] `public/assets/styles.css`
- [x] `public/js/data-model.js`
- [x] `public/js/app.js`
- [x] `public/downloads/otoniel_andrade_25222_TO_2026.xlsx`
- [x] `tests/web/data-model.test.mjs`
- [x] `docs/SITE_LOCAL.md`

## Pendências

- [ ] Concluir inspeção visual em desktop e viewport móvel.
- [ ] Confirmar contraste por ferramenta ou inspeção em navegador.
- [ ] Confirmar visualmente ausência de overflow e usabilidade móvel.
