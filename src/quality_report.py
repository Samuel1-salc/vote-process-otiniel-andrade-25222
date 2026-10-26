"""Verificações globais, totalização e relatório auditável da votação."""

from __future__ import annotations

import json
import os
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.section_votes import CandidateSectionVotes
from src.tse_bu import CONTRACT_VERSION


class QualityValidationError(RuntimeError):
    """Uma invariante obrigatória de qualidade falhou."""

    def __init__(self, rule: str, detail: str) -> None:
        self.rule = rule
        self.detail = detail
        super().__init__(f"{rule}: {detail}")


@dataclass(frozen=True)
class QualityBaseline:
    records: int
    municipalities: int
    aggregated_records: int
    total_votes: int


@dataclass(frozen=True)
class QualityMetrics:
    records: int
    municipalities: int
    aggregated_records: int
    total_votes: int
    minimum_votes: int
    maximum_votes: int


@dataclass(frozen=True)
class QualityReport:
    status: str
    contract_version: str
    candidate: dict[str, Any]
    metrics: QualityMetrics
    checks: tuple[dict[str, str], ...]
    municipality_subtotals: dict[str, dict[str, Any]]
    source: dict[str, Any]
    generated_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "versao_contrato": self.contract_version,
            "candidato": self.candidate,
            "metricas": {
                "registros": self.metrics.records,
                "municipios": self.metrics.municipalities,
                "registros_com_secao_agregada": self.metrics.aggregated_records,
                "total_votos": self.metrics.total_votes,
                "minimo_votos_por_registro": self.metrics.minimum_votes,
                "maximo_votos_por_registro": self.metrics.maximum_votes,
            },
            "verificacoes": list(self.checks),
            "subtotais_municipios": self.municipality_subtotals,
            "fonte": self.source,
            "gerado_em": self.generated_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


OFFICIAL_BASELINE = QualityBaseline(
    records=1_225,
    municipalities=89,
    aggregated_records=19,
    total_votes=7_180,
)

EXPECTED_IDENTITY: dict[str, Any] = {
    "numero": "25222",
    "nome": "OTONIEL ANDRADE",
    "cargo": "Deputado Estadual",
    "uf": "TO",
    "ano_eleicao": 2026,
    "turno": 1,
}


def _fail(rule: str, detail: str) -> None:
    raise QualityValidationError(rule, detail)


def _validate_text(value: object, field: str, key: object) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("campos_obrigatorios", f"{field} vazio ou inválido na chave {key!r}")
    return value


def _validate_source(source: Mapping[str, Any] | None) -> dict[str, Any]:
    if source is None:
        return {}
    normalized = dict(source)
    expected_hash = normalized.get("hash_esperado")
    calculated_hash = normalized.get("hash_calculado")
    if expected_hash is not None and calculated_hash is not None and expected_hash != calculated_hash:
        _fail("proveniencia", "hash esperado e hash calculado são diferentes")
    source_contract = normalized.get("versao_contrato")
    if source_contract is not None and source_contract != CONTRACT_VERSION:
        _fail(
            "proveniencia",
            f"contrato da fonte {source_contract!r} difere do contrato vigente {CONTRACT_VERSION!r}",
        )
    return normalized


