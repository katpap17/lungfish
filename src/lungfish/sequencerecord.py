"""Sequence Record definition"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SequenceRecord:
    id: str
    description: str
    sequence: str
    quality: str | None = None
