"""Regression cases for the two observed capture-dimension failures."""
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from check_capture import png_dimensions


def png(width, height):
    def chunk(kind, body):
        return (struct.pack('>I', len(body)) + kind + body
                + struct.pack('>I', zlib.crc32(kind + body)))
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    rows = (b'\0' + b'\0\0\0' * width) * height
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header)
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.image = Path(self.tmp.name) / 'capture.png'

    def run_check(self, actual, expected):
        self.image.write_bytes(png(*actual))
        return subprocess.run([sys.executable, str(Path(__file__).with_name('check_capture.py')),
                               str(self.image), '--width', str(expected[0]),
                               '--height', str(expected[1])], capture_output=True, text=True)

    def test_measured_size_matches_capture(self):
        self.assertEqual(self.run_check((1100, 760), (1100, 760)).returncode, 0)
        self.assertEqual(png_dimensions(self.image), (1100, 760))

    def test_desktop_padding_is_rejected_against_measured_window(self):
        self.assertEqual(self.run_check((1440, 960), (1100, 760)).returncode, 1)

    def test_cut_off_large_window_is_rejected(self):
        self.assertEqual(self.run_check((1100, 760), (1440, 960)).returncode, 1)

    def test_bad_or_truncated_header_is_rejected(self):
        self.image.write_bytes(png(4, 4)[:20])
        with self.assertRaisesRegex(ValueError, 'complete IHDR'):
            png_dimensions(self.image)
        data = bytearray(png(4, 4))
        data[18] ^= 1
        self.image.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            png_dimensions(self.image)


if __name__ == '__main__':
    unittest.main()
