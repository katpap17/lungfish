from collections.abc import Iterator

from lungfish.reader.sequencereader import SequenceReader
from lungfish.sequencerecord import SequenceRecord

class LengthFilter:
    def __init__(
        self,
        sequence_records: SequenceReader,
        *,
        min_cutoff: int = 0,
        max_cutoff: int | None = None,
    ):
        if max_cutoff is not None and min_cutoff > max_cutoff:
            raise ValueError(f"min_cutoff {min_cutoff} is greater than max_cutoff {max_cutoff}")
        self.sequence_records = sequence_records
        self.min_cutoff = min_cutoff
        self.max_cutoff = max_cutoff

    def records(self) -> Iterator[SequenceRecord]:
        for record in self.sequence_records.records():
            length = len(record.sequence)
            if length < self.min_cutoff:
                continue
            if self.max_cutoff is not None and length > self.max_cutoff:
                continue
            yield record
