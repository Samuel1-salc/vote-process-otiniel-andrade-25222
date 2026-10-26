from __future__ import annotations

import csv
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.tse_bu import (
    CSV_NAME,
    REQUIRED_SOURCE_COLUMNS,
    SourceContractError,
    describe_archive,
    iter_bu_chunks,
)


def write_archive(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    content = io.StringIO()
    writer = csv.DictWriter(content, fieldnames=columns, delimiter=";", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(CSV_NAME, content.getvalue().encode("iso-8859-1"))


class TSEBUReaderTest(unittest.TestCase):
    def test_reads_rows_in_bounded_chunks(self) -> None:
        columns = sorted(REQUIRED_SOURCE_COLUMNS)
        rows = [{column: "1" for column in columns} for _ in range(3)]
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "bu.zip"
            write_archive(archive, columns, rows)
            chunks = list(iter_bu_chunks(archive, chunk_size=2))
        self.assertEqual([len(chunk) for chunk in chunks], [2, 1])

    def test_rejects_missing_required_column(self) -> None:
        columns = sorted(REQUIRED_SOURCE_COLUMNS - {"QT_VOTOS"})
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "bu.zip"
            write_archive(archive, columns, [{column: "1" for column in columns}])
            with self.assertRaisesRegex(SourceContractError, "QT_VOTOS"):
                describe_archive(archive)


if __name__ == "__main__":
    unittest.main()
