from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

PPT_EXTENSIONS = {".ppt", ".pptx"}
CONVERT_TIMEOUT_SECONDS = 120
SOFFICE_INSTALL_HINT = "sudo dnf install libreoffice-headless"


class SofficeNotFoundError(FileNotFoundError):
    """Raised when neither soffice nor libreoffice is on PATH."""


@dataclass
class ConversionResult:
    converted: list[Path] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)
    failed: list[tuple[Path, str]] = field(default_factory=list)


def find_soffice() -> Path:
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return Path(found)
    raise SofficeNotFoundError(
        "LibreOffice was not found on PATH (looked for 'soffice' and 'libreoffice'). "
        f"On Fedora, install it with: {SOFFICE_INSTALL_HINT}"
    )


def resolve_folder(folder: Path) -> Path:
    resolved = folder.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Folder does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Not a directory: {resolved}")
    return resolved


def is_powerpoint(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in PPT_EXTENSIONS


def convert_file(source: Path, soffice: Path) -> None:
    outdir = source.parent
    cmd = [
        str(soffice),
        "--headless",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        str(outdir),
        str(source),
    ]
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=CONVERT_TIMEOUT_SECONDS,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "unknown error").strip()
        raise RuntimeError(detail)

    pdf = source.with_suffix(".pdf")
    if not pdf.is_file():
        raise RuntimeError("LibreOffice finished but the PDF was not created")


def convert_folder(
    folder: Path,
    *,
    skip_existing: bool = False,
    dry_run: bool = False,
    soffice: Path | None = None,
) -> ConversionResult:
    folder = resolve_folder(folder)
    soffice_bin = None if dry_run else (soffice or find_soffice())

    result = ConversionResult()
    entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())

    for path in entries:
        if path.is_dir():
            continue
        if not is_powerpoint(path):
            result.skipped.append((path, "not a .ppt or .pptx file"))
            continue

        pdf = path.with_suffix(".pdf")
        if skip_existing and pdf.is_file():
            result.skipped.append((path, "PDF already exists"))
            continue

        if dry_run:
            result.converted.append(path)
            continue

        assert soffice_bin is not None
        try:
            convert_file(path, soffice_bin)
        except subprocess.TimeoutExpired:
            result.failed.append(
                (path, f"timed out after {CONVERT_TIMEOUT_SECONDS}s")
            )
        except Exception as exc:
            result.failed.append((path, str(exc)))
        else:
            result.converted.append(path)

    return result
