"""Minimal entry point: read a sequence file, filter it, and print its records."""

import argparse

from lungfish.filter.length import LengthFilter
from lungfish.reader.factory import new_reader


def main() -> None:
    parser = argparse.ArgumentParser(prog="lungfish")
    parser.add_argument("file", help="FASTA, FASTQ or GenBank file")
    parser.add_argument("--min-length", type=int, default=0, help="drop records shorter than this")
    parser.add_argument("--max-length", type=int, default=None, help="drop records longer than this")
    args = parser.parse_args()

    reader = new_reader(args.file)
    filtered = LengthFilter(reader, min_cutoff=args.min_length, max_cutoff=args.max_length)

    for record in filtered.records():
        print(f">{record.id} {record.description}")
        print(record.sequence)
