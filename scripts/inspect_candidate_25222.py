#!/usr/bin/env python3
"""Inspeciona a seleção de Otoniel Andrade/25222 no BU oficial."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.candidate_selection import CandidateSelectionError, select_candidate_rows  # noqa: E402
from src.tse_bu import (  # noqa: E402
    ARCHIVE_NAME,
    SourceArchiveError,
    SourceContractError,
    iter_bu_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / ARCHIVE_NAME,
        help="ZIP oficial validado na Issue 02.",
    )
    arguments = parser.parse_args()

    records = 0
    municipalities: set[str] = set()
    try:
        for row in select_candidate_rows(iter_bu_rows(arguments.input)):
            records += 1
            municipalities.add(row["CD_MUNICIPIO"])
    except (CandidateSelectionError, SourceArchiveError, SourceContractError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print("Candidato: OTONIEL ANDRADE (25222)")
    print(f"Registros selecionados: {records}")
    print(f"Municípios: {len(municipalities)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
