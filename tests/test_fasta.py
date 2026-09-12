from pathlib import Path

from lungfish.reader.fasta import FastaReader
from lungfish.reader.sequencereader import SequenceReader


def write_fasta(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "reads.fasta"
    path.write_text(text)
    return path


def test_parses_id_description_and_sequence(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, ">seq1 a description\nACGT\n")
    (record,) = FastaReader(path).records()

    assert record.id == "seq1"
    assert record.description == "a description"
    assert record.sequence == "ACGT"


def test_joins_multiline_sequence(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, ">seq1 x\nACGT\nTTTT\nGG\n")
    (record,) = FastaReader(path).records()

    assert record.sequence == "ACGTTTTTGG"


def test_emits_final_record(tmp_path: Path) -> None:
    """The record at EOF has no following header to flush it."""
    path = write_fasta(tmp_path, ">a x\nAA\n>b y\nCC\n>c z\nGG\n")
    records = list(FastaReader(path).records())

    assert [r.id for r in records] == ["a", "b", "c"]


def test_header_without_description(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, ">seq1\nACGT\n")
    (record,) = FastaReader(path).records()

    assert record.id == "seq1"
    assert record.description == ""


def test_ignores_blank_lines(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, "\n>seq1 x\nACGT\n\n\nTTTT\n\n")
    (record,) = FastaReader(path).records()

    assert record.sequence == "ACGTTTTT"


def test_handles_missing_trailing_newline(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, ">seq1 x\nACGT")
    (record,) = FastaReader(path).records()

    assert record.sequence == "ACGT"


def test_empty_file_yields_no_records(tmp_path: Path) -> None:
    path = write_fasta(tmp_path, "")

    assert list(FastaReader(path).records()) == []


def test_records_is_reiterable(tmp_path: Path) -> None:
    """Each call reopens the file, so the reader is not single-use."""
    path = write_fasta(tmp_path, ">seq1 x\nACGT\n")
    reader = FastaReader(path)

    assert len(list(reader.records())) == 1
    assert len(list(reader.records())) == 1


def test_satisfies_sequencereader_protocol(tmp_path: Path) -> None:
    """Structural conformance is only checked where it is used — this is that place."""
    reader: SequenceReader = FastaReader(tmp_path / "reads.fasta")

    assert reader is not None
