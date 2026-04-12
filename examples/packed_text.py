#!/usr/bin/env python3
"""Example: Packed Text Recipe

Render multi-line text into a fixed-size canvas using the packed_text recipe.

Usage:
    uv run python examples/packed_text.py "Momentary lapse of Reason"
    uv run python examples/packed_text.py "Hello world" --size 256x256
    uv run python examples/packed_text.py "Hello world" --size 196 --output output/packed_text.png
"""

import argparse
from pathlib import Path

from invariant import Executor
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.recipes import packed_text


def parse_size(value: str) -> tuple[int, int]:
    """Parse size string into (width, height)."""
    cleaned = value.strip().lower()
    if "x" in cleaned:
        parts = cleaned.split("x")
    elif "," in cleaned:
        parts = cleaned.split(",")
    else:
        size = int(cleaned)
        if size <= 0:
            raise ValueError("Size values must be positive integers.")
        return (size, size)

    if len(parts) != 2:
        raise ValueError(f"Invalid size format: {value}. Expected WxH or N.")

    width = int(parts[0].strip())
    height = int(parts[1].strip())
    if width <= 0 or height <= 0:
        raise ValueError("Size values must be positive integers.")
    return (width, height)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Render text into a fixed-size image using packed_text"
    )
    parser.add_argument(
        "text",
        type=str,
        help="Text to render",
    )
    parser.add_argument(
        "--size",
        type=parse_size,
        default=(196, 196),
        help="Canvas size as WxH or N (default: 196x196)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/packed_text.png",
        help="Output PNG file path (default: output/packed_text.png)",
    )

    args = parser.parse_args()

    graph = {
        "packed": packed_text(
            args.text,
            size=args.size,
            font="Geneva",
            min_font_size=10,
            max_font_size=64,
            align_horizontal="center",
            align_vertical="center",
        )
    }

    registry = OpRegistry()
    register_core_ops(registry)
    executor = Executor(registry=registry, store=MemoryStore())

    print("Generating packed text image...")
    print(f"  Text: {args.text}")
    print(f"  Size: {args.size[0]}x{args.size[1]}")

    results = executor.execute(graph)
    image = results["packed"].image

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")

    print(f"\n✓ Saved to: {output_path}")
    print(f"  Dimensions: {image.width}x{image.height}")
    print(f"  Mode: {image.mode}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
