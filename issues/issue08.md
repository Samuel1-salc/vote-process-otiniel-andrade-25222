# Issue 08 — Preparar o dataset para consumo web

**Status:** concluída em 26/10/2026.

## Objetivo

Gerar um dataset JSON estático, validado e auditável para consumo direto pelo
frontend. O arquivo deverá conter os 1.225 registros por unidade de apuração,
metadados eleitorais, total de 7.180 votos e proveniência oficial, sem repetir
informações globais em cada linha.

## Escopo

### Incluído

- Definição e versionamento do esquema JSON público.
- Exportação dos registros canônicos da Issue 05.
- Bloqueio da exportação por relatório de qualidade não aprovado.
- Metadados de candidato, eleição, fonte, contrato e totalização.
- Representação explícita de seções agregadas.
- Serialização UTF-8 determinística e escrita atômica.
- Checksum SHA-256 do artefato JSON publicado.
- Testes de esquema, conteúdo, integridade e reprodutibilidade.

### Excluído

- Componentes HTML, estilos e filtros visuais, pertencentes às Issues 09 e 10.
- API, banco de dados ou servidor de aplicação.
- Atualização automática em tempo real.
- Geração ou alteração do XLSX da Issue 07.

## Arquivos previstos

- Dataset: `public/data/votos_otoniel_25222_TO_2026.json`
- Checksum: `public/data/votos_otoniel_25222_TO_2026.json.sha256`
- Esquema: `schemas/votos-candidato.schema.json`

O nome do dataset será estável para permitir referência direta pelo frontend.

## Estrutura proposta

```json
{
  "versao_schema": "1.0.0",
  "versao_contrato": "1.1.0",
  "gerado_em": "<ISO 8601>",
  "candidato": {
    "numero": "25222",
    "nome": "OTONIEL ANDRADE",
    "cargo": "Deputado Estadual"
  },
  "eleicao": {
    "ano": 2026,
    "turno": 1,
    "uf": "TO"
  },
  "resumo": {
    "registros": 1225,
    "municipios": 89,
    "registros_com_secao_agregada": 19,
    "total_votos": 7180
  },
  "fonte": {
    "nome": "TSE — Boletim de Urna 2026, TO, 1º turno",
    "url": "<URL oficial>",
    "algoritmo_hash": "SHA-512",
    "hash_arquivo_origem": "<hash validado>"
  },
  "registros": [
    {
      "cidade": "NATIVIDADE",
      "codigo_municipio_tse": "94811",
      "zona": "19",
      "secao": "81",
      "secoes_agregadas": [],
      "votos": 4
    }
  ]
}
```

Dados globais do candidato e da eleição não serão repetidos em cada registro.

## Tipos e invariantes públicas

| Campo | Tipo | Regra |
| --- | --- | --- |
| `cidade` | string | Nome oficial do TSE, não vazio |
| `codigo_municipio_tse` | string | Identificador decimal preservado como texto |
| `zona` | string | Identificador decimal preservado como texto |
| `secao` | string | Identificador decimal preservado como texto |
| `secoes_agregadas` | array de strings | Vazio ou identificadores oficiais, sem duplicar votos |
| `votos` | inteiro | Maior ou igual a zero |

A ordem dos registros deverá ser a mesma saída determinística da Issue 05:
município, código, zona e seção.

## Plano de execução

- [x] Criar `schemas/votos-candidato.schema.json` com o contrato público e
  bloqueio de propriedades inesperadas onde aplicável.
- [x] Criar `src/web_dataset.py` com o modelo do documento e serialização JSON.
- [x] Exigir `QualityReport` com status `aprovado` antes da exportação.
- [x] Reconciliar quantidade de registros, municípios, agregações e votos com o
  relatório aprovado antes de serializar.
- [x] Remover dos registros a repetição de candidato, cargo, UF, ano e turno,
  mantendo essas informações no cabeçalho do documento.
- [x] Preservar cidade e identificadores como strings e votos como inteiros.
- [x] Representar `secoes_agregadas` como array, sem criar registros adicionais.
- [x] Serializar em UTF-8 com caracteres legíveis, chaves estáveis e quebra de
  linha final.
- [x] Implementar escrita atômica do JSON no mesmo sistema de arquivos.
- [x] Calcular SHA-256 sobre os bytes finais e publicar o arquivo `.sha256`
  também de forma atômica.
- [x] Criar `scripts/export_candidate_votes_json.py` para executar leitura,
  seleção, normalização, qualidade e exportação numa única cadeia.
- [x] Reabrir o JSON publicado e validar tipos, métricas e checksum antes de
  considerar a exportação concluída.
