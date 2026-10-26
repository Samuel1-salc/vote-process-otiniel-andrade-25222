# Aquisição do Boletim de Urna do TSE

## Finalidade

O script `scripts/fetch_tse_bu_to_2026.py` obtém o ZIP oficial do Boletim de
Urna de Tocantins, 1º turno de 2026, e só o publica localmente quando o hash
SHA-512 calculado confere com o hash distribuído pelo TSE.

## Execução

```bash
python3 scripts/fetch_tse_bu_to_2026.py
```

Por padrão, os artefatos são gravados em `data/raw/`, diretório ignorado pelo Git.
Para escolher outro destino, passe-o como primeiro argumento:

```bash
python3 scripts/fetch_tse_bu_to_2026.py --output-dir /caminho/para/dados
```

## Artefatos gerados

- `bweb_1t_TO_051020261403.zip`: download oficial validado.
- `bweb_1t_TO_051020261403.zip.sha512`: hash fornecido pelo TSE.
- `bweb_1t_TO_051020261403.zip.metadata.json`: proveniência, hashes, horário da
  aquisição, versão do contrato e nome do CSV interno.

Em caso de erro de rede, hash divergente, ZIP inválido ou CSV interno ausente, o
script encerra com erro antes de copiar qualquer arquivo para o destino.
