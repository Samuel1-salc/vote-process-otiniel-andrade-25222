# Exportação XLSX

## Preparação

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Geração

Após obter o BU pela Issue 02:

```bash
.venv/bin/python scripts/export_candidate_votes_xlsx.py
```

Para indicar outro ZIP ou destino:

```bash
.venv/bin/python scripts/export_candidate_votes_xlsx.py \
  --input /caminho/bu.zip \
  --output /caminho/resultado.xlsx
```

A exportação executa seleção, normalização e qualidade antes de criar o arquivo.
O XLSX só é publicado após ser reaberto e validado pela própria biblioteca.
