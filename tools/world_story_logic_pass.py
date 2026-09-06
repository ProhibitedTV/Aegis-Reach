"""Bind authored Vesper world props to sparse story behaviour inside Relayfall.

Runs after world_story_pass.py. Keeps the geometry pass focused on map construction and
adds dynamic Lua only to the few props that should react to the player.
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
from environment_pass import get_suffix, set_suffix

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "world-story-logic.json"

STORY_NAMES = {
    "WORLD // MIRA SURVEY WRECK",
    "WORLD // TIDE GAUGE 17",
    "WORLD // TIDE GAUGE 22",
}


def patch(map_ele: bytes):
    version, entities = read_ele(map_ele)
    bound = []
    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        if name not in STORY_NAMES:
            continue
        set_suffix(entity, "staticflag", 0)
        set_suffix(entity, "eleprof.aimain_s", r"aegis_reach\aegis_story.lua")
        set_suffix(entity, "eleprof.phyalways", 1)
        set_suffix(entity, "eleprof.isimmobile", 1)
        set_suffix(entity, "eleprof.strength", 0)
        bound.append(name)
    result = write_ele(version, entities)
    check_version, check_entities = read_ele(result)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result, bound


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False):
    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}
    if "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele")
    patched, bound = patch(payload["map.ele"])
    payload["map.ele"] = patched
    report = {"map": str(path), "dry_run": dry_run, "story_entities": bound}
    if dry_run:
        return report
    if backup:
        backup_path = path.with_name(path.stem + ".pre-story-logic.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)
    with tempfile.NamedTemporaryFile(prefix="relayfall-story-logic-", suffix=".fpm", delete=False, dir=path.parent) as handle:
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
    print("AEGIS REACH // WORLD STORY LOGIC")
    print("Story props bound:", len(report["story_entities"]))
    for name in report["story_entities"]:
        print(" -", name)
    if not args.dry_run:
        print("Story logic injected and archive validation passed.")


if __name__ == "__main__":
    main()
