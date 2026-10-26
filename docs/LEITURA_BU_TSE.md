# Leitura escalável do Boletim de Urna

O módulo `src/tse_bu.py` lê diretamente o CSV dentro do ZIP oficial: não extrai o
arquivo e não o carrega integralmente na memória. A leitura usa Latin-1, o
delimitador `;` e valida os campos exigidos pelo contrato antes de entregar dados.

## Verificação manual

```bash
python3 scripts/inspect_tse_bu_to_2026.py
```

O tamanho de lote pode ser ajustado sem alterar o código:

```bash
python3 scripts/inspect_tse_bu_to_2026.py --chunk-size 100000
```

Para processamento posterior, use `iter_bu_rows()` quando uma linha por vez for
suficiente ou `iter_bu_chunks()` quando uma etapa precisar operar em lotes limitados.
