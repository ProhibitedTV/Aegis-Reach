"""Build and inject the first authored Aegis Reach environment landmark kit.

The combat layout stays untouched. This pass adds non-colliding visual landmarks and
skyline detail around Relayfall so the map reads as a defended colony installation
rather than an arena floating in darkness.

Generated assets:
  * Aurelia - a huge distant banded gas giant
  * Orbital Spine - broken defense-network truss segments in the skyline
  * Relay Crown - large objective framing architecture
  * Service Gantry - industrial arches at important transitions
  * Horizon Beacon - distant perimeter/navigation silhouettes

Usage:
    python tools/environment_pass.py
    python tools/environment_pass.py --dry-run
    python tools/environment_pass.py --backup
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

GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"
ASSETS = FILES / "entitybank" / "Aegis Reach"
MAP = FILES / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "environment-pass-3.json"


class Mesh:
    def __init__(self):
        self.verts = []
        self.norm = []
        self.uv = []
        self.faces = []

    def box(self, x, y, z, w, h, l, color=0, angle=0):
        a = math.radians(angle)
        co, si = math.cos(a), math.sin(a)
        corners = [
            (-w / 2, 0, -l / 2), (w / 2, 0, -l / 2),
            (w / 2, h, -l / 2), (-w / 2, h, -l / 2),
            (-w / 2, 0, l / 2), (w / 2, 0, l / 2),
            (w / 2, h, l / 2), (-w / 2, h, l / 2),
        ]
        groups = [
            ((0, 3, 2, 1), (0, 0, -1)), ((4, 5, 6, 7), (0, 0, 1)),
            ((1, 2, 6, 5), (1, 0, 0)), ((0, 4, 7, 3), (-1, 0, 0)),
            ((3, 7, 6, 2), (0, 1, 0)), ((0, 1, 5, 4), (0, -1, 0)),
        ]
        for inds, n in groups:
            start = len(self.verts)
            for j, idx in enumerate(inds):
                xx, yy, zz = corners[idx]
                self.verts.append((x + xx * co + zz * si, y + yy, z - xx * si + zz * co))
                self.norm.append((n[0] * co + n[2] * si, n[1], -n[0] * si + n[2] * co))
                u, v = ((.07, .93), (.07, .07), (.93, .07), (.93, .93))[j]
                self.uv.append(((color + u) / 8, v))
            self.faces.extend(((start, start + 1, start + 2), (start, start + 2, start + 3)))

    def sphere(self, radius=4500, segments=40, rings=20):
        for ring in range(rings + 1):
            v = ring / rings
            phi = math.pi * v
            y = math.cos(phi) * radius
            rr = math.sin(phi) * radius
            for seg in range(segments + 1):
                u = seg / segments
                theta = math.tau * u
                x = math.cos(theta) * rr
                z = math.sin(theta) * rr
                self.verts.append((x, y, z))
                self.norm.append((x / radius, y / radius, z / radius))
                self.uv.append((u, v))
        for ring in range(rings):
            for seg in range(segments):
                a = ring * (segments + 1) + seg
                b = a + segments + 1
                self.faces.extend(((a, b, a + 1), (a + 1, b, b + 1)))

    def write(self, path: Path, texture: str):
        def seq(rows):
            return ",\n".join(";".join(f"{v:.6f}" for v in row) + ";" for row in rows) + ";"

        faces = ",\n".join("3;" + ",".join(map(str, face)) + ";" for face in self.faces) + ";"
        text = "xof 0303txt 0032\nMesh AegisMesh {\n" + str(len(self.verts)) + ";\n"
        text += seq(self.verts) + "\n" + str(len(self.faces)) + ";\n" + faces
        text += "\nMeshNormals {\n" + str(len(self.norm)) + ";\n" + seq(self.norm)
        text += "\n" + str(len(self.faces)) + ";\n" + faces + "\n}\n"
        text += "MeshTextureCoords {\n" + str(len(self.uv)) + ";\n" + seq(self.uv) + "\n}\n"
        text += "MeshMaterialList {\n1;\n" + str(len(self.faces)) + ";\n"
        text += ",".join("0" for _ in self.faces) + ";;\n"
        text += (
            "Material {1.0;1.0;1.0;1.0;;32.0;0.15;0.15;0.15;;0.0;0.0;0.0;;"
            f'TextureFilename {{"{texture}";}} }}\n}}\n}}\n'
        )
        path.write_text(text, encoding="utf-8")


def write_fpe(name: str, texture: str, *, cast_shadow: bool = True):
    (ASSETS / f"{name}.fpe").write_text(
        "; Original Aegis Reach environment asset\n"
        f"desc = {name}\n"
        f"model = {name}.x\n"
        "scale = 100\n"
        f"textured = {texture}\n"
        f"baseColorMap = {texture}\n"
        "effect = effectbank\\reloaded\\apbr_basic.fx\n"
        "collisionmode = 0\n"
        "materialindex = 2\n"
        "defaultstatic = 1\n"
        "strength = 0\n"
        f"castshadow = {1 if cast_shadow else 0}\n"
        "roughnessStrength = 0.82\n"
        "metalnessStrength = 0.32\n"
        "reflectance = 0.12\n"
        "basecolor = 4294967295\n"
        "aimain = no_behavior_selected.lua\n",
        encoding="utf-8",
    )


def build_aurelia_texture(path: Path):
    width, height = 1024, 512
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    random.seed(9302)
    for y in range(height):
        band = 0.5 + 0.5 * math.sin(y * 0.12 + 2.4 * math.sin(y * 0.021))
        for x in range(width):
            wave = math.sin(x * 0.022 + y * 0.047 + 2 * math.sin(x * 0.005))
            shear = math.sin(x * 0.006 - y * 0.037)
            noise = random.random() * 0.08
            t = 0.42 * band + 0.28 * (wave * 0.5 + 0.5) + 0.22 * (shear * 0.5 + 0.5) + noise
            warm = math.exp(-((y / height - 0.47) / 0.09) ** 2) * math.exp(-((x / width - 0.68) / 0.20) ** 2)
            r = int(24 + 35 * t + 55 * warm)
            g = int(46 + 70 * t + 25 * warm)
            b = int(70 + 95 * t - 5 * warm)
            pixels[x, y] = tuple(max(0, min(255, c)) for c in (r, g, b))

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(9):
        pad = i * 9
        alpha = max(8, 55 - i * 5)
        draw.ellipse((610 + pad, 200 + pad // 3, 820 - pad, 300 - pad // 3), outline=(218, 160, 116, alpha), width=3)
    overlay = overlay.filter(ImageFilter.GaussianBlur(6))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    image.filter(ImageFilter.GaussianBlur(0.45)).save(path, optimize=True)


def build_assets():
    ASSETS.mkdir(parents=True, exist_ok=True)

    build_aurelia_texture(ASSETS / "aurelia_surface.png")
    mesh = Mesh(); mesh.sphere(); mesh.write(ASSETS / "Aurelia.x", "aurelia_surface.png")
    write_fpe("Aurelia", "aurelia_surface.png", cast_shadow=False)

    mesh = Mesh()
    mesh.box(0, 0, 0, 2200, 110, 180, 1)
    mesh.box(0, 105, 0, 1750, 55, 220, 6)
    for x in range(-900, 901, 300): mesh.box(x, 20, 0, 42, 260, 260, 2)
    for x in (-1050, 1050):
        mesh.box(x, 0, 0, 110, 520, 320, 1)
        mesh.box(x, 420, -165, 140, 75, 520, 3)
    mesh.box(0, 160, -130, 1500, 24, 26, 3)
    mesh.write(ASSETS / "Orbital Spine.x", "aegis_atlas.png")
    write_fpe("Orbital Spine", "aegis_atlas.png")

    mesh = Mesh()
    for i in range(8):
        angle = -70 + i * 20
        radius = 320
        x = math.sin(math.radians(angle)) * radius
        y = math.cos(math.radians(angle)) * radius + 70
        mesh.box(x, y, 0, 135, 48, 110, 2, angle=-angle)
    for x in (-310, 310):
        mesh.box(x, 0, 0, 70, 460, 100, 1)
        mesh.box(x, 250, -55, 20, 180, 8, 3)
    mesh.box(0, 410, 0, 720, 45, 95, 6)
    mesh.box(0, 440, -52, 580, 20, 5, 3)
    mesh.write(ASSETS / "Relay Crown.x", "aegis_atlas.png")
    write_fpe("Relay Crown", "aegis_atlas.png")

    mesh = Mesh()
    for x in (-340, 340):
        mesh.box(x, 0, 0, 90, 560, 120, 1)
        mesh.box(x, 120, -68, 20, 330, 10, 3)
    mesh.box(0, 500, 0, 780, 80, 150, 2)
    mesh.box(0, 548, -78, 640, 22, 8, 3)
    mesh.box(-230, 240, 0, 350, 48, 70, 6, angle=-20)
    mesh.box(230, 240, 0, 350, 48, 70, 6, angle=20)
    mesh.write(ASSETS / "Service Gantry.x", "aegis_atlas.png")
    write_fpe("Service Gantry", "aegis_atlas.png")

    mesh = Mesh()
    mesh.box(0, 0, 0, 180, 120, 180, 6)
    mesh.box(0, 120, 0, 82, 900, 82, 1)
    for y in (260, 480, 700): mesh.box(0, y, -45, 120, 50, 10, 3)
    mesh.box(0, 980, 0, 340, 65, 100, 2)
    mesh.box(0, 1045, -54, 240, 30, 8, 3)
    mesh.write(ASSETS / "Horizon Beacon.x", "aegis_atlas.png")
    write_fpe("Horizon Beacon", "aegis_atlas.png")

    return [
        "Aurelia.fpe", "Aurelia.x", "aurelia_surface.png",
        "Orbital Spine.fpe", "Orbital Spine.x",
        "Relay Crown.fpe", "Relay Crown.x",
        "Service Gantry.fpe", "Service Gantry.x",
        "Horizon Beacon.fpe", "Horizon Beacon.x",
    ]


def suffix_key(entity: dict, suffix: str):
    for key in entity:
        if key.split(":", 1)[-1] == suffix:
            return key
    return None


def get_suffix(entity: dict, suffix: str, default=None):
    key = suffix_key(entity, suffix)
    return entity.get(key, default) if key else default


def set_suffix(entity: dict, suffix: str, value):
    key = suffix_key(entity, suffix)
    if key:
        current = entity[key]
        if isinstance(current, int): value = int(round(value))
        elif isinstance(current, float): value = float(value)
        elif isinstance(current, str): value = str(value)
        entity[key] = value
        return True
    return False


def parse_bank(data: bytes):
    count = struct.unpack_from("<i", data)[0]
    text = data[4:].decode("latin1")
    bank = [line for line in text.splitlines() if line]
    if len(bank) != count:
        raise RuntimeError(f"map.ent count mismatch: header={count} parsed={len(bank)}")
    return bank


def write_bank(bank):
    return struct.pack("<i", len(bank)) + ("\r\n".join(bank) + "\r\n").encode("latin1")


def clean_template(entity: dict):
    base = copy.deepcopy(entity)
    for key in list(base):
        if key.startswith(("319:", "334:")) or "ObjectRelationships" in key:
            base[key] = "" if isinstance(base[key], str) else 0
        if key.startswith("material"):
            base[key] = "" if isinstance(base[key], str) else 0
    for suffix, value in (
        ("eleprof.parententityindex", 0), ("eleprof.parentlimbindex", 0),
        ("iHasParentIndex", 0), ("creationOfGroupID", 0), ("quatmode", 0),
        ("eleprof.bAutoFlatten", 0), ("quatw", 1.0),
    ):
        set_suffix(base, suffix, value)
    return base


PLACEMENTS = [
    # Skyline scale cues - deliberately well outside combat/navigation space.
    ("ENV // AURELIA", "Aurelia", -15000, 11800, 22000, 0, 28, 0, "aurelia_surface.png"),
    ("ENV // ORBITAL SPINE 01", "Orbital Spine", 8200, 7200, 15800, 12, 28, 18, "aegis_atlas.png"),
    ("ENV // ORBITAL SPINE 02", "Orbital Spine", 10600, 8500, 17600, -8, 58, -12, "aegis_atlas.png"),
    ("ENV // ORBITAL SPINE 03", "Orbital Spine", 12600, 6800, 19400, 20, 12, 27, "aegis_atlas.png"),
    ("ENV // ORBITAL SPINE 04", "Orbital Spine", -11200, 9000, 19000, -15, 72, 14, "aegis_atlas.png"),
    # Objective framing: strong landmarks, no collision/navmesh changes.
    ("ENV // NORTHSTAR CROWN", "Relay Crown", -700, 600, -1100, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // LANTERN CROWN", "Relay Crown", 800, 600, 850, 0, 180, 0, "aegis_atlas.png"),
    ("ENV // AEGIS CROWN", "Relay Crown", 0, 600, 2870, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // INSERTION GANTRY", "Service Gantry", 0, 600, -2510, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // NORTHSTAR GANTRY", "Service Gantry", -700, 600, -1510, 0, 90, 0, "aegis_atlas.png"),
    ("ENV // CORE GANTRY", "Service Gantry", 0, 600, 2440, 0, 0, 0, "aegis_atlas.png"),
    # Exterior silhouettes imply a functioning installation beyond this combat slice.
    ("ENV // BEACON WEST 01", "Horizon Beacon", -3300, 600, -900, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // BEACON EAST 01", "Horizon Beacon", 3300, 600, 700, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // BEACON WEST 02", "Horizon Beacon", -3450, 600, 2250, 0, 0, 0, "aegis_atlas.png"),
    ("ENV // BEACON EAST 02", "Horizon Beacon", 3500, 600, 3350, 0, 0, 0, "aegis_atlas.png"),
]


def patch_environment(map_ele: bytes, map_ent: bytes):
    version, entities = read_ele(map_ele)
    bank = parse_bank(map_ent)

    # Re-running the tool is deterministic. Remove only our appended environment set.
    entities = [e for e in entities if not str(get_suffix(e, "eleprof.name_s", "")).startswith("ENV //")]

    template = None
    for entity in entities:
        idx = int(get_suffix(entity, "bankindex", 0) or 0)
        path = bank[idx - 1] if 0 < idx <= len(bank) else ""
        if path.lower().startswith("aegis reach\\") and "signal spire" in path.lower():
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
        raise RuntimeError("Could not find an Aegis Reach static entity template in Relayfall")

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

    patched_ele, patched_ent, added, entity_count, bank_count = patch_environment(payload["map.ele"], payload["map.ent"])
    payload["map.ele"] = patched_ele
    payload["map.ent"] = patched_ent
    report = {
        "map": str(path),
        "dry_run": dry_run,
        "generated_assets": assets,
        "placements": added,
        "entity_count": entity_count,
        "bank_entries": bank_count,
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-environment-pass-3.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-env-pass-", suffix=".fpm", delete=False, dir=path.parent) as handle:
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
    print("AEGIS REACH // ENVIRONMENT PASS 3")
    print("Map:", report["map"])
    print("Generated assets:", len(report["generated_assets"]))
    print("Environment placements:", len(report["placements"]))
    print("Map entities after pass:", report["entity_count"])
    if args.dry_run:
        print("Dry run only; map archive was not replaced.")
    else:
        print("Environment injected and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
