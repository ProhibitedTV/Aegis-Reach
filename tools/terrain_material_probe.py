"""Inventory GameGuru MAX terrain materials/settings without changing the level.

This exists so Aegis Reach never guesses native terrain material IDs. It reads the
terrain JSON embedded in Relayfall's FPM and samples terrain texture folders from the
user's installed MAX roots discovered by ecosystem_scan.py.
"""
from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from max_archive import PASSWORD
from native_format import ROOT
from ecosystem_scan import candidate_files_roots

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "terrain-materials.json"


def extract_json(data: bytes) -> dict:
    start, end = data.find(b"{"), data.rfind(b"}")
    if start < 0 or end < start:
        return {}
    try:
        return json.loads(data[start : end + 1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}


def relevant_settings(settings: dict) -> dict:
    keep = {}
    probes = ("material", "layer", "slope", "texture", "bump", "tiling", "reflect", "heightmap", "editable_size")
    for key, value in settings.items():
        lower = str(key).lower()
        if any(probe in lower for probe in probes):
            keep[key] = value
    return keep


def material_number(path: Path) -> int | None:
    match = re.search(r"(?:^|[^a-z])mat(?:erial)?[_ -]?(\d+)", path.name.lower())
    return int(match.group(1)) if match else None


def scan(map_path: Path = MAP, roots: list[Path] | None = None) -> dict:
    with zipfile.ZipFile(map_path) as source:
        source.setpassword(PASSWORD)
        settings = extract_json(source.read("ggterrain.dat")) if "ggterrain.dat" in source.namelist() else {}

    roots = roots or candidate_files_roots()
    existing = [root for root in roots if root.exists()]
    materials = []
    seen = set()
    for root in existing:
        for folder_name in ("terraintextures", "terrainbank"):
            base = root / folder_name
            if not base.exists():
                continue
            for path in sorted(base.iterdir()):
                if not path.is_dir():
                    continue
                key = str(path).lower()
                if key in seen:
                    continue
                seen.add(key)
                files = [p.name for p in path.iterdir() if p.is_file()][:20]
                materials.append({
                    "root": str(root),
                    "folder": folder_name,
                    "name": path.name,
                    "index_hint": material_number(path),
                    "files": files,
                })

    report = {
        "map": str(map_path),
        "terrain_settings": relevant_settings(settings),
        "max_roots": [str(root) for root in existing],
        "terrain_material_folders": materials,
        "next_step": "Use verified material indices/settings to author MAX native 4096x4096 paint data; do not infer IDs from prop materialindex fields.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, default=MAP)
    parser.add_argument("--root", type=Path, action="append", help="optional MAX Files root; may be repeated")
    args = parser.parse_args()
    report = scan(args.map, args.root)
    print("AEGIS REACH // MAX TERRAIN MATERIAL PROBE")
    print("MAX roots:", len(report["max_roots"]))
    print("Terrain material folders:", len(report["terrain_material_folders"]))
    print("Embedded material-related settings:", len(report["terrain_settings"]))
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
