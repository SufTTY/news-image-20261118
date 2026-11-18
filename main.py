#!/usr/bin/env python3
"""Copy the composed v2 front page (entry.png) to the output stage."""

# v2
import os
import shutil

MAX_SIZE = 1048576
FILE_NAME = "entry.png"
FALLBACK_DEST = "/output"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def find_source():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, FILE_NAME)


def looks_like_png(path):
    with open(path, "rb") as handle:
        return handle.read(len(PNG_MAGIC)) == PNG_MAGIC


def stage():
    target_root = os.environ.get("MAKEFUN_OUTPUT_DIR", FALLBACK_DEST)
    os.makedirs(target_root, exist_ok=True)
    source = find_source()
    if not os.path.isfile(source):
        raise SystemExit(f"source image not found: {source}")
    # PNG files start with a fixed 8-byte signature; anything else is rejected.
    if not looks_like_png(source):
        raise SystemExit(f"source is not a PNG file: {source}")
    target = os.path.join(target_root, FILE_NAME)
    shutil.copyfile(source, target)
    if os.path.getsize(target) > MAX_SIZE:
        raise SystemExit("entry.png is larger than the 1 MiB budget")


if __name__ == "__main__":
    stage()
