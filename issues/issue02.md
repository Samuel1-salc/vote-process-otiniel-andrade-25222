# Issue 02 — Implementar aquisição e validação do arquivo oficial

**Status:** concluída em 26/10/2026.

## Entrega

- Script reprodutível: `scripts/fetch_tse_bu_to_2026.sh`.
- Instruções: `docs/AQUISICAO_BU_TSE.md`.
- Validações: download do hash oficial, SHA-512, integridade do ZIP e presença do
  CSV previsto no contrato.
- Proveniência: arquivo de metadados JSON emitido junto aos artefatos.

## Aceite

- [x] Obtém o ZIP e o hash exclusivamente no CDN oficial do TSE.
- [x] Interrompe a publicação quando o hash não confere.
- [x] Verifica a integridade do ZIP e o CSV interno esperado.
- [x] Preserva URL, hashes e data de aquisição em JSON.
- [x] Permite definir um diretório de saída sem alterar o código.
