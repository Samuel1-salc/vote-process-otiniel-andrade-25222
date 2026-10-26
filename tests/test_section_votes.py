from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.section_votes import (
    DuplicateSectionError,
    SectionNormalizationError,
    normalize_and_consolidate,
    normalize_section_row,
)

FIXTURES = Path(__file__).parent / "fixtures"


def valid_source() -> dict[str, str]:
    document = json.loads(
        (FIXTURES / "tse-bu-to-2026-candidato-25222.valido.json").read_text(encoding="utf-8")
    )
    return {field: str(value) for field, value in document["fonte"].items()}


class SectionVotesTest(unittest.TestCase):
    def test_normalizes_valid_record(self) -> None:
        record = normalize_section_row(valid_source())
        self.assertEqual(record.cidade, "NATIVIDADE")
        self.assertEqual(record.zona_eleitoral, "19")
        self.assertEqual(record.secao, "81")
        self.assertEqual(record.votos, 4)
        self.assertEqual(record.secoes_agregadas, ())

    def test_accepts_zero_votes(self) -> None:
        row = dict(valid_source(), QT_VOTOS="0")
        self.assertEqual(normalize_section_row(row).votos, 0)

    def test_rejects_invalid_vote_values(self) -> None:
        for value in ("-1", "", "quatro"):
            with self.subTest(value=value), self.assertRaises(SectionNormalizationError):
                normalize_section_row(dict(valid_source(), QT_VOTOS=value))

    def test_preserves_aggregated_sections_without_duplicating_record(self) -> None:
        row = dict(valid_source(), DS_SECOES_AGREGADAS="057, 58")
        records = normalize_and_consolidate([row])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].secoes_agregadas, ("57", "58"))
        self.assertEqual(records[0].votos, 4)

    def test_rejects_missing_required_field(self) -> None:
        row = valid_source()
        del row["NR_SECAO"]
        with self.assertRaisesRegex(SectionNormalizationError, "NR_SECAO"):
            normalize_section_row(row)

    def test_rejects_duplicate_canonical_key(self) -> None:
        row = valid_source()
        with self.assertRaises(DuplicateSectionError):
            normalize_and_consolidate([row, dict(row)])

    def test_sorts_deterministically_by_city_zone_and_section(self) -> None:
        base = valid_source()
        later_section = dict(base, NR_SECAO="100")
        earlier_section = dict(base, NR_SECAO="9")
        other_city = dict(
            base,
            NM_MUNICIPIO="PALMAS",
            CD_MUNICIPIO="73440",
            NR_SECAO="1",
        )
        records = normalize_and_consolidate([other_city, later_section, earlier_section])
        self.assertEqual(
            [(record.cidade, record.secao) for record in records],
            [("NATIVIDADE", "9"), ("NATIVIDADE", "100"), ("PALMAS", "1")],
        )


if __name__ == "__main__":
    unittest.main()
