# lungfish 🐟

A small toolkit for reading, filtering and inspecting sequence files (FASTA, FASTQ, GenBank).

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```
make install
```

## Usage

```
uv run lungfish FILE [--quality-cutoff Q] [--window-size N] [--min-length N] [--max-length N]
```

Reads `FILE`, trims low-quality read ends, drops any records outside the length range, and prints the rest in FASTA format.

| Option | Default | Effect |
|---|---|---|
| `FILE` | required | Sequence file to read. Format is chosen by extension (see below). |
| `--quality-cutoff Q` | `20` | Trim each read at the first window whose average quality is below `Q`. `0` disables trimming. |
| `--window-size N` | `4` | Number of bases averaged per window when trimming. |
| `--min-length N` | `0` | Drop records shorter than `N` bases. |
| `--max-length N` | no limit | Drop records longer than `N` bases. |
| `-h`, `--help` | | Show usage and exit. |

### How the steps combine

1. **Quality trimming** runs first. Each read is cut at the first window of `--window-size` bases whose average quality is below `--quality-cutoff`; everything from that point on is removed. Only FASTQ has quality scores, so FASTA and GenBank records pass through untouched.
2. **Length filtering** runs on the trimmed reads. Both limits are inclusive: a record of exactly `N` bases is kept. `--min-length` must not be greater than `--max-length`.

Because trimming comes first, a read can be trimmed down to nothing. Use `--min-length 1` or higher to drop those.

### Examples

```
# print every record, trimmed at the default quality cutoff (20)
uv run lungfish reads.fastq

# print every record without any trimming
uv run lungfish reads.fastq --quality-cutoff 0

# stricter trimming, then drop reads left shorter than 30 bases
uv run lungfish reads.fastq --quality-cutoff 30 --min-length 30

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