- [x] Adicionar `tests/test_web_dataset.py` cobrindo esquema, reconciliação,
  determinismo, UTF-8, agregações, checksum e falhas atômicas.
- [x] Executar a suíte completa dentro da `.venv`.
- [x] Gerar o dataset oficial em `public/data/` e registrar tamanho e checksum.
- [x] Atualizar esta issue marcando somente os itens efetivamente concluídos.

## Regras de publicação

1. A exportação só ocorre após aprovação da Issue 06.
2. O JSON deve ser válido e reabrível pela biblioteca padrão do Python.
3. A soma de `registros[].votos` deve ser exatamente `resumo.total_votos`.
4. A quantidade de registros deve coincidir com `resumo.registros`.
5. O conjunto de códigos municipais deve coincidir com `resumo.municipios`.
6. A quantidade de arrays não vazios em `secoes_agregadas` deve coincidir com o
   resumo de agregações.
7. O checksum publicado deve corresponder exatamente aos bytes do JSON final.
8. Falhas não podem deixar JSON ou checksum parcial no destino.
9. Nenhum valor vindo da fonte será inserido futuramente no HTML por `innerHTML`;
   a Issue 09 deverá usar APIs seguras de texto.

## Casos de teste

- [x] Documento válido atende ao esquema público.
- [x] O recurso homologado produz 1.225 registros e 7.180 votos.
- [x] Os registros abrangem 89 municípios.
- [x] Exatamente 19 registros possuem seções agregadas.
- [x] Identificadores permanecem strings após round-trip JSON.
- [x] Votos permanecem inteiros após round-trip JSON.
- [x] Nomes com acentos são gravados diretamente em UTF-8.
- [x] Ordem dos registros é determinística.
- [x] Serialização com horário fixo produz bytes idênticos.
- [x] Relatório não aprovado impede a publicação.
- [x] Divergência entre registros e relatório impede a publicação.
- [x] JSON truncado ou inválido é detectado na verificação pós-gravação.
- [x] Checksum divergente é detectado.
- [x] Falha não deixa arquivos temporários ou artefatos parciais.

## Critérios de aceite

- [x] JSON público contém 1.225 registros e soma exatamente 7.180 votos.
- [x] Resumo informa 89 municípios e 19 registros com agregação.
- [x] Metadados identificam candidato, eleição, contrato e fonte oficial.
- [x] O checksum SHA-256 acompanha o dataset e foi verificado.
- [x] O arquivo pode ser carregado diretamente por `fetch()` num site estático.
- [x] O esquema público está documentado e versionado.
- [x] A exportação é determinística quando o horário é fixado.
- [x] Todos os testes existentes e novos permanecem aprovados na `.venv`.

## Riscos e decisões

- O JSON será legível, não minimizado. Com 1.225 registros, a simplicidade e a
  auditabilidade têm prioridade sobre uma pequena economia de bytes.
- O SHA-256 verifica o artefato web; ele não substitui o SHA-512 do ZIP oficial
  do TSE, que continuará registrado na proveniência.
- A data de geração é o único campo esperado a variar entre execuções sobre a
  mesma fonte. Testes determinísticos usarão horário injetado.
- O frontend deverá interpretar seções agregadas como uma única unidade de
  apuração e nunca repartir seus votos.
- Alterações incompatíveis no JSON exigirão incremento da versão do esquema.

## Dependências

- **Pré-requisitos:** Issues 01 a 06 concluídas e relatório de qualidade aprovado.
- **Relacionada:** Issue 07 usa os mesmos registros validados, mas não bloqueia a
  implementação técnica desta exportação.
- **Desbloqueia:** Issue 09 — construção da página HTML de consulta.

## Validação executada

- 42 testes da suíte completa aprovados dentro da `.venv`.
- Dataset final relido e validado após a publicação atômica.
- 1.225 registros, 89 municípios, 19 agregações e 7.180 votos reconciliados.
- Arquivo JSON final com 211.191 bytes.
- SHA-256 verificado:
  `538ba91797834223a13084444e2262d61be6767ec8550805785f6073d37b7bdb`.

## Entregas realizadas

- [x] `schemas/votos-candidato.schema.json`.
- [x] `src/web_dataset.py`.
- [x] `scripts/export_candidate_votes_json.py`.
- [x] `tests/test_web_dataset.py`.
- [x] `public/data/votos_otoniel_25222_TO_2026.json`.
- [x] `public/data/votos_otoniel_25222_TO_2026.json.sha256`.
- [x] Issue atualizada com evidências da execução.
