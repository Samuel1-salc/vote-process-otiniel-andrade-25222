# Issue 01 — Definir contrato dos dados de entrada e saída

**Status:** concluída em 26/10/2026. Contrato homologado em `docs/CONTRATO_DADOS_TSE_BU_V1.md`.

## Objetivo

Especificar, versionar e validar o contrato que liga o Boletim de Urna oficial do
TSE ao dataset tratado, à planilha XLSX e ao dataset do site. O contrato deve
impedir que uma alteração no layout da fonte gere uma apuração incorreta ou
silenciosamente incompleta.

## Contexto fixo

| Item | Valor |
| --- | --- |
| Eleição | Eleições Gerais 2026 — 1º turno |
| UF | Tocantins (`TO`) |
| Cargo | Deputado Estadual |
| Candidato | Otoniel Andrade |
| Número | `25222` |
| Fonte | Boletim de Urna (BU), CSV oficial do TSE |
| Saídas | Dataset tratado, XLSX e JSON para HTML |

## Escopo

### Incluído

- Identificar o recurso oficial do TSE e o hash SHA-2 associado.
- Inspecionar o cabeçalho, a codificação, o delimitador e tipos do CSV de BU de TO.
- Mapear os campos fonte indispensáveis para localizar a eleição, o cargo, o
  candidato, o município, a zona, a seção e a quantidade de votos.
- Definir o esquema canônico de saída e as regras de tipo, normalização e chave.
- Especificar os metadados de rastreabilidade que acompanharão cada publicação.
- Registrar critérios de aceite e exemplos de registros válidos e inválidos.

### Excluído

- Download, conferência do hash e leitura em lote do arquivo (Issue 02 e 03).
- Implementação do filtro do candidato (Issue 04).
- Transformação, exportação XLSX, API/dataset web ou interface HTML.

## Plano de execução

1. Confirmar a URL do recurso `TO — Boletim de Urna — Primeiro turno — 05.10.2026`
   e a URL/valor do respectivo arquivo SHA-2 no Portal de Dados Abertos do TSE.
2. Coletar uma amostra controlada do CSV e registrar: nome dos campos, ordem,
   delimitador, codificação, formato de números e indicação de valores nulos.
3. Relacionar cada campo necessário ao seu uso no sistema. Nenhum filtro deverá
   depender exclusivamente do nome do candidato; o número `25222` será obrigatório.
4. Escrever o esquema de saída por seção, incluindo tipos e formatos de
   `cidade`, `zona_eleitoral`, `secao` e `votos`.
5. Definir a chave lógica da saída: `eleicao + turno + uf + codigo_municipio + zona_eleitoral + secao + numero_candidato`.
6. Definir metadados obrigatórios de proveniência: URL fonte, nome do recurso,
   hash esperado e calculado, data/hora de processamento, versão do contrato e
   total de registros.
7. Criar uma especificação versionada e exemplos de fixture mínima para ser usada
   pelos testes das Issues 03 a 06.
8. Revisar o contrato contra um segundo registro/amostra e obter aceite antes da
   implementação do processamento.

## Contrato proposto

### Entrada: CSV oficial do BU

Os nomes exatos serão confirmados no passo 2. O processador deverá exigir campos
equivalentes aos seguintes conceitos:

| Conceito | Uso | Regra |
| --- | --- | --- |
| Ano/eleição | Confirmar pleito 2026 | Obrigatório |
| Turno | Restringir ao 1º turno | Obrigatório |
| UF | Restringir a `TO` | Obrigatório |
| Cargo | Restringir a Deputado Estadual | Obrigatório |
| Número do candidato | Selecionar `25222` | Obrigatório; tratar como texto |
| Nome do candidato | Conferência humana | Obrigatório após seleção |
| Município/código IBGE | Exibir e identificar a cidade | Código preferido como chave |
| Zona eleitoral | Filtro e chave de seção | Tratar como texto preservando zeros |
| Seção eleitoral | Filtro e chave de seção | Tratar como texto preservando zeros |
| Quantidade de votos | Totalização | Inteiro não negativo |

Se qualquer conceito obrigatório estiver ausente, duplicado de modo ambíguo ou com
tipo incompatível, o processamento deverá falhar com diagnóstico explícito.

### Saída: registro canônico por seção

```json
{
  "cidade": "PALMAS",
  "codigo_municipio": "73458",
  "zona_eleitoral": "0029",
  "secao": "0142",
  "votos": 0,
  "numero_candidato": "25222",
  "nome_candidato": "OTONIEL ANDRADE",
  "cargo": "DEPUTADO ESTADUAL",
  "uf": "TO",
  "ano_eleicao": 2026,
  "turno": 1
}
```

Regras:

- `votos` é inteiro, maior ou igual a zero e nunca texto formatado.
- `numero_candidato`, `zona_eleitoral` e `secao` permanecem strings para preservar
  zeros à esquerda.
- `cidade` é o nome exibível; `codigo_municipio` é a referência estável quando
  disponível na fonte.
- A saída não terá dados de outros candidatos ou cargos.
- A combinação da chave lógica não pode ocorrer mais de uma vez após consolidação.

### Metadados de publicação

```json
{
  "versao_contrato": "1.0.0",
  "fonte": "TSE — Boletim de Urna 2026, TO, 1º turno",
  "url_origem": "<URL oficial do CSV>",
  "sha256_esperado": "<hash publicado pelo TSE>",
  "sha256_calculado": "<hash do arquivo processado>",
  "processado_em": "<ISO 8601>",
  "total_registros": 0,
  "total_votos": 0
}
```

## Critérios de aceite

- [x] O recurso do TSE e o arquivo de hash correspondente estão identificados por URL.
- [x] O layout real do CSV está documentado, sem campos presumidos como definitivos.
- [x] Cada conceito obrigatório possui campo fonte, tipo e regra de validação.
- [x] O filtro usa cargo e número `25222`; o nome é apenas uma validação adicional.
- [x] O esquema de saída, a chave lógica e os metadados estão definidos.
- [x] Há ao menos uma fixture/documentação de exemplo para testes posteriores.
- [x] Um CSV que não cumpra o contrato falha antes de gerar XLSX ou JSON público.

## Riscos e decisões em aberto

- O layout real foi homologado na versão 1.0.0 do contrato; novas publicações
  exigem nova inspeção antes do processamento.
- Zona e seção são numéricas na fonte e serão exibidas como strings sem
  preenchimento artificial de zeros.
- Se o BU registrar mais de uma linha para a mesma chave de seção, a regra de
  consolidação será definida na Issue 05, com evidência da fonte.

## Dependências e próximos passos

- **Pré-requisito:** nenhum.
- **Desbloqueia:** Issues 02, 03, 04, 05, 06, 07 e 08.
- **Próxima issue sugerida:** Issue 02 — aquisição e validação do arquivo oficial.
