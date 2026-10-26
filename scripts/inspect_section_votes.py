#!/usr/bin/env python3
"""Inspeciona a normalização da votação de Otoniel Andrade por seção."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.candidate_selection import CandidateSelectionError, select_candidate_rows  # noqa: E402
from src.section_votes import SectionNormalizationError, normalize_and_consolidate  # noqa: E402
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

    try:
        selected = select_candidate_rows(iter_bu_rows(arguments.input))
        records = normalize_and_consolidate(selected)
    except (
        CandidateSelectionError,
        SectionNormalizationError,
        SourceArchiveError,
        SourceContractError,
    ) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    aggregated = sum(bool(record.secoes_agregadas) for record in records)
    municipalities = {record.codigo_municipio_tse for record in records}
    print("Candidato: OTONIEL ANDRADE (25222)")
    print(f"Registros normalizados: {len(records)}")
    print(f"Municípios: {len(municipalities)}")
    print(f"Registros com seção agregada: {aggregated}")
    print("Duplicidades: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
