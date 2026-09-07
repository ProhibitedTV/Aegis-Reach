"""Author Vesper directly in GameGuru MAX's native editable terrain sculpt buffer.

This is deliberately different from the older mesh-based terrain experiments.
GameGuru MAX stores its editable sculpt field as a fixed 4096x4096 grid inside the
FPM. The serialized sculpt payload is:

    4096*4096 uint8 edit-type values
    4096*4096 float32 edit-height values

Edit type 1 is MAX's native REPLACE mode. Heights are normalized against the terrain
settings' positive/negative height ranges and offset_y. This pass modifies only the
central Relayfall/Vesper region, leaving the rest of the user's editable terrain field
alone. The result remains editable with MAX's normal Terrain Editing tools.

It also removes the broad collision-mesh slabs/ridges from our earlier prototype
passes and snaps authored exterior story/combat props onto the new native terrain.

Usage:
    python tools/native_terrain_pass.py
    python tools/native_terrain_pass.py --dry-run
    python tools/native_terrain_pass.py --backup
    python tools/native_terrain_pass.py --inspect
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele
from environment_pass import get_suffix, set_suffix

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "native-terrain-pass.json"

GRID = 4096
CELL_COUNT = GRID * GRID
TYPE_BYTES = CELL_COUNT
FLOAT_BYTES = CELL_COUNT * 4
SCULPT_BYTES = TYPE_BYTES + FLOAT_BYTES
SCULPT_NAME = f"{SCULPT_BYTES}.dat"

# Region in MAX world units (1 GameGuru unit = 1 inch) that this pass owns.
OWNED_X_MIN = -11500.0
OWNED_X_MAX = 11500.0
OWNED_Z_MIN = -12000.0
OWNED_Z_MAX = 7600.0

# Prototype entities that used box meshes as substitute terrain. These are removed
# after the native field exists. Architectural/story props remain.
DEPRECATED_GROUND_NAMES = {
    "WORLD // BRINE SHELF",
    "WORLD // GATE APRON",
    "WORLD // BASALT RIDGE WEST",
    "WORLD // BASALT RIDGE EAST",
    "WORLD // BASALT RIDGE FAR",
    "TERRAIN // CHANNEL 01",
    "TERRAIN // TIDAL BENCH WEST",
    "TERRAIN // TIDAL BENCH EAST",
    "TERRAIN // OUTER SHELF",
    "TERRAIN // OUTER BENCH WEST",
    "TERRAIN // OUTER BENCH EAST",
    "TERRAIN // DISTANT RIM WEST",
    "TERRAIN // DISTANT RIM EAST",
}


def smoothstep(a: float, b: float, x: float) -> float:
    if a == b:
        return 0.0
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def gauss(x: float, z: float, cx: float, cz: float, sx: float, sz: float) -> float:
    dx = (x - cx) / sx
    dz = (z - cz) / sz
    return math.exp(-0.5 * (dx * dx + dz * dz))


def rect_mask(x: float, z: float, cx: float, cz: float, hx: float, hz: float, feather: float) -> float:
    dx = max(0.0, abs(x - cx) - hx)
    dz = max(0.0, abs(z - cz) - hz)
    d = math.sqrt(dx * dx + dz * dz)
    return 1.0 - smoothstep(0.0, feather, d)


def vesper_height_units(x: float, z: float) -> float:
    """Authored Vesper macro terrain in MAX world units.

    One unit is one inch in MAX. The values are intentionally large enough to create
    real 10-30 m relief while keeping slopes broad enough for FPS traversal/navmesh.
    """
    # Base wind-scoured shelf: low-frequency variation only.
    h = 405.0
    h += 22.0 * math.sin(x / 1750.0)
    h += 17.0 * math.sin((x + z) / 2600.0)
    h += 9.0 * math.sin(z / 820.0 + 0.7 * math.sin(x / 1900.0))

    # Relayfall's military footprint was graded, but not the entire moon. Keep native
    # terrain just below the modeled decks/floors so exterior courtyards still feel
    # connected without terrain cutting through architecture.
    fort = rect_mask(x, z, 0.0, -50.0, 3050.0, 2750.0, 1050.0)
    h = h * (1.0 - fort) + 535.0 * fort

    # A broad exterior basin is the exposed bed of Vesper's vanished brine sea.
    south = smoothstep(2850.0, 5200.0, -z)
    h -= 145.0 * south

    # The south breach is a geological/military threshold, not a slab edge. The old
    # service route rises gently to meet Relayfall, then rolls down into the basin.
    breach = gauss(x, z, 0.0, -3350.0, 1450.0, 720.0)
    h = h * (1.0 - 0.86 * breach) + 585.0 * (0.86 * breach)

    # Main outdoor combat grammar: two large basalt shoulders frame an open crossing.
    h += 470.0 * gauss(x, z, -2350.0, -5000.0, 1250.0, 1750.0)
    h += 540.0 * gauss(x, z, 2450.0, -5700.0, 1350.0, 1850.0)

    # A lower, quieter outer shelf creates the vista/release after the first basin.
    outer = gauss(x, z, 0.0, -7650.0, 3300.0, 1500.0)
    h -= 95.0 * outer

    # A secondary shelf/ridge makes the outer space readable from a distance and gives
    # future White Meridian combat an elevated route without random noise hills.
    h += 285.0 * gauss(x, z, -1050.0, -8050.0, 2750.0, 850.0)

    # Dried brine channel: meandering low line through the basin. This is actual
    # topography now, so the civilian causeway has a reason to exist.
    channel_x = 360.0 * math.sin((z + 5300.0) / 1180.0) + 280.0
    channel_band = math.exp(-((x - channel_x) / 430.0) ** 2)
    channel_window = gauss(x, z, 0.0, -5700.0, 5200.0, 2650.0)
    h -= 125.0 * channel_band * channel_window

    # East tidal fracture / future Undertide approach. It should feel naturally
    # dangerous before the player knows why the survey teams cared about it.
    fracture_x = 3300.0 + 180.0 * math.sin((z + 6200.0) / 900.0)
    fracture = math.exp(-((x - fracture_x) / 420.0) ** 2) * gauss(x, z, 3300.0, -6500.0, 1100.0, 2900.0)
    h -= 300.0 * fracture

    # North/east escarpments make Relayfall feel nested in geology rather than placed
    # on an infinite plane. These remain broad enough to read as natural landforms.
    north = smoothstep(3450.0, 7200.0, z)
    h += north * (510.0 + 115.0 * math.sin(x / 2400.0))
    h += 360.0 * gauss(x, z, -5200.0, 1200.0, 2100.0, 3300.0)

    # Far south rim. The playable shelf visually resolves into terrain, not map bounds.
    south_rim = smoothstep(9000.0, 11800.0, -z)
    h += south_rim * (760.0 + 170.0 * math.sin(x / 1700.0))

    # Small erosion comes LAST and stays subordinate to the macro composition.
    exterior = 1.0 - fort
    h += exterior * (10.0 * math.sin(x / 285.0 + z / 710.0) + 6.0 * math.sin(z / 355.0 - x / 630.0))
    return h


def _extract_json(data: bytes) -> dict:
    """Read MAX's JSON settings from the Dark Basic memblock wrapper."""
    start = data.find(b"{")
    end = data.rfind(b"}")
    if start < 0 or end < start:
        return {}
    try:
        return json.loads(data[start : end + 1].decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def terrain_settings(payload: dict[str, bytes]) -> dict:
    parsed = _extract_json(payload.get("ggterrain.dat", b""))
    height = float(parsed.get("height", 20000.0) or 20000.0)
    min_height = float(parsed.get("minHeight", height) or height)
    offset_y = float(parsed.get("offset_y", 0.0) or 0.0)
    editable_size = float(parsed.get("editable_size", 50000.0) or 50000.0)
    # A zero range cannot interpret replace-mode sculpt values. Default MAX terrain
    # uses 20000 units; use that only if a malformed/legacy settings file reports 0.
    if abs(height) < 1.0:
        height = 20000.0
    if abs(min_height) < 1.0:
        min_height = height
    if editable_size < 12000.0:
        raise RuntimeError(f"MAX editable terrain area is too small for Relayfall: {editable_size}")
    return {
        "height": height,
        "minHeight": min_height,
        "offset_y": offset_y,
        "editable_size": editable_size,
        "heightmap_scale": parsed.get("heightmap_scale"),
        "terrain_json_found": bool(parsed),
    }


def world_to_grid(value: float, editable_size: float) -> int:
    normalized = value / editable_size
    return max(0, min(GRID - 1, int((normalized * 0.5 + 0.5) * GRID)))


def grid_to_world(index: int, editable_size: float) -> float:
    return ((index / GRID) * 2.0 - 1.0) * editable_size


def sculpt_index(gx: int, gz: int) -> int:
    # MAX stores the Z row upside-down relative to the logical sculpt coordinate.
    return (GRID - 1 - gz) * GRID + gx


def normalized_height(world_y: float, settings: dict) -> float:
    relative = world_y - settings["offset_y"]
    divisor = settings["height"] if relative >= 0 else settings["minHeight"]
    if abs(divisor) < 1.0:
        raise RuntimeError("MAX terrain height range is zero; cannot author native sculpt data")
    return relative / divisor


def patch_sculpt(existing: bytes | None, settings: dict) -> tuple[bytes, dict]:
    if existing is None:
        data = bytearray(SCULPT_BYTES)
        source = "created"
    else:
        if len(existing) != SCULPT_BYTES:
            raise RuntimeError(
                f"Unexpected MAX sculpt payload size {len(existing):,}; expected {SCULPT_BYTES:,}"
            )
        data = bytearray(existing)
        source = "existing"

    editable = settings["editable_size"]
    gx0 = world_to_grid(OWNED_X_MIN, editable)
    gx1 = world_to_grid(OWNED_X_MAX, editable)
    gz0 = world_to_grid(OWNED_Z_MIN, editable)
    gz1 = world_to_grid(OWNED_Z_MAX, editable)

    min_y = float("inf")
    max_y = float("-inf")
    cells = 0
    for gz in range(gz0, gz1 + 1):
        z = grid_to_world(gz, editable)
        for gx in range(gx0, gx1 + 1):
            x = grid_to_world(gx, editable)
            y = vesper_height_units(x, z)
            idx = sculpt_index(gx, gz)
            data[idx] = 1  # native MAX replace mode
            struct.pack_into("<f", data, TYPE_BYTES + idx * 4, normalized_height(y, settings))
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            cells += 1

    return bytes(data), {
        "source": source,
        "grid_bounds": [gx0, gz0, gx1, gz1],
        "world_bounds": [OWNED_X_MIN, OWNED_Z_MIN, OWNED_X_MAX, OWNED_Z_MAX],
        "cells_authored": cells,
        "height_units": [round(min_y, 2), round(max_y, 2)],
        "height_meters": [round(min_y * 0.0254, 2), round(max_y * 0.0254, 2)],
    }


def _ground_offset(name: str) -> float | None:
    # None means leave this entity's authored Y untouched.
    if name.startswith("SHELF // SHELF WARDEN"):
        return 8.0
    if name.startswith("SHELF // MERIDIAN CACHE"):
        return 22.0
    if name in {"WORLD // TIDE GAUGE 17", "WORLD // TIDE GAUGE 22"}:
        return 0.0
    if name == "WORLD // MIRA SURVEY WRECK":
        return 6.0
    if name.startswith("WORLD // GEOTHERMAL VENT"):
        return 0.0
    if name == "TERRAIN // CAUSEWAY 01":
        return 24.0
    if name in {"TERRAIN // MERIDIAN SHELTER 12", "TERRAIN // FIELD CAIRN M-4", "TERRAIN // RESONANCE CUT 03"}:
        return 2.0
    return None


def patch_entities(map_ele: bytes) -> tuple[bytes, dict]:
    version, entities = read_ele(map_ele)
    kept = []
    removed: list[str] = []
    snapped: list[dict] = []
    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        if name in DEPRECATED_GROUND_NAMES:
            removed.append(name)
            continue

        offset = _ground_offset(name)
        if offset is not None:
            x = float(get_suffix(entity, "x", 0.0) or 0.0)
            z = float(get_suffix(entity, "z", 0.0) or 0.0)
            old_y = float(get_suffix(entity, "y", 0.0) or 0.0)
            new_y = vesper_height_units(x, z) + offset
            set_suffix(entity, "y", new_y)
            snapped.append({"name": name, "x": x, "z": z, "before_y": old_y, "after_y": round(new_y, 2)})
        kept.append(entity)

    result = write_ele(version, kept)
    check_version, check_entities = read_ele(result)
    assert check_version == version
    assert len(check_entities) == len(kept)
    return result, {"removed_mesh_ground": removed, "snapped_entities": snapped, "entity_count": len(kept)}


def inspect_archive(path: Path = MAP) -> dict:
    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        names = source.namelist()
        payload = {}
        if "ggterrain.dat" in names:
            payload["ggterrain.dat"] = source.read("ggterrain.dat")
        settings = terrain_settings(payload)
        sculpt_name = SCULPT_NAME if SCULPT_NAME in names else None
        paint_names = [name for name in names if name.endswith(".ptd")]
        tt_folders = sorted({name.split("/", 1)[0] for name in names if name.lower().startswith("tt") and "/" in name})
        return {
            "map": str(path),
            "settings": settings,
            "sculpt_file": sculpt_name,
            "sculpt_bytes_expected": SCULPT_BYTES,
            "heightmapdata_raw": "heightmapdata.raw" in names,
            "paint_files": paint_names,
            "terrain_node_folders": tt_folders,
        }


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}

    if "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele")

    settings = terrain_settings(payload)
    sculpt, terrain_report = patch_sculpt(payload.get(SCULPT_NAME), settings)
    patched_ele, entity_report = patch_entities(payload["map.ele"])
    payload[SCULPT_NAME] = sculpt
    payload["map.ele"] = patched_ele

    report = {
        "map": str(path),
        "dry_run": dry_run,
        "native_format": {
            "grid": GRID,
            "sculpt_file": SCULPT_NAME,
            "type_bytes": TYPE_BYTES,
            "float_bytes": FLOAT_BYTES,
            "total_bytes": SCULPT_BYTES,
            "replace_edit_type": 1,
        },
        "settings": settings,
        "terrain": terrain_report,
        "entities": entity_report,
        "design_intent": "Native MAX terrain: fortress mesa -> brine basin -> basalt shoulders -> outer shelf -> tidal fracture -> geological rim",
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-native-terrain.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    existing_names = {info.filename for info in infos}
    with tempfile.NamedTemporaryFile(prefix="relayfall-native-terrain-", suffix=".fpm", delete=False, dir=path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as output:
            for info in infos:
                output.writestr(info.filename, payload[info.filename])
            if SCULPT_NAME not in existing_names:
                output.writestr(SCULPT_NAME, sculpt)
        convert(temp_path)

        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert check.read("map.ele") == patched_ele
            sculpt_check = check.read(SCULPT_NAME)
            assert len(sculpt_check) == SCULPT_BYTES
            # Spot-check a few authored terrain cells survived encryption/archive rewrite.
            for x, z in ((0, -3400), (-2350, -5000), (2450, -5700), (3300, -6500)):
                gx = world_to_grid(x, settings["editable_size"])
                gz = world_to_grid(z, settings["editable_size"])
                idx = sculpt_index(gx, gz)
                assert sculpt_check[idx] == 1

        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="report MAX-native terrain files/settings without modifying the map")
    args = parser.parse_args()

    if args.inspect:
        print(json.dumps(inspect_archive(args.map), indent=2))
        return

    report = rewrite_archive(args.map, dry_run=args.dry_run, backup=args.backup)
    print("AEGIS REACH // GAMEGURU MAX NATIVE TERRAIN")
    print("Map:", report["map"])
    print("MAX sculpt grid:", GRID, "x", GRID)
    print("Authored terrain cells:", report["terrain"]["cells_authored"])
    print("Terrain height:", report["terrain"]["height_units"], "units /", report["terrain"]["height_meters"], "m")
    print("Prototype mesh-ground entities removed:", len(report["entities"]["removed_mesh_ground"]))
    print("Exterior entities snapped to terrain:", len(report["entities"]["snapped_entities"]))
    if args.dry_run:
        print("Dry run only; no FPM was replaced.")
    else:
        print("Native sculpt payload written and encrypted FPM validation passed.")
        print("Terrain remains editable with MAX Terrain Editing tools.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