def validate_candidate_votes(
    records: Iterable[CandidateSectionVotes],
    *,
    baseline: QualityBaseline | None = None,
    source: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
) -> QualityReport:
    """Valida invariantes, reconcilia totais e devolve relatório aprovado."""
    materialized = list(records)
    if not materialized:
        _fail("conjunto_nao_vazio", "nenhum registro foi recebido")

    seen_keys: set[tuple[int, int, str, str, str, str, str]] = set()
    municipality_names: dict[str, str] = {}
    municipality_votes: defaultdict[str, int] = defaultdict(int)
    aggregated_records = 0
    total_votes = 0

    for record in materialized:
        if not isinstance(record, CandidateSectionVotes):
            _fail("tipo_registro", f"tipo inesperado: {type(record).__name__}")
        if record.key in seen_keys:
            _fail("chave_unica", f"chave duplicada: {record.key!r}")
        seen_keys.add(record.key)

        _validate_text(record.cidade, "cidade", record.key)
        _validate_text(record.codigo_municipio_tse, "codigo_municipio_tse", record.key)
        _validate_text(record.zona_eleitoral, "zona_eleitoral", record.key)
        _validate_text(record.secao, "secao", record.key)
        if not record.codigo_municipio_tse.isdecimal():
            _fail("identificadores", f"código municipal não decimal: {record.codigo_municipio_tse!r}")
        if not record.zona_eleitoral.isdecimal() or not record.secao.isdecimal():
            _fail("identificadores", f"zona/seção inválida na chave {record.key!r}")

        identity = {
            "numero": record.numero_candidato,
            "nome": record.nome_candidato,
            "cargo": record.cargo,
            "uf": record.uf,
            "ano_eleicao": record.ano_eleicao,
            "turno": record.turno,
        }
        if identity != EXPECTED_IDENTITY:
            _fail("identidade_eleitoral", f"identidade inesperada na chave {record.key!r}: {identity!r}")

        if type(record.votos) is not int or record.votos < 0:
            _fail("votos_validos", f"votos inválidos na chave {record.key!r}: {record.votos!r}")

        existing_name = municipality_names.setdefault(record.codigo_municipio_tse, record.cidade)
        if existing_name != record.cidade:
            _fail(
                "municipio_consistente",
                f"código {record.codigo_municipio_tse} associado a {existing_name!r} e {record.cidade!r}",
            )
        if record.secao in record.secoes_agregadas:
            _fail(
                "secao_agregada",
                f"seção {record.secao} agrega a si mesma na chave {record.key!r}",
            )
        if record.secoes_agregadas:
            aggregated_records += 1
        total_votes += record.votos
        municipality_votes[record.codigo_municipio_tse] += record.votos

    reconciled_total = sum(municipality_votes.values())
    if reconciled_total != total_votes:
        _fail(
            "reconciliacao",
            f"soma por município {reconciled_total} difere do total direto {total_votes}",
        )

    metrics = QualityMetrics(
        records=len(materialized),
        municipalities=len(municipality_names),
        aggregated_records=aggregated_records,
        total_votes=total_votes,
        minimum_votes=min(record.votos for record in materialized),
        maximum_votes=max(record.votos for record in materialized),
    )
    if baseline is not None:
        comparisons = {
            "records": metrics.records,
            "municipalities": metrics.municipalities,
            "aggregated_records": metrics.aggregated_records,
            "total_votes": metrics.total_votes,
        }
        for field, expected in asdict(baseline).items():
            actual = comparisons[field]
            if actual != expected:
                _fail("baseline", f"{field}: esperado {expected}, calculado {actual}")

    subtotals = {
        code: {"cidade": municipality_names[code], "votos": municipality_votes[code]}
        for code in sorted(municipality_names, key=int)
    }
    checks = (
        {"regra": "conjunto_nao_vazio", "status": "aprovado"},
        {"regra": "identidade_eleitoral", "status": "aprovado"},
        {"regra": "chave_unica", "status": "aprovado"},
        {"regra": "votos_validos", "status": "aprovado"},
        {"regra": "municipio_consistente", "status": "aprovado"},
        {"regra": "secao_agregada", "status": "aprovado"},
        {"regra": "reconciliacao", "status": "aprovado"},
        {"regra": "baseline", "status": "aprovado" if baseline else "não executado"},
    )
    timestamp = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return QualityReport(
        status="aprovado",
        contract_version=CONTRACT_VERSION,
        candidate=dict(EXPECTED_IDENTITY),
        metrics=metrics,
        checks=checks,
        municipality_subtotals=subtotals,
        source=_validate_source(source),
        generated_at=timestamp,
    )


def write_quality_report(report: QualityReport, destination: Path) -> None:
    """Publica o relatório por troca atômica no mesmo sistema de arquivos."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(report.to_json())
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
