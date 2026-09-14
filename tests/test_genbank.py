from pathlib import Path

from Bio import SeqIO

from lungfish.reader.genbank import GenBankReader
from lungfish.reader.sequencereader import SequenceReader

SAMPLE = Path(__file__).parent / "data" / "sample.gb"


def test_parses_id_description_and_sequence() -> None:
    record = next(GenBankReader(SAMPLE).records())

    assert record.id == "TEST001.1"
    assert record.description == "first test record"
    assert record.sequence == "ACGTACGTACGTTTTTGGGGCCCC"


def test_sequence_is_a_plain_string() -> None:
    """The adapter's core job: Biopython's Seq becomes a str."""
    record = next(GenBankReader(SAMPLE).records())

    assert type(record.sequence) is str


def test_parses_multiple_records() -> None:
    records = list(GenBankReader(SAMPLE).records())

    assert [r.id for r in records] == ["TEST001.1", "TEST002.1"]


def test_quality_is_none() -> None:
    """GenBank carries no per-base quality."""
    record = next(GenBankReader(SAMPLE).records())

    assert record.quality is None


def test_features_are_dropped() -> None:
    """The adapter narrows to SequenceReader, so the feature table is lost by design."""
    source = next(SeqIO.parse(SAMPLE, "genbank"))
    assert source.features, "fixture should carry features to make this meaningful"

    record = next(GenBankReader(SAMPLE).records())

    assert not hasattr(record, "features")


def test_records_is_reiterable() -> None:
    reader = GenBankReader(SAMPLE)

    assert len(list(reader.records())) == 2
    assert len(list(reader.records())) == 2


def test_satisfies_sequencereader_protocol() -> None:
    reader: SequenceReader = GenBankReader(SAMPLE)

    assert reader is not None
