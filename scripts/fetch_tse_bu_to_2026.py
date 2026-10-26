#!/usr/bin/env python3
"""Baixa e valida o Boletim de Urna oficial do TSE para TO/2026."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.tse_bu import SourceArchiveError, acquire_official_archive  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw",
        help="Diretório dos artefatos validados (padrão: data/raw).",
    )
    arguments = parser.parse_args()
    try:
        metadata = acquire_official_archive(arguments.output_dir)
    except SourceArchiveError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    print(f"Arquivo validado e publicado em: {arguments.output_dir}")
    print(f"SHA-512: {metadata['hash_calculado']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
