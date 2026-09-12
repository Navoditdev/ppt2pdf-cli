from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ppt_to_pdf.convert import (
    SofficeNotFoundError,
    ConversionResult,
    convert_folder,
    find_soffice,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppt-to-pdf",
        description=(
            "Convert .ppt and .pptx files in a folder to PDFs. "
            "Other files are skipped. PDFs are written next to the originals."
        ),
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing PowerPoint files (not recursive)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Do not overwrite a PDF that already exists next to the PowerPoint file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List what would be converted without calling LibreOffice",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete each PowerPoint file after it converts successfully",
    )
    return parser


def print_result(result: ConversionResult, *, dry_run: bool) -> None:
    convert_verb = "Would convert" if dry_run else "Converted"
    delete_verb = "Would delete" if dry_run else "Deleted"
    deleted = {path for path in result.deleted}
    for path in result.converted:
        extra = f"; {delete_verb.lower()}" if path in deleted else ""
        print(f"{convert_verb}{extra}: {path.name}")
    for path, reason in result.skipped:
        print(f"Skipped: {path.name} ({reason})")
    for path, reason in result.failed:
        print(f"Failed: {path.name} ({reason})", file=sys.stderr)

    print(
        f"\nSummary: {len(result.converted)} converted, "
        f"{len(result.deleted)} deleted, "
        f"{len(result.skipped)} skipped, {len(result.failed)} failed"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if not args.dry_run:
            find_soffice()
        result = convert_folder(
            args.folder,
            skip_existing=args.skip_existing,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, NotADirectoryError, SofficeNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print_result(result, dry_run=args.dry_run)
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())
