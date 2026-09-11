"""Sequence Record definition"""

from dataclasses import dataclass

@dataclass
class SequenceRecord:
    id : str
    sequence: str
    quality: str | None = None