from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.candidate_selection import (
    CandidateIdentityError,
    CandidateNotFoundError,
    CandidateSelectionError,
    is_candidate_row,
    select_candidate_rows,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load_source_fixture(name: str) -> dict[str, str]:
    document = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return {field: str(value) for field, value in document["fonte"].items()}


class CandidateSelectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.valid = load_source_fixture("tse-bu-to-2026-candidato-25222.valido.json")

    def test_selects_expected_candidate(self) -> None:
        self.assertTrue(is_candidate_row(self.valid))
        self.assertEqual(list(select_candidate_rows(iter([self.valid]))), [self.valid])

    def test_discards_other_candidate_and_keeps_streaming(self) -> None:
        other = dict(self.valid, NR_VOTAVEL="22122", NM_VOTAVEL="NILMAR")
        self.assertEqual(list(select_candidate_rows(iter([other, self.valid]))), [self.valid])

    def test_discards_record_outside_election_scope(self) -> None:
        other_election = dict(self.valid, CD_ELEICAO="9999")
        self.assertEqual(
            list(select_candidate_rows(iter([other_election, self.valid]))),
            [self.valid],
        )

    def test_discards_non_nominal_vote(self) -> None:
        blank = dict(
            self.valid,
            CD_TIPO_VOTAVEL="2",
            DS_TIPO_VOTAVEL="Branco",
            NR_VOTAVEL="95",
            NM_VOTAVEL="Branco",
        )
        self.assertEqual(list(select_candidate_rows(iter([blank, self.valid]))), [self.valid])

    def test_rejects_candidate_identity_mismatch(self) -> None:
        invalid = load_source_fixture("tse-bu-to-2026-candidato-25222.invalido.json")
        with self.assertRaises(CandidateIdentityError):
            list(select_candidate_rows(iter([invalid])))

    def test_rejects_description_mismatch(self) -> None:
        invalid = dict(self.valid, DS_CARGO_PERGUNTA="Cargo inesperado")
        with self.assertRaisesRegex(CandidateSelectionError, "Descrição do cargo"):
            list(select_candidate_rows(iter([invalid])))

    def test_rejects_empty_result(self) -> None:
        with self.assertRaises(CandidateNotFoundError):
            list(select_candidate_rows(iter(())))


if __name__ == "__main__":
    unittest.main()
