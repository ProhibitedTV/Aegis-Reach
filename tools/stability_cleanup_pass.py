"""Remove known prototype overlap hazards from Relayfall before playtest deploy.

Aegis Reach has accumulated several environment passes while we learned GameGuru MAX.
Some of those passes deliberately layered large landmark meshes directly over the
original fortress geometry. They looked acceptable in a top-down authoring model but
produce obvious clipping/z-fighting in first person.

This pass is intentionally conservative. It does NOT rebuild the level. It removes the
known interior overlay experiments, removes the old wall-mounted tide-scar overlays,
and deduplicates exact repeated generated placements while preserving the original
combat layout, native terrain, exterior story props, lights, enemies and objectives.

Run after the environment/world/native-terrain passes and before final visual polish.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele
from environment_pass import get_suffix

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "stability-cleanup-pass.json"

# These were useful blockout landmarks but overlap existing Relayfall architecture.
# We will re-introduce objective framing later with fitted modular/DLC pieces instead
# of dropping whole generated arches/crowns at objective coordinates.
REMOVE_NAMES = {
    "ENV // NORTHSTAR CROWN",
    "ENV // LANTERN CROWN",
    "ENV // AEGIS CROWN",
    "ENV // INSERTION GANTRY",
    "ENV // NORTHSTAR GANTRY",
    "ENV // CORE GANTRY",
    "WORLD // TIDE SCAR SOUTH A",
    "WORLD // TIDE SCAR SOUTH B",
}

GENERATED_PREFIXES = (
    "ENV //",
    "WORLD //",
    "TERRAIN //",
    "SHELF //",
    "NATIVE //",
)


def _round(value, places=3):
    try:
        return round(float(value), places)
    except (TypeError, ValueError):
        return 0.0


def transform_key(entity: dict) -> tuple:
    return (
        int(get_suffix(entity, "bankindex", 0) or 0),
        _round(get_suffix(entity, "x", 0)),
        _round(get_suffix(entity, "y", 0)),
        _round(get_suffix(entity, "z", 0)),
        _round(get_suffix(entity, "rx", 0)),
        _round(get_suffix(entity, "ry", 0)),
        _round(get_suffix(entity, "rz", 0)),
    )


def patch(map_ele: bytes):
    version, entities = read_ele(map_ele)
    kept = []
    removed = []
    seen_generated = {}

    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        if name in REMOVE_NAMES:
            removed.append({"name": name, "reason": "known interior overlay"})
            continue

        generated = name.startswith(GENERATED_PREFIXES)
        if generated:
            key = transform_key(entity)
            previous = seen_generated.get(key)
            if previous is not None:
                removed.append({
                    "name": name,
                    "reason": "exact generated transform duplicate",
                    "duplicate_of": previous,
                })
                continue
            seen_generated[key] = name

        kept.append(entity)

    result = write_ele(version, kept)
    check_version, check_entities = read_ele(result)
    assert check_version == version
    assert len(check_entities) == len(kept)
    return result, removed, len(entities), len(kept)


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False):
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}

    if "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele")

    patched, removed, before, after = patch(payload["map.ele"])
    payload["map.ele"] = patched

    report = {
        "map": str(path),
        "dry_run": dry_run,
        "entities_before": before,
        "entities_after": after,
        "removed_count": len(removed),
        "removed": removed,
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-stability-cleanup.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-stability-", suffix=".fpm", delete=False, dir=path.parent) as handle:
        temp_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as output:
            for info in infos:
                output.writestr(info.filename, payload[info.filename])
        convert(temp_path)
        with zipfile.ZipFile(temp_path) as check:
            check.setpassword(PASSWORD)
            assert check.read("map.ele") == patched
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
    print("AEGIS REACH // STABILITY CLEANUP")
    print("Entities:", report["entities_before"], "->", report["entities_after"])
    print("Removed overlap hazards:", report["removed_count"])
    if args.dry_run:
        print("Dry run only; map archive unchanged.")
    else:
        print("Cleanup injected and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
