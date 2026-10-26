from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.quality_report import validate_candidate_votes
from src.section_votes import CandidateSectionVotes
from src.web_dataset import (
    WebDatasetError,
    build_web_dataset,
    publish_web_dataset_atomic,
    serialize_web_dataset,
    sha256_bytes,
    validate_web_dataset,
    verify_published_dataset,
)


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


def report_for(records: list[CandidateSectionVotes]):
    return validate_candidate_votes(
        records,
        source={
            "versao_contrato": "1.1.0",
            "fonte": "TSE — Boletim de Urna",
            "url_origem": "https://example.invalid/bu.zip",
            "algoritmo_hash": "SHA-512",
            "hash_calculado": "abc123",
        },
        generated_at="2026-10-26T00:00:00Z",
    )


class WebDatasetTest(unittest.TestCase):
    def test_valid_document_reconciles_and_preserves_types(self) -> None:
        records = [record(), record(secao="82", votos=3, secoes_agregadas=("83",))]
        document = build_web_dataset(
            records,
            report_for(records),
            generated_at="2026-10-26T00:00:00Z",
        )
        validate_web_dataset(document)
        decoded = json.loads(serialize_web_dataset(document).decode("utf-8"))
        self.assertEqual(decoded["resumo"]["total_votos"], 7)
        self.assertIsInstance(decoded["registros"][0]["zona"], str)
        self.assertIsInstance(decoded["registros"][0]["votos"], int)
        self.assertEqual(decoded["registros"][1]["secoes_agregadas"], ["83"])

    def test_serialization_is_deterministic_and_utf8(self) -> None:
        records = [record(cidade="SÃO VALÉRIO")]
        report = report_for(records)
        first = build_web_dataset(records, report, generated_at="2026-10-26T00:00:00Z")
        second = build_web_dataset(records, report, generated_at="2026-10-26T00:00:00Z")
        first_bytes = serialize_web_dataset(first)
        self.assertEqual(first_bytes, serialize_web_dataset(second))
        self.assertIn("SÃO VALÉRIO".encode(), first_bytes)
        self.assertNotIn(b"\\u00e3", first_bytes)

    def test_records_are_sorted_deterministically(self) -> None:
        records = [
            record(cidade="PALMAS", codigo_municipio_tse="73440", secao="1"),
            record(secao="100"),
            record(secao="9"),
        ]
        document = build_web_dataset(records, report_for(records), generated_at="2026-10-26T00:00:00Z")
        self.assertEqual(
            [(item["cidade"], item["secao"]) for item in document["registros"]],
            [("NATIVIDADE", "9"), ("NATIVIDADE", "100"), ("PALMAS", "1")],
        )

    def test_rejects_unapproved_report(self) -> None:
        records = [record()]
        report = replace(report_for(records), status="reprovado")
        with self.assertRaises(WebDatasetError):
            build_web_dataset(records, report)

    def test_rejects_report_mismatch(self) -> None:
        first = record()
        with self.assertRaises(WebDatasetError):
            build_web_dataset([first, record(secao="82")], report_for([first]))

    def test_publish_writes_verified_json_and_checksum(self) -> None:
        records = [record()]
        document = build_web_dataset(records, report_for(records), generated_at="2026-10-26T00:00:00Z")
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory) / "data.json"
            checksum = publish_web_dataset_atomic(document, dataset)
            checksum_path = dataset.with_name("data.json.sha256")
            verified = verify_published_dataset(dataset, checksum_path)
            self.assertEqual(verified, document)
            self.assertEqual(checksum, sha256_bytes(dataset.read_bytes()))
            self.assertEqual(list(dataset.parent.glob("*.tmp")), [])

    def test_detects_invalid_json_and_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory) / "data.json"
            checksum = Path(directory) / "data.json.sha256"
            dataset.write_text("{", encoding="utf-8")
            checksum.write_text(f"{sha256_bytes(dataset.read_bytes())}  data.json\n", encoding="ascii")
            with self.assertRaisesRegex(WebDatasetError, "JSON publicado"):
                verify_published_dataset(dataset, checksum)
            dataset.write_text("{}", encoding="utf-8")
            checksum.write_text("0" * 64 + "  data.json\n", encoding="ascii")
            with self.assertRaisesRegex(WebDatasetError, "Checksum"):
                verify_published_dataset(dataset, checksum)

    def test_failure_does_not_create_artifacts(self) -> None:
        records = [record()]
        report = replace(report_for(records), status="reprovado")
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory) / "data.json"
            with self.assertRaises(WebDatasetError):
                document = build_web_dataset(records, report)
                publish_web_dataset_atomic(document, dataset)
            self.assertFalse(dataset.exists())
            self.assertFalse(dataset.with_name("data.json.sha256").exists())


if __name__ == "__main__":
    unittest.main()
