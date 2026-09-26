"""Encoder and decoder for the OWO1 lossless image format.

The public API intentionally uses Pillow images, while accepting any object
with a Pillow-compatible ``convert`` method for encoding.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import BinaryIO, Union

from PIL import Image

MAGIC = b"OWO1"
HEADER_STRUCT = struct.Struct("<4sIIBBH")
HEADER_SIZE = HEADER_STRUCT.size
COMPRESSION_RAW = 0
COMPRESSION_RLE = 1
_SUPPORTED_CHANNELS = (3, 4)
_MAX_DIMENSION = 100_000

PathLike = Union[str, Path]


def _image_bytes(image: Image.Image) -> tuple[int, int, int, bytes]:
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
    channels = len(image.getbands())
    return image.width, image.height, channels, image.tobytes()


def _rle_encode(data: bytes, pixel_size: int) -> bytes:
    """Encode pixels as little-endian uint32 run length + one pixel."""
    output = bytearray()
    pixel_count = len(data) // pixel_size
    index = 0
    while index < pixel_count:
        pixel = data[index * pixel_size : (index + 1) * pixel_size]
        run = 1
        while index + run < pixel_count and run < 0xFFFFFFFF:
            candidate = data[(index + run) * pixel_size : (index + run + 1) * pixel_size]
            if candidate != pixel:
                break
            run += 1
        output.extend(struct.pack("<I", run))
        output.extend(pixel)
        index += run
    return bytes(output)


def _rle_decode(data: bytes, pixel_size: int, expected_size: int) -> bytes:
    output = bytearray()
    offset = 0
    while offset < len(data):
        if len(data) - offset < 4 + pixel_size:
            raise ValueError("truncated RLE packet")
        (run,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if run == 0:
            raise ValueError("RLE packet has a zero length")
        pixel = data[offset : offset + pixel_size]
        offset += pixel_size
        output.extend(pixel * run)
        if len(output) > expected_size:
            raise ValueError("RLE data exceeds the image dimensions")
    if len(output) != expected_size:
        raise ValueError("RLE data does not match the image dimensions")
    return bytes(output)


def encode(image: Image.Image, output: PathLike, compression: str = "raw") -> None:
    """Write *image* to *output* using ``raw`` or lossless ``rle`` compression."""
    width, height, channels, pixels = _image_bytes(image)
    if compression.lower() not in ("raw", "rle"):
        raise ValueError("compression must be 'raw' or 'rle'")
    compression_id = COMPRESSION_RAW if compression.lower() == "raw" else COMPRESSION_RLE
    payload = pixels if compression_id == COMPRESSION_RAW else _rle_encode(pixels, channels)
    header = HEADER_STRUCT.pack(MAGIC, width, height, channels, compression_id, 0)
    with open(output, "wb") as stream:
        stream.write(header)
        stream.write(payload)


def decode(source: PathLike) -> Image.Image:
    """Read an OWO file and return a Pillow RGB or RGBA image."""
    with open(source, "rb") as stream:
        header = stream.read(HEADER_SIZE)
        if len(header) != HEADER_SIZE:
            raise ValueError("file is shorter than an OWO header")
        magic, width, height, channels, compression, reserved = HEADER_STRUCT.unpack(header)
        if magic != MAGIC:
            raise ValueError("invalid OWO magic number")
        if not (0 < width <= _MAX_DIMENSION and 0 < height <= _MAX_DIMENSION):
            raise ValueError("invalid image dimensions")
        if channels not in _SUPPORTED_CHANNELS:
            raise ValueError("OWO supports only RGB and RGBA")
        if reserved != 0:
            raise ValueError("unsupported header flags")
        if compression not in (COMPRESSION_RAW, COMPRESSION_RLE):
            raise ValueError("unsupported compression method")
        expected_size = width * height * channels
        payload = stream.read()

    if compression == COMPRESSION_RAW:
        if len(payload) != expected_size:
            raise ValueError("raw data does not match the image dimensions")
        pixels = payload
    else:
        pixels = _rle_decode(payload, channels, expected_size)
    mode = "RGB" if channels == 3 else "RGBA"
    return Image.frombytes(mode, (width, height), pixels)
