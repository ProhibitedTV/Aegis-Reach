"""Expand Relayfall onto Vesper's exterior brine shelf and add environmental story.

The pass is deterministic and intended to run after environment_pass.py. It opens a
controlled breach in the south perimeter and extends a walkable exterior shelf beyond
the fortress without rebuilding the authored combat interior.

The open shelf is deliberately simple collision geometry: broad readable terrain first,
art-density later. Generated props communicate Vesper's vanished brine sea, civilian
survey history, tidal geology, and the later military occupation.

Usage:
    python tools/world_story_pass.py
    python tools/world_story_pass.py --dry-run
    python tools/world_story_pass.py --backup
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import random
import shutil
import struct
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
REPORT = GAME / "Design" / "world-story-pass.json"
ATLAS = "vesper_story_atlas.png"
GROUND = "vesper_brine_surface.png"


def write_fpe(name: str, texture: str, collision: int, *, material: int = 1, cast_shadow=True):
    (ASSETS / f"{name}.fpe").write_text(
        "; Original Aegis Reach / Vesper environment asset\n"
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
        "roughnessStrength = 0.9\n"
        "metalnessStrength = 0.12\n"
        "reflectance = 0.08\n"
        "basecolor = 4294967295\n"
        "aimain = no_behavior_selected.lua\n",
        encoding="utf-8",
    )


def build_story_atlas(path: Path):
    """Eight material strips used by the simple authored meshes.

    0 basalt, 1 blue basalt, 2 salt/mineral, 3 oxidized metal,
    4 faded cyan survey paint, 5 warning amber, 6 dark machinery, 7 rust.
    """
    palette = [
        (28, 31, 34), (49, 61, 70), (190, 199, 190), (83, 87, 82),
        (67, 175, 184), (189, 126, 54), (20, 27, 31), (116, 62, 43),
    ]
    image = Image.new("RGB", (1024, 128), (0, 0, 0))
    px = image.load()
    rng = random.Random(7729)
    for x in range(1024):
        index = min(7, x // 128)
        base = palette[index]
        for y in range(128):
            grain = 7 * math.sin((x + y * 3) * 0.11) + 4 * math.sin(y * 0.31)
            noise = rng.randint(-8, 8)
            edge = 0.78 if x % 128 < 4 or x % 128 > 123 or y < 4 or y > 123 else 1.0
            c = tuple(max(0, min(255, int((v + grain + noise) * edge))) for v in base)
            px[x, y] = c

    draw = ImageDraw.Draw(image)
    # Salt/mineral strip: layered old-water deposition.
    salt_x = 2 * 128
    for y in (24, 39, 58, 84, 105):
        draw.line((salt_x + 4, y, salt_x + 123, y + rng.randint(-2, 2)), fill=(225, 226, 211), width=2)
    # Survey paint is old, scratched, and imperfect.
    survey_x = 4 * 128
    for x in range(survey_x + 14, survey_x + 120, 29):
        draw.line((x, 14, x - 8, 112), fill=(30, 80, 85), width=2)
    # Rust / oxidation streaks.
    rust_x = 7 * 128
    for x in range(rust_x + 12, rust_x + 122, 18):
        draw.line((x, 5, x + rng.randint(-7, 8), 123), fill=(74, 36, 30), width=rng.choice((1, 2, 3)))

    image.filter(ImageFilter.GaussianBlur(0.35)).save(path, optimize=True)


def build_ground_texture(path: Path):
    size = 1024
    image = Image.new("RGB", (size, size), (112, 118, 114))
    px = image.load()
    rng = random.Random(44017)
    for y in range(size):
        # Broad mineral terraces flow mostly east/west; subtle diagonal drift keeps it natural.
        band = 22 * math.sin(y * 0.035 + 1.2 * math.sin(y * 0.006))
        for x in range(size):
            channel = 13 * math.sin(x * 0.018 + y * 0.011)
            fine = rng.randint(-15, 15)
            basalt = max(0.0, math.sin(x * 0.0047 + y * 0.0031) - 0.52)
            salt = max(0.0, math.sin(y * 0.014 + x * 0.0018) - 0.1)
            r = 112 + band * 0.25 + channel * 0.13 + fine + salt * 35 - basalt * 55
            g = 119 + band * 0.30 + channel * 0.16 + fine + salt * 37 - basalt * 49
            b = 116 + band * 0.34 + channel * 0.22 + fine + salt * 31 - basalt * 38
            px[x, y] = tuple(max(0, min(255, int(v))) for v in (r, g, b))

    draw = ImageDraw.Draw(image)
    # Long dried brine fractures. They fork, but avoid noisy spider-web coverage.
    for seed in range(18):
        x = rng.randint(-100, size + 100)
        y = rng.randint(0, size)
        pts = [(x, y)]
        for step in range(7):
            x += rng.randint(35, 90)
            y += rng.randint(-26, 26)
            pts.append((x, y))
        draw.line(pts, fill=(71, 79, 78), width=rng.choice((1, 2, 3)))
        if seed % 3 == 0:
            draw.line([(px_, py_ + 3) for px_, py_ in pts], fill=(179, 184, 174), width=1)

    image.filter(ImageFilter.GaussianBlur(0.45)).save(path, optimize=True)


def build_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_story_atlas(ASSETS / ATLAS)
    build_ground_texture(ASSETS / GROUND)

    # Walkable exterior shelf. Top surface sits 20 units below the fortress deck.
    mesh = Mesh(); mesh.box(0, 0, 0, 5200, 40, 3600, 2)
    mesh.write(ASSETS / "Vesper Brine Shelf.x", GROUND)
    write_fpe("Vesper Brine Shelf", GROUND, 1, material=13)

    # A shallow transition apron bridges the fortress deck to the older shelf.
    mesh = Mesh(); mesh.box(0, 0, 0, 2200, 24, 520, 1)
    mesh.write(ASSETS / "Vesper Gate Apron.x", GROUND)
    write_fpe("Vesper Gate Apron", GROUND, 1, material=13)

    # Low basalt ridge groups form readable flanking silhouettes, not maze clutter.
    mesh = Mesh()
    for x, z, w, h, l, a in [
        (-520, -80, 1000, 150, 500, -8), (420, 80, 850, 110, 460, 11),
        (-110, 390, 1350, 90, 360, 3),
    ]:
        mesh.box(x, 0, z, w, h, l, 0, angle=a)
    mesh.write(ASSETS / "Vesper Basalt Ridge.x", ATLAS)
    write_fpe("Vesper Basalt Ridge", ATLAS, 1, material=1)

    # Tide gauge: old civilian survey equipment with a visible historical flood band.
    mesh = Mesh(); mesh.box(0, 0, 0, 70, 620, 70, 3)
    mesh.box(0, 165, -37, 92, 55, 10, 2)  # mineral line
    mesh.box(0, 420, -39, 120, 32, 8, 4)  # faded survey marker
    mesh.box(0, 585, 0, 230, 34, 85, 6)
    mesh.write(ASSETS / "Vesper Tide Gauge.x", ATLAS)
    write_fpe("Vesper Tide Gauge", ATLAS, 0, material=2)

    # Wrecked civilian survey skiff: enough shape language to read as a machine from a distance.
    mesh = Mesh(); mesh.box(0, 0, 0, 540, 70, 260, 3, angle=-7)
    mesh.box(-90, 54, -5, 250, 85, 190, 1, angle=-7)
    mesh.box(120, 65, -92, 180, 38, 60, 4, angle=-7)
    mesh.box(-245, 28, 0, 45, 120, 310, 7, angle=-12)
    mesh.box(245, 16, 20, 40, 80, 270, 7, angle=-2)
    mesh.write(ASSETS / "Vesper Survey Skiff Wreck.x", ATLAS)
    write_fpe("Vesper Survey Skiff Wreck", ATLAS, 0, material=2)

    # Wind/thermal vents imply the living geology below the shelf.
    mesh = Mesh(); mesh.box(0, 0, 0, 150, 160, 150, 0)
    for i in range(5):
        a = math.radians(i * 72)
        mesh.box(math.cos(a) * 115, 80 + i * 18, math.sin(a) * 115, 70, 260 + i * 25, 70, 1, angle=i * 17)
    mesh.write(ASSETS / "Vesper Vent Cluster.x", ATLAS)
    write_fpe("Vesper Vent Cluster", ATLAS, 11, material=1)

    # Thin mineral scar overlay, used repeatedly along old exterior surfaces.
    mesh = Mesh(); mesh.box(0, 0, 0, 1100, 32, 14, 2)
    mesh.write(ASSETS / "Vesper Tide Scar.x", ATLAS)
    write_fpe("Vesper Tide Scar", ATLAS, 11, material=1, cast_shadow=False)

    # Correct backdrop-only pass-3 assets to truly non-physical collision.
    for backdrop in ("Aurelia", "Orbital Spine", "Relay Crown", "Service Gantry", "Horizon Beacon"):
        fpe = ASSETS / f"{backdrop}.fpe"
        if fpe.exists():
            text = fpe.read_text(encoding="utf-8", errors="ignore")
            import re
            text = re.sub(r"(?mi)^collisionmode\s*=\s*\d+", "collisionmode = 11", text)
            fpe.write_text(text, encoding="utf-8")

    return [
        ATLAS, GROUND,
        "Vesper Brine Shelf.x", "Vesper Brine Shelf.fpe",
        "Vesper Gate Apron.x", "Vesper Gate Apron.fpe",
        "Vesper Basalt Ridge.x", "Vesper Basalt Ridge.fpe",
        "Vesper Tide Gauge.x", "Vesper Tide Gauge.fpe",
        "Vesper Survey Skiff Wreck.x", "Vesper Survey Skiff Wreck.fpe",
        "Vesper Vent Cluster.x", "Vesper Vent Cluster.fpe",
        "Vesper Tide Scar.x", "Vesper Tide Scar.fpe",
    ]


PLACEMENTS = [
    # Walkable open approach south of the current fortress perimeter.
    ("WORLD // BRINE SHELF", "Vesper Brine Shelf", 0, 540, -4800, 0, 0, 0, GROUND),
    ("WORLD // GATE APRON", "Vesper Gate Apron", 0, 576, -3070, 0, 0, 0, GROUND),

    # Large, sparse ridge shapes create choices and depth without turning the shelf into clutter.
    ("WORLD // BASALT RIDGE WEST", "Vesper Basalt Ridge", -1450, 578, -5050, 0, 18, 0, ATLAS),
    ("WORLD // BASALT RIDGE EAST", "Vesper Basalt Ridge", 1500, 578, -5650, 0, 203, 0, ATLAS),
    ("WORLD // BASALT RIDGE FAR", "Vesper Basalt Ridge", 200, 578, -6350, 0, 91, 0, ATLAS),

    # Civilian history / optional detour.
    ("WORLD // TIDE GAUGE 17", "Vesper Tide Gauge", -1180, 580, -3900, 0, 13, 0, ATLAS),
    ("WORLD // TIDE GAUGE 22", "Vesper Tide Gauge", 1720, 580, -5200, 0, 188, 0, ATLAS),
    ("WORLD // MIRA SURVEY WRECK", "Vesper Survey Skiff Wreck", -1680, 580, -5480, 0, 28, -7, ATLAS),
    ("WORLD // GEOTHERMAL VENT 01", "Vesper Vent Cluster", 2050, 580, -6150, 0, 0, 0, ATLAS),
    ("WORLD // GEOTHERMAL VENT 02", "Vesper Vent Cluster", -2300, 580, -4450, 0, 0, 0, ATLAS),

    # A repeated flood elevation on the south face of the fort. These thin overlays
    # are deliberately consistent so the player can infer the vanished sea.
    ("WORLD // TIDE SCAR SOUTH A", "Vesper Tide Scar", -1500, 705, -3004, 0, 0, 0, ATLAS),
    ("WORLD // TIDE SCAR SOUTH B", "Vesper Tide Scar", 1500, 705, -3004, 0, 0, 0, ATLAS),
]


def is_south_gate_bastion(entity, bank):
    idx = int(get_suffix(entity, "bankindex", 0) or 0)
    path = bank[idx - 1].lower() if 0 < idx <= len(bank) else ""
    if "aegis reach\\bastion wall.fpe" not in path:
        return False
    x = float(get_suffix(entity, "x", 99999) or 99999)
    z = float(get_suffix(entity, "z", 99999) or 99999)
    # Original south perimeter is at z=-2960. Remove the four central segments to
    # create an unmistakable exterior opening while leaving defensive shoulders.
    return abs(z + 2960) < 8 and -900 <= x <= 900


def patch_world(map_ele: bytes, map_ent: bytes):
    version, entities = read_ele(map_ele)
    bank = parse_bank(map_ent)

    # Remove prior generated world entities so repeated production deploys remain stable.
    entities = [e for e in entities if not str(get_suffix(e, "eleprof.name_s", "")).startswith("WORLD //")]

    before_gate = len(entities)
    entities = [e for e in entities if not is_south_gate_bastion(e, bank)]
    removed_gate = before_gate - len(entities)

    template = None
    for entity in entities:
        idx = int(get_suffix(entity, "bankindex", 0) or 0)
        path = bank[idx - 1] if 0 < idx <= len(bank) else ""
        if path.lower().startswith("aegis reach\\") and "station deck" in path.lower():
            template = entity; break
    if template is None:
        template = next((e for e in entities if str(get_suffix(e, "eleprof.name_s", ""))), None)
    if template is None:
        raise RuntimeError("No static template found for Vesper world pass")

    # Keep spawn in the current insertion for now. The shelf is immediately accessible
    # through the opened south breach, so geometry can be playtested before we commit
    # the mission start/cinematic to the exterior.

    added = []
    for name, asset, x, y, z, rx, ry, rz, texture in PLACEMENTS:
        bank_path = f"Aegis Reach\\{asset}.fpe"
        if bank_path not in bank:
            bank.append(bank_path)
        base = clean_template(template)
        set_suffix(base, "maintype", 1)
        set_suffix(base, "bankindex", bank.index(bank_path) + 1)
        set_suffix(base, "x", x); set_suffix(base, "y", y); set_suffix(base, "z", z)
        set_suffix(base, "rx", rx); set_suffix(base, "ry", ry); set_suffix(base, "rz", rz)
        set_suffix(base, "eleprof.name_s", name)
        set_suffix(base, "staticflag", 1)
        set_suffix(base, "eleprof.scale", 100.0)
        set_suffix(base, "scalex", 0.0); set_suffix(base, "scaley", 0.0); set_suffix(base, "scalez", 0.0)
        set_suffix(base, "eleprof.strength", 0)
        set_suffix(base, "eleprof.isimmobile", 1)
        set_suffix(base, "eleprof.texd_s", texture)
        set_suffix(base, "eleprof.effect_s", r"effectbank\reloaded\apbr_basic.fx")
        set_suffix(base, "eleprof.aimain_s", "no_behavior_selected.lua")
        set_suffix(base, "eleprof.soundset4_s", "")
        entities.append(base)
        added.append({"name": name, "asset": asset, "x": x, "y": y, "z": z})

    result_ele = write_ele(version, entities)
    check_version, check_entities = read_ele(result_ele)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result_ele, write_bank(bank), added, removed_gate, len(entities), len(bank)


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

    patched_ele, patched_ent, added, removed_gate, entity_count, bank_count = patch_world(payload["map.ele"], payload["map.ent"])
    payload["map.ele"] = patched_ele; payload["map.ent"] = patched_ent
    report = {
        "map": str(path), "dry_run": dry_run, "generated_assets": assets,
        "placements": added, "south_gate_segments_removed": removed_gate,
        "entity_count": entity_count, "bank_entries": bank_count,
        "design_intent": "Walkable Vesper brine shelf + readable vanished-sea story layer",
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-vesper-world-pass.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path); report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-world-pass-", suffix=".fpm", delete=False, dir=path.parent) as handle:
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
        if temp_path.exists(): temp_path.unlink()

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
    print("AEGIS REACH // VESPER WORLD STORY PASS")
    print("Map:", report["map"])
    print("Generated assets:", len(report["generated_assets"]))
    print("World placements:", len(report["placements"]))
    print("South gate segments removed:", report["south_gate_segments_removed"])
    print("Map entities after pass:", report["entity_count"])
    if args.dry_run:
        print("Dry run only; map archive was not replaced.")
    else:
        print("Open brine shelf injected and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
