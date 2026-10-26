# Issue 04 — Implementar seleção eleitoral do candidato

**Status:** concluída em 26/10/2026.

## Objetivo

Selecionar, em fluxo, somente os registros oficiais de votação nominal de
**Otoniel Andrade**, número **25222**, para **Deputado Estadual**, no Tocantins,
1º turno das Eleições Gerais de 2026. A seleção deverá falhar explicitamente
quando a fonte estiver vazia, inconsistente ou incompatível com o contrato.

## Contexto eleitoral fixo

| Campo do TSE | Valor esperado |
| --- | --- |
| `ANO_ELEICAO` | `2026` |
| `NR_TURNO` | `1` |
| `CD_ELEICAO` | `6259` |
| `DS_ELEICAO` | `Eleições Gerais Estaduais 2026` |
| `SG_UF` | `TO` |
| `CD_CARGO_PERGUNTA` | `7` |
| `DS_CARGO_PERGUNTA` | `Deputado Estadual` |
| `CD_TIPO_VOTAVEL` | `1` |
| `DS_TIPO_VOTAVEL` | `Nominal` |
| `NR_VOTAVEL` | `25222` |
| `NM_VOTAVEL` | `OTONIEL ANDRADE` |

O número, a eleição e o cargo são os identificadores determinantes. O nome do
candidato e as descrições textuais serão usados como verificações adicionais de
consistência.

## Escopo

### Incluído

- Representação tipada dos critérios eleitorais fixos.
- Filtro de registros diretamente sobre o iterador da Issue 03.
- Validação de código e descrição da eleição, cargo e tipo votável.
- Validação da correspondência entre o número `25222` e o nome do candidato.
- Erro explícito quando nenhum registro válido for encontrado.
- CLI de inspeção para conferir a seleção no arquivo oficial.
- Testes unitários para casos válidos, descartados e inconsistentes.

### Excluído

- Normalização de cidade, zona, seção e votos, pertencente à Issue 05.
- Consolidação de possíveis registros duplicados ou seções agregadas.
- Totalização oficial e relatório de qualidade, pertencentes à Issue 06.
- Geração de XLSX, JSON público ou interface HTML.

## Plano de execução

- [x] Criar `src/candidate_selection.py` com uma estrutura imutável contendo os
  critérios oficiais de eleição, cargo, tipo votável, UF e candidato.
- [x] Implementar um predicado de seleção que compare os códigos determinantes
  antes das descrições textuais e mantenha os registros no formato bruto do TSE.
- [x] Implementar um iterador que receba as linhas de `iter_bu_rows()` e entregue
  somente registros correspondentes a Otoniel Andrade/25222.
- [x] Rejeitar registros em que o número `25222` esteja associado a nome, cargo,
  eleição, turno ou UF incompatíveis.
- [x] Diferenciar linhas legítimas não correspondentes de inconsistências que
  devem interromper o processamento.
- [x] Criar `scripts/inspect_candidate_25222.py` para percorrer o BU oficial e
  informar quantidade de registros e municípios encontrados, sem gerar artefato.
- [x] Adicionar testes em `tests/test_candidate_selection.py` usando as fixtures
  válida e inválida criadas na Issue 01.
- [x] Executar os testes e validar a seleção contra o arquivo oficial completo.
- [x] Registrar resultados e decisões nesta issue antes de marcá-la como concluída.

## Regras de seleção

1. Descartar silenciosamente linhas que não pertençam à eleição estadual `6259`,
   ao Tocantins, ao 1º turno ou ao cargo de Deputado Estadual.
2. Dentro do escopo eleitoral correto, descartar linhas não nominais e números
   de outros candidatos.
3. Para `NR_VOTAVEL=25222`, exigir `NM_VOTAVEL=OTONIEL ANDRADE` e todas as
   descrições previstas pelo contrato.
4. Entregar a linha bruta sem converter tipos ou modificar textos.
5. Ao terminar a leitura, produzir erro se nenhuma linha válida tiver sido
   encontrada.

## Casos de teste

- Linha completa de Otoniel Andrade é selecionada.
- Linha de outro candidato no mesmo cargo é descartada.
- Linha de Otoniel para eleição, turno, UF ou cargo diferente é descartada.
- Voto branco, nulo ou de legenda é descartado.
- Número `25222` associado a nome diferente produz erro de contrato.
- Código e descrição de cargo incompatíveis produzem erro.
- Fonte sem qualquer registro válido produz erro de candidato não encontrado.
- O iterador continua operando em fluxo, sem acumular todas as linhas na memória.

## Critérios de aceite

- [x] Apenas registros de votação nominal do candidato 25222 são entregues.
- [x] Todos os campos eleitorais fixos são verificados conforme o contrato vigente.
- [x] Inconsistências de identidade ou descrição interrompem o processamento.
- [x] Ausência total do candidato produz mensagem de erro clara.
- [x] O filtro funciona sobre iteradores e preserva a leitura escalável.
- [x] Testes unitários cobrem seleção, descarte, inconsistência e resultado vazio.
- [x] A execução no BU oficial encontra a referência observada de 1.225 registros
  em 89 municípios; a totalização dos votos permanece responsabilidade da Issue 06.

## Riscos e decisões

- O nome não será usado isoladamente para selecionar o candidato, evitando
  ambiguidades de grafia.
- Valores numéricos chegam do CSV como strings e serão comparados como strings
  nesta etapa; conversões pertencem à normalização.
- A contagem oficial observada serve como teste de regressão para este recurso,
  mas não deve substituir as validações do contrato em futuras republicações.
- Seções agregadas não serão consolidadas implicitamente nesta issue.

## Dependências

- **Pré-requisitos:** Issues 01, 02 e 03.
- **Desbloqueia:** Issue 05 — normalização e consolidação por seção.

## Validação executada

- 9 testes da suíte completa aprovados.
- BU oficial: 1.225 registros selecionados em 89 municípios.
- A seleção foi executada diretamente sobre o iterador do ZIP, sem materializar
  o conjunto completo na memória.

## Entregas previstas

- `src/candidate_selection.py`
- `scripts/inspect_candidate_25222.py`
- `tests/test_candidate_selection.py`
- Atualização de `issues/issue04.md` com evidências da execução
