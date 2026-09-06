"""Deploy Aegis Reach to GameGuru MAX's user Files area and collect playtest data.

Examples:
    python tools/max_playtest.py deploy --production
    python tools/max_playtest.py deploy --polish
    python tools/max_playtest.py deploy
    python tools/max_playtest.py collect

The Git checkout remains authoritative. MAX receives a focused playtest copy rather
than requiring a full manual xcopy of every stock engine asset on each iteration.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"


def default_max_files() -> Path:
    profile = os.environ.get("USERPROFILE")
    if not profile:
        raise RuntimeError("USERPROFILE is not set; pass --target explicitly")
    return Path(profile) / "Documents" / "GameGuruApps" / "GameGuruMAX" / "Files"


def copy_tree(source: Path, target: Path) -> int:
    if not source.exists():
        return 0
    count = 0
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        count += 1
    return count


def prepare_production_content() -> None:
    from environment_pass import rewrite_archive as environment_archive, MAP
    from world_story_pass import rewrite_archive as world_archive
    from cineguru_bootstrap import build_original_cine_assets, shotlist, SHOTLIST
    from ecosystem_scan import scan as scan_ecosystem

    ecosystem = scan_ecosystem()
    usable_categories = [name for name, paths in ecosystem["categories"].items() if paths]
    print(
        "GameGuru ecosystem scanned:",
        len(ecosystem["existing_roots"]),
        "roots /",
        len(usable_categories),
        "useful content categories",
    )

    environment = environment_archive(MAP, dry_run=False, backup=False)
    print(
        "Environment pass applied:",
        len(environment["generated_assets"]),
        "assets /",
        len(environment["placements"]),
        "placements",
    )

    world = world_archive(MAP, dry_run=False, backup=False)
    print(
        "Vesper world-story pass applied:",
        len(world["generated_assets"]),
        "assets /",
        len(world["placements"]),
        "placements /",
        world["south_gate_segments_removed"],
        "south-gate segments removed",
    )

    cards = build_original_cine_assets()
    SHOTLIST.parent.mkdir(parents=True, exist_ok=True)
    SHOTLIST.write_text(json.dumps(shotlist(), indent=2), encoding="utf-8")
    print("Cinematic presentation assets generated:", len(cards), "image cards")


def apply_visual_polish() -> None:
    from polish_relayfall import rewrite_archive, MAP

    report = rewrite_archive(MAP, dry_run=False, backup=False)
    print(
        "Visual pass applied:",
        len(report["visual_settings"]),
        "settings /",
        len(report["lights"]),
        "lights",
    )


def deploy(target: Path, polish: bool, production: bool) -> None:
    # Production is the preferred integrated path: ecosystem discovery and authored
    # world/presentation first, visual settings second, then validated map/assets deploy.
    if production:
        prepare_production_content()
    if polish or production:
        apply_visual_polish()

    target.mkdir(parents=True, exist_ok=True)

    # These are the project-authored/runtime-critical areas. Stock/DLC GameGuru
    # assets stay in the user's licensed MAX install and are discovered separately.
    mappings = [
        (FILES / "mapbank", target / "mapbank"),
        (FILES / "scriptbank" / "aegis_reach", target / "scriptbank" / "aegis_reach"),
        (FILES / "entitybank" / "Aegis Reach", target / "entitybank" / "Aegis Reach"),
        (FILES / "audiobank" / "aegis_reach", target / "audiobank" / "aegis_reach"),
        (FILES / "imagebank" / "aegis_reach", target / "imagebank" / "aegis_reach"),
        (FILES / "projectbank" / "Aegis Reach", target / "projectbank" / "Aegis Reach"),
    ]

    total = 0
    for source, destination in mappings:
        copied = copy_tree(source, destination)
        total += copied
        print(f"{source.relative_to(ROOT)} -> {destination} ({copied} files)")

    print()
    print("AEGIS REACH // MAX PLAYTEST DEPLOYED")
    print("Target:", target)
    print("Files copied:", total)
    if production:
        print("Mode: PRODUCTION SLICE (ecosystem + sky + open Vesper shelf + presentation + polish)")
        print("DLC report: Aegis Reach\\Design\\gameguru-ecosystem.json")
        print("World report: Aegis Reach\\Design\\world-story-pass.json")
        print("CineGuru setup: python tools\\cineguru_bootstrap.py")
    elif polish:
        print("Mode: VISUAL POLISH")
    else:
        print("Mode: FAST SCRIPT/MAP SYNC")
    print("Restart GameGuru MAX before testing so scripts and map data reload cleanly.")


def collect(target: Path) -> None:
    candidates = [
        target / "aegis-native-runtime.log",
        target.parent / "aegis-native-runtime.log",
    ]
    available = [path for path in candidates if path.exists()]
    if not available:
        print("No new Aegis runtime log found in the MAX user area.")
        print("Checked:")
        for path in candidates:
            print(" -", path)
        raise SystemExit(2)

    source = max(available, key=lambda path: path.stat().st_mtime)
    destination = GAME / "Design" / "native-runtime.log"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    print("AEGIS REACH // PLAYTEST COLLECTED")
    print("Source:", source)
    print("Repo log:", destination)
    print("Next: python tools\\summarize_playtest.py --json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("deploy", "collect"),
        help="deploy repo content to MAX or collect the latest runtime log",
    )
    parser.add_argument("--target", type=Path, help="override GameGuru MAX user Files directory")
    parser.add_argument(
        "--polish",
        action="store_true",
        help="apply tools/polish_relayfall.py before deploying",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="scan ecosystem + build environment/world/cinematic assets + visual polish before deploying",
    )
    args = parser.parse_args()

    target = args.target or default_max_files()
    if args.command == "deploy":
        deploy(target, args.polish, args.production)
    else:
        collect(target)


if __name__ == "__main__":
    main()
