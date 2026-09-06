"""Inventory the local GameGuru MAX ecosystem for Aegis Reach production work.

The scanner never copies DLC. It discovers licensed local content and produces a
small JSON report that can be used to choose environment, cinematic, VFX, HUD,
audio, creature, and weapon assets for later authored passes.

Usage:
    python tools/ecosystem_scan.py
    python tools/ecosystem_scan.py --root "D:\\SteamLibrary\\steamapps\\common\\GameGuru MAX\\Files"
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "Aegis Reach"
REPORT = GAME / "Design" / "gameguru-ecosystem.json"

BANKS = ("entitybank", "scriptbank", "gamecore", "effectbank", "imagebank", "audiobank")

# These are intentionally broad path/name probes. MAX DLC folder naming is not
# perfectly uniform between authors/releases, so positive keyword evidence is more
# robust than assuming one hard-coded pack path.
CATEGORIES = {
    "cinematic": ("cineguru", "cine guru", "cg_", "cinematic", "camera marker"),
    "offworld_architecture": ("offworld", "space station", "sci-fi", "scifi", "future bunker", "futuristic bunker"),
    "cyber_city": ("cyber", "hologram", "holographic", "neon", "future city"),
    "future_characters": ("warriors of the future", "future soldier", "future character", "sci-fi character"),
    "robotics_creatures": ("robot", "robotic", "drone", "droid", "alien"),
    "particles_vfx": ("particle", "particles", "explosion", "spark", "smoke", "energy"),
    "future_hud": ("cyberpunk hud", "far future hud", "future hud", "hud"),
    "future_weapons": ("scifi blade", "sci-fi blade", "energy blade", "laser", "plasma", "future weapon"),
    "industrial": ("industrial", "bunker", "scaffold", "sewer", "hazard"),
    "audio": ("audio ambience", "ambience", "ambient", "machine", "alarm", "radio"),
}


def _steam_library_roots() -> list[Path]:
    candidates = [
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Steam",
        Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Steam",
        Path(r"D:\SteamLibrary"),
        Path(r"E:\SteamLibrary"),
        Path(r"F:\SteamLibrary"),
    ]
    roots: list[Path] = []
    for steam in candidates:
        if steam.exists():
            roots.append(steam)
        vdf = steam / "steamapps" / "libraryfolders.vdf"
        if not vdf.exists():
            continue
        try:
            text = vdf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for match in re.finditer(r'"path"\s+"([^"]+)"', text):
            roots.append(Path(match.group(1).replace("\\\\", "\\")))
    seen = set(); result = []
    for root in roots:
        key = str(root).lower()
        if key not in seen:
            seen.add(key); result.append(root)
    return result


def candidate_files_roots() -> list[Path]:
    roots: list[Path] = []
    profile = os.environ.get("USERPROFILE")
    if profile:
        roots.append(Path(profile) / "Documents" / "GameGuruApps" / "GameGuruMAX" / "Files")
    env_root = os.environ.get("GAMEGURU_MAX_FILES")
    if env_root:
        roots.append(Path(env_root))
    for library in _steam_library_roots():
        if library.name.lower() == "steam":
            candidate = library / "steamapps" / "common" / "GameGuru MAX" / "Files"
        else:
            candidate = library / "steamapps" / "common" / "GameGuru MAX" / "Files"
        roots.append(candidate)
    # Default fallback even if Steam discovery cannot read libraryfolders.vdf.
    roots.append(Path(r"C:\Program Files (x86)\Steam\steamapps\common\GameGuru MAX\Files"))
    seen = set(); result = []
    for path in roots:
        key = str(path).lower()
        if key not in seen:
            seen.add(key); result.append(path)
    return result


def classify(relative: str) -> list[str]:
    text = relative.lower().replace("_", " ").replace("-", " ")
    matches = []
    for category, probes in CATEGORIES.items():
        if any(probe in text for probe in probes):
            matches.append(category)
    return matches


def scan(roots: list[Path] | None = None) -> dict:
    roots = roots or candidate_files_roots()
    existing = [path for path in roots if path.exists()]
    categories = {key: [] for key in CATEGORIES}
    seen_paths = set()
    bank_counts = {}

    # Limit samples instead of writing a gigantic manifest; this report is a scout,
    # not a redistribution mechanism.
    sample_limit = 80
    for root in existing:
        root_counts = {}
        for bank in BANKS:
            base = root / bank
            if not base.exists():
                continue
            count = 0
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                count += 1
                rel = str(path.relative_to(root)).replace("\\", "/")
                marker = rel.lower()
                if marker in seen_paths:
                    continue
                seen_paths.add(marker)
                for category in classify(rel):
                    if len(categories[category]) < sample_limit:
                        categories[category].append(rel)
            root_counts[bank] = count
        bank_counts[str(root)] = root_counts

    recommendations = []
    if categories["offworld_architecture"]:
        recommendations.append("Use off-world/future architecture for relay machinery, corridors, doors, and AEGIS-core infrastructure; preserve current combat lanes.")
    if categories["cyber_city"]:
        recommendations.append("Use cyber-city/hologram assets as signage, distant skyline dressing, maintenance displays, and navigation landmarks rather than dense street clutter.")
    if categories["cinematic"]:
        recommendations.append("Bind CineGuru cameras, triggers, lights, actors, subtitles, and image/audio cues to the structured Relayfall shot list.")
    if categories["particles_vfx"]:
        recommendations.append("Add authored sparks, steam, energy discharge, impacts, and orbital-strike debris at landmark moments; keep combat silhouettes readable.")
    if categories["future_hud"]:
        recommendations.append("Mine future HUD packs for frame/reticle vocabulary only where it strengthens the existing cyan/amber tactical HUD.")
    if categories["robotics_creatures"] or categories["future_characters"]:
        recommendations.append("Prototype one non-rifleman sci-fi enemy role before increasing enemy count: shield/support/drone/area-denial behavior preferred.")
    if categories["future_weapons"]:
        recommendations.append("Reserve future weapons for sandbox roles that change engagement distance or movement; avoid redundant reskins of the Mk18/AR/shotgun trio.")

    report = {
        "searched_roots": [str(path) for path in roots],
        "existing_roots": [str(path) for path in existing],
        "bank_file_counts": bank_counts,
        "categories": categories,
        "recommendations": recommendations,
        "policy": "Discovery only. No third-party DLC files are copied into the repository by this tool.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", help="GameGuru MAX Files root; may be repeated")
    args = parser.parse_args()
    report = scan(args.root)
    print("AEGIS REACH // GAMEGURU MAX ECOSYSTEM SCAN")
    print("MAX roots found:", len(report["existing_roots"]))
    for category, samples in report["categories"].items():
        if samples:
            print(f"  {category}: {len(samples)} sampled matches")
    print("Recommendations:", len(report["recommendations"]))
    print("Report:", REPORT)


if __name__ == "__main__":
    main()
