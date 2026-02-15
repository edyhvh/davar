#!/usr/bin/env python3
"""Generate a tileable noise texture PNG for the splash screen grain effect."""
import struct, zlib, random, os

random.seed(42)

def create_noise_png(width, height, filename):
    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r = random.random()
            if r < 0.30:
                brightness = random.randint(220, 255) if random.random() < 0.5 else random.randint(0, 50)
                alpha = random.randint(10, 38)
                raw.extend([brightness, brightness, brightness, alpha])
            else:
                raw.extend([0, 0, 0, 0])
    compressed = zlib.compress(bytes(raw), 9)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', ihdr))
        f.write(chunk(b'IDAT', compressed))
        f.write(chunk(b'IEND', b''))
    print(f'Created {filename} ({width}x{height}, {os.path.getsize(filename)} bytes)')

create_noise_png(150, 150, 'assets/images/noise-texture.png')
