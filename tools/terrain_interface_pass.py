"""Grade the Relayfall south breach into Vesper's native MAX terrain.

A macro height field should not simply crash into hard-surface architecture. This pass
mirrors the Level/Ramp stage an environment artist would perform in MAX after shaping
the large geology: preserve the moon's macro terrain, but deliberately grade the old
service approach into the fortress threshold.

Runs immediately after native_terrain_pass.py.
"""
from __future__ import annotations

import argparse
import json
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele
from environment_pass import get_suffix, set_suffix
from native_terrain_pass import (
    GRID,
    TYPE_BYTES,
    SCULPT_BYTES,
    SCULPT_NAME,
    terrain_settings,
    world_to_grid,
    grid_to_world,
    sculpt_index,
    normalized_height,
    vesper_height_units,
    gauss,
    smoothstep,
    _ground_offset,
)

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "terrain-interface-pass.json"


def final_height_units(x: float, z: float) -> float:
    """Macro Vesper terrain plus a deliberately graded Relayfall service approach."""
    h = vesper_height_units(x, z)
    # 575 units is ~14.6m: close to the modeled deck elevation without punching through
    # it. The path then descends ~4.2m into the old sea floor over a long, playable run.
    target = 575.0 - 165.0 * smoothstep(2850.0, 4300.0, -z)
    transition = gauss(x, z, 0.0, -3400.0, 1800.0, 1300.0)
    blend = 0.96 * transition
    return h * (1.0 - blend) + target * blend


def patch_sculpt(existing: bytes, settings: dict) -> tuple[bytes, dict]:
    if len(existing) != SCULPT_BYTES:
        raise RuntimeError(f"Expected native MAX sculpt block {SCULPT_BYTES:,} bytes, got {len(existing):,}")
    data = bytearray(existing)
    editable = settings["editable_size"]

    x0, x1 = -3200.0, 3200.0
    z0, z1 = -4800.0, -2100.0
    gx0, gx1 = world_to_grid(x0, editable), world_to_grid(x1, editable)
    gz0, gz1 = world_to_grid(z0, editable), world_to_grid(z1, editable)

    cells = 0
    min_y = float("inf")
    max_y = float("-inf")
    for gz in range(gz0, gz1 + 1):
        z = grid_to_world(gz, editable)
        for gx in range(gx0, gx1 + 1):
            x = grid_to_world(gx, editable)
            # The Gaussian itself determines how much of the surrounding terrain is
            # affected, so it is safe to author the rectangular working region.
            y = final_height_units(x, z)
            idx = sculpt_index(gx, gz)
            data[idx] = 1
            struct.pack_into("<f", data, TYPE_BYTES + idx * 4, normalized_height(y, settings))
            cells += 1
            min_y = min(min_y, y)
            max_y = max(max_y, y)

    return bytes(data), {
        "cells_authored": cells,
        "world_bounds": [x0, z0, x1, z1],
        "height_units": [round(min_y, 2), round(max_y, 2)],
        "height_meters": [round(min_y * 0.0254, 2), round(max_y * 0.0254, 2)],
    }


def patch_entities(map_ele: bytes) -> tuple[bytes, list[dict]]:
    version, entities = read_ele(map_ele)
    snapped = []
    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        offset = _ground_offset(name)
        if offset is None:
            continue
        x = float(get_suffix(entity, "x", 0.0) or 0.0)
        z = float(get_suffix(entity, "z", 0.0) or 0.0)
        # Re-snap all generated exterior actors/props to the final composite profile;
        # outside the interface zone this is effectively the macro terrain value.
        new_y = final_height_units(x, z) + offset
        old_y = float(get_suffix(entity, "y", 0.0) or 0.0)
        set_suffix(entity, "y", new_y)
        snapped.append({"name": name, "before_y": old_y, "after_y": round(new_y, 2)})

    result = write_ele(version, entities)
    check_version, check_entities = read_ele(result)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result, snapped


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False) -> dict:
    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}
    if SCULPT_NAME not in payload:
        raise RuntimeError("Native terrain pass must run before terrain_interface_pass")
    if "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele")

    settings = terrain_settings(payload)
    sculpt, terrain_report = patch_sculpt(payload[SCULPT_NAME], settings)
    map_ele, snapped = patch_entities(payload["map.ele"])
    payload[SCULPT_NAME] = sculpt
    payload["map.ele"] = map_ele

    report = {"map": str(path), "dry_run": dry_run, "terrain": terrain_report, "snapped_entities": snapped}
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-terrain-interface.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-terrain-interface-", suffix=".fpm", delete=False, dir=path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as output:
            for info in infos:
                output.writestr(info.filename, payload[info.filename])
        convert(temp_path)
        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert len(check.read(SCULPT_NAME)) == SCULPT_BYTES
            assert check.read("map.ele") == map_ele
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
    args = parser.parse_args()
    report = rewrite_archive(args.map, dry_run=args.dry_run, backup=args.backup)
    print("AEGIS REACH // NATIVE TERRAIN INTERFACE GRADING")
    print("Approach cells:", report["terrain"]["cells_authored"])
    print("Approach height:", report["terrain"]["height_meters"], "m")
    print("Exterior entities re-snapped:", len(report["snapped_entities"]))
    if args.dry_run:
        print("Dry run only.")
    else:
        print("Relayfall service approach graded into MAX native terrain.")


if __name__ == "__main__":
    main()
