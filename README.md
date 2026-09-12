# ppt2pdf

A small Python CLI that converts every PowerPoint file in a folder to PDF.

Point it at a directory. It converts `.ppt` and `.pptx` files (case-insensitive), skips everything else, and writes each PDF next to the original with the same name.

```text
decks/
  kickoff.pptx   →  kickoff.pdf
  archive.ppt    →  archive.pdf
  notes.txt      (skipped)
  photo.png      (skipped)
```

Subfolders are not scanned. Conversion uses LibreOffice in headless mode, which is what makes both legacy `.ppt` and modern `.pptx` work on Linux.

## Requirements

- Python 3.10+
- [LibreOffice](https://www.libreoffice.org/) on your `PATH` (`soffice` or `libreoffice`)

On Fedora:

```bash
sudo dnf install libreoffice-headless
```

On Debian/Ubuntu:

```bash
sudo apt install libreoffice-nogui
```

## Install

From this repository:

```bash
pip install -e .
```

That exposes the `ppt2pdf` command.

You can also run it without installing:

```bash
python -m ppt_to_pdf /path/to/folder
```

## Usage

```bash
ppt2pdf /path/to/folder
```

| Flag | What it does |
| --- | --- |
| `--dry-run` | List what would be converted without calling LibreOffice |
| `--skip-existing` | Leave a PDF alone if it already exists next to the PowerPoint file |

By default, an existing PDF with the same name is overwritten.

Example:

```bash
ppt2pdf ~/Documents/slides --dry-run
ppt2pdf ~/Documents/slides --skip-existing
```

The command prints each converted, skipped, and failed file, then a summary. It exits with status `1` if the folder is invalid, LibreOffice is missing, or any conversion fails.

## How it works

For each PowerPoint file, the CLI runs:

```bash
soffice --headless --norestore --convert-to pdf --outdir "<folder>" "<file>"
```

Each conversion is given 120 seconds. If LibreOffice is not installed, the CLI tells you how to install it instead of failing with a generic error.
