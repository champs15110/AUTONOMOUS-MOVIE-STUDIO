"""
Generate the studio's image textures locally with pure Python (no Blender):

  06_ASSETS/textures/gauge_dial.png  - WICK's chest dial: 0-100 tick ring,
                                       red arc over the 0-40 danger zone.
  06_ASSETS/textures/noise_tile.png  - seamless-ish value-noise bump tile.

Run:  python3 06_ASSETS/scripts/make_textures.py
"""

import math
import os
import random
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "textures"))


def write_png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw.extend(px[y * w * 4:(y + 1) * w * 4])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


def gauge_dial(size=512):
    px = bytearray(size * size * 4)
    cx = cy = size / 2
    R = size * 0.46

    def angle(v):  # value 0..100 -> radians; 270 degree sweep, 0 at lower-left
        return math.radians(225 - 2.7 * v)

    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, cy - y
            d = math.hypot(dx, dy)
            r = g = b = a = 0
            if d <= R:
                # aged dark brass face
                r, g, b = 26, 20, 12
                a = 255
                ang = math.degrees(math.atan2(dy, dx)) % 360
                # value from angle (inverse of angle())
                val = (225 - ang) / 2.7 if ang <= 225 else (225 - ang + 360) / 2.7
                if 0 <= val <= 100:
                    # red danger arc 0-40 near rim
                    if val <= 40 and R * 0.80 <= d <= R * 0.92:
                        r, g, b = 160, 22, 18
                    # ticks
                    minor = abs(val / 2 - round(val / 2)) < 0.06
                    major = abs(val / 10 - round(val / 10)) < 0.03
                    if major and R * 0.70 <= d <= R * 0.92:
                        r, g, b = 235, 225, 200
                    elif minor and R * 0.80 <= d <= R * 0.92:
                        r, g, b = 190, 180, 150
                # rim
                if d >= R * 0.94:
                    r, g, b = 90, 70, 35
                # hub
                if d <= R * 0.07:
                    r, g, b = 120, 95, 50
            i = (y * size + x) * 4
            px[i:i + 4] = bytes((r, g, b, a))
    return px


def noise_tile(size=256, grid=16, seed=92):
    rnd = random.Random(seed)
    g = [[rnd.random() for _ in range(grid + 1)] for _ in range(grid + 1)]

    def smooth(t):
        return t * t * (3 - 2 * t)

    px = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            fx = x / size * grid
            fy = y / size * grid
            x0, y0 = int(fx), int(fy)
            tx, ty = smooth(fx - x0), smooth(fy - y0)
            x1, y1 = min(x0 + 1, grid), min(y0 + 1, grid)
            v = (g[y0][x0] * (1 - tx) + g[y0][x1] * tx) * (1 - ty) + \
                (g[y1][x0] * (1 - tx) + g[y1][x1] * tx) * ty
            c = int(60 + 140 * v)
            i = (y * size + x) * 4
            px[i:i + 4] = bytes((c, c, c, 255))
    return px


def main():
    os.makedirs(OUT, exist_ok=True)
    write_png(os.path.join(OUT, "gauge_dial.png"), 512, 512, gauge_dial())
    write_png(os.path.join(OUT, "noise_tile.png"), 256, 256, noise_tile())
    for f in ("gauge_dial.png", "noise_tile.png"):
        p = os.path.join(OUT, f)
        print(f, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
