from collections.abc import Iterator
from pathlib import Path

import pytest

from lungfish.filter.length import LengthFilter
from lungfish.reader.fasta import FastaReader
from lungfish.reader.sequencereader import SequenceReader
from lungfish.sequencerecord import SequenceRecord

SAMPLE = Path(__file__).parent / "data" / "sample.fasta"


def rec(seq_id: str, sequence: str) -> SequenceRecord:
    return SequenceRecord(seq_id, "", sequence)


class ListSource:
    """In-memory SequenceReader: satisfies the protocol structurally, no inheritance."""

    def __init__(self, records: list[SequenceRecord]):
        self._records = records
        self.passes = 0

    def records(self) -> Iterator[SequenceRecord]:
        self.passes += 1
        yield from self._records


def ids(source: SequenceReader) -> list[str]:
    return [r.id for r in source.records()]


# lengths 2, 5, 8, 10
MIXED = [rec("len2", "AC"), rec("len5", "ACGTA"), rec("len8", "ACGTACGT"), rec("len10", "ACGTACGTAC")]


def test_no_cutoffs_keeps_everything() -> None:
    assert ids(LengthFilter(ListSource(MIXED))) == ["len2", "len5", "len8", "len10"]


def test_min_cutoff_drops_shorter_records() -> None:
    assert ids(LengthFilter(ListSource(MIXED), min_cutoff=6)) == ["len8", "len10"]


def test_max_cutoff_drops_longer_records() -> None:
    assert ids(LengthFilter(ListSource(MIXED), max_cutoff=6)) == ["len2", "len5"]


def test_min_and_max_cutoff_together() -> None:
    assert ids(LengthFilter(ListSource(MIXED), min_cutoff=3, max_cutoff=9)) == ["len5", "len8"]


def test_cutoffs_are_inclusive() -> None:
    assert ids(LengthFilter(ListSource(MIXED), min_cutoff=5, max_cutoff=8)) == ["len5", "len8"]


def test_equal_min_and_max_keeps_only_that_length() -> None:
    assert ids(LengthFilter(ListSource(MIXED), min_cutoff=8, max_cutoff=8)) == ["len8"]


def test_min_greater_than_max_is_rejected() -> None:
    with pytest.raises(ValueError, match="min_cutoff"):
        LengthFilter(ListSource(MIXED), min_cutoff=10, max_cutoff=5)


def test_everything_filtered_yields_nothing() -> None:
    assert ids(LengthFilter(ListSource(MIXED), min_cutoff=100)) == []


def test_empty_source_yields_nothing() -> None:
    assert ids(LengthFilter(ListSource([]), min_cutoff=1)) == []


def test_preserves_order() -> None:
    source = ListSource([rec("c", "CCCCC"), rec("x", "A"), rec("a", "AAAAA"), rec("b", "BBBBB")])

    assert ids(LengthFilter(source, min_cutoff=5)) == ["c", "a", "b"]


def test_passes_records_through_unchanged() -> None:
    original = rec("a", "ACGTACGT")

    (result,) = LengthFilter(ListSource([original]), min_cutoff=5).records()

    assert result is original


def test_is_lazy() -> None:
    """Nothing is pulled from the source until the filter is iterated."""
    source = ListSource([rec("a", "ACGTACGT")])
    stream = LengthFilter(source, min_cutoff=5).records()

    assert source.passes == 0
    next(stream)
    assert source.passes == 1


def test_is_reiterable() -> None:
    """Each call starts a fresh pass over the source rather than an exhausted iterator."""
    source = ListSource([rec("a", "ACGTACGT")])
    length_filter = LengthFilter(source, min_cutoff=5)

    assert ids(length_filter) == ["a"]
    assert ids(length_filter) == ["a"]
    assert source.passes == 2


def test_stacks_with_another_filter() -> None:
    stacked = LengthFilter(LengthFilter(ListSource(MIXED), min_cutoff=3), max_cutoff=9)

    assert ids(stacked) == ["len5", "len8"]


def test_wraps_a_real_reader() -> None:
    # sample.fasta: seq1 = 8 bp, seq2 = 8 bp, seq3 = 4 bp
    assert ids(LengthFilter(FastaReader(SAMPLE), min_cutoff=5)) == ["seq1", "seq2"]


def test_satisfies_sequencereader_protocol() -> None:
    length_filter: SequenceReader = LengthFilter(ListSource([]))

    assert length_filter is not None
