# Issue 10 — Implementar filtros e total dinâmico

**Status:** parcialmente concluída em 26/10/2026 — implementação, regressões e
validação HTTP concluídas; QA visual/interativa em navegador permanece pendente.

## Objetivo

Adicionar filtros combináveis por cidade, zona eleitoral e seção à consulta web.
A tabela, paginação, quantidade de registros e total de votos deverão responder
imediatamente ao recorte ativo, sem modificar o dataset original nem confundir o
resultado filtrado com o total oficial geral. Um campo de pesquisa por nome da
cidade deverá operar simultaneamente com os três filtros estruturados.

## Referências para homologação

| Recorte | Registros | Votos |
| --- | ---: | ---: |
| Sem filtros | 1.225 | 7.180 |
| Cidade `PALMAS` | 359 | 574 |
| Pesquisa parcial `palm` | 361 | 576 |
| Cidade `NATIVIDADE` | 27 | 85 |
| `NATIVIDADE` + zona `19` + seção `81` | 1 | 4 |

Esses valores foram calculados diretamente sobre o JSON validado da Issue 08 e
serão usados como testes de regressão.

## Escopo

### Incluído

- Filtros por cidade, zona eleitoral e seção.
- Pesquisa parcial por nome da cidade, sem diferenciar caixa ou acentos.
- Combinação dos três filtros por interseção.
- Opções dependentes baseadas no recorte atual.
- Total de votos, registros e municípios do resultado filtrado.
- Reinício da paginação ao alterar filtros.
- Botão para limpar todos os filtros.
- Estado sem resultados com recuperação simples.
- Estado dos filtros refletido na URL para compartilhamento e recarga.
- Testes unitários e validação responsiva/acessível.

### Excluído

- Alteração do dataset JSON ou dos totais oficiais de origem.
- Ordenação configurável ou exportação do recorte.
- Backend, banco de dados ou persistência no servidor.
- Publicação/hosting do site.

## Comportamento dos filtros

### Pesquisa por cidade

- Campo do tipo `search` posicionado antes dos selects.
- Correspondência parcial, sem diferenciar maiúsculas, minúsculas ou acentos.
- Restringe simultaneamente registros e opções de cidade, zona e seção.
- Limpa seleções dependentes quando elas deixam de ser compatíveis.
- Usa o parâmetro `q` na URL compartilhável.

### Cidade

- Select ordenado alfabeticamente pelo nome oficial.
- Valor interno baseado em `codigo_municipio_tse`, evitando ambiguidade de nome.
- Opção inicial “Todas as cidades”.

### Zona eleitoral

- Select numérico ordenado por valor.
- Quando uma cidade estiver selecionada, listar somente zonas presentes nela.
- Opção inicial “Todas as zonas”.

### Seção

- Select numérico ordenado por valor.
- Listar somente seções compatíveis com cidade e zona já selecionadas.
- Opção inicial “Todas as seções”.

### Dependências

- Se uma alteração tornar zona ou seção inválida, limpar apenas o filtro
  dependente incompatível.
- Nunca alterar o array original de registros.
- Aplicar os filtros por interseção lógica.

## Resultado dinâmico

Adicionar uma faixa de resumo próxima à tabela com:

- Votos no recorte.
- Registros encontrados.
- Municípios presentes no resultado.
- Texto descritivo dos filtros ativos.

Os quatro cards do topo continuam representando o total oficial geral. O resumo
do recorte terá estilo e rótulo próprios para não sugerir que o total oficial foi
alterado.

## Estado na URL

Usar parâmetros opcionais:

```text
?q=natividade&cidade=94811&zona=19&secao=81
```

- Ler os parâmetros somente após validar o dataset.
- Ignorar valores inexistentes ou incompatíveis.
- Atualizar a URL com `history.replaceState`, sem recarregar a página.
- Remover parâmetros correspondentes a filtros limpos.

## Plano de execução

- [x] Atualizar `public/index.html` com um formulário/fieldset de filtros,
  labels explícitos, selects e botão “Limpar filtros”.
