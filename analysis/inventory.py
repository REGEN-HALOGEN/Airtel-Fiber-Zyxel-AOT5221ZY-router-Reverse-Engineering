#!/usr/bin/env python3
"""Read-only SHA-256, duplicate, and format inventory for supplied artifacts."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "files"
OUT = ROOT / "analysis" / "reports"


def format_of(path: Path, head: bytes) -> str:
    ext = path.suffix.lower()
    if head.startswith(b"\x7fELF"):
        cls = {1: "ELF32", 2: "ELF64"}.get(head[4], "ELF")
        endian = {1: "little-endian", 2: "big-endian"}.get(head[5], "unknown-endian")
        machine = "unknown"
        if len(head) >= 20:
            e = "<" if head[5] == 1 else ">"
            machine = {183: "AArch64", 40: "ARM", 62: "x86-64", 3: "x86"}.get(struct.unpack(e + "H", head[18:20])[0], str(struct.unpack(e + "H", head[18:20])[0]))
        return f"{cls} {endian} {machine}"
    if head.startswith(b"\xd0\x0d\xfe\xed") or head.startswith(b"\xed\xfe\x0d\xd0"):
        return "Device Tree Blob"
    if head.startswith(b"hsqs"):
        return "SquashFS"
    if head.startswith(b"UBI#"):
        return "UBI erase-counter header"
    if head.startswith(b"UBI!"):
        return "UBI volume identifier header"
    if head.startswith(b"070701") or head.startswith(b"070702"):
        return "cpio newc archive"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP archive"
    if head.startswith(b"<?xml") or head.lstrip().startswith(b"<"):
        return "XML/text (signature heuristic)"
    if head.startswith(b"\x5d\x00\x00"):
        return "LZMA-alone candidate (properties signature)"
    if head.startswith(b"\x1f\x8b"):
        return "gzip"
    if head.startswith(b"FIT\x0d\x0a\x00"):
        return "FIT image"
    if ext in {".so", ".ko"}:
        return f"Unknown binary ({ext} extension)"
    if ext in {".lz", ".rdm", ".bin"}:
        return f"Unknown binary ({ext} extension)"
    try:
        head.decode("utf-8")
        if b"\x00" not in head:
            return "UTF-8 text (heuristic)"
    except UnicodeDecodeError:
        pass
    return "Unknown binary/data"


def main() -> None:
    if not SOURCE.is_dir():
        raise SystemExit(f"Source directory does not exist: {SOURCE}")
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in SOURCE.rglob("*") if p.is_file())
    records = []
    by_hash: dict[str, list[str]] = defaultdict(list)
    for p in files:
        h = hashlib.sha256()
        with p.open("rb") as f:
            head = f.read(4096)
            h.update(head)
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
        digest = h.hexdigest()
        rel = p.relative_to(SOURCE).as_posix()
        by_hash[digest].append(rel)
        records.append({
            "path": rel,
            "size_bytes": p.stat().st_size,
            "sha256": digest,
            "format": format_of(p, head),
        })
    with (OUT / "binary-inventory.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["path", "size_bytes", "sha256", "format"])
        w.writeheader()
        w.writerows(records)
    duplicates = [{"sha256": digest, "paths": paths} for digest, paths in sorted(by_hash.items()) if len(paths) > 1]
    summary = {
        "source_directory": str(SOURCE),
        "file_count": len(records),
        "total_bytes": sum(r["size_bytes"] for r in records),
        "files_with_duplicate_content": sum(len(d["paths"]) for d in duplicates),
        "duplicate_groups": duplicates,
        "format_counts": dict(sorted(__import__("collections").Counter(r["format"] for r in records).items())),
    }
    (OUT / "inventory-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (OUT / "inventory-summary.md").open("w", encoding="utf-8", newline="\n") as f:
        f.write("# Artifact inventory summary\n\n")
        f.write(f"- Source: `{SOURCE}`\n- Files: {len(records)}\n- Total size: {summary['total_bytes']:,} bytes\n")
        f.write(f"- Files in duplicate-content groups: {summary['files_with_duplicate_content']}\n\n")
        f.write("## Format counts\n\n| Detected format | Count |\n|---|---:|\n")
        for fmt, count in summary["format_counts"].items():
            f.write(f"| {fmt} | {count} |\n")
        f.write("\n## Exact duplicate groups (SHA-256)\n\n")
        if duplicates:
            for d in duplicates:
                f.write(f"- `{d['sha256']}`: " + ", ".join(f"`{p}`" for p in d["paths"]) + "\n")
        else:
            f.write("None found.\n")
        f.write("\nDetailed per-file hashes and format guesses are in `binary-inventory.csv`.\n")
    print(f"Inventoried {len(records)} files ({summary['total_bytes']} bytes); duplicate groups: {len(duplicates)}")
    print(f"Reports: {OUT}")


if __name__ == "__main__":
    main()
