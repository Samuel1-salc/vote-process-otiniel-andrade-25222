"""Dataset JSON estático da votação validada para consumo no frontend."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.quality_report import QualityReport
from src.section_votes import CandidateSectionVotes

SCHEMA_VERSION = "1.0.0"
TOP_LEVEL_FIELDS = {
    "versao_schema",
    "versao_contrato",
    "gerado_em",
    "candidato",
    "eleicao",
    "resumo",
    "fonte",
    "registros",
}
RECORD_FIELDS = {
    "cidade",
    "codigo_municipio_tse",
    "zona",
    "secao",
    "secoes_agregadas",
    "votos",
}


class WebDatasetError(RuntimeError):
    """Dataset web incompatível com o contrato público."""


def _sort_key(record: CandidateSectionVotes) -> tuple[object, ...]:
    city = unicodedata.normalize("NFKD", record.cidade)
    city = "".join(character for character in city if not unicodedata.combining(character))
    return (
        city.casefold(),
        record.cidade.casefold(),
        int(record.codigo_municipio_tse),
        int(record.zona_eleitoral),
        int(record.secao),
    )


def _validate_export_inputs(records: list[CandidateSectionVotes], report: QualityReport) -> None:
    if report.status != "aprovado":
        raise WebDatasetError("O relatório de qualidade não está aprovado.")
    calculated = {
        "registros": len(records),
        "municipios": len({record.codigo_municipio_tse for record in records}),
        "registros_com_secao_agregada": sum(bool(record.secoes_agregadas) for record in records),
        "total_votos": sum(record.votos for record in records),
    }
    expected = {
        "registros": report.metrics.records,
        "municipios": report.metrics.municipalities,
        "registros_com_secao_agregada": report.metrics.aggregated_records,
        "total_votos": report.metrics.total_votes,
    }
    if calculated != expected:
        raise WebDatasetError(
            f"Registros e relatório de qualidade divergem: {calculated!r} != {expected!r}."
        )


def build_web_dataset(
    records: Iterable[CandidateSectionVotes],
    report: QualityReport,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Cria o documento público sem repetir metadados globais por registro."""
    materialized = sorted(records, key=_sort_key)
    _validate_export_inputs(materialized, report)
    source = report.source
    timestamp = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    document: dict[str, Any] = {
        "versao_schema": SCHEMA_VERSION,
        "versao_contrato": report.contract_version,
        "gerado_em": timestamp,
        "candidato": {
            "numero": report.candidate["numero"],
            "nome": report.candidate["nome"],
            "cargo": report.candidate["cargo"],
        },
        "eleicao": {
            "ano": report.candidate["ano_eleicao"],
            "turno": report.candidate["turno"],
            "uf": report.candidate["uf"],
        },
        "resumo": {
            "registros": report.metrics.records,
            "municipios": report.metrics.municipalities,
            "registros_com_secao_agregada": report.metrics.aggregated_records,
            "total_votos": report.metrics.total_votes,
        },
        "fonte": {
            "nome": source.get("fonte", "TSE — Boletim de Urna"),
            "url": source.get("url_origem", ""),
            "algoritmo_hash": source.get("algoritmo_hash", ""),
            "hash_arquivo_origem": source.get("hash_calculado") or source.get("hash_esperado", ""),
        },
        "registros": [
            {
                "cidade": record.cidade,
                "codigo_municipio_tse": record.codigo_municipio_tse,
                "zona": record.zona_eleitoral,
                "secao": record.secao,
                "secoes_agregadas": list(record.secoes_agregadas),
                "votos": record.votos,
            }
            for record in materialized
        ],
    }
    validate_web_dataset(document)
    return document


def _require_exact_fields(value: Mapping[str, Any], expected: set[str], context: str) -> None:
    actual = set(value)
    if actual != expected:
        raise WebDatasetError(
            f"Campos inválidos em {context}: ausentes={sorted(expected - actual)!r}, "
            f"extras={sorted(actual - expected)!r}."
        )


def _is_integer(value: object) -> bool:
    return type(value) is int


