"""Minimal entry point: read a sequence file and print its records."""

import sys

from lungfish.reader.factory import new_reader


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: lungfish <file>")

    reader = new_reader(sys.argv[1])
    for record in reader.records():
        print(f">{record.id} {record.description}")
        print(record.sequence)
