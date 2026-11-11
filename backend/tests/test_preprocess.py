from io import BytesIO
import struct
import zlib

import pytest
from PIL import Image

from app.services.preprocess import build_transform, load_image
from app.utils.errors import InvalidImageError


def test_transform_shape():
    transform = build_transform(224, [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    image = Image.new("RGB", (640, 480), (120, 60, 30))
    assert transform(image).shape == (3, 224, 224)


def test_exif_rotation_is_applied():
    image = Image.new("RGB", (60, 40), (200, 100, 50))
    exif = image.getexif()
    exif[274] = 6  # orientation: rotate 90 degrees
    buffer = BytesIO()
    image.save(buffer, format="JPEG", exif=exif)

    loaded = load_image(buffer.getvalue())
    assert loaded.size == (40, 60)


def test_corrupt_bytes_raise():
    with pytest.raises(InvalidImageError):
        load_image(b"this is not an image")


def _png_with_size(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00")
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", idat)
        + chunk(b"IEND", b"")
    )


def test_huge_dimensions_are_rejected_before_decode():
    with pytest.raises(InvalidImageError):
        load_image(_png_with_size(7000, 7000))
