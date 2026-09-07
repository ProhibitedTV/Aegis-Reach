"""Add a second environmental-story layer to Vesper's exterior terrain.

Runs after world_story_pass.py. The first Vesper pass establishes the open brine shelf;
this pass gives that space geological hierarchy and human history so it stops reading as
one flat test arena.

Design grammar:
  inner evaporite basin -> tidal channel -> raised basalt benches -> civilian causeway
  -> outer shelf -> distant rim

The geometry is intentionally broad and low-frequency. Combat readability wins over
terrain noise. Static story props establish three historical layers: Vesper geology,
Meridian civilian survey work, and the later AEGIS military occupation.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import random
import shutil
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele
from environment_pass import Mesh, parse_bank, write_bank, clean_template, get_suffix, set_suffix

GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"
ASSETS = FILES / "entitybank" / "Aegis Reach"
MAP = FILES / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "terrain-story-pass.json"
PREFIX = "TERRAIN //"
ATLAS = "vesper_terrain_atlas.png"
CHANNEL = "vesper_brine_channel.png"


def write_fpe(name: str, texture: str, collision: int, *, material: int = 1, cast_shadow=True):
    (ASSETS / f"{name}.fpe").write_text(
        "; Original Aegis Reach / Vesper terrain asset\n"
        f"desc = {name}\n"
        f"model = {name}.x\n"
        "scale = 100\n"
        f"textured = {texture}\n"
        f"baseColorMap = {texture}\n"
        "effect = effectbank\\reloaded\\apbr_basic.fx\n"
        f"collisionmode = {collision}\n"
        f"materialindex = {material}\n"
        "defaultstatic = 1\n"
        "strength = 0\n"
        f"castshadow = {1 if cast_shadow else 0}\n"
        "roughnessStrength = 0.92\n"
        "metalnessStrength = 0.10\n"
        "reflectance = 0.07\n"
        "basecolor = 4294967295\n"
        "aimain = no_behavior_selected.lua\n",
        encoding="utf-8",
    )


def build_atlas(path: Path):
    """Eight repeatable material bands with directional Vesper weathering."""
    palette = [
        (34, 39, 43),      # 0 fractured basalt
        (61, 70, 76),      # 1 wet-looking blue basalt
        (194, 201, 190),   # 2 old salt crust
        (138, 145, 137),   # 3 compacted evaporite
        (76, 90, 93),      # 4 survey concrete/ceramic
        (65, 171, 183),    # 5 faded Meridian cyan
        (99, 72, 49),      # 6 oxidized field metal
        (17, 23, 27),      # 7 Choir / carbon-black mineral
    ]
    image = Image.new("RGB", (1024, 128), (0, 0, 0))
    px = image.load()
    rng = random.Random(77119)
    for x in range(1024):
        band = min(7, x // 128)
        base = palette[band]
        for y in range(128):
            directional = 7 * math.sin(y * 0.17 + x * 0.013)
            grain = 4 * math.sin((x * 0.21) + (y * 0.09))
            salt = 0
            if band in (0, 1, 4, 6):
                # Pale residue always drifts in the same direction: prevailing wind.
                salt = max(0, 12 - ((x + y * 3) % 41))
            noise = rng.randint(-10, 10)
            px[x, y] = tuple(
                max(0, min(255, int(c + directional + grain + noise + salt)))
                for c in base
            )

    draw = ImageDraw.Draw(image)
    # Salt band remembers multiple historic water levels.
    for y in (18, 31, 52, 79, 104):
        draw.line((2 * 128 + 3, y, 3 * 128 - 4, y + rng.randint(-2, 2)), fill=(229, 230, 215), width=2)
    # Survey paint is old and mechanically scraped.
    for x in range(5 * 128 + 8, 6 * 128 - 8, 24):
        draw.line((x, 6, x - 11, 119), fill=(29, 83, 88), width=2)
    # Choir mineral has faint parallel structures; visible, not neon.
    for y in range(12, 122, 14):
        draw.line((7 * 128 + 5, y, 8 * 128 - 5, y), fill=(42, 58, 61), width=1)

    image.filter(ImageFilter.GaussianBlur(0.28)).save(path, optimize=True)


def build_channel_texture(path: Path):
    size = 1024
    image = Image.new("RGB", (size, size), (69, 78, 80))
    px = image.load()
    rng = random.Random(77120)
    for y in range(size):
        for x in range(size):
            meander = math.sin(y * 0.015 + math.sin(x * 0.007) * 1.7)
            pale = max(0.0, math.sin(y * 0.055 + x * 0.009) - 0.45)
            fine = rng.randint(-9, 9)
            r = 63 + meander * 8 + pale * 43 + fine
            g = 73 + meander * 9 + pale * 46 + fine
            b = 76 + meander * 11 + pale * 40 + fine
            px[x, y] = tuple(max(0, min(255, int(v))) for v in (r, g, b))
    draw = ImageDraw.Draw(image)
    # Repeating salt rims tell the eye that liquid flowed here more than once.
    for y in (112, 224, 388, 606, 824):
        points = []
        for x in range(-30, size + 40, 38):
            points.append((x, y + int(18 * math.sin(x * 0.018 + y))))
        draw.line(points, fill=(185, 190, 181), width=3)
    image.filter(ImageFilter.GaussianBlur(0.45)).save(path, optimize=True)


def build_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_atlas(ASSETS / ATLAS)
    build_channel_texture(ASSETS / CHANNEL)

    # Slightly lower outer shelf extends the landscape beyond the first combat bowl.
    mesh = Mesh(); mesh.box(0, 0, 0, 4800, 36, 2200, 3)
    mesh.write(ASSETS / "Vesper Outer Shelf.x", ATLAS)
    write_fpe("Vesper Outer Shelf", ATLAS, 1, material=13)

    # Broad geological benches: low-frequency terrain, useful as cover and elevation.
    mesh = Mesh()
    mesh.box(-360, 0, 0, 1500, 92, 760, 0, angle=-5)
    mesh.box(520, 0, 270, 1050, 62, 620, 1, angle=8)
    mesh.write(ASSETS / "Vesper Tidal Bench.x", ATLAS)
    write_fpe("Vesper Tidal Bench", ATLAS, 1, material=1)

    # A shallow old channel is visual rather than collision-critical; the causeway tells
    # the player humans had to account for repeated brine flow here.
    mesh = Mesh(); mesh.box(0, 0, 0, 520, 5, 3100, 0, angle=0)
    mesh.write(ASSETS / "Vesper Brine Channel.x", CHANNEL)
    write_fpe("Vesper Brine Channel", CHANNEL, 11, material=13, cast_shadow=False)

    mesh = Mesh(); mesh.box(0, 0, 0, 700, 24, 920, 4)
    # Retaining shoes / old supports.
    for z in (-330, -110, 110, 330):
        mesh.box(-315, -30, z, 46, 54, 72, 6)
        mesh.box(315, -30, z, 46, 54, 72, 6)
    mesh.write(ASSETS / "Meridian Causeway.x", ATLAS)
    write_fpe("Meridian Causeway", ATLAS, 1, material=2)

    # A small survey shelter built around a warm spot. Open front keeps it readable.
    mesh = Mesh()
    mesh.box(0, 0, 110, 760, 42, 520, 4)
    mesh.box(-350, 40, 110, 50, 330, 520, 4)
    mesh.box(350, 40, 110, 50, 330, 520, 4)
    mesh.box(0, 330, 110, 760, 38, 520, 4)
    mesh.box(-210, 50, -165, 180, 130, 70, 5)  # old console
    mesh.box(220, 50, -165, 150, 90, 70, 6)    # heater / field box
    mesh.box(0, 162, 365, 770, 26, 12, 2)      # old flood/mineral line
    mesh.write(ASSETS / "Meridian Survey Shelter.x", ATLAS)
    write_fpe("Meridian Survey Shelter", ATLAS, 1, material=2)

    # Exposed Choir rib: almost geological, but too regular. It should be noticed only
    # after the player has accepted the more ordinary terrain grammar.
    mesh = Mesh()
    for i in range(6):
        x = (i - 2.5) * 115
        mesh.box(x, i * 18, 0, 52, 300 + i * 28, 78, 7, angle=-9 + i * 3)
    mesh.box(0, 0, 0, 840, 44, 250, 1, angle=7)
    mesh.write(ASSETS / "Vesper Resonance Cut.x", ATLAS)
    write_fpe("Vesper Resonance Cut", ATLAS, 11, material=1)

    # Human-scale story detail: maintenance cairn / field memorial, intentionally tiny.
    mesh = Mesh()
    for i, (x, z, w, h, l, a) in enumerate([
        (0, 0, 130, 50, 110, 7), (-30, 22, 105, 45, 90, -11),
        (28, -18, 82, 38, 75, 14), (2, 5, 58, 31, 55, -4),
    ]):
        mesh.box(x, i * 38, z, w, h, l, 0, angle=a)
    mesh.box(0, 155, -42, 16, 92, 18, 5)
    mesh.write(ASSETS / "Meridian Field Cairn.x", ATLAS)
    write_fpe("Meridian Field Cairn", ATLAS, 11, material=1)

    # Long distant rim silhouette keeps the horizon from ending at the play-space edge.
    mesh = Mesh()
    for x, z, w, h, l, a in [
        (-1300, 0, 2100, 520, 500, -8), (900, 170, 1800, 690, 540, 11),
        (2200, -40, 1250, 420, 420, 5),
    ]:
        mesh.box(x, 0, z, w, h, l, 0, angle=a)
    mesh.write(ASSETS / "Vesper Distant Rim.x", ATLAS)
    write_fpe("Vesper Distant Rim", ATLAS, 11, material=1)

    return [
        ATLAS, CHANNEL,
        "Vesper Outer Shelf.x", "Vesper Outer Shelf.fpe",
        "Vesper Tidal Bench.x", "Vesper Tidal Bench.fpe",
        "Vesper Brine Channel.x", "Vesper Brine Channel.fpe",
        "Meridian Causeway.x", "Meridian Causeway.fpe",
        "Meridian Survey Shelter.x", "Meridian Survey Shelter.fpe",
        "Vesper Resonance Cut.x", "Vesper Resonance Cut.fpe",
        "Meridian Field Cairn.x", "Meridian Field Cairn.fpe",
        "Vesper Distant Rim.x", "Vesper Distant Rim.fpe",
    ]


PLACEMENTS = [
    # The first shelf at z=-4800 remains the readable combat bowl. These elements
    # organize it without burying it in terrain noise.
    ("TERRAIN // CHANNEL 01", "Vesper Brine Channel", 520, 581, -5000, 0, -9, 0, CHANNEL),
    ("TERRAIN // CAUSEWAY 01", "Meridian Causeway", 390, 580, -4930, 0, -9, 0, ATLAS),
    ("TERRAIN // TIDAL BENCH WEST", "Vesper Tidal Bench", -1900, 510, -4380, 0, 17, 0, ATLAS),
    ("TERRAIN // TIDAL BENCH EAST", "Vesper Tidal Bench", 1780, 515, -5920, 0, 194, 0, ATLAS),

    # Outer shelf drops subtly away from the old basin. This is mostly vista/traversal
    # space for now and gives the next mission room to grow without a hard world edge.
    ("TERRAIN // OUTER SHELF", "Vesper Outer Shelf", 0, 528, -7600, 0, 0, 0, ATLAS),
    ("TERRAIN // OUTER BENCH WEST", "Vesper Tidal Bench", -1450, 500, -7350, 0, 30, 0, ATLAS),
    ("TERRAIN // OUTER BENCH EAST", "Vesper Tidal Bench", 1510, 500, -7920, 0, 210, 0, ATLAS),

    # Civilian layer: shelter and field cairn sit where people logically worked,
    # adjacent to the old channel and geothermal activity rather than randomly placed.
    ("TERRAIN // MERIDIAN SHELTER 12", "Meridian Survey Shelter", -2260, 579, -6150, 0, 14, 0, ATLAS),
    ("TERRAIN // FIELD CAIRN M-4", "Meridian Field Cairn", -2030, 584, -6000, 0, -14, 0, ATLAS),

    # Mystery layer appears near a mapped tidal fracture, away from the obvious route.
    ("TERRAIN // RESONANCE CUT 03", "Vesper Resonance Cut", 2190, 578, -6810, 0, 26, 0, ATLAS),

    # Backdrop silhouettes keep Vesper larger than the collision boundary.
    ("TERRAIN // DISTANT RIM WEST", "Vesper Distant Rim", -4800, 420, -9600, 0, 24, 0, ATLAS),
    ("TERRAIN // DISTANT RIM EAST", "Vesper Distant Rim", 4700, 380, -10100, 0, 204, 0, ATLAS),
]


def patch_terrain(map_ele: bytes, map_ent: bytes):
    version, entities = read_ele(map_ele)
    bank = parse_bank(map_ent)

    entities = [
        entity for entity in entities
        if not str(get_suffix(entity, "eleprof.name_s", "")).startswith(PREFIX)
    ]

    template = None
    for entity in entities:
        idx = int(get_suffix(entity, "bankindex", 0) or 0)
        path = bank[idx - 1] if 0 < idx <= len(bank) else ""
        if path.lower().startswith("aegis reach\\") and "vesper brine shelf" in path.lower():
            template = entity
            break
    if template is None:
        for entity in entities:
            idx = int(get_suffix(entity, "bankindex", 0) or 0)
            path = bank[idx - 1] if 0 < idx <= len(bank) else ""
            if path.lower().startswith("aegis reach\\"):
                template = entity
                break
    if template is None:
        raise RuntimeError("No Aegis Reach static template found for terrain story pass")

    added = []
    for name, asset, x, y, z, rx, ry, rz, texture in PLACEMENTS:
        bank_path = f"Aegis Reach\\{asset}.fpe"
        if bank_path not in bank:
            bank.append(bank_path)
        entity = clean_template(template)
        set_suffix(entity, "maintype", 1)
        set_suffix(entity, "bankindex", bank.index(bank_path) + 1)
        set_suffix(entity, "x", x); set_suffix(entity, "y", y); set_suffix(entity, "z", z)
        set_suffix(entity, "rx", rx); set_suffix(entity, "ry", ry); set_suffix(entity, "rz", rz)
        set_suffix(entity, "eleprof.name_s", name)
        set_suffix(entity, "staticflag", 1)
        set_suffix(entity, "eleprof.scale", 100.0)
        set_suffix(entity, "scalex", 0.0); set_suffix(entity, "scaley", 0.0); set_suffix(entity, "scalez", 0.0)
        set_suffix(entity, "eleprof.strength", 0)
        set_suffix(entity, "eleprof.isimmobile", 1)
        set_suffix(entity, "eleprof.texd_s", texture)
        set_suffix(entity, "eleprof.effect_s", r"effectbank\reloaded\apbr_basic.fx")
        set_suffix(entity, "eleprof.aimain_s", "no_behavior_selected.lua")
        set_suffix(entity, "eleprof.soundset4_s", "")
        entities.append(entity)
        added.append({"name": name, "asset": asset, "x": x, "y": y, "z": z})

    result_ele = write_ele(version, entities)
    check_version, check_entities = read_ele(result_ele)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result_ele, write_bank(bank), added, len(entities), len(bank)


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False):
    if not path.exists():
        raise FileNotFoundError(path)
    assets = build_assets()
    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}
    if "map.ele" not in payload or "map.ent" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele or map.ent")

    patched_ele, patched_ent, added, entity_count, bank_count = patch_terrain(payload["map.ele"], payload["map.ent"])
    payload["map.ele"] = patched_ele
    payload["map.ent"] = patched_ent

    report = {
        "map": str(path),
        "dry_run": dry_run,
        "generated_assets": assets,
        "placements": added,
        "entity_count": entity_count,
        "bank_entries": bank_count,
        "story_rules": [
            "geology uses broad terraces, not noise",
            "human infrastructure follows old water and geothermal logic",
            "salt/weathering always has a directional history",
            "the Choir appears as impossible regularity inside otherwise natural geology",
        ],
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-terrain-story-pass.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-terrain-story-", suffix=".fpm", delete=False, dir=path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for info in infos:
                output.writestr(info.filename, payload[info.filename])
        convert(temp_path)
        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert check.read("map.ele") == patched_ele
            assert check.read("map.ent") == patched_ent
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    args = parser.parse_args()
    report = rewrite_archive(args.map, dry_run=args.dry_run, backup=args.backup)
    print("AEGIS REACH // VESPER TERRAIN STORY PASS")
    print("Generated terrain assets:", len(report["generated_assets"]))
    print("Terrain/story placements:", len(report["placements"]))
    print("Map entities after pass:", report["entity_count"])
    if args.dry_run:
        print("Dry run only; map archive was not replaced.")
    else:
        print("Layered terrain/story pass injected and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
