# Issue 05 — Normalizar e consolidar dados por seção

**Status:** concluída em 26/10/2026.

## Objetivo

Transformar os registros brutos selecionados na Issue 04 em registros canônicos,
tipados e ordenados por município, zona e seção. A etapa deverá preservar a
rastreabilidade de seções agregadas e impedir contagem duplicada de votos.

## Evidências do arquivo oficial

A inspeção dos registros de Otoniel Andrade no BU oficial encontrou:

| Verificação | Resultado |
| --- | ---: |
| Registros selecionados | 1.225 |
| Chaves únicas por município/zona/seção/candidato | 1.225 |
| Chaves duplicadas | 0 |
| Registros com `QT_VOTOS=0` | 0 |
| Registros sem seção agregada | 1.206 |
| Registros que informam seção agregada | 19 |

Como a fonte atual não contém chaves duplicadas, uma duplicidade futura será
tratada como inconsistência, e não somada automaticamente. Os 19 registros com
seção agregada continuarão como uma única unidade de apuração; seus votos não
serão replicados para a seção agregada.

## Escopo

### Incluído

- Conversão dos registros brutos para uma estrutura Python tipada e imutável.
- Normalização de município, zona, seção, candidato e quantidade de votos.
- Conversão estrita de `QT_VOTOS` para inteiro não negativo.
- Conversão de `DS_SECOES_AGREGADAS` em coleção explícita.
- Definição e validação da chave canônica por seção.
- Detecção de duplicidades antes da publicação.
- Ordenação determinística do conjunto normalizado.
- CLI de inspeção e testes unitários.

### Excluído

- Soma oficial e relatório de qualidade global, pertencentes à Issue 06.
- Geração da planilha XLSX, pertencente à Issue 07.
- Geração do JSON público, pertencente à Issue 08.
- Interface HTML e filtros visuais.

## Modelo canônico implementado

A estrutura imutável `CandidateSectionVotes` foi implementada com os campos:

| Campo | Tipo | Origem/regra |
| --- | --- | --- |
| `cidade` | `str` | `NM_MUNICIPIO`, grafia oficial preservada |
| `codigo_municipio_tse` | `str` | `CD_MUNICIPIO` |
| `zona_eleitoral` | `str` | `NR_ZONA`, sem preenchimento artificial |
| `secao` | `str` | `NR_SECAO`, sem preenchimento artificial |
| `secoes_agregadas` | `tuple[str, ...]` | vazio para `#NULO#`; valores oficiais nos demais casos |
| `votos` | `int` | `QT_VOTOS`, inteiro maior ou igual a zero |
| `numero_candidato` | `str` | `25222` |
| `nome_candidato` | `str` | `OTONIEL ANDRADE` |
| `cargo` | `str` | `Deputado Estadual` |
| `uf` | `str` | `TO` |
| `ano_eleicao` | `int` | `2026` |
| `turno` | `int` | `1` |

### Chave canônica

`ano_eleicao + turno + uf + codigo_municipio_tse + zona_eleitoral + secao + numero_candidato`

`secoes_agregadas` não integra a chave: é um atributo auditável da unidade de
apuração representada pela seção principal.

## Plano de execução

- [x] Criar `src/section_votes.py` com a estrutura imutável
  `CandidateSectionVotes` e os erros específicos de normalização.
- [x] Implementar a conversão de uma linha bruta selecionada em registro
  canônico, exigindo todos os campos necessários.
- [x] Converter `QT_VOTOS`, ano e turno de forma estrita, rejeitando valores
  vazios, não numéricos ou negativos.
- [x] Preservar zona e seção como strings, sem adicionar zeros ou alterar o valor
  publicado pelo TSE.
- [x] Interpretar `DS_SECOES_AGREGADAS=#NULO#` como coleção vazia e preservar os
  identificadores oficiais quando houver agregação.
- [x] Implementar consolidação por chave que rejeite qualquer duplicidade com
  diagnóstico contendo município, zona e seção.
- [x] Ordenar deterministicamente por cidade, código do município, zona e seção,
  usando valores numéricos de zona/seção apenas como chave de ordenação.
