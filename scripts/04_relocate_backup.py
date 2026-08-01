"""Copy every decrypted iOS-backup file into its manifest-mapped path."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import shutil
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "data" / "decrypted"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "extracted" / "backup"
METADATA_FILES = ("Manifest.db", "Manifest.plist", "Info.plist", "Status.plist")


@dataclass(frozen=True)
class BackupRecord:
    file_id: str
    domain: str
    relative_path: str


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true", help="replace existing files")
    parser.add_argument("--dry-run", action="store_true", help="report work without copying")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    manifest = source / "Manifest.db"
    if not manifest.is_file():
        parser.error(f"Manifest database does not exist: {manifest}")
    if output.is_relative_to(source):
        parser.error("Output directory must not be inside the decrypted backup")

    records, directories, symbolic_links = manifest_records(manifest)
    copied = skipped = missing = total_bytes = 0
    index_rows: list[tuple[str, str, str, str, str]] = []

    if not args.dry_run:
        output.mkdir(parents=True, exist_ok=True)
        for directory in directories:
            (output / safe_relative_path(directory)).mkdir(parents=True, exist_ok=True)

    for record in records:
        source_file = source / record.file_id[:2] / record.file_id
        destination = output / safe_relative_path(record, use_file_id_when_empty=True)
        if not source_file.is_file():
            missing += 1
            index_rows.append((*record_tuple(record), str(destination.relative_to(output)), "missing"))
            continue

        total_bytes += source_file.stat().st_size
        if destination.exists() and not args.overwrite:
            skipped += 1
            index_rows.append((*record_tuple(record), str(destination.relative_to(output)), "existing"))
            continue

        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)
        copied += 1
        index_rows.append((*record_tuple(record), str(destination.relative_to(output)), "copied"))

    metadata_copied = copy_metadata(source, output, args.dry_run, args.overwrite)
    if not args.dry_run:
        write_index(output / "manifest-index.tsv", index_rows)

    mode = "Dry run" if args.dry_run else "Completed"
    print(f"{mode}: {copied} file(s) {'would be copied' if args.dry_run else 'copied'}")
    print(f"Existing skipped: {skipped}; missing source files: {missing}")
    print(f"Metadata files {'found' if args.dry_run else 'copied'}: {metadata_copied}")
    print(f"Directories {'to recreate' if args.dry_run else 'recreated'}: {len(directories)}")
    print(f"Symbolic-link records kept in metadata only: {symbolic_links}")
    print(f"Regular-file payload: {format_bytes(total_bytes)}")
    print(f"Output: {output}")


def manifest_records(manifest: Path) -> tuple[list[BackupRecord], list[BackupRecord], int]:
    database_uri = f"{manifest.as_uri()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        records = [
            BackupRecord(*row)
            for row in connection.execute(
                "SELECT fileID, domain, relativePath FROM Files "
                "WHERE flags = 1 ORDER BY domain, relativePath"
            )
        ]
        directories = [
            BackupRecord(*row)
            for row in connection.execute(
                "SELECT fileID, domain, relativePath FROM Files "
                "WHERE flags = 2 ORDER BY domain, relativePath"
            )
        ]
        symbolic_links = connection.execute(
            "SELECT COUNT(*) FROM Files WHERE flags NOT IN (1, 2)"
        ).fetchone()[0]
    return records, directories, symbolic_links


def safe_relative_path(record: BackupRecord, *, use_file_id_when_empty: bool = False) -> Path:
    path = PurePosixPath(record.relative_path)
    if not path.parts and use_file_id_when_empty:
        path = PurePosixPath(record.file_id)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe manifest path for {record.file_id}: {record.relative_path!r}")
    domain = record.domain.replace("/", "_")
    if not domain or domain in {".", ".."}:
        raise ValueError(f"Unsafe manifest domain for {record.file_id}: {record.domain!r}")
    return Path(domain, *path.parts)


def copy_metadata(source: Path, output: Path, dry_run: bool, overwrite: bool) -> int:
    metadata_count = 0
    for name in METADATA_FILES:
        source_file = source / name
        destination = output / "metadata" / name
        if not source_file.is_file() or (destination.exists() and not overwrite):
            continue
        metadata_count += 1
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)
    return metadata_count


def write_index(path: Path, rows: list[tuple[str, str, str, str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as index_file:
        writer = csv.writer(index_file, delimiter="\t")
        writer.writerow(("file_id", "domain", "relative_path", "extracted_path", "status"))
        writer.writerows(rows)


def record_tuple(record: BackupRecord) -> tuple[str, str, str]:
    return record.file_id, record.domain, record.relative_path


def format_bytes(byte_count: int) -> str:
    value = float(byte_count)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
