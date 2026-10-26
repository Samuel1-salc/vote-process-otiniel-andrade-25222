# Contrato de Dados — Boletim de Urna TSE/TO 2026 (v1.1.0)

## Fonte homologada

| Item | Valor |
| --- | --- |
| Portal | https://dadosabertos.tse.jus.br/pt_BR/dataset/resultados-2026-boletim-de-urna |
| Arquivo | `bweb_1t_TO_051020261403.zip` |
| URL CSV/ZIP | https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_TO_051020261403.zip |
| Hash oficial | https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_TO_051020261403.zip.sha512 |
| Algoritmo | SHA-512 |
| Hash homologado | `b936b450693c00741226bd1b6c09843c6671e41abafa393ef31606a7038272011b9030ec8d62a8f61d7ff31f532b7979321cac456bef3b44925e0b00026bc614` |
| Conteúdo do ZIP | `bweb_1t_TO_051020261403.csv` e `_leiame-boletimurnaweb.pdf` |

O hash foi conferido em 26/10/2026 contra o arquivo baixado. Apenas o CSV é
entrada do processador; o PDF é documentação auxiliar.

## Formato real do CSV

- Codificação: ISO-8859-1 (Latin-1).
- Delimitador: ponto e vírgula (`;`).
- Aspas: campos textuais aparecem entre aspas duplas.
- Cabeçalho: primeira linha.
- Datas: `DT_GERACAO` usa `DD/MM/AAAA`; campos de data/hora usam
  `AAAA-MM-DD HH:MM:SS`.
- Valores ausentes: podem ser representados por `#NULO#`.

O leitor deve interpretar o arquivo em Latin-1 antes de comparar textos com
acentos. Não é permitido supor UTF-8.

## Seleção obrigatória

Uma linha só é elegível quando atender simultaneamente aos valores abaixo:

| Campo | Valor exigido |
| --- | --- |
| `ANO_ELEICAO` | `2026` |
| `NR_TURNO` | `1` |
| `SG_UF` | `TO` |
| `CD_ELEICAO` | `6259` |
| `DS_ELEICAO` | `Eleições Gerais Estaduais 2026` |
| `CD_CARGO_PERGUNTA` | `7` |
| `DS_CARGO_PERGUNTA` | `Deputado Estadual` |
| `CD_TIPO_VOTAVEL` | `1` |
| `DS_TIPO_VOTAVEL` | `Nominal` |
| `NR_VOTAVEL` | `25222` |
| `NM_VOTAVEL` | `OTONIEL ANDRADE` |

O número e o cargo são os filtros determinantes. O nome é uma validação de
segurança: divergência entre `NR_VOTAVEL=25222` e o nome acima deve interromper a
execução, em vez de publicar dados.

## Mapeamento de campos

| Campo do BU | Campo canônico | Tipo de saída | Regra |
| --- | --- | --- | --- |
| `NM_MUNICIPIO` | `cidade` | string | Converter de Latin-1; preservar grafia do TSE. |
| `CD_MUNICIPIO` | `codigo_municipio_tse` | string | Converter para string; é código TSE, não declarar como IBGE. |
| `NR_ZONA` | `zona_eleitoral` | string | Converter o inteiro para string sem preenchimento artificial. |
| `NR_SECAO` | `secao` | string | Converter o inteiro para string sem preenchimento artificial. |
| `QT_VOTOS` | `votos` | inteiro | Obrigatório e maior ou igual a zero. |
| `DS_SECOES_AGREGADAS` | `secoes_agregadas` | lista de strings | `#NULO#` vira lista vazia; não replica votos. |
| `NR_VOTAVEL` | `numero_candidato` | string | Deve ser `25222`. |
| `NM_VOTAVEL` | `nome_candidato` | string | Deve ser `OTONIEL ANDRADE`. |
| `DS_CARGO_PERGUNTA` | `cargo` | string | Deve ser `Deputado Estadual`. |
| `SG_UF` | `uf` | string | Deve ser `TO`. |
| `ANO_ELEICAO` | `ano_eleicao` | inteiro | Deve ser `2026`. |
| `NR_TURNO` | `turno` | inteiro | Deve ser `1`. |

## Registro canônico

```json
{
  "cidade": "NATIVIDADE",
  "codigo_municipio_tse": "94811",
  "zona_eleitoral": "19",
  "secao": "81",
  "secoes_agregadas": [],
  "votos": 4,
  "numero_candidato": "25222",
  "nome_candidato": "OTONIEL ANDRADE",
  "cargo": "Deputado Estadual",
  "uf": "TO",
  "ano_eleicao": 2026,
  "turno": 1
}
```

## Chave e validações

A chave de uma linha canônica é:

`CD_ELEICAO + SG_UF + CD_MUNICIPIO + NR_ZONA + NR_SECAO + NR_VOTAVEL`

Antes de gerar qualquer saída pública, o processo deve falhar se:

- o ZIP, o CSV interno ou o hash SHA-512 não forem os esperados;
- faltar qualquer campo do mapeamento;
- o arquivo não usar o cabeçalho ou delimitador homologados;
- uma linha elegível tiver UF, eleição, cargo, tipo votável, número ou nome fora
  dos valores obrigatórios;
- `QT_VOTOS` não for inteiro não negativo;
- houver mais de uma linha para a chave sem regra explícita de consolidação;
- a soma de `votos` não for igual ao total calculado a partir das linhas válidas.

## Metadados obrigatórios de publicação

```json
{
  "versao_contrato": "1.1.0",
  "fonte": "TSE — Boletim de Urna 2026, TO, 1º turno",
  "url_origem": "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_1t_TO_051020261403.zip",
  "algoritmo_hash": "SHA-512",
  "hash_esperado": "b936b450...26bc614",
  "hash_calculado": "<hash completo do arquivo processado>",
  "processado_em": "<ISO 8601>",
  "total_registros": 0,
  "total_votos": 0
}
```

## Compatibilidade

Este contrato vale somente para o recurso homologado. Uma nova publicação do TSE,
novo turno ou mudança de cabeçalho exige nova inspeção e incremento da versão do
contrato antes de ser processada.
