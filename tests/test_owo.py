"""Tests for exact raw and RLE round trips."""

from PIL import Image

from owo import decode, encode


def sample_image() -> Image.Image:
    return Image.frombytes(
        "RGBA",
        (4, 3),
        bytes([
            255, 0, 0, 255, 255, 0, 0, 255, 0, 0, 255, 255, 0, 0, 255, 255,
            0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255,
            0, 0, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 255, 255,
        ]),
    )


def test_raw_round_trip(tmp_path):
    original = sample_image()
    path = tmp_path / "image.owo"
    encode(original, path, "raw")
    restored = decode(path)
    assert restored.mode == original.mode
    assert restored.size == original.size
    assert restored.tobytes() == original.tobytes()


def test_rle_round_trip(tmp_path):
    original = sample_image()
    path = tmp_path / "image-rle.owo"
    encode(original, path, "rle")
    restored = decode(path)
    assert restored.tobytes() == original.tobytes()
