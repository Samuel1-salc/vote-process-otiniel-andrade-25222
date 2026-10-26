# Issue 03 — Implementar leitura escalável do CSV

**Status:** concluída em 26/10/2026.

## Objetivo

Consolidar a leitura escalável do BU oficial em Python, processando o CSV
diretamente dentro do ZIP, em codificação Latin-1 e lotes limitados. O leitor
será a base segura para as próximas etapas de filtro, normalização e totalização.

## Escopo

### Incluído

- Validação do ZIP, do CSV interno e do cabeçalho.
- Leitura do CSV em fluxo, sem extração permanente.
- Leitura em lotes de tamanho configurável.
- CLI de inspeção e métricas da leitura.
- Testes unitários do leitor e das falhas de contrato.
- Documentação de uso.

### Excluído

- Download e validação do hash do arquivo, tratados na Issue 02.
- Filtro do candidato Otoniel Andrade, tratado na Issue 04.
- Normalização e consolidação, tratadas na Issue 05.
- Geração de XLSX, JSON público ou interface HTML.

## Plano de execução

- [x] Definir em `src/tse_bu.py` as constantes do CSV interno, codificação,
  delimitador e campos obrigatórios do contrato.
- [x] Implementar `describe_archive()` para validar a existência do ZIP, do CSV
  interno e do cabeçalho antes da leitura.
- [x] Implementar `iter_bu_rows()` para entregar uma linha por vez, sem extrair
  ou carregar integralmente o CSV.
- [x] Implementar `iter_bu_chunks()` com tamanho de lote configurável e
  validação para valores inválidos.
- [x] Criar `scripts/inspect_tse_bu_to_2026.py` para percorrer o arquivo, exibir
  progresso e informar colunas, lotes e linhas lidas.
- [x] Adicionar testes em `tests/test_tse_bu.py` para leitura em lotes e falha
  quando um campo obrigatório estiver ausente.
- [x] Executar o leitor contra o ZIP oficial validado e registrar a contagem
  final desta issue.
- [x] Documentar o uso da leitura em fluxo em `docs/LEITURA_BU_TSE.md`.

## Entregas

- Leitor em fluxo: `src/tse_bu.py`.
- CLI de inspeção: `scripts/inspect_tse_bu_to_2026.py`.
- Testes unitários: `tests/test_tse_bu.py`.
- Instruções: `docs/LEITURA_BU_TSE.md`.

## Critérios de aceite

- [x] O CSV é lido diretamente do ZIP.
- [x] O conteúdo é decodificado como ISO-8859-1.
- [x] O cabeçalho é validado contra os campos obrigatórios do contrato.
- [x] A API permite consumir uma linha por vez ou lotes limitados.
- [x] Um tamanho de lote menor que 1 produz erro explícito.
- [x] Um CSV sem campo obrigatório é rejeitado antes do processamento.
- [x] O arquivo oficial completo pode ser percorrido sem extração permanente.

## Validação executada

- Testes unitários: 2 aprovados.
- Arquivo oficial: 426.458 linhas, 45 colunas, lidas diretamente do ZIP em 5
  lotes de 100.000 linhas (o último lote contém o restante).

## Decisões

- O tamanho padrão de lote é 50.000 linhas e pode ser alterado pela CLI.
- O leitor mantém os valores como strings; conversão de tipos e regras de
  consolidação pertencem às Issues 04 e 05.
- Seções agregadas serão analisadas na Issue 05, sem tratamento implícito no
  leitor de baixo nível.

## Dependências

- **Pré-requisitos:** Issue 01 e Issue 02.
- **Desbloqueia:** Issue 04 — seleção eleitoral do candidato.
