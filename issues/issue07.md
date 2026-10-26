# Issue 07 — Gerar a planilha XLSX de distribuição

**Status:** concluída em 26/10/2026.

## Objetivo

Gerar uma planilha XLSX auditável com a votação validada de Otoniel Andrade por
município, zona e seção. O arquivo deverá preservar identificadores eleitorais
como texto, oferecer filtros nativos, mostrar total dinâmico e registrar a
proveniência oficial em uma aba separada.

## Decisão de dependência

O projeto não possui atualmente uma biblioteca para gerar XLSX. A implementação
usará `openpyxl` dentro de um ambiente virtual próprio do projeto.

- Ambiente: `.venv/`
- Dependência: `openpyxl`, com a versão efetivamente validada fixada no arquivo
  de dependências.
- Execução: sempre por `.venv/bin/python` ou após ativar o ambiente.
- Isolamento: `.venv/` será ignorado pelo Git.

A biblioteca não será instalada globalmente.

## Escopo

### Incluído

- Criação e documentação do ambiente virtual Python.
- Exportação dos 1.225 registros validados para XLSX.
- Filtros nativos por cidade, código municipal, zona, seção e agregação.
- Total geral e total dinâmico compatível com filtros da planilha.
- Formatação de zona e seção como texto.
- Aba de metadados e proveniência.
- Escrita atômica do arquivo final.
- Testes estruturais reabrindo o XLSX gerado.

### Excluído

- Dataset JSON para o frontend, pertencente à Issue 08.
- Interface HTML e filtros no navegador.
- Edição manual ou importação de alterações feitas na planilha.
- Macros, fórmulas externas, dashboards ou gráficos.

## Estrutura da pasta de trabalho

### Aba `Votos por seção`

Informações de identificação e resumo no topo, seguidas pela tabela:

| Coluna | Tipo no XLSX | Regra |
| --- | --- | --- |
| Cidade | texto | Nome oficial do TSE |
| Código Município TSE | texto | Identificador auditável |
| Zona Eleitoral | texto | Não converter para número |
| Seção | texto | Não converter para número |
| Seções Agregadas | texto | Vazio quando não houver agregação |
| Votos | número inteiro | Formato numérico sem casas decimais |

Recursos previstos:

- Cabeçalho destacado e primeira linha de dados congelada.
- AutoFilter em todas as colunas da tabela.
- Larguras de coluna legíveis e alinhamento coerente.
- Total geral visível.
- Fórmula `SUBTOTAL` para recalcular os votos quando filtros forem aplicados.
- Indicação clara de que votos de seções agregadas não foram distribuídos entre
  as seções de origem.

### Aba `Metadados`

Deverá registrar:

- Candidato, número, cargo, UF, ano e turno.
- Quantidade de registros, municípios, agregações e total de votos.
- Versão do contrato de dados.
- URL oficial do TSE.
- Algoritmo e hash SHA-512 do arquivo processado.
- Data/hora de aquisição e de geração da planilha.
- Status do relatório da Issue 06.
- Observação sobre seções agregadas.

## Nome e destino

Arquivo previsto:

`artifacts/otoniel_andrade_25222_TO_2026.xlsx`

O diretório poderá ser substituído por argumento da CLI. Um arquivo temporário
será criado no mesmo diretório e promovido por troca atômica somente após a
validação do workbook.

## Plano de execução

- [x] Adicionar `.venv/` ao `.gitignore`.
- [x] Criar o ambiente com `python3 -m venv .venv`.
- [x] Atualizar `pip` dentro do ambiente virtual e instalar `openpyxl`.
- [x] Registrar a versão validada em `requirements.txt` ou arquivo equivalente.
- [x] Criar `src/xlsx_export.py` com geração da pasta de trabalho, estilos e
  escrita atômica.
- [x] Exigir um `QualityReport` aprovado antes de iniciar a exportação.
- [x] Conferir se quantidade de registros, municípios e total de votos recebidos
  coincidem com o relatório aprovado.
- [x] Construir a aba `Votos por seção` com identificadores textuais, filtros,
  congelamento, formatação e total dinâmico.
- [x] Construir a aba `Metadados` com proveniência e métricas da Issue 06.
- [x] Neutralizar textos iniciados por `=`, `+`, `-` ou `@` antes de gravá-los,
  evitando interpretação indevida como fórmula.
- [x] Criar `scripts/export_candidate_votes_xlsx.py` para executar leitura,
  seleção, normalização, qualidade e exportação numa única cadeia.
- [x] Reabrir o XLSX gerado com `openpyxl` antes da publicação para confirmar
  integridade, abas, cabeçalhos, quantidade de linhas e células essenciais.
