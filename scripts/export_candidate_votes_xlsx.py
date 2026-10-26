#!/usr/bin/env python3
"""Gera a planilha XLSX validada de Otoniel Andrade/25222."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.candidate_selection import CandidateSelectionError, select_candidate_rows  # noqa: E402
from src.quality_report import OFFICIAL_BASELINE, QualityValidationError, validate_candidate_votes  # noqa: E402
from src.section_votes import SectionNormalizationError, normalize_and_consolidate  # noqa: E402
from src.tse_bu import (  # noqa: E402
    ARCHIVE_NAME,
    CONTRACT_VERSION,
    SOURCE_URL,
    SourceArchiveError,
    SourceContractError,
    iter_bu_rows,
    sha512_file,
)
from src.xlsx_export import XlsxExportError, export_workbook_atomic  # noqa: E402


def _source_metadata(archive: Path, metadata_path: Path | None) -> dict[str, object]:
    candidate = metadata_path or archive.with_name(f"{archive.name}.metadata.json")
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return {
        "versao_contrato": CONTRACT_VERSION,
        "fonte": "TSE — Boletim de Urna 2026, TO, 1º turno",
        "url_origem": SOURCE_URL,
        "algoritmo_hash": "SHA-512",
        "hash_calculado": sha512_file(archive),
        "arquivo": archive.name,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "raw" / ARCHIVE_NAME)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "artifacts" / "otoniel_andrade_25222_TO_2026.xlsx",
    )
    arguments = parser.parse_args()
    try:
        rows = select_candidate_rows(iter_bu_rows(arguments.input))
        records = normalize_and_consolidate(rows)
        report = validate_candidate_votes(
            records,
            baseline=OFFICIAL_BASELINE,
            source=_source_metadata(arguments.input, arguments.metadata),
        )
        export_workbook_atomic(records, report, arguments.output)
    except (
        CandidateSelectionError,
        json.JSONDecodeError,
        OSError,
        QualityValidationError,
        SectionNormalizationError,
        SourceArchiveError,
        SourceContractError,
        XlsxExportError,
    ) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"Planilha: {arguments.output}")
    print(f"Registros: {report.metrics.records}")
    print(f"Total de votos: {report.metrics.total_votes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
