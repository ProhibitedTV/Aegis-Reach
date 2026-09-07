"""Generate an editable native-terrain source for Relayfall's Vesper landscape.

This does not replace the current .fpm terrain automatically. It produces a 16-bit
heightmap, a base-color reference, and a machine-readable layout manifest intended for
GameGuru MAX's Terrain Generator / Terrain Editing workflow.

The terrain is deliberately composed as a sequence of large readable landforms rather
than random noise: fortress mesa -> old evaporite basin -> brine channel -> basalt
benches -> outer shelf -> distant rim.

Usage:
    python tools/vesper_terrain_source.py
    python tools/vesper_terrain_source.py --size 2048
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Aegis Reach" / "Design" / "terrain-source"
DEFAULT_SIZE = 1024
EXTENT = 11000.0  # conceptual world-space span used by the design manifest


def smoothstep(a: float, b: float, x: float) -> float:
    if a == b:
        return 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def gauss(x: float, z: float, cx: float, cz: float, sx: float, sz: float) -> float:
    dx = (x - cx) / sx
    dz = (z - cz) / sz
    return math.exp(-(dx * dx + dz * dz) * 0.5)


def rect_blend(x: float, z: float, hx: float, hz: float, feather: float) -> float:
    dx = max(0.0, abs(x) - hx)
    dz = max(0.0, abs(z) - hz)
    d = math.sqrt(dx * dx + dz * dz)
    return 1.0 - smoothstep(0.0, feather, d)


def terrain_height(x: float, z: float) -> float:
    """Return conceptual terrain elevation in meters."""
    # Quiet macro undulation. Keep noise subordinate to authored landforms.
    h = 72.0
    h += 5.0 * math.sin(x / 1700.0)
    h += 4.0 * math.sin((x + z) / 2400.0)
    h += 2.5 * math.sin(z / 730.0 + math.sin(x / 1600.0))

    # Old Vesper sea basin south of the fortress.
    basin = smoothstep(-2600.0, -4300.0, z)
    h -= basin * 24.0

    # Fortress sits on a geologically plausible older mesa, then military engineers
    # flattened only the center rather than the entire moon.
    mesa = gauss(x, z, 0.0, -200.0, 3900.0, 4100.0)
    h += mesa * 18.0
    fort_flat = rect_blend(x, z + 50.0, 3050.0, 3050.0, 650.0)
    h = h * (1.0 - fort_flat) + 82.0 * fort_flat

    # South threshold slopes away rather than dropping off a slab edge.
    apron = gauss(x, z, 0.0, -3300.0, 1800.0, 900.0)
    h = h * (1.0 - apron * 0.38) + 66.0 * (apron * 0.38)

    # Dried brine channel. It bends because tidal flow followed old fractures.
    channel_x = 420.0 * math.sin((z + 5100.0) / 1250.0) - 260.0
    channel = math.exp(-((x - channel_x) / 430.0) ** 2) * gauss(x, z, 0.0, -5600.0, 6000.0, 3000.0)
    h -= channel * 16.0

    # Broad basalt benches: useful combat elevation and strong horizon silhouettes.
    h += 30.0 * gauss(x, z, -2350.0, -4700.0, 1150.0, 1500.0)
    h += 34.0 * gauss(x, z, 2400.0, -5600.0, 1250.0, 1600.0)
    h += 21.0 * gauss(x, z, 600.0, -7350.0, 2600.0, 850.0)

    # East-side tidal fracture: future path toward deeper / stranger spaces.
    fracture = math.exp(-((x - 3300.0) / 520.0) ** 2) * gauss(x, z, 3300.0, -4700.0, 850.0, 3300.0)
    h -= fracture * 22.0

    # Northern escarpment turns the interior-facing side into a framed basin rather
    # than a flat board with walls floating on it.
    north = smoothstep(3600.0, 7600.0, z)
    h += north * (30.0 + 15.0 * math.sin(x / 2200.0))

    # Distant geological rim keeps the level feeling contained by terrain, not by map bounds.
    edge = max(abs(x), abs(z)) / EXTENT
    h += smoothstep(0.72, 1.0, edge) * 52.0

    # Small-scale erosion only after macro forms are established.
    h += 1.7 * math.sin(x / 190.0 + z / 430.0)
    h += 1.2 * math.sin(z / 260.0 - x / 570.0)
    return h


def world_coord(i: int, size: int) -> float:
    return -EXTENT + (2.0 * EXTENT) * (i / (size - 1))


def base_color(x: float, z: float, h: float) -> tuple[int, int, int]:
    basin = smoothstep(-2800.0, -5200.0, z)
    channel_x = 420.0 * math.sin((z + 5100.0) / 1250.0) - 260.0
    channel = math.exp(-((x - channel_x) / 520.0) ** 2) * gauss(x, z, 0.0, -5600.0, 6000.0, 3200.0)

    # Low old sea floor is salt/evaporite; higher relief returns to dark basalt.
    if basin > 0.35 and h < 67.0:
        salt = min(1.0, basin * 0.9 + max(0.0, (66.0 - h) / 20.0))
        r = 142 + int(52 * salt)
        g = 151 + int(48 * salt)
        b = 149 + int(38 * salt)
    else:
        t = max(0.0, min(1.0, (h - 58.0) / 70.0))
        r = int(65 - 24 * t)
        g = int(76 - 25 * t)
        b = int(82 - 22 * t)

    if channel > 0.28:
        r = int(r * 0.70 + 36 * 0.30)
        g = int(g * 0.70 + 59 * 0.30)
        b = int(b * 0.70 + 67 * 0.30)

    # Directional mineral/weather variation; avoid multicolor procedural confetti.
    grain = int(4.0 * math.sin(x / 83.0) + 3.0 * math.sin((x + z) / 117.0))
    return tuple(max(0, min(255, c + grain)) for c in (r, g, b))


def build(size: int) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    heights: list[float] = []
    minimum = float("inf")
    maximum = float("-inf")

    for j in range(size):
        z = world_coord(size - 1 - j, size)
        for i in range(size):
            x = world_coord(i, size)
            h = terrain_height(x, z)
            heights.append(h)
            minimum = min(minimum, h)
            maximum = max(maximum, h)

    span = max(1e-6, maximum - minimum)
    encoded = [int(max(0, min(65535, round((h - minimum) / span * 65535.0)))) for h in heights]

    height_img = Image.new("I;16", (size, size))
    height_img.putdata(encoded)
    height_path = OUT / "vesper_relayfall_height_16bit.png"
    height_img.save(height_path)

    color = Image.new("RGB", (size, size))
    pixels = []
    idx = 0
    for j in range(size):
        z = world_coord(size - 1 - j, size)
        for i in range(size):
            x = world_coord(i, size)
            pixels.append(base_color(x, z, heights[idx]))
            idx += 1
    color.putdata(pixels)
    color_path = OUT / "vesper_relayfall_basecolor.png"
    color.save(color_path, optimize=True)

    manifest = {
        "world": "Vesper / Relayfall Meridian Shelf",
        "heightmap": height_path.name,
        "basecolor_reference": color_path.name,
        "resolution": size,
        "conceptual_extent_units": [-EXTENT, EXTENT],
        "conceptual_height_meters": {"min": round(minimum, 2), "max": round(maximum, 2)},
        "terrain_generator_starting_range_meters": 180,
        "composition": [
            "fortress mesa",
            "south threshold slope",
            "evaporite combat basin",
            "dried brine channel",
            "west and east basalt benches",
            "outer shelf",
            "east tidal fracture",
            "north escarpment",
            "distant geological rim",
        ],
        "landmarks": {
            "relayfall_fortress": [0, -200],
            "south_breach": [0, -3100],
            "mira_wreck_zone": [-1700, -5500],
            "meridian_shelter_12": [2050, -6400],
            "resonance_cut_03": [3250, -5750],
            "future_undertide_entry": [3500, -7000],
        },
        "design_rule": "large geological sentences first; combat and structures inherit the terrain",
    }
    manifest_path = OUT / "vesper_relayfall_terrain.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=DEFAULT_SIZE, choices=(512, 1024, 2048, 4096))
    args = parser.parse_args()
    manifest = build(args.size)
    print("AEGIS REACH // VESPER NATIVE TERRAIN SOURCE")
    print("Resolution:", manifest["resolution"], "x", manifest["resolution"])
    print("Height range:", manifest["conceptual_height_meters"])
    print("Output:", OUT)
    print("Next: import the 16-bit heightmap in GameGuru MAX's Terrain Generator, then save Relayfall.")


if __name__ == "__main__":
    main()
