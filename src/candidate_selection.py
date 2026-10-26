"""Seleção dos registros eleitorais de Otoniel Andrade no BU do TSE."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass


class CandidateSelectionError(RuntimeError):
    """Dados eleitorais incompatíveis com os critérios de seleção."""


class CandidateNotFoundError(CandidateSelectionError):
    """Nenhum registro do candidato foi encontrado."""


class CandidateIdentityError(CandidateSelectionError):
    """Número e identidade do candidato são incompatíveis."""


@dataclass(frozen=True)
class CandidateCriteria:
    election_year: str = "2026"
    round_number: str = "1"
    election_code: str = "6259"
    election_description: str = "Eleições Gerais Estaduais 2026"
    state: str = "TO"
    office_code: str = "7"
    office_description: str = "Deputado Estadual"
    votable_type_code: str = "1"
    votable_type_description: str = "Nominal"
    candidate_number: str = "25222"
    candidate_name: str = "OTONIEL ANDRADE"


DEFAULT_CRITERIA = CandidateCriteria()


def _required_value(row: Mapping[str, str], field: str) -> str:
    try:
        return row[field]
    except KeyError as error:
        raise CandidateSelectionError(f"Campo obrigatório ausente: {field}") from error


def _matches_election_scope(row: Mapping[str, str], criteria: CandidateCriteria) -> bool:
    return (
        _required_value(row, "ANO_ELEICAO") == criteria.election_year
        and _required_value(row, "NR_TURNO") == criteria.round_number
        and _required_value(row, "CD_ELEICAO") == criteria.election_code
        and _required_value(row, "SG_UF") == criteria.state
        and _required_value(row, "CD_CARGO_PERGUNTA") == criteria.office_code
    )


def _validate_description(
    row: Mapping[str, str], field: str, expected: str, context: str
) -> None:
    actual = _required_value(row, field)
    if actual != expected:
        raise CandidateSelectionError(
            f"{context} incompatível: esperado {expected!r}, recebido {actual!r}."
        )


def is_candidate_row(
    row: Mapping[str, str], criteria: CandidateCriteria = DEFAULT_CRITERIA
) -> bool:
    """Classifica uma linha, rejeitando inconsistências dentro do pleito-alvo."""
    if not _matches_election_scope(row, criteria):
        return False

    _validate_description(
        row,
        "DS_ELEICAO",
        criteria.election_description,
        "Descrição da eleição",
    )
    _validate_description(
        row,
        "DS_CARGO_PERGUNTA",
        criteria.office_description,
        "Descrição do cargo",
    )

    if _required_value(row, "CD_TIPO_VOTAVEL") != criteria.votable_type_code:
        return False
    _validate_description(
        row,
        "DS_TIPO_VOTAVEL",
        criteria.votable_type_description,
        "Descrição do tipo votável",
    )

    if _required_value(row, "NR_VOTAVEL") != criteria.candidate_number:
        return False
    actual_name = _required_value(row, "NM_VOTAVEL")
    if actual_name != criteria.candidate_name:
        raise CandidateIdentityError(
            f"Número {criteria.candidate_number} associado ao nome inesperado {actual_name!r}."
        )
    return True


def select_candidate_rows(
    rows: Iterable[dict[str, str]],
    criteria: CandidateCriteria = DEFAULT_CRITERIA,
) -> Iterator[dict[str, str]]:
    """Entrega somente linhas do candidato e falha se o resultado for vazio."""
    selected = 0
    for row in rows:
        if is_candidate_row(row, criteria):
            selected += 1
            yield row
    if selected == 0:
        raise CandidateNotFoundError(
            f"Nenhum registro nominal do candidato {criteria.candidate_number} foi encontrado."
        )
