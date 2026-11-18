#!/usr/bin/env python3
"""Stage the composed front page into the output directory."""

import os
import shutil

LIMIT = 1048576
NAME = "entry.png"
FALLBACK = "/output"
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", FALLBACK)
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME)
    if not os.path.isfile(src):
        raise SystemExit(f"missing source: {src}")
    with open(src, "rb") as fh:
        if fh.read(len(SIGNATURE)) != SIGNATURE:
            raise SystemExit(f"not a png: {src}")
    dst = os.path.join(out_dir, NAME)
    shutil.copyfile(src, dst)
    if os.path.getsize(dst) > LIMIT:
        raise SystemExit("copy exceeds the 1 MiB budget")


if __name__ == "__main__":
    main()
