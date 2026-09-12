from pathlib import Path

import pytest

from lungfish.reader.factory import new_reader
from lungfish.reader.fasta import FastaReader

SAMPLE = Path(__file__).parent / "data" / "sample.fasta"


@pytest.mark.parametrize("suffix", [".fasta", ".fa", ".fna"])
def test_dispatches_fasta_extensions(suffix: str) -> None:
    assert isinstance(new_reader(f"reads{suffix}"), FastaReader)


def test_rejects_unknown_extension() -> None:
    with pytest.raises(ValueError):
        new_reader("reads.txt")


def test_reads_sample_file_end_to_end() -> None:
    records = list(new_reader(SAMPLE).records())

    assert [r.id for r in records] == ["seq1", "seq2", "seq3"]
    assert records[0].sequence == "ACGTTTTT"
    assert records[1].description == ""