def validate_web_dataset(document: Mapping[str, Any]) -> None:
    """Valida estrutura e reconcilia todas as métricas do documento."""
    _require_exact_fields(document, TOP_LEVEL_FIELDS, "raiz")
    if document["versao_schema"] != SCHEMA_VERSION:
        raise WebDatasetError("Versão de schema incompatível.")
    for field in ("versao_contrato", "gerado_em"):
        if not isinstance(document[field], str) or not document[field]:
            raise WebDatasetError(f"{field} deve ser uma string não vazia.")

    candidate = document["candidato"]
    election = document["eleicao"]
    summary = document["resumo"]
    source = document["fonte"]
    records = document["registros"]
    if not isinstance(candidate, Mapping) or not isinstance(election, Mapping):
        raise WebDatasetError("Candidato e eleição devem ser objetos.")
    if not isinstance(summary, Mapping) or not isinstance(source, Mapping):
        raise WebDatasetError("Resumo e fonte devem ser objetos.")
    _require_exact_fields(candidate, {"numero", "nome", "cargo"}, "candidato")
    _require_exact_fields(election, {"ano", "turno", "uf"}, "eleicao")
    _require_exact_fields(
        summary,
        {"registros", "municipios", "registros_com_secao_agregada", "total_votos"},
        "resumo",
    )
    _require_exact_fields(
        source,
        {"nome", "url", "algoritmo_hash", "hash_arquivo_origem"},
        "fonte",
    )
    if not all(isinstance(candidate[field], str) and candidate[field] for field in candidate):
        raise WebDatasetError("Campos do candidato devem ser strings não vazias.")
    if not _is_integer(election["ano"]) or not _is_integer(election["turno"]):
        raise WebDatasetError("Ano e turno devem ser inteiros.")
    if not isinstance(election["uf"], str) or len(election["uf"]) != 2:
        raise WebDatasetError("UF deve ser uma string de duas letras.")
    if not all(isinstance(source[field], str) and source[field] for field in source):
        raise WebDatasetError("Proveniência deve conter strings não vazias.")
    if not isinstance(records, list) or not records:
        raise WebDatasetError("registros deve ser uma lista não vazia.")

    municipalities: set[str] = set()
    total_votes = 0
    aggregated_records = 0
    for index, item in enumerate(records):
        if not isinstance(item, Mapping):
            raise WebDatasetError(f"Registro {index} não é um objeto.")
        _require_exact_fields(item, RECORD_FIELDS, f"registro {index}")
        for field in ("cidade", "codigo_municipio_tse", "zona", "secao"):
            if not isinstance(item[field], str) or not item[field]:
                raise WebDatasetError(f"{field} inválido no registro {index}.")
        for field in ("codigo_municipio_tse", "zona", "secao"):
            if not item[field].isdecimal():
                raise WebDatasetError(f"{field} não decimal no registro {index}.")
        aggregated = item["secoes_agregadas"]
        if not isinstance(aggregated, list) or any(
            not isinstance(section, str) or not section.isdecimal() for section in aggregated
        ):
            raise WebDatasetError(f"secoes_agregadas inválida no registro {index}.")
        if len(aggregated) != len(set(aggregated)):
            raise WebDatasetError(f"secoes_agregadas duplicada no registro {index}.")
        votes = item["votos"]
        if not _is_integer(votes) or votes < 0:
            raise WebDatasetError(f"votos inválidos no registro {index}.")
        municipalities.add(item["codigo_municipio_tse"])
        total_votes += votes
        aggregated_records += bool(aggregated)

    calculated = {
        "registros": len(records),
        "municipios": len(municipalities),
        "registros_com_secao_agregada": aggregated_records,
        "total_votos": total_votes,
    }
    if any(not _is_integer(summary[field]) or summary[field] < 0 for field in summary):
        raise WebDatasetError("Métricas do resumo devem ser inteiros não negativos.")
    if calculated != dict(summary):
        raise WebDatasetError(f"Resumo não reconciliado: {calculated!r} != {dict(summary)!r}.")


def serialize_web_dataset(document: Mapping[str, Any]) -> bytes:
    validate_web_dataset(document)
    text = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return text.encode("utf-8")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def verify_published_dataset(dataset_path: Path, checksum_path: Path) -> dict[str, Any]:
    content = dataset_path.read_bytes()
    expected_checksum = checksum_path.read_text(encoding="ascii").split(maxsplit=1)[0]
    actual_checksum = sha256_bytes(content)
    if expected_checksum != actual_checksum:
        raise WebDatasetError(
            f"Checksum SHA-256 divergente: esperado {expected_checksum}, calculado {actual_checksum}."
        )
    try:
        document = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WebDatasetError("JSON publicado é inválido ou não está em UTF-8.") from error
    validate_web_dataset(document)
    return document


def publish_web_dataset_atomic(
    document: Mapping[str, Any], dataset_path: Path, checksum_path: Path | None = None
) -> str:
    """Publica JSON e checksum, restaurando versões anteriores em caso de falha."""
    checksum_path = checksum_path or dataset_path.with_name(f"{dataset_path.name}.sha256")
    if dataset_path.parent != checksum_path.parent:
        raise WebDatasetError("Dataset e checksum devem compartilhar o diretório de publicação.")
    content = serialize_web_dataset(document)
    checksum = sha256_bytes(content)
    checksum_content = f"{checksum}  {dataset_path.name}\n".encode("ascii")
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_paths: list[Path] = []
    backups: dict[Path, Path] = {}
    published: list[Path] = []
    try:
        staged: dict[Path, Path] = {}
        for destination, payload in (
            (dataset_path, content),
            (checksum_path, checksum_content),
        ):
            descriptor, name = tempfile.mkstemp(
                prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
            )
            temporary = Path(name)
            temporary_paths.append(temporary)
            with os.fdopen(descriptor, "wb") as output:
                output.write(payload)
                output.flush()
                os.fsync(output.fileno())
            staged[destination] = temporary

        staged_document = json.loads(staged[dataset_path].read_text(encoding="utf-8"))
        validate_web_dataset(staged_document)
        if sha256_bytes(staged[dataset_path].read_bytes()) != checksum:
            raise WebDatasetError("Checksum do artefato temporário é inválido.")

        for destination in (dataset_path, checksum_path):
            if destination.exists():
                descriptor, backup_name = tempfile.mkstemp(
                    prefix=f".{destination.name}.", suffix=".bak", dir=destination.parent
                )
                os.close(descriptor)
                backup = Path(backup_name)
                backup.unlink()
                os.replace(destination, backup)
                backups[destination] = backup

        for destination in (dataset_path, checksum_path):
            os.replace(staged[destination], destination)
            published.append(destination)

        verify_published_dataset(dataset_path, checksum_path)
    except Exception:
        for destination in reversed(published):
            destination.unlink(missing_ok=True)
        for destination, backup in backups.items():
            if backup.exists():
                os.replace(backup, destination)
        raise
    finally:
        for temporary in temporary_paths:
            temporary.unlink(missing_ok=True)
        for backup in backups.values():
            backup.unlink(missing_ok=True)
    return checksum
