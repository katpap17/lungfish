# lungfish 🐟

A small toolkit for reading, filtering and inspecting sequence files (FASTA, FASTQ, GenBank).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```
make install
```

## Usage

```
uv run lungfish FILE [--min-length N] [--max-length N]
```

Reads `FILE`, drops any records outside the length range, and prints the rest in FASTA format.

| Option | Default | Effect |
|---|---|---|
| `FILE` | required | Sequence file to read. Format is chosen by extension (see below). |
| `--min-length N` | `0` | Drop records shorter than `N` bases. |
| `--max-length N` | no limit | Drop records longer than `N` bases. |
| `-h`, `--help` | | Show usage and exit. |

Both limits are inclusive: a record of exactly `N` bases is kept. `--min-length` must not be greater than `--max-length`.

### Examples

```
# print every record
uv run lungfish reads.fastq

# keep reads of at least 50 bases
uv run lungfish reads.fastq --min-length 50

# keep reads between 50 and 300 bases
uv run lungfish reads.fastq --min-length 50 --max-length 300
```

### Supported formats

| Format | Extensions |
|---|---|
| FASTA | `.fasta`, `.fa`, `.fna` |
| FASTQ | `.fastq`, `.fq` |
| GenBank | `.gb`, `.gbk`, `.gbff`, `.genbank` |

Extensions are case-sensitive, so `reads.FASTQ` is rejected. Output is always FASTA: FASTQ quality scores and GenBank feature annotations are not printed.

## Development

| Command | Effect |
|---|---|
| `make` | List all commands |
| `make test` | Run the test suite |
| `make typecheck` | Type-check with mypy (strict) |
| `make check` | Tests and type check |
| `make run FILE=reads.fastq` | Run the CLI on a file |
| `make clean` | Remove caches and build artifacts |

To run a single test file: `uv run pytest tests/test_length_filter.py`.

### Test data

Small fixtures live in `tests/data/` and are committed. Larger files are gitignored. To download one:

```
# Lambda phage, FASTA (~48 kb)
curl -o lambda.fasta "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001416.1&rettype=fasta&retmode=text"

# Lambda phage, GenBank
curl -o lambda.gb "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=NC_001416.1&rettype=gb&retmode=text"
```
