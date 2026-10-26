from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.quality_report import (
    QualityBaseline,
    QualityValidationError,
    validate_candidate_votes,
    write_quality_report,
)
from src.section_votes import CandidateSectionVotes


def record(**changes: object) -> CandidateSectionVotes:
    base = CandidateSectionVotes(
        cidade="NATIVIDADE",
        codigo_municipio_tse="94811",
        zona_eleitoral="19",
        secao="81",
        secoes_agregadas=(),
        votos=4,
        numero_candidato="25222",
        nome_candidato="OTONIEL ANDRADE",
        cargo="Deputado Estadual",
        uf="TO",
        ano_eleicao=2026,
        turno=1,
    )
    return replace(base, **changes)


class QualityReportTest(unittest.TestCase):
    def test_valid_set_produces_approved_report_and_total(self) -> None:
        records = [record(), record(secao="82", votos=3)]
        report = validate_candidate_votes(records, generated_at="2026-10-26T00:00:00Z")
        self.assertEqual(report.status, "aprovado")
        self.assertEqual(report.metrics.total_votes, 7)
        self.assertEqual(report.municipality_subtotals["94811"]["votos"], 7)

    def test_rejects_empty_set(self) -> None:
        with self.assertRaisesRegex(QualityValidationError, "conjunto_nao_vazio"):
            validate_candidate_votes([])

    def test_rejects_identity_mismatch(self) -> None:
        with self.assertRaisesRegex(QualityValidationError, "identidade_eleitoral"):
            validate_candidate_votes([record(numero_candidato="99999")])

    def test_rejects_duplicate_key(self) -> None:
        item = record()
        with self.assertRaisesRegex(QualityValidationError, "chave_unica"):
            validate_candidate_votes([item, item])

    def test_rejects_invalid_votes(self) -> None:
        for value in (-1, "4"):
            with self.subTest(value=value), self.assertRaisesRegex(
                QualityValidationError, "votos_validos"
            ):
                validate_candidate_votes([record(votos=value)])  # type: ignore[arg-type]

    def test_rejects_conflicting_municipality_names(self) -> None:
        with self.assertRaisesRegex(QualityValidationError, "municipio_consistente"):
            validate_candidate_votes([record(), record(secao="82", cidade="OUTRO NOME")])

    def test_rejects_empty_location_field(self) -> None:
        with self.assertRaisesRegex(QualityValidationError, "campos_obrigatorios"):
            validate_candidate_votes([record(zona_eleitoral="")])

    def test_rejects_self_aggregated_section(self) -> None:
        with self.assertRaisesRegex(QualityValidationError, "secao_agregada"):
            validate_candidate_votes([record(secoes_agregadas=("81",))])

    def test_rejects_baseline_mismatch(self) -> None:
        baseline = QualityBaseline(1, 1, 0, 999)
        with self.assertRaisesRegex(QualityValidationError, "total_votes"):
            validate_candidate_votes([record()], baseline=baseline)

    def test_rejects_source_hash_mismatch(self) -> None:
        source = {"hash_esperado": "a", "hash_calculado": "b"}
        with self.assertRaisesRegex(QualityValidationError, "proveniencia"):
            validate_candidate_votes([record()], source=source)

    def test_json_is_deterministic_with_fixed_timestamp(self) -> None:
        timestamp = "2026-10-26T00:00:00Z"
        first = validate_candidate_votes([record()], generated_at=timestamp).to_json()
        second = validate_candidate_votes([record()], generated_at=timestamp).to_json()
        self.assertEqual(first, second)

    def test_atomic_writer_creates_valid_report(self) -> None:
        report = validate_candidate_votes([record()], generated_at="2026-10-26T00:00:00Z")
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "nested" / "report.json"
            write_quality_report(report, destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), report.to_json())
            self.assertEqual(list(destination.parent.glob("*.tmp")), [])

    def test_validation_failure_does_not_create_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "report.json"
            with self.assertRaises(QualityValidationError):
                report = validate_candidate_votes([])
                write_quality_report(report, destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
