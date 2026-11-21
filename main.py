#!/usr/bin/env python3
"""Entry point for the VELMARIS travel poster.

Copies the pre-rendered poster (entry.png, shipped in this repository)
into the output directory and verifies the copy byte-for-byte.

Standard library only; no network. Never deletes the output directory.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    dest = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(SOURCE):
        print(f"error: source poster not found: {SOURCE}", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SOURCE, dest)

    src_hash = sha256_of(SOURCE)
    dst_hash = sha256_of(dest)
    if src_hash != dst_hash:
        print("error: sha256 mismatch after copy", file=sys.stderr)
        return 1

    size = os.path.getsize(dest)
    print(f"wrote {dest} ({size} bytes, sha256 {dst_hash})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
