# Issue 06 — Criar verificações de qualidade e totalização

**Status:** concluída em 26/10/2026.

## Objetivo

Validar o conjunto canônico produzido pela Issue 05, calcular o total confiável
de votos de Otoniel Andrade e gerar um relatório auditável. Nenhum artefato para
XLSX ou web poderá ser produzido quando uma verificação obrigatória falhar.

## Referência homologada

A execução atual sobre o BU oficial validado produziu os seguintes valores de
referência:

| Métrica | Valor |
| --- | ---: |
| Registros por seção/unidade de apuração | 1.225 |
| Municípios com registro do candidato | 89 |
| Registros com seção agregada | 19 |
| Chaves duplicadas | 0 |
| Total de votos | 7.180 |
| Menor quantidade de votos em um registro | 1 |
| Maior quantidade de votos em um registro | 45 |

Esses valores serão usados como baseline do recurso homologado, sem substituir
as validações estruturais. O módulo de qualidade deve aceitar outros valores
esperados explicitamente para não esconder futuras republicações do TSE.

## Escopo

### Incluído

- Validação global dos registros canônicos.
- Conferência de identidade eleitoral e consistência entre município e código.
- Nova verificação de unicidade das chaves antes da exportação.
- Totalização geral e reconciliação com subtotais.
- Comparação opcional com uma baseline esperada para o recurso oficial.
- Relatório de qualidade serializável em JSON.
- CLI de validação ponta a ponta e testes unitários.

### Excluído

- Geração da planilha XLSX, pertencente à Issue 07.
- Dataset JSON destinado ao frontend, pertencente à Issue 08.
- Interface HTML, filtros e publicação.
- Consulta ou combinação com fontes eleitorais não oficiais.

## Modelo de relatório implementado

O relatório deverá conter, no mínimo:

```json
{
  "status": "aprovado",
  "versao_contrato": "1.1.0",
  "candidato": {
    "numero": "25222",
    "nome": "OTONIEL ANDRADE",
    "cargo": "Deputado Estadual",
    "uf": "TO",
    "ano_eleicao": 2026,
    "turno": 1
  },
  "metricas": {
    "registros": 1225,
    "municipios": 89,
    "registros_com_secao_agregada": 19,
    "total_votos": 7180
  },
  "verificacoes": [],
  "fonte": {},
  "gerado_em": "<ISO 8601>"
}
```

O relatório de validação não substitui o dataset público da Issue 08.

## Plano de execução

- [x] Criar `src/quality_report.py` com estruturas imutáveis para baseline,
  resultado das verificações e relatório final.
- [x] Implementar erro específico de qualidade que identifique a regra, a chave
  e o valor causador da falha.
- [x] Validar que o conjunto não está vazio e contém somente Otoniel
  Andrade/25222, no cargo, UF, ano e turno contratados.
- [x] Verificar novamente a unicidade da chave canônica como defesa antes das
  exportações.
- [x] Validar que cada código de município está associado a um único nome e que
  os campos de cidade, zona e seção não estão vazios.
- [x] Validar votos inteiros e não negativos, além de impedir que uma seção seja
  listada como agregada a ela mesma.
- [x] Calcular total geral, quantidade de registros, municípios e registros com
  agregação.
- [x] Calcular subtotais por município e reconciliar a soma desses subtotais com
  o total geral, falhando em qualquer divergência.
- [x] Implementar comparação opcional com a baseline homologada de 1.225
  registros, 89 municípios, 19 agregações e 7.180 votos.
- [x] Incorporar ao relatório os metadados da Issue 02 quando o arquivo
  `.metadata.json` estiver disponível, incluindo URL e SHA-512 validado.
- [x] Criar `scripts/validate_candidate_votes.py` para executar aquisição já
  disponível, leitura, seleção, normalização e qualidade em uma única cadeia.
- [x] Permitir que a CLI grave o relatório JSON de forma atômica, sem publicar
  um relatório parcial quando houver falha.
- [x] Adicionar `tests/test_quality_report.py` com casos válidos e violações de
  cada invariante relevante.
- [x] Executar toda a suíte e validar o relatório contra o BU oficial.
- [x] Atualizar esta issue com os itens concluídos, resultados e impedimentos.

## Verificações obrigatórias

1. O conjunto contém ao menos um registro.
2. Todos os registros pertencem ao mesmo candidato, cargo, UF, eleição e turno.
3. Cada chave canônica ocorre exatamente uma vez.
4. Todo voto é inteiro e maior ou igual a zero.
5. Cada código municipal possui um único nome oficial no conjunto.
6. Município, código, zona e seção possuem valores válidos.
7. Nenhuma seção agregada referencia a própria seção principal.
8. A soma dos votos por município coincide com a soma direta dos registros.
9. O total geral coincide com a soma de todos os subtotais municipais.
10. Quando fornecida, cada métrica da baseline coincide com o relatório calculado.

## Casos de teste

- [x] Conjunto válido gera relatório aprovado e total correto.
- [x] Conjunto vazio é rejeitado.
- [x] Identidade eleitoral divergente é rejeitada.
- [x] Chave canônica duplicada é rejeitada.
- [x] Votos negativos ou de tipo inválido são rejeitados.
- [x] Mesmo código municipal associado a nomes diferentes é rejeitado.
- [x] Cidade, zona ou seção vazia é rejeitada.
- [x] Autorrelacionamento em seção agregada é rejeitado.
- [x] Subtotais municipais são reconciliados com o total geral.
- [x] Baseline divergente produz erro indicando a métrica incorreta.
- [x] Relatório JSON é determinístico, exceto pelo horário de geração.
- [x] Falha de validação não deixa arquivo de relatório parcial.

## Critérios de aceite

- [x] Nenhuma exportação posterior recebe registros que falharam na qualidade.
- [x] O total é calculado exclusivamente a partir dos registros oficiais
  normalizados, sem valores manuais.
- [x] O relatório contém métricas, verificações, versão do contrato e proveniência.
- [x] A baseline é configurável e não está embutida no validador reutilizável.
- [x] A execução no recurso homologado confirma 7.180 votos em 1.225 registros e
  89 municípios.
- [x] Todos os testes unitários e de integração do projeto permanecem aprovados.

## Riscos e decisões

- Ausência de uma linha do candidato em determinada seção não significa
  necessariamente dado faltante: o BU pode omitir candidatos com zero voto.
- O total de 7.180 votos é uma referência do arquivo homologado; uma nova versão
  oficial deverá atualizar a baseline de forma explícita e auditável.
- O horário torna o relatório variável. Comparações determinísticas deverão
  ignorar ou injetar esse campo nos testes.
- O relatório deve registrar falhas sem alterar os dados de origem.
- O processo interromperá antes das Issues 07 e 08 se qualquer verificação
  obrigatória ou baseline configurada falhar.

## Dependências

- **Pré-requisitos:** Issues 01 a 05.
- **Desbloqueia:** Issues 07 e 08 — geração de XLSX e dataset web.

## Validação executada

- 29 testes da suíte completa aprovados.
- Relatório oficial com status `aprovado`.
- 1.225 registros reconciliados em 89 municípios.
- Total confirmado de 7.180 votos.
- 19 registros com informação de seção agregada.
- Relatório JSON relido e validado após escrita atômica.

## Entregas realizadas

- [x] `src/quality_report.py`
- [x] `scripts/validate_candidate_votes.py`
- [x] `tests/test_quality_report.py`
- [x] `reports/quality_report.json`
- [x] Issue atualizada com evidências da execução.
