#!/usr/bin/env python3
"""
Render the favicon's design as a PNG: the apple-touch-icon Messages shows beside a link.

    python3 tools/icon.py icon-2.png

The favicon in index.html is an inline SVG - a 32-unit rounded square in the header blue with
the H of the wordmark in the ink colour, hanging from its cord - and link previews ignore inline
SVG. This draws the same thing at 180x180, full bleed (iOS rounds the corners itself), with 4x
supersampling on the edges. The cord comes down from the top edge between the stems to the
crossbar, as the wordmark's does, at the risers' 55% (icon-2, 1.11.15). Standard library only. Change the design, change the filename: iMessage caches a
preview per URL.
"""
import struct, sys, zlib

SIZE, SS = 180, 4                       # output pixels, supersample factor
# the header blue behind the ink; --test swaps it for the weight orange, so a branch preview's
# link card reads orange in Messages and cannot be mistaken for the live game.
BG, INK = (0x16, 0x1d, 0x4a), (0xdf, 0xe6, 0xff)
TEST_BG = (0xc9, 0x8f, 0x4a)
# the H, in the favicon's 32-unit space: two stems and a crossbar, at full ink; and the cord,
# from the top edge down to the crossbar, at the wordmark's riser strength
RECTS = [(8, 7, 13.5, 25, 1.0), (18.5, 7, 24, 25, 1.0), (13.5, 13.25, 18.5, 17.75, 1.0),
         (15.4, 0, 16.6, 13.25, 0.55)]


def inside(x, y):
    return max((k for x0, y0, x1, y1, k in RECTS if x0 <= x < x1 and y0 <= y < y1), default=0.0)


def render(bg=BG):
    k = 32.0 / (SIZE * SS)
    rows = []
    for py in range(SIZE):
        row = bytearray()
        for px in range(SIZE):
            hit = 0
            for sy in range(SS):
                for sx in range(SS):
                    hit += inside((px * SS + sx + 0.5) * k, (py * SS + sy + 0.5) * k)
            t = hit / (SS * SS)
            row += bytes(round(b + (i - b) * t) for b, i in zip(bg, INK))
        rows.append(bytes(row))
    return rows


def png(rows):
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    raw = b"".join(b"\x00" + r for r in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--test"]
    test = "--test" in sys.argv
    out = args[0] if args else ("icon-test.png" if test else "icon-2.png")
    open(out, "wb").write(png(render(TEST_BG if test else BG)))
    print("wrote", out)