- [x] Criar `scripts/inspect_section_votes.py` para mostrar quantidade de
  registros normalizados, duplicidades e seções agregadas, sem gerar XLSX/JSON.
- [x] Adicionar `tests/test_section_votes.py` cobrindo conversão, agregação,
  valores inválidos, duplicidade e ordenação.
- [x] Validar o conjunto oficial e registrar as evidências nesta issue.
- [x] Atualizar o contrato de dados caso `secoes_agregadas` seja incorporado ao
  esquema público, incrementando sua versão de forma explícita.

## Regras de normalização

1. Não alterar a grafia oficial de `NM_MUNICIPIO`; apenas rejeitar valor vazio.
2. Converter campos numéricos de identificação para strings canônicas sem
   preenchimento artificial de zeros.
3. Converter `QT_VOTOS` para inteiro decimal e rejeitar valores negativos.
4. Tratar somente o marcador exato `#NULO#` como ausência de seção agregada.
5. Não criar uma nova linha para `DS_SECOES_AGREGADAS`, pois isso duplicaria os
   votos que pertencem à unidade agregada de apuração.
6. Não somar registros com a mesma chave; interromper o processamento para
   investigação da fonte.
7. Não descartar registros com zero voto caso apareçam em futuras publicações;
   zero é um valor válido, embora não ocorra no recurso homologado atual.

## Casos de teste

- [x] Registro bruto válido é convertido para o modelo canônico.
- [x] `QT_VOTOS` é convertido de string para inteiro.
- [x] Votos zero são aceitos e votos negativos são rejeitados.
- [x] Votos vazios ou não numéricos são rejeitados.
- [x] Zona e seção permanecem strings e não recebem zeros artificiais.
- [x] `#NULO#` gera `secoes_agregadas=()`.
- [x] Uma seção agregada é preservada sem duplicar o registro ou seus votos.
- [x] Campo obrigatório ausente ou vazio produz erro explícito.
- [x] Duas linhas com a mesma chave canônica produzem erro de duplicidade.
- [x] Registros fora de ordem resultam em saída determinística.

## Critérios de aceite

- [x] Todo registro selecionado produz exatamente um registro canônico.
- [x] A quantidade de votos é representada como inteiro não negativo.
- [x] Município, zona e seção mantêm os identificadores oficiais do TSE.
- [x] Seções agregadas são preservadas sem replicar votos.
- [x] Duplicidades são rejeitadas antes das etapas de exportação.
- [x] A saída é determinística e independente da ordem do CSV.
- [x] Os testes cobrem entradas válidas, limites e falhas de contrato.
- [x] A validação oficial mantém 1.225 registros únicos e identifica 19 registros
  com seção agregada.

## Riscos e decisões

- Uma seção agregada não permite atribuir parte dos votos a cada seção original;
  a interface deverá indicar a agregação sem inventar uma distribuição.
- Somar duplicidades automaticamente poderia dobrar votos por erro de fonte;
  portanto, o comportamento seguro é falhar.
- A ordenação textual de municípios pode variar conforme regras de locale. Para
  reprodutibilidade, será usada uma chave explícita e independente do sistema.
- A Issue 06 será responsável por conferir totais e demais invariantes globais;
  esta etapa apenas tipa, preserva e organiza os registros.

## Dependências

- **Pré-requisitos:** Issues 01 a 04.
- **Desbloqueia:** Issue 06 — verificações de qualidade e totalização.

## Validação executada

- 16 testes da suíte completa aprovados.
- BU oficial: 1.225 registros normalizados em 89 municípios.
- 19 registros preservam informação de seção agregada sem replicação de votos.
- Nenhuma chave canônica duplicada foi encontrada.
- Contrato de dados atualizado para a versão 1.1.0.

## Entregas realizadas

- [x] `src/section_votes.py`
- [x] `scripts/inspect_section_votes.py`
- [x] `tests/test_section_votes.py`
- [x] Contrato de dados atualizado para a versão 1.1.0.
- [x] Issue atualizada com as evidências da execução.
