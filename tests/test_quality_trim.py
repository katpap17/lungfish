from collections.abc import Iterator
from pathlib import Path

import pytest

from lungfish.filter.length import LengthFilter
from lungfish.filter.quality import QualityTrim
from lungfish.reader.fastq import FastqReader
from lungfish.reader.sequencereader import SequenceReader
from lungfish.sequencerecord import SequenceRecord

SAMPLE = Path(__file__).parent / "data" / "sample.fastq"


def rec(seq_id: str, scores: list[int]) -> SequenceRecord:
    """Build a read whose quality string encodes the given Phred scores."""
    sequence = ("ACGT" * len(scores))[: len(scores)]
    quality = "".join(chr(score + 33) for score in scores)
    return SequenceRecord(seq_id, "desc", sequence, quality)


class ListSource:
    def __init__(self, records: list[SequenceRecord]):
        self._records = records
        self.passes = 0

    def records(self) -> Iterator[SequenceRecord]:
        self.passes += 1
        yield from self._records


def trim_one(record: SequenceRecord, **options: int) -> SequenceRecord:
    (result,) = QualityTrim(ListSource([record]), **options).records()
    return result


def test_leaves_high_quality_read_untouched() -> None:
    result = trim_one(rec("r", [40] * 10))

    assert len(result.sequence) == 10


def test_trims_low_quality_tail() -> None:
    result = trim_one(rec("r", [30, 30, 30, 30, 10, 10]), window_size=1)

    assert result.sequence == "ACGT"


def test_cuts_sequence_and_quality_at_the_same_place() -> None:
    result = trim_one(rec("r", [30, 30, 30, 30, 10, 10]), window_size=1)

    assert result.quality is not None
    assert len(result.sequence) == len(result.quality) == 4


def test_window_tolerates_a_single_bad_base() -> None:
    """A lone low score is averaged out by its neighbours instead of triggering a cut."""
    scores = [30, 30, 30, 10, 30, 30, 30, 30]

    assert len(trim_one(rec("r", scores), window_size=4).sequence) == 8
    assert len(trim_one(rec("r", scores), window_size=1).sequence) == 3


def test_read_bad_from_the_start_is_trimmed_to_empty() -> None:
    result = trim_one(rec("r", [5, 5, 5, 5, 40, 40]))

    assert result.sequence == ""
    assert result.quality == ""


def test_zero_cutoff_trims_nothing() -> None:
    result = trim_one(rec("r", [0, 0, 0, 0]), quality_cutoff=0)

    assert len(result.sequence) == 4


def test_keeps_id_and_description() -> None:
    result = trim_one(rec("read7", [30, 30, 5, 5]), window_size=1)

    assert result.id == "read7"
    assert result.description == "desc"


def test_passes_through_records_without_quality() -> None:
    """FASTA and GenBank records have no scores to trim."""
    fasta_record = SequenceRecord("r", "", "ACGTACGT")

    assert trim_one(fasta_record) is fasta_record


def test_rejects_window_size_below_one() -> None:
    with pytest.raises(ValueError, match="window_size"):
        QualityTrim(ListSource([]), window_size=0)


def test_is_lazy() -> None:
    source = ListSource([rec("r", [40] * 4)])
    stream = QualityTrim(source).records()

    assert source.passes == 0
    next(stream)
    assert source.passes == 1


def test_is_reiterable() -> None:
    source = ListSource([rec("r", [40] * 4)])
    trim = QualityTrim(source)

    assert len(list(trim.records())) == 1
    assert len(list(trim.records())) == 1


def test_length_filter_drops_reads_trimmed_to_nothing() -> None:
    source = ListSource([rec("good", [40] * 8), rec("bad", [2] * 8)])

    stacked = LengthFilter(QualityTrim(source), min_cutoff=1)

    assert [r.id for r in stacked.records()] == ["good"]


def test_wraps_a_real_reader() -> None:
    # sample.fastq: read1 is all Q40 ('I'), read2 is all Q0 ('!')
    read1, read2 = QualityTrim(FastqReader(SAMPLE)).records()

    assert read1.sequence == "ACGTACGT"
    assert read2.sequence == ""


def test_satisfies_sequencereader_protocol() -> None:
    trim: SequenceReader = QualityTrim(ListSource([]))

    assert trim is not None
