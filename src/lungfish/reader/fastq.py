"""Reader for the FASTQ format."""

from collections.abc import Iterable, Iterator
from pathlib import Path

from lungfish.sequencerecord import SequenceRecord


class FastqReader:
    def __init__(self, filepath: str | Path):
        self.filepath = filepath

    def records(self) -> Iterator[SequenceRecord]:
        with open(self.filepath) as fh:
            yield from self._parse_fastq(fh)

    def _parse_fastq(self, lines: Iterable[str]) -> Iterator[SequenceRecord]:
        # Fixed four lines per record. FASTQ cannot be parsed by line prefix the
        # way FASTA can, because '@' and '+' are both legal quality characters.
        stream = iter(lines)

        for header in stream:
            header = header.strip()
            if not header:
                continue
            if not header.startswith("@"):
                raise ValueError(f"expected '@' header, got {header[:20]!r}")

            try:
                sequence = next(stream).strip()
                separator = next(stream).strip()
                quality = next(stream).strip()
            except StopIteration:
                raise ValueError(f"truncated record: {header[:20]!r}") from None

            if not separator.startswith("+"):
                raise ValueError(f"expected '+' separator, got {separator[:20]!r}")
            if len(sequence) != len(quality):
                raise ValueError(
                    f"quality length {len(quality)} does not match sequence "
                    f"length {len(sequence)} in {header[:20]!r}"
                )

            seq_id, _, rest = header[1:].partition(" ")
            yield SequenceRecord(seq_id, rest.strip(), sequence, quality)
