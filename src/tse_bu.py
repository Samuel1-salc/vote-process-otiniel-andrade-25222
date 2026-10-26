"""Aquisição e leitura escalável do Boletim de Urna do TSE."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
import tempfile
import time
import urllib.request
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ARCHIVE_NAME = "bweb_1t_TO_051020261403.zip"
CSV_NAME = "bweb_1t_TO_051020261403.csv"
SOURCE_URL = (
    "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/"
    f"{ARCHIVE_NAME}"
)
HASH_URL = f"{SOURCE_URL}.sha512"
CONTRACT_VERSION = "1.1.0"
ENCODING = "iso-8859-1"
REQUIRED_SOURCE_COLUMNS = frozenset(
    {
        "ANO_ELEICAO",
        "NR_TURNO",
        "CD_ELEICAO",
        "DS_ELEICAO",
        "SG_UF",
        "CD_MUNICIPIO",
        "NM_MUNICIPIO",
        "NR_ZONA",
        "NR_SECAO",
        "CD_CARGO_PERGUNTA",
        "DS_CARGO_PERGUNTA",
        "CD_TIPO_VOTAVEL",
        "DS_TIPO_VOTAVEL",
        "NR_VOTAVEL",
        "NM_VOTAVEL",
        "QT_VOTOS",
        "DS_SECOES_AGREGADAS",
    }
)


class SourceArchiveError(RuntimeError):
    """Arquivo de origem incompatível com o contrato."""


class SourceContractError(RuntimeError):
    """Cabeçalho CSV incompatível com o contrato."""


@dataclass(frozen=True)
class SourceDescriptor:
    archive: Path
    csv_name: str
    columns: tuple[str, ...]


def _download(url: str, destination: Path, retries: int = 3) -> None:
    """Baixa um recurso HTTPS em blocos, com tentativas limitadas."""
    request = urllib.request.Request(url, headers={"User-Agent": "otoniel-tse-bu/1.0"})
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
            return
        except Exception as error:  # pragma: no cover - depende de rede
            last_error = error
            if attempt < retries:
                time.sleep(attempt)
    raise SourceArchiveError(f"Não foi possível baixar {url}: {last_error}")


def _read_expected_sha512(hash_file: Path) -> str:
    token = hash_file.read_text(encoding="ascii").split(maxsplit=1)[0].lower()
    if len(token) != 128 or any(character not in "0123456789abcdef" for character in token):
        raise SourceArchiveError("O arquivo de hash oficial não contém um SHA-512 válido.")
    return token


def sha512_file(path: Path) -> str:
    digest = hashlib.sha512()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def describe_archive(archive: Path) -> SourceDescriptor:
    """Valida o ZIP e o cabeçalho sem carregar o CSV integralmente."""
    if not archive.is_file():
        raise SourceArchiveError(f"Arquivo não encontrado: {archive}")

    try:
        with zipfile.ZipFile(archive) as bundle:
            if CSV_NAME not in bundle.namelist():
                raise SourceArchiveError(f"CSV esperado não encontrado no ZIP: {CSV_NAME}")
            with bundle.open(CSV_NAME) as raw_csv:
                text_csv = io.TextIOWrapper(raw_csv, encoding=ENCODING, newline="")
                reader = csv.DictReader(text_csv, delimiter=";")
                columns = tuple(reader.fieldnames or ())
    except zipfile.BadZipFile as error:
        raise SourceArchiveError(f"ZIP inválido: {archive}") from error

    missing = REQUIRED_SOURCE_COLUMNS.difference(columns)
    if missing:
        raise SourceContractError(
            "Cabeçalho CSV incompatível; campos ausentes: " + ", ".join(sorted(missing))
        )
    return SourceDescriptor(archive=archive, csv_name=CSV_NAME, columns=columns)


def acquire_official_archive(output_dir: Path) -> dict[str, str]:
    """Baixa, confere e publica o ZIP do TSE e seus metadados de proveniência."""
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tse-bu-") as temporary:
        temporary_dir = Path(temporary)
        archive_tmp = temporary_dir / ARCHIVE_NAME
        hash_tmp = temporary_dir / f"{ARCHIVE_NAME}.sha512"
        _download(HASH_URL, hash_tmp)
        expected_hash = _read_expected_sha512(hash_tmp)
        _download(SOURCE_URL, archive_tmp)
        calculated_hash = sha512_file(archive_tmp)
        if calculated_hash != expected_hash:
            raise SourceArchiveError("Hash SHA-512 divergente; nenhum arquivo foi publicado.")

        try:
            with zipfile.ZipFile(archive_tmp) as bundle:
                invalid_member = bundle.testzip()
            if invalid_member is not None:
                raise SourceArchiveError(f"ZIP corrompido no membro: {invalid_member}")
        except zipfile.BadZipFile as error:
            raise SourceArchiveError("ZIP baixado é inválido.") from error

        descriptor = describe_archive(archive_tmp)
        metadata = {
            "versao_contrato": CONTRACT_VERSION,
            "fonte": "TSE — Boletim de Urna 2026, TO, 1º turno",
            "url_origem": SOURCE_URL,
            "url_hash": HASH_URL,
            "algoritmo_hash": "SHA-512",
            "hash_esperado": expected_hash,
            "hash_calculado": calculated_hash,
            "arquivo": ARCHIVE_NAME,
            "csv_interno": descriptor.csv_name,
            "adquirido_em": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        metadata_tmp = temporary_dir / f"{ARCHIVE_NAME}.metadata.json"
        metadata_tmp.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        shutil.copy2(archive_tmp, output_dir / ARCHIVE_NAME)
        shutil.copy2(hash_tmp, output_dir / f"{ARCHIVE_NAME}.sha512")
        shutil.copy2(metadata_tmp, output_dir / metadata_tmp.name)
    return metadata


def iter_bu_rows(archive: Path) -> Iterator[dict[str, str]]:
    """Entrega linhas do CSV como dicionários, mantendo somente uma linha em memória."""
    describe_archive(archive)
    with zipfile.ZipFile(archive) as bundle, bundle.open(CSV_NAME) as raw_csv:
        text_csv = io.TextIOWrapper(raw_csv, encoding=ENCODING, newline="")
        reader = csv.DictReader(text_csv, delimiter=";")
        for row in reader:
            if None in row:
                raise SourceContractError("Linha CSV possui mais campos que o cabeçalho.")
            yield row


def iter_bu_chunks(archive: Path, chunk_size: int = 50_000) -> Iterator[list[dict[str, str]]]:
    """Entrega linhas em lotes de tamanho limitado para processamento escalável."""
    if chunk_size < 1:
        raise ValueError("chunk_size deve ser maior que zero.")
    batch: list[dict[str, str]] = []
    for row in iter_bu_rows(archive):
        batch.append(row)
        if len(batch) == chunk_size:
            yield batch
            batch = []
    if batch:
        yield batch