- [x] Adicionar campo de pesquisa textual e correlacioná-lo com cidade, zona e
  seção.
- [x] Adicionar ao HTML o resumo do recorte e a mensagem específica de nenhum
  resultado para filtros ativos.
- [x] Atualizar `public/assets/styles.css` para a barra de filtros, resumo ativo,
  chips descritivos e layout móvel.
- [x] Implementar em `public/js/data-model.js` funções puras para filtrar,
  calcular opções dependentes, resumir resultados e validar query parameters.
- [x] Manter registros e opções em ordem determinística, com cidade alfabética e
  zona/seção numéricas.
- [x] Atualizar `public/js/app.js` com estado de filtros separado do dataset e da
  página atual.
- [x] Preencher os selects com criação explícita de elementos e `textContent`.
- [x] Recalcular registros, votos e municípios imediatamente após cada mudança.
- [x] Reiniciar a paginação na primeira página após cada alteração de filtro.
- [x] Limpar zona/seção dependentes quando deixarem de ser válidas.
- [x] Implementar limpeza total e restaurar os 1.225 registros/7.180 votos.
- [x] Sincronizar filtros válidos com a URL usando `history.replaceState`.
- [x] Restaurar filtros válidos da URL durante a inicialização.
- [x] Ampliar `tests/web/data-model.test.mjs` com combinações, dependências,
  resumos, URLs inválidas e invariância do dataset original.
- [x] Adicionar teste de regressão para Palmas, Natividade e seção 81.
- [x] Validar por HTTP que a página e o dataset continuam carregando.
- [ ] Validar visualmente desktop e móvel, incluindo selects longos, estado sem
  resultado, teclado, foco e ausência de overflow.
- [x] Executar os testes JavaScript e toda a suíte Python.
- [x] Atualizar esta issue com os itens concluídos e registrar qualquer limite de
  validação visual.

## Funções puras previstas

```text
filterRecords(records, filters)
normalizeSearchText(value)
availableCities(records)
availableZones(records, cityCode)
availableSections(records, cityCode, zone)
summarizeRecords(records)
normalizeFilters(records, candidateFilters)
filtersFromSearchParams(searchParams)
filtersToSearchParams(filters)
```

Essas funções não acessarão o DOM e serão testadas diretamente pelo Node.

## Regras de integridade

1. Filtrar nunca altera, remove ou reordena permanentemente o dataset de origem.
2. O total do recorte é sempre a soma de `votos` dos registros visíveis.
3. A contagem de municípios usa `codigo_municipio_tse`, não apenas o nome.
4. Seções agregadas permanecem uma única linha e seus votos não são repartidos.
5. Filtros inválidos vindos da URL são ignorados, não causam erro da página.
6. Limpar filtros restaura exatamente as métricas oficiais do JSON.
7. A paginação opera somente sobre o resultado já filtrado.
8. Nenhum texto do dataset é inserido por `innerHTML`.
9. A pesquisa ignora caixa e acentos, preservando o nome oficial na exibição.

## Acessibilidade

- [x] Filtros agrupados em `fieldset` com `legend` descritiva.
- [x] Campo de pesquisa e selects possuem labels programaticamente associados.
- [x] Resultado atualizado é anunciado por região `aria-live` sem interromper a
  navegação do usuário.
- [x] Botão de limpeza informa claramente sua ação e estado desabilitado.
- [x] Ordem de foco segue pesquisa, cidade, zona, seção, limpeza e resultados.
- [x] Alterações não movem o foco automaticamente.
- [x] Estado sem resultado oferece botão acessível para limpar os filtros.
- [ ] Controles permanecem utilizáveis em zoom e viewport móvel.

## Casos de teste

- [x] Sem filtros retorna 1.225 registros, 89 municípios e 7.180 votos.
- [x] Palmas retorna 359 registros e 574 votos.
- [x] Natividade retorna 27 registros e 85 votos.
- [x] Natividade + zona 19 + seção 81 retorna um registro e quatro votos.
- [x] Pesquisa exata por `PALMAS` retorna 359 registros e 574 votos.
- [x] Pesquisa parcial por `palm` retorna 361 registros, três municípios e 576
  votos.
