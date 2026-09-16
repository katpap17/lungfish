"""Trims the low-quality end off each read using a sliding window."""

from collections.abc import Iterator
from dataclasses import replace

from lungfish.reader.sequencereader import SequenceReader
from lungfish.sequencerecord import SequenceRecord

# FASTQ stores each score as the character with code (score + 33).
PHRED_OFFSET = 33


class QualityTrim:
    def __init__(
        self,
        sequence_records: SequenceReader,
        *,
        quality_cutoff: int = 20,
        window_size: int = 4,
    ):
        if window_size < 1:
            raise ValueError(f"window_size must be at least 1, got {window_size}")
        self.sequence_records = sequence_records
        self.quality_cutoff = quality_cutoff
        self.window_size = window_size

    def records(self) -> Iterator[SequenceRecord]:
        for record in self.sequence_records.records():
            # FASTA and GenBank records have no quality scores, so there is nothing to trim.
            if record.quality is None:
                yield record
                continue

            scores = [ord(char) - PHRED_OFFSET for char in record.quality]

            # Cut at the start of the first window whose average falls below the cutoff.
            cut = len(scores)
            for start in range(len(scores)):
                window = scores[start : start + self.window_size]
                if sum(window) / len(window) < self.quality_cutoff:
                    cut = start
                    break

            yield replace(record, sequence=record.sequence[:cut], quality=record.quality[:cut])
