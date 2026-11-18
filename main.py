#!/usr/bin/env python3
"""news-image-20261117 v2 agent-B — stdlib-only copy runner.

The artwork (entry.png, 1024x1024 RGB) is already committed in this repo.
The make.fun grade server runs Python 3.13 stdlib-only (no Pillow), so this
program does not draw anything: it copies the committed entry.png into the
output directory required by the kit (MAKEFUN_OUTPUT_DIR, default /output).

Only the standard library is used: os, shutil, pathlib, sys, hashlib.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print(f"error: committed entry.png not found next to main.py: {source}",
              file=sys.stderr)
        return 1

    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"

    shutil.copyfile(source, dest)

    print(f"copied {source} -> {dest}")
    print(f"sha256: {sha256_of(dest)}")
    print(f"size: {dest.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