- [x] Pesquisa por `sao` encontra cidades com `SÃO` no nome.
- [x] Pesquisa textual funciona simultaneamente com cidade, zona e seção.
- [x] Filtros inexistentes retornam lista vazia quando aplicados diretamente.
- [x] Parâmetros inválidos da URL são ignorados durante normalização.
- [x] Zonas disponíveis respeitam a cidade selecionada.
- [x] Seções disponíveis respeitam cidade e zona selecionadas.
- [x] Alterar cidade limpa zona/seção incompatíveis.
- [x] Alterar zona limpa seção incompatível.
- [ ] Paginação volta para a primeira página após mudança.
- [ ] Limpar restaura todos os registros e desabilita o botão de limpeza.
- [x] Dataset original permanece inalterado após todas as operações.
- [ ] Resultado vazio mostra mensagem específica e permite limpar filtros.
- [ ] URL é atualizada e restaurada sem recarregar a página.

## Critérios de aceite

- [ ] Usuário pode filtrar por cidade, zona e seção individualmente ou em conjunto.
- [x] Usuário pode pesquisar o nome da cidade em conjunto com os filtros.
- [ ] Tabela, faixa exibida e paginação refletem somente o recorte ativo.
- [ ] Total de votos e quantidade de registros atualizam imediatamente.
- [ ] Totais gerais permanecem visíveis e identificados como oficiais.
- [ ] Limpeza dos filtros restaura 1.225 registros e 7.180 votos.
- [ ] Estado dos filtros pode ser compartilhado pela URL.
- [ ] Interface funciona por teclado e em tela móvel.
- [x] Nenhum filtro duplica votos de seções agregadas.
- [x] Testes JavaScript e Python permanecem aprovados.

## Riscos e decisões

- Números de zona e seção podem se repetir em municípios diferentes; por isso,
  as opções dependentes sempre consideram o contexto selecionado.
- A URL usará o código municipal TSE, que é estável e não depende de acentos.
- Selects nativos foram escolhidos pela acessibilidade e pelo tamanho moderado do
  conjunto de opções.
- O resumo filtrado será separado visualmente dos cards oficiais gerais.
- A Issue 09 permanece parcialmente concluída até a inspeção visual; a execução
  da Issue 10 deverá aproveitar a mesma rodada de QA para encerrar ambas.

## Dependências

- **Pré-requisitos:** implementação funcional da Issue 09 e dataset da Issue 08.
- **Desbloqueia:** Issue 11 — homologação ponta a ponta e fluxo de atualização.

## Validação executada

- 20 testes JavaScript aprovados, incluindo pesquisa parcial, busca sem acentos,
  correlação com os filtros e os valores de regressão oficiais.
- 42 testes Python aprovados.
- Sintaxe dos dois módulos JavaScript validada pelo Node.
- URL compartilhável respondeu HTTP 200 em localhost.
- Carregamento real do JSON via HTTP confirmou o recorte `94811/19/81` com um
  registro e quatro votos.
- A captura visual pelo Firefox headless falhou por indisponibilidade do
  compositor gráfico (`RenderCompositorSWGL`) e não gerou imagem.

## Entregas realizadas

- [x] Atualização de `public/index.html`.
- [x] Atualização de `public/assets/styles.css`.
- [x] Atualização de `public/js/data-model.js`.
- [x] Atualização de `public/js/app.js`.
- [x] Ampliação de `tests/web/data-model.test.mjs`.
- [x] Atualização de `docs/SITE_LOCAL.md`.
- [x] Issue atualizada com evidências da execução.

## Pendências

- [ ] Concluir QA visual desktop e móvel em navegador com compositor disponível.
- [ ] Confirmar interações dos selects, limpeza, paginação e restauração da URL
  diretamente no DOM do navegador.
- [ ] Confirmar contraste, zoom, foco e ausência de overflow em viewport móvel.
