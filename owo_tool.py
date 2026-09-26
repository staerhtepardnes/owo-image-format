#!/usr/bin/env python3
"""Command-line utility for encoding and decoding OWO images."""

import argparse

from PIL import Image

from owo import encode, decode


def main() -> int:
    parser = argparse.ArgumentParser(prog="owo_tool.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc = subparsers.add_parser("encode", help="encode an image as .owo")
    enc.add_argument("input")
    enc.add_argument("output")
    enc.add_argument("--compression", choices=("raw", "rle"), default="raw")

    dec = subparsers.add_parser("decode", help="decode .owo to a standard image")
    dec.add_argument("input")
    dec.add_argument("output")

    args = parser.parse_args()
    if args.command == "encode":
        with Image.open(args.input) as image:
            encode(image, args.output, args.compression)
    else:
        image = decode(args.input)
        image.save(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
