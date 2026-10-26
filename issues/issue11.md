# Issue 11 — Homologar rastreabilidade e fluxo de atualização

**Status:** planejada — execução adiada antes da implementação para atender à
melhoria solicitada na busca de cidades da Issue 10.

## Objetivo

Consolidar todo o processamento em um fluxo reproduzível, verificar os artefatos
finais contra a fonte oficial, registrar hashes e tamanhos num manifesto de
release e documentar como atualizar os dados com segurança. A mesma execução
deverá concluir a QA visual/interativa pendente das Issues 09 e 10.

## Escopo

### Incluído

- Orquestração das Issues 02 a 10 numa execução única.
- Validação da baseline oficial e de amostras conhecidas do BU.
- Geração coordenada de relatório, XLSX, JSON e cópia pública do XLSX.
- Manifesto de release com hashes, tamanhos, métricas e proveniência.
- Verificador independente dos artefatos publicados.
- Teste de integração do pipeline com dados controlados.
- Documentação operacional de atualização e recuperação.
- QA visual/interativa desktop e móvel pelo portal Maestri.
- Atualização final dos arquivos das Issues 09, 10 e 11.

### Excluído

- Agendamento automático de atualizações.
- Publicação num domínio ou alteração de audiência.
- Suporte a outros candidatos, UFs, cargos ou eleições.
- Alteração manual dos dados oficiais.

## Artefatos da release

- `reports/quality_report.json`
- `artifacts/otoniel_andrade_25222_TO_2026.xlsx`
- `public/data/votos_otoniel_25222_TO_2026.json`
- `public/data/votos_otoniel_25222_TO_2026.json.sha256`
- `public/downloads/otoniel_andrade_25222_TO_2026.xlsx`
- `reports/release_manifest.json`

## Plano de execução

- [ ] Criar `src/release_pipeline.py` para executar seleção, normalização,
  qualidade, XLSX, JSON, cópia pública e manifesto numa única transação lógica.
- [ ] Permitir injetar baseline e horário para testes determinísticos.
- [ ] Calcular SHA-256 e tamanho de todos os artefatos finais.
- [ ] Registrar no manifesto a URL e o SHA-512 da fonte oficial, contrato, schema,
  métricas e horário da release.
- [ ] Criar `scripts/build_release.py` com parâmetros para ZIP, metadados e raiz
  de saída.
- [ ] Criar `scripts/verify_release.py` para reler o manifesto, conferir hashes,
  validar JSON, reabrir XLSX e reconciliar métricas.
- [ ] Garantir que o XLSX público seja byte a byte idêntico ao artefato auditado.
- [ ] Adicionar `tests/test_release_pipeline.py` com pipeline controlado,
  manifesto, hashes, verificação e detecção de adulteração.
- [ ] Executar a suíte Python e JavaScript completa.
- [ ] Gerar novamente a release oficial e executar o verificador independente.
- [ ] Conferir amostras oficiais: Natividade/zona 19/seção 81 com quatro votos,
  Palmas com 359 registros/574 votos e total geral de 7.180 votos.
- [ ] Criar `docs/ATUALIZACAO_DADOS.md` com pré-requisitos, comandos, validações,
  resolução de falhas e rollback seguro.
- [ ] Servir `public/` por HTTP e abrir portal Maestri em desktop.
- [ ] Validar cards, tabela, paginação, filtros, limpeza, URL compartilhável,
  download e console do navegador.
- [ ] Redimensionar o portal para viewport móvel e validar overflow, foco,
  controles, tabela e resumo filtrado.
- [ ] Capturar screenshots desktop e móvel como evidência local de QA.
- [ ] Atualizar Issues 09 e 10 marcando somente a QA efetivamente concluída.
- [ ] Atualizar esta issue com todos os resultados e impedimentos.

## Verificações do manifesto

1. Todos os artefatos listados existem.
2. Tamanho e SHA-256 coincidem com os arquivos presentes.
3. JSON e checksum próprio são válidos.
4. XLSX abre com as duas abas previstas e contém 1.225 registros.
5. XLSX público e XLSX auditado são idênticos.
6. Relatório possui status aprovado e total de 7.180 votos.
7. JSON possui 1.225 registros, 89 municípios e 19 agregações.
8. Proveniência aponta para a URL oficial e o SHA-512 calculado da fonte.

## Casos de teste

- [ ] Pipeline controlado gera todos os artefatos previstos.
- [ ] Manifesto registra hashes e tamanhos corretos.
- [ ] Verificador aceita uma release íntegra.
- [ ] Alteração posterior em JSON, XLSX ou relatório é detectada.
- [ ] Divergência de baseline interrompe a release.
- [ ] Cópia pública do XLSX é idêntica ao artefato original.
- [ ] Horário fixo produz manifesto determinístico.
- [ ] Release oficial confirma todas as métricas homologadas.
- [ ] Amostras de Natividade e Palmas coincidem com o BU processado.
- [ ] Site carrega sem erro no console em desktop e móvel.
- [ ] Filtros e URL compartilhável funcionam no navegador real.

## Critérios de aceite

- [ ] Um comando reproduz todos os artefatos finais a partir do ZIP validado.
- [ ] Um comando independente verifica integralmente a release.
- [ ] Manifesto contém hashes, tamanhos, métricas e proveniência.
- [ ] Toda a suíte automatizada está aprovada.
- [ ] Release oficial confirma 1.225 registros, 89 municípios e 7.180 votos.
- [ ] Atualização operacional está documentada sem etapas implícitas.
- [ ] QA desktop e móvel das Issues 09 e 10 está registrada.
- [ ] Nenhum artefato parcial é promovido após falha.

## Riscos e decisões

- O download oficial é grande; o orquestrador aceitará um ZIP previamente
  validado para evitar download desnecessário durante testes.
- O manifesto usará SHA-256 para artefatos locais e preservará SHA-512 para a
  fonte do TSE.
- A publicação web continuará fora do escopo; a pasta `public/` será considerada
  o pacote estático homologado.
- Em falha, a versão anterior dos artefatos deve permanecer disponível até a
  nova release ser integralmente validada.

## Dependências

- **Pré-requisitos:** Issues 01 a 08 concluídas; Issues 09 e 10 implementadas.
- **Conclui:** fluxo funcional completo do projeto.

## Entregas previstas

- `src/release_pipeline.py`
- `scripts/build_release.py`
- `scripts/verify_release.py`
- `tests/test_release_pipeline.py`
- `reports/release_manifest.json`
- `docs/ATUALIZACAO_DADOS.md`
- Screenshots de QA desktop e móvel
- Atualização das Issues 09, 10 e 11
