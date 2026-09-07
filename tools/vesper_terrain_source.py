"""Generate optional GameGuru MAX Terrain Generator import sources for Vesper.

The production build now authors Relayfall directly into MAX's native sculpt buffer via
`native_terrain_pass.py`. This tool is retained for artists who want to start from the
same Vesper macro shape in MAX's *Terrain Generator* UI.

MAX's native heightmap importer accepts 16-bit RAW. The community/engine convention is
Little Endian when that option is selected in the Terrain Generator. We therefore emit:

  * vesper_relayfall_height_16le.raw  -- 16-bit unsigned little-endian RAW
  * vesper_relayfall_preview.png      -- visual reference only, not the primary import
  * vesper_relayfall_terrain.json     -- dimensions/scaling/composition notes

This fixes the previous script, which incorrectly treated a 16-bit PNG and conceptual
meter coordinates as if they were the authoritative MAX terrain workflow.
"""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from PIL import Image

from native_terrain_pass import vesper_height_units

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Aegis Reach" / "Design" / "terrain-source"
DEFAULT_SIZE = 2048

# The authored play-space we want represented by the imported source. GameGuru MAX
# uses one world unit per inch; this span is intentionally expressed in those units.
WORLD_HALF_EXTENT_UNITS = 12500.0


def world_coord(index: int, size: int) -> float:
    return -WORLD_HALF_EXTENT_UNITS + (2.0 * WORLD_HALF_EXTENT_UNITS) * (index / (size - 1))


def build(size: int) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)

    heights: list[float] = []
    minimum = float("inf")
    maximum = float("-inf")
    for row in range(size):
        # MAX's terrain data is stored with Z flipped relative to intuitive image rows.
        z = world_coord(size - 1 - row, size)
        for col in range(size):
            x = world_coord(col, size)
            h = vesper_height_units(x, z)
            heights.append(h)
            minimum = min(minimum, h)
            maximum = max(maximum, h)

    span = max(1e-6, maximum - minimum)
    values = [max(0, min(65535, int(round((h - minimum) / span * 65535.0)))) for h in heights]

    raw_path = OUT / "vesper_relayfall_height_16le.raw"
    with raw_path.open("wb") as handle:
        # Explicit little endian: Terrain Generator -> Import Heightmap -> RAW -> Little Endian.
        for value in values:
            handle.write(struct.pack("<H", value))

    preview = Image.new("I;16", (size, size))
    preview.putdata(values)
    preview_path = OUT / "vesper_relayfall_preview.png"
    preview.save(preview_path)

    meters_per_unit = 0.0254
    width_meters = 2.0 * WORLD_HALF_EXTENT_UNITS * meters_per_unit
    pixels_per_meter = size / width_meters

    manifest = {
        "world": "Vesper / Relayfall Meridian Shelf",
        "primary_import_file": raw_path.name,
        "preview_only": preview_path.name,
        "raw_format": {
            "bits": 16,
            "signed": False,
            "byte_order": "little-endian",
            "width": size,
            "height": size,
            "bytes": size * size * 2,
        },
        "max_units": {
            "unit_definition": "1 GameGuru MAX world unit = 1 inch = 0.0254 m",
            "half_extent_units": WORLD_HALF_EXTENT_UNITS,
            "span_units": WORLD_HALF_EXTENT_UNITS * 2,
            "span_meters": round(width_meters, 2),
            "source_pixels_per_meter": round(pixels_per_meter, 4),
        },
        "source_height_units": {"min": round(minimum, 2), "max": round(maximum, 2), "span": round(span, 2)},
        "source_height_meters": {
            "min": round(minimum * meters_per_unit, 2),
            "max": round(maximum * meters_per_unit, 2),
            "span": round(span * meters_per_unit, 2),
        },
        "terrain_generator_workflow": [
            "Open Terrain Generator",
            "Choose Import Heightmap / RAW heightmap",
            "Select vesper_relayfall_height_16le.raw",
            "Set the RAW dimensions to match this manifest",
            "Choose Little Endian",
            "Adjust Heightmap Scale / Max Height until the authored span matches the intended ~10-30m macro relief",
            "Generate Terrain and Open Level Editor",
            "Use Terrain Editing Raise/Lower/Level/Blend/Ramp for art-direction passes",
        ],
        "production_note": "Aegis Reach production deploy does not require this manual import; native_terrain_pass.py writes MAX's editable sculpt buffer directly.",
        "composition": [
            "Relayfall graded military plateau",
            "south breach transition slope",
            "evaporite basin",
            "west/east basalt shoulders",
            "meandering dried brine channel",
            "lower outer shelf",
            "east tidal fracture / Undertide approach",
            "north escarpment",
            "far south geological rim",
        ],
    }

    manifest_path = OUT / "vesper_relayfall_terrain.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE, choices=(1024, 2048, 4096))
    args = parser.parse_args()
    manifest = build(args.size)
    print("AEGIS REACH // OPTIONAL MAX TERRAIN GENERATOR SOURCE")
    print("RAW:", OUT / manifest["primary_import_file"])
    print("Format: 16-bit unsigned little-endian", manifest["raw_format"]["width"], "x", manifest["raw_format"]["height"])
    print("World span:", manifest["max_units"]["span_meters"], "m")
    print("Production terrain remains: python tools\\native_terrain_pass.py")


if __name__ == "__main__":
    main()
