#!/usr/bin/env python3
import math
import os
import random
import struct
import zlib

WIDTH = 1080
HEIGHT = 1920
OUT = "/Users/jhonny/davar/mobile/assets/images/splash-native-ios.png"

TOP_LEFT = (99, 137, 191)
MID = (168, 200, 240)
BOTTOM_RIGHT = (198, 143, 85)

random.seed(23)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mix(c1, c2, t: float):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


def add_color(base, overlay, alpha: float):
    r = int(base[0] * (1 - alpha) + overlay[0] * alpha)
    g = int(base[1] * (1 - alpha) + overlay[1] * alpha)
    b = int(base[2] * (1 - alpha) + overlay[2] * alpha)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def radial_alpha(x, y, cx, cy, radius):
    dx = x - cx
    dy = y - cy
    d = math.sqrt(dx * dx + dy * dy)
    if d >= radius:
        return 0.0
    t = 1.0 - (d / radius)
    return t * t


def png_chunk(ctype: bytes, data: bytes) -> bytes:
    payload = ctype + data
    return (
        struct.pack(">I", len(data))
        + payload
        + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


raw = bytearray()

for y in range(HEIGHT):
    raw.append(0)
    ny = y / (HEIGHT - 1)
    for x in range(WIDTH):
        nx = x / (WIDTH - 1)

        diag = (nx + ny) * 0.5
        c = mix(TOP_LEFT, MID, min(1.0, diag * 1.1))
        c = mix(c, BOTTOM_RIGHT, max(0.0, (diag - 0.45) / 0.55) * 0.45)

        top_alpha = radial_alpha(x, y, WIDTH * 0.96, HEIGHT * 0.08, WIDTH * 0.82) * 0.70
        c = add_color(c, (198, 143, 85), top_alpha)

        bottom_alpha = radial_alpha(x, y, WIDTH * 0.08, HEIGHT * 0.92, WIDTH * 0.78) * 0.72
        c = add_color(c, (61, 90, 140), bottom_alpha)

        center_alpha = radial_alpha(x, y, WIDTH * 0.5, HEIGHT * 0.56, WIDTH * 0.54) * 0.25
        c = add_color(c, (200, 216, 240), center_alpha)

        grain = random.randint(-12, 12)
        grain = int(grain * 0.55)
        r = max(0, min(255, c[0] + grain))
        g = max(0, min(255, c[1] + grain))
        b = max(0, min(255, c[2] + grain))

        raw.extend((r, g, b, 255))

image_data = zlib.compress(bytes(raw), level=9)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0)
    f.write(png_chunk(b"IHDR", ihdr))
    f.write(png_chunk(b"IDAT", image_data))
    f.write(png_chunk(b"IEND", b""))

print(f"Created {OUT} ({WIDTH}x{HEIGHT})")
