"""The interface every sequence reader shares."""

from collections.abc import Iterator
from typing import Protocol

from lungfish.sequencerecord import SequenceRecord


class SequenceReader(Protocol):
    def records(self) -> Iterator[SequenceRecord]:
        ...
