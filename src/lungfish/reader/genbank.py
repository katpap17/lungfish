"""Reader for the GenBank format."""

from Bio import SeqIO
from collections.abc import Iterable, Iterator
from pathlib import Path

from lungfish.sequencerecord import SequenceRecord


class GenBankReader:
    def __init__(self, filepath: str | Path):
        self.filepath = filepath

    def records(self) -> Iterator[SequenceRecord]:
        with open(self.filepath) as fh:
            records = SeqIO.parse(fh, "genbank")
            for record in records:
                yield SequenceRecord(record.id, record.description, str(record.seq), None)

