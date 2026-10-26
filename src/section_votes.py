"""Normalização e consolidação da votação do candidato por seção."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass


class SectionNormalizationError(RuntimeError):
    """Registro bruto incompatível com o modelo canônico."""


class DuplicateSectionError(SectionNormalizationError):
    """Mais de um registro foi encontrado para a mesma chave canônica."""


@dataclass(frozen=True)
class CandidateSectionVotes:
    cidade: str
    codigo_municipio_tse: str
    zona_eleitoral: str
    secao: str
    secoes_agregadas: tuple[str, ...]
    votos: int
    numero_candidato: str
    nome_candidato: str
    cargo: str
    uf: str
    ano_eleicao: int
    turno: int

    @property
    def key(self) -> tuple[int, int, str, str, str, str, str]:
        return (
            self.ano_eleicao,
            self.turno,
            self.uf,
            self.codigo_municipio_tse,
            self.zona_eleitoral,
            self.secao,
            self.numero_candidato,
        )


def _required_text(row: Mapping[str, str], field: str) -> str:
    try:
        value = row[field]
    except KeyError as error:
        raise SectionNormalizationError(f"Campo obrigatório ausente: {field}") from error
    if not isinstance(value, str) or not value.strip():
        raise SectionNormalizationError(f"Campo obrigatório vazio: {field}")
    return value


def _decimal_identifier(row: Mapping[str, str], field: str) -> str:
    value = _required_text(row, field).strip()
    if not value.isdecimal():
        raise SectionNormalizationError(f"{field} deve conter um inteiro decimal: {value!r}")
    return str(int(value))


def _non_negative_integer(row: Mapping[str, str], field: str) -> int:
    value = _required_text(row, field).strip()
    try:
        converted = int(value, 10)
    except ValueError as error:
        raise SectionNormalizationError(f"{field} deve ser um inteiro: {value!r}") from error
    if converted < 0:
        raise SectionNormalizationError(f"{field} não pode ser negativo: {value!r}")
    return converted


def _parse_aggregated_sections(row: Mapping[str, str]) -> tuple[str, ...]:
    value = _required_text(row, "DS_SECOES_AGREGADAS").strip()
    if value == "#NULO#":
        return ()
    tokens = [token for token in re.split(r"[,;|\s]+", value) if token]
    if not tokens or any(not token.isdecimal() for token in tokens):
        raise SectionNormalizationError(
            f"DS_SECOES_AGREGADAS possui formato inválido: {value!r}"
        )
    return tuple(dict.fromkeys(str(int(token)) for token in tokens))


def normalize_section_row(row: Mapping[str, str]) -> CandidateSectionVotes:
    """Converte uma linha já selecionada para o modelo canônico."""
    return CandidateSectionVotes(
        cidade=_required_text(row, "NM_MUNICIPIO"),
        codigo_municipio_tse=_decimal_identifier(row, "CD_MUNICIPIO"),
        zona_eleitoral=_decimal_identifier(row, "NR_ZONA"),
        secao=_decimal_identifier(row, "NR_SECAO"),
        secoes_agregadas=_parse_aggregated_sections(row),
        votos=_non_negative_integer(row, "QT_VOTOS"),
        numero_candidato=_decimal_identifier(row, "NR_VOTAVEL"),
        nome_candidato=_required_text(row, "NM_VOTAVEL"),
        cargo=_required_text(row, "DS_CARGO_PERGUNTA"),
        uf=_required_text(row, "SG_UF"),
        ano_eleicao=_non_negative_integer(row, "ANO_ELEICAO"),
        turno=_non_negative_integer(row, "NR_TURNO"),
    )


def _city_sort_key(city: str) -> tuple[str, str]:
    decomposed = unicodedata.normalize("NFKD", city)
    without_accents = "".join(character for character in decomposed if not unicodedata.combining(character))
    return without_accents.casefold(), city.casefold()


def _sort_key(record: CandidateSectionVotes) -> tuple[object, ...]:
    return (
        *_city_sort_key(record.cidade),
        int(record.codigo_municipio_tse),
        int(record.zona_eleitoral),
        int(record.secao),
        int(record.numero_candidato),
    )


def normalize_and_consolidate(
    rows: Iterable[Mapping[str, str]],
) -> list[CandidateSectionVotes]:
    """Normaliza, rejeita chaves duplicadas e devolve ordem determinística."""
    records: list[CandidateSectionVotes] = []
    seen: set[tuple[int, int, str, str, str, str, str]] = set()
    for row in rows:
        record = normalize_section_row(row)
        if record.key in seen:
            raise DuplicateSectionError(
                "Registro duplicado para "
                f"{record.cidade}, zona {record.zona_eleitoral}, seção {record.secao}."
            )
        seen.add(record.key)
        records.append(record)
    records.sort(key=_sort_key)
    return records
