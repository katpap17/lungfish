from pathlib import Path

import pytest

from lungfish.reader.fastq import FastqReader
from lungfish.reader.sequencereader import SequenceReader

RECORD = "@read1 a description\nACGT\n+\nIIII\n"


def write_fastq(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "reads.fastq"
    path.write_text(text)
    return path


def test_parses_all_four_fields(tmp_path: Path) -> None:
    (record,) = FastqReader(write_fastq(tmp_path, RECORD)).records()

    assert record.id == "read1"
    assert record.description == "a description"
    assert record.sequence == "ACGT"
    assert record.quality == "IIII"


def test_parses_multiple_records(tmp_path: Path) -> None:
    path = write_fastq(tmp_path, RECORD + "@read2\nTTTT\n+\n!!!!\n")
    records = list(FastqReader(path).records())

    assert [r.id for r in records] == ["read1", "read2"]


def test_header_without_description(tmp_path: Path) -> None:
    (record,) = FastqReader(write_fastq(tmp_path, "@read1\nACGT\n+\nIIII\n")).records()

    assert record.description == ""


def test_at_sign_in_quality_is_not_a_header(tmp_path: Path) -> None:
    """'@' is a legal quality score, so prefix-based parsing would break here."""
    (record,) = FastqReader(write_fastq(tmp_path, "@read1 x\nACGT\n+\n@@@@\n")).records()

    assert record.quality == "@@@@"


def test_empty_file_yields_no_records(tmp_path: Path) -> None:
    assert list(FastqReader(write_fastq(tmp_path, "")).records()) == []


def test_rejects_truncated_record(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="truncated"):
        list(FastqReader(write_fastq(tmp_path, "@read1 x\nACGT\n+\n")).records())


def test_rejects_quality_length_mismatch(tmp_path: Path) -> None:
    path = write_fastq(tmp_path, "@read1 x\nACGTACGT\n+\nIIII\n")

    with pytest.raises(ValueError, match="does not match"):
        list(FastqReader(path).records())


def test_rejects_missing_separator(tmp_path: Path) -> None:
    path = write_fastq(tmp_path, "@read1 x\nACGT\nIIII\n+\n")

    with pytest.raises(ValueError, match="separator"):
        list(FastqReader(path).records())


def test_satisfies_sequencereader_protocol(tmp_path: Path) -> None:
    reader: SequenceReader = FastqReader(tmp_path / "reads.fastq")

    assert reader is not None
