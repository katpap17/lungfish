"""Reader for the FASTA format."""

from collections.abc import Iterable, Iterator
from pathlib import Path

from lungfish.sequencerecord import SequenceRecord


class FastaReader:
    def __init__(self, filepath: str | Path):
        self.filepath = filepath

    def records(self) -> Iterator[SequenceRecord]:
        with open(self.filepath) as fh:
            yield from self._parse_fasta(fh)

    def _parse_fasta(self, lines: Iterable[str]) -> Iterator[SequenceRecord]:
        seq_id: str | None = None
        description = ""
        chunks: list[str] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                # A record is only complete once the *next* header appears,
                # because FASTA sequences span multiple lines.
                if seq_id is not None:
                    yield SequenceRecord(seq_id, description, "".join(chunks))
                seq_id, _, rest = line[1:].partition(" ")
                description = rest.strip()
                chunks = []
            else:
                chunks.append(line)

        # Flushes the final record, which has no following header to trigger it.
        if seq_id is not None:
            yield SequenceRecord(seq_id, description, "".join(chunks))