- [x] Adicionar `tests/test_xlsx_export.py` com testes de conteúdo, tipos,
  filtros, fórmula, metadados, escrita atômica e bloqueio sem qualidade aprovada.
- [x] Executar toda a suíte dentro da `.venv`.
- [x] Gerar o XLSX oficial em `artifacts/` e registrar tamanho e validações.
- [x] Atualizar esta issue marcando apenas os itens efetivamente concluídos.

## Regras de segurança e integridade

1. A exportação só pode receber relatório de qualidade com status `aprovado`.
2. As métricas do relatório devem coincidir com os registros fornecidos.
3. Zona, seção, código municipal e número do candidato permanecem texto.
4. `votos` é a única coluna eleitoral gravada como número.
5. Seções agregadas são apresentadas como informação auditável, sem duplicação.
6. Valores textuais potencialmente interpretáveis como fórmula são escapados.
7. Nenhum arquivo parcial permanece no destino após erro.
8. O arquivo final é reaberto e inspecionado antes de ser considerado válido.

## Casos de teste

- [x] Workbook válido contém exatamente as abas previstas.
- [x] A tabela possui 1.225 linhas de dados no recurso homologado.
- [x] Cidade, código municipal, zona e seção são gravados como texto.
- [x] Votos são gravados como inteiros.
- [x] Seções agregadas aparecem numa única linha, sem replicação de votos.
- [x] Filtro automático cobre todas as colunas e linhas de dados.
- [x] Fórmula `SUBTOTAL` referencia integralmente a coluna de votos.
- [x] Congelamento de painéis mantém o cabeçalho visível.
- [x] Aba de metadados contém URL, SHA-512, contrato e total de 7.180 votos.
- [x] Texto semelhante a fórmula é neutralizado.
- [x] Relatório não aprovado impede a criação do XLSX.
- [x] Divergência entre registros e relatório impede a criação do XLSX.
- [x] Falha durante a geração não deixa arquivo parcial.
- [x] Arquivo final pode ser reaberto pela biblioteca sem aviso de corrupção.

## Critérios de aceite

- [x] O XLSX contém os 1.225 registros validados e total de 7.180 votos.
- [x] Os filtros funcionam por cidade, zona e seção.
- [x] O total dinâmico responde aos filtros no Excel ou LibreOffice.
- [x] Identificadores eleitorais não perdem sua representação textual.
- [x] As 19 unidades com seção agregada são identificáveis sem votos duplicados.
- [x] A proveniência oficial está disponível na aba `Metadados`.
- [x] A exportação é determinística, exceto por horários e propriedades do XLSX.
- [x] Todos os testes existentes e novos permanecem aprovados na `.venv`.

## Riscos e decisões

- Fórmulas são recalculadas pelo aplicativo de planilha; o valor armazenado pode
  não estar disponível até a primeira abertura. O total validado também será
  gravado como valor estático nos metadados.
- Excel e LibreOffice podem renderizar estilos de forma ligeiramente diferente;
  o aceite funcional será baseado em dados, filtros, fórmulas e estrutura.
- Não será distribuído o diretório `.venv`; apenas a especificação da dependência.
- Alterações futuras de versão do `openpyxl` exigirão nova execução dos testes de
  abertura e estrutura do arquivo.

## Dependências

- **Pré-requisitos:** Issues 01 a 06 concluídas e relatório de qualidade aprovado.
- **Desbloqueia:** distribuição da planilha e continuidade da Issue 08.

## Validação executada

- Ambiente virtual criado com Python 3.12.3.
- `openpyxl 3.1.5` instalado e fixado em `requirements.txt`.
- 34 testes da suíte completa aprovados dentro da `.venv`.
- Workbook oficial reaberto com sucesso após a publicação atômica.
- Arquivo com 1.225 registros, 7.180 votos e 19 unidades agregadas.
- Filtro `A6:F1231` e fórmula `=SUBTOTAL(109,F7:F1231)` confirmados.
- Tamanho do artefato gerado: 40.880 bytes.

## Entregas realizadas

- [x] `.venv/` local e ignorado pelo Git.
- [x] `requirements.txt` com `openpyxl==3.1.5`.
- [x] `src/xlsx_export.py`.
- [x] `scripts/export_candidate_votes_xlsx.py`.
- [x] `tests/test_xlsx_export.py`.
- [x] `docs/EXPORTACAO_XLSX.md`.
- [x] `artifacts/otoniel_andrade_25222_TO_2026.xlsx`.
- [x] Issue atualizada com evidências da execução.
