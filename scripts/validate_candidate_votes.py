#!/usr/bin/env python3
"""Valida e totaliza a votação oficial de Otoniel Andrade/25222."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.candidate_selection import CandidateSelectionError, select_candidate_rows  # noqa: E402
from src.quality_report import (  # noqa: E402
    OFFICIAL_BASELINE,
    QualityValidationError,
    validate_candidate_votes,
    write_quality_report,
)
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


def _load_source_metadata(archive: Path, metadata_path: Path | None) -> dict[str, object]:
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
    parser.add_argument("--metadata", type=Path, help="Metadados gerados pela aquisição.")
    parser.add_argument("--report", type=Path, help="Destino opcional do relatório JSON.")
    parser.add_argument("--no-baseline", action="store_true", help="Não compara a baseline homologada.")
    arguments = parser.parse_args()

    try:
        rows = select_candidate_rows(iter_bu_rows(arguments.input))
        records = normalize_and_consolidate(rows)
        source = _load_source_metadata(arguments.input, arguments.metadata)
        report = validate_candidate_votes(
            records,
            baseline=None if arguments.no_baseline else OFFICIAL_BASELINE,
            source=source,
        )
        if arguments.report:
            write_quality_report(report, arguments.report)
    except (
        CandidateSelectionError,
        json.JSONDecodeError,
        OSError,
        QualityValidationError,
        SectionNormalizationError,
        SourceArchiveError,
        SourceContractError,
    ) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1

    print(f"Status: {report.status}")
    print(f"Registros: {report.metrics.records}")
    print(f"Municípios: {report.metrics.municipalities}")
    print(f"Total de votos: {report.metrics.total_votes}")
    if arguments.report:
        print(f"Relatório: {arguments.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
