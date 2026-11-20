#!/usr/bin/env python3
"""Entry for make.fun's news-image-20261119: sum up 19 November 2026's world
news in one image.

Thursday 19 November 2026, as reported that day: Trump, Xi and Putin shake
hands as leaders gather in Beijing for the APEC 2026 summit; Democrats
nominate Hakeem Jeffries, set to become the first Black Speaker of the House,
and win Alaska to take the Senate 56-44; the Crimean Bridge is attacked again;
a Van Gogh sells for a record $190.4m; Anthropic raises $81.3bn in the biggest
IPO of all time; Voyager 1 reaches one light-day, fifty years after launch;
GTA VI begins its global rollout; the EU proposes a 45bn euro Ukraine loan;
Israeli tanks cross the Gaza ceasefire line; Myanmar faces a genocide verdict
at the UN court; Cyclone Akvan nears the Indian coast -- and thirty more
stories besides, from seven regions.

The picture in assets/entry.png is a broadsheet front page drawn for that
day: a masthead naming Thursday 19 November 2026, the Beijing summit as the
lead story beside a drawn world map marking seven regions, three hero
pictures (the Beijing handshake, Van Gogh's record $190.4m sale, Voyager 1
at one light-day), a grid of 28 sourced stories across seven regions, and a
numbered "In Brief" band of 12 more -- 41 stories in all, every item
carrying its source, so a reader who missed the day can tell what happened
from the page alone.

This program validates the bundled image against the competition's own caps
(real PNG, at most 1024x1024, at most 1 MiB) and writes it, byte for byte, to
<output>/entry.png. It touches no network and is fully deterministic: run it
twice and both runs produce identical bytes.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1_048_576  # 1 MiB
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Read width and height from the IHDR chunk of a PNG byte string."""
    if data[:8] != PNG_MAGIC:
        raise ValueError("asset is not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("asset is missing its IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def png_is_whole(data: bytes) -> bool:
    """True when the PNG ends with a complete IEND chunk (no truncation)."""
    if len(data) < 12 or data[-12:-8] != b"\x00\x00\x00\x00":
        return False
    return data[-8:-4] == b"IEND" and data[-4:] == b"\xaeB`\x82"


def load_validated_image(path: str) -> bytes:
    """Read the asset and refuse it unless it fits the competition caps."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        raise ValueError(f"asset is {len(data)} bytes, over the {MAX_BYTES} cap")
    width, height = png_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"asset is {width}x{height}, over the {MAX_SIDE}px cap")
    if not png_is_whole(data):
        raise ValueError("asset is a truncated PNG (no complete IEND chunk)")
    return data


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    asset = os.path.join(here, "assets", "entry.png")
    data = load_validated_image(asset)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as fh:
        fh.write(data)

    digest = hashlib.sha256(data).hexdigest()

    # Read the written file back and prove it is byte-identical to the
    # validated asset, so a short or corrupted write can never slip through.
    with open(out_path, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != digest:
        raise ValueError("written file does not match the validated asset")

    width, height = png_dimensions(data)
    print(f"wrote {out_path}: {len(data)} bytes, {width}x{height}, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
