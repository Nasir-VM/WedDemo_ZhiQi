from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "icons"


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def make_icon(size: int, path: Path, maskable: bool = False) -> None:
    bg = (27, 57, 181, 255)
    fg = (255, 255, 255, 255)
    accent = (147, 197, 253, 255)
    rows = []
    margin = size * 0.22 if maskable else size * 0.14
    bar_w = size * 0.12
    gap = size * 0.06
    start_x = (size - (bar_w * 3 + gap * 2)) / 2
    for y in range(size):
        row = bytearray()
        for x in range(size):
            color = bg

            heights = [0.28, 0.42, 0.56]
            for index, height in enumerate(heights):
                bx = start_x + index * (bar_w + gap)
                by = size - margin - size * height
                if bx <= x < bx + bar_w and by <= y < size - margin:
                    color = fg if index == 2 else accent
            if margin <= x < size - margin and margin <= y < margin + size * 0.08:
                color = fg
            row.extend(color)
        rows.append(bytes(row))
    raw = b"".join(b"\x00" + row for row in rows)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    make_icon(192, OUT / "icon-192.png")
    make_icon(512, OUT / "icon-512.png")
    make_icon(512, OUT / "icon-maskable-512.png", maskable=True)
    print("icons generated")
