#!/usr/bin/env python3
"""Lê o BU oficial do TSE em lotes e mostra métricas de leitura."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.tse_bu import ARCHIVE_NAME, SourceArchiveError, SourceContractError, describe_archive, iter_bu_chunks  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "raw" / ARCHIVE_NAME)
    parser.add_argument("--chunk-size", type=int, default=50_000)
    parser.add_argument("--progress-every", type=int, default=250_000)
    arguments = parser.parse_args()
    if arguments.chunk_size < 1 or arguments.progress_every < 1:
        parser.error("--chunk-size e --progress-every devem ser positivos.")

    try:
        descriptor = describe_archive(arguments.input)
        rows_read = 0
        chunks_read = 0
        for chunk in iter_bu_chunks(arguments.input, arguments.chunk_size):
            rows_read += len(chunk)
            chunks_read += 1
            if rows_read % arguments.progress_every < len(chunk):
                print(f"Linhas lidas: {rows_read}")
    except (SourceArchiveError, SourceContractError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"CSV: {descriptor.csv_name}")
    print(f"Colunas: {len(descriptor.columns)}")
    print(f"Lotes: {chunks_read}")
    print(f"Linhas lidas: {rows_read}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
