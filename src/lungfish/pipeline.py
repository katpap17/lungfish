"""Minimal entry point: read a sequence file, filter it, and print its records."""

import argparse

from lungfish.filter.length import LengthFilter
from lungfish.filter.quality import QualityTrim
from lungfish.reader.factory import new_reader
from lungfish.reader.sequencereader import SequenceReader


def main() -> None:
    parser = argparse.ArgumentParser(prog="lungfish")
    parser.add_argument("file", help="FASTA, FASTQ or GenBank file")
    parser.add_argument("--min-length", type=int, default=0, help="drop records shorter than this")
    parser.add_argument("--max-length", type=int, default=None, help="drop records longer than this")
    parser.add_argument("--quality-cutoff", type=int, default=20, help="trim reads where window quality drops below this (0 disables)")
    parser.add_argument("--window-size", type=int, default=4, help="number of bases averaged when trimming")
    args = parser.parse_args()

    reader = new_reader(args.file)
    filtered: SequenceReader = QualityTrim(reader, quality_cutoff=args.quality_cutoff, window_size=args.window_size)
    filtered = LengthFilter(filtered, min_cutoff=args.min_length, max_cutoff=args.max_length)

    for record in filtered.records():
        print(f">{record.id} {record.description}")
        print(record.sequence)
