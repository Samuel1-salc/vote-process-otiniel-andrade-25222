# Planejamento do Core — Consulta de Votos por Seção

## Contexto

Construir o núcleo de uma aplicação que consulta a votação de **Otoniel Andrade**, candidato a **Deputado Estadual**, número **25222**, no **Tocantins**, nas Eleições Gerais de **2026**. A aplicação usará exclusivamente os dados oficiais de Boletim de Urna (BU) publicados pelo Tribunal Superior Eleitoral (TSE).

O resultado processado será disponibilizado em uma planilha XLSX e exibido numa página HTML, com filtros por cidade, zona eleitoral e seção.

## Fonte oficial prevista

- Conjunto: [Resultados 2026 — Boletim de Urna](https://dadosabertos.tse.jus.br/pt_BR/dataset/resultados-2026-boletim-de-urna)
- Recurso: `TO — Boletim de Urna — Primeiro turno — 05.10.2026` (CSV)
- Integridade: hash SHA-2 publicado pelo TSE para o recurso correspondente
- Escopo: Tocantins, 1º turno, cargo Deputado Estadual, candidato 25222

## Resultado esperado

Cada registro da saída representa a votação do candidato em uma seção eleitoral:

| Cidade | Zona eleitoral | Seção | Votos |
| --- | ---: | ---: | ---: |

O site deverá exibir a tabela e o total de votos compatível com os filtros ativos.

## Steps / Issues

### Issue 01 — Definir contrato dos dados de entrada e saída

**Status:** concluída em 26/10/2026. Consulte `docs/CONTRATO_DADOS_TSE_BU_V1.md`.

Documentar o arquivo oficial de origem, os campos necessários, a codificação, o separador, a tipagem e o esquema final do conjunto tratado e do XLSX.

**Entrega:** contrato de dados versionado.

### Issue 02 — Implementar aquisição e validação do arquivo oficial

**Status:** concluída em 26/10/2026. Consulte `scripts/fetch_tse_bu_to_2026.py`.

Criar o mecanismo para obter o CSV do BU do Tocantins e validar sua integridade contra o hash SHA-2 publicado pelo TSE, preservando metadados de origem e data de processamento.

**Entrega:** rotina reprodutível de download, validação e registro de proveniência.

### Issue 03 — Implementar leitura escalável do CSV

**Status:** concluída em 26/10/2026. Consulte `src/tse_bu.py`.

Ler o arquivo oficial em lotes/streaming, sem depender da abertura em Excel e sem carregar o arquivo integralmente na memória.

**Entrega:** leitor validado para arquivos grandes do TSE.

### Issue 04 — Implementar seleção eleitoral do candidato

**Status:** concluída em 26/10/2026. Consulte `src/candidate_selection.py`.

Filtrar os dados por UF `TO`, cargo `Deputado Estadual`, número de candidato `25222` e turno/eleição definidos. Incluir validações para impedir resultados vazios ou inconsistentes por mudança de layout, cargo ou eleição.

**Entrega:** conjunto reduzido exclusivamente à votação de Otoniel Andrade.

### Issue 05 — Normalizar e consolidar dados por seção

**Status:** concluída em 26/10/2026. Consulte `src/section_votes.py`.

Transformar os registros selecionados no formato canônico `cidade`, `zona_eleitoral`, `secao` e `votos`. Padronizar textos, zeros à esquerda quando aplicável, ordenar a listagem e definir como tratar duplicidades ou seções sem voto.

**Entrega:** dataset tratado por cidade, zona e seção.

### Issue 06 — Criar verificações de qualidade e totalização

**Status:** concluída em 26/10/2026. Consulte `src/quality_report.py`.

Implementar testes e regras de consistência: campos obrigatórios, votos numéricos e não negativos, unicidade da chave de seção e conferência do total geral com a soma dos registros processados.

**Entrega:** relatório de validação e total confiável de votos.

### Issue 07 — Gerar a planilha XLSX de distribuição

**Status:** concluída em 26/10/2026. Consulte `src/xlsx_export.py`.

Exportar o dataset tratado para uma planilha XLSX de uma aba, com cabeçalho, formatação básica, filtros e total geral. Incluir uma aba ou metadados de origem, sem alterar os dados eleitorais.

**Entrega:** arquivo XLSX pronto para consulta e auditoria.

### Issue 08 — Preparar o dataset para consumo web

**Status:** concluída em 26/10/2026. Consulte `src/web_dataset.py`.

Gerar uma versão leve e determinística dos dados para o frontend (por exemplo, JSON), acompanhada de eleição, candidato, fonte TSE, hash validado, data de geração e total geral.

**Entrega:** artefato estático para a página HTML.

### Issue 09 — Construir a página HTML de consulta

**Status:** parcialmente concluída em 26/10/2026; QA visual pendente.

Criar a interface da listagem com identificação explícita do candidato, cargo, eleição e origem oficial. Exibir tabela paginada ou virtualizada, estado sem resultados e data de atualização.

**Entrega:** página HTML funcional de visualização.

### Issue 10 — Implementar filtros e total dinâmico

**Status:** parcialmente concluída em 26/10/2026; QA visual/interativa pendente.

Adicionar filtros combináveis por cidade, zona eleitoral e seção. Atualizar tabela, contagem de linhas e total de votos de forma imediata e acessível; permitir limpar filtros e preservar formatos numéricos.

**Entrega:** busca interativa por localidade eleitoral.

### Issue 11 — Testar rastreabilidade e publicar o fluxo de atualização

Executar testes ponta a ponta, comparar amostras com o BU oficial e documentar como reexecutar a importação quando houver republicação oficial ou atualização de dados.

**Entrega:** checklist de homologação e instruções operacionais.

## Dependências principais

`01 → 02 → 03 → 04 → 05 → 06 → 07 e 08 → 09 → 10 → 11`

As issues 07 e 08 podem avançar em paralelo após a Issue 06. A Issue 09 pode ser iniciada com dados de exemplo, mas só deve ser homologada após a Issue 08.

## Fora do escopo inicial

- Apuração de outros candidatos, cargos, UFs ou eleições
- Alteração manual de dados eleitorais
- Integração com fontes não oficiais
- Login, administração de usuários ou edição via interface
