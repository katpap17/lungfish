"""Simple Factory: maps a file extension to a concrete reader."""

from pathlib import Path

from lungfish.reader.fasta import FastaReader
from lungfish.reader.sequencereader import SequenceReader


def new_reader(filepath: str | Path) -> SequenceReader:
    match Path(filepath).suffix:
        case ".fasta" | ".fa" | ".fna":
            return FastaReader(filepath)
        case _:
            raise ValueError("Unknown filetype")
