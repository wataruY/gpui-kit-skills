#!/usr/bin/env python3
"""Compare PNG header dimensions with supplied measured physical window bounds."""
import argparse
import json
from pathlib import Path
import struct
import zlib


def png_dimensions(path):
    with Path(path).open('rb') as stream:
        header = stream.read(33)
    if (len(header) != 33 or header[:8] != b'\x89PNG\r\n\x1a\n'
            or header[8:16] != b'\x00\x00\x00\rIHDR'):
        raise ValueError('Expected a PNG signature and complete IHDR header')
    if zlib.crc32(header[12:29]) != struct.unpack('>I', header[29:33])[0]:
        raise ValueError('Invalid PNG IHDR checksum')
    width, height = struct.unpack('>II', header[16:24])
    if not width or not height:
        raise ValueError('PNG dimensions must be positive')
    return width, height


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--width', type=int, required=True)
    parser.add_argument('--height', type=int, required=True)
    args = parser.parse_args()
    if args.width < 1 or args.height < 1:
        parser.error('Measured physical width and height must be positive')
    try:
        actual = png_dimensions(args.image)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    expected = (args.width, args.height)
    result = {'image': str(args.image), 'measured_window_pixels': list(expected),
              'png_header_pixels': list(actual),
              'result': 'match' if actual == expected else 'mismatch',
              'scope': 'header dimensions only; no capture, content or bounds-measurement validation'}
    print(json.dumps(result, indent=2))
    return 0 if actual == expected else 1


if __name__ == '__main__':
    raise SystemExit(main())
