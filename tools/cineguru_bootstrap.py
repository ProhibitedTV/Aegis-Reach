"""Discover the user's CineGuru MAX install and prepare Relayfall cinematic assets.

This does not copy or redistribute CineGuru DLC files. It scans the user's licensed
GameGuru MAX installation and user Files area, records the exact local CineGuru entity
and script paths, and generates original Aegis Reach title-card assets for CineGuru
image triggers.

Usage:
    python tools/cineguru_bootstrap.py
    python tools/cineguru_bootstrap.py --root "D:\\SteamLibrary\\steamapps\\common\\GameGuru MAX\\Files"
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"
REPORT = GAME / "Design" / "cineguru-discovery.json"
SHOTLIST = GAME / "Design" / "cineguru-shotlist.json"
CINE_IMAGES = FILES / "imagebank" / "aegis_reach" / "cine"


def candidate_roots():
    roots = []
    profile = os.environ.get("USERPROFILE")
    if profile:
        roots.append(Path(profile) / "Documents" / "GameGuruApps" / "GameGuruMAX" / "Files")
    roots += [
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\GameGuru MAX\Files"),
        Path(r"C:\Program Files\Steam\steamapps\common\GameGuru MAX\Files"),
    ]
    # Keep order, remove duplicate paths case-insensitively.
    seen = set(); result = []
    for path in roots:
        key = str(path).lower()
        if key not in seen:
            seen.add(key); result.append(path)
    return result


def text_lower(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return ""


def classify_fpe(path: Path):
    text = (path.name + "\n" + text_lower(path))
    if not ("cine" in text or "cg_" in text or "cg " in text):
        return None
    if "camera" in text and ("cinematic" in text or "cg" in text):
        return "camera"
    if "trigger" in text and "zone" in text:
        return "trigger_zone"
    if "trigger" in text:
        return "trigger"
    if "focus" in text:
        return "focus"
    if "light" in text:
        return "light"
    if "actor" in text:
        return "actor"
    if "mark" in text:
        return "mark"
    return "other"


def discover(roots):
    found_roots = [path for path in roots if path.exists()]
    entities = []
    scripts = []
    for root in found_roots:
        entitybank = root / "entitybank"
        if entitybank.exists():
            for path in entitybank.rglob("*.fpe"):
                kind = classify_fpe(path)
                if kind:
                    entities.append({
                        "kind": kind,
                        "root": str(root),
                        "path": str(path.relative_to(entitybank)),
                        "full_path": str(path),
                    })
        scriptbank = root / "scriptbank"
        if scriptbank.exists():
            for path in scriptbank.rglob("*.lua"):
                name = path.name.lower()
                text = "" if not (name.startswith("cg") or "cine" in name) else text_lower(path)
                if name.startswith("cg") or "cineguru" in text or "cine guru" in text:
                    scripts.append({
                        "root": str(root),
                        "path": str(path.relative_to(scriptbank)),
                        "full_path": str(path),
                    })
    # Deduplicate because the user Files area can contain a staged copy of install DLC.
    def unique(items, key):
        seen = set(); result = []
        for item in items:
            marker = key(item).lower()
            if marker not in seen:
                seen.add(marker); result.append(item)
        return result
    entities = unique(entities, lambda item: item["path"] + "|" + item["kind"])
    scripts = unique(scripts, lambda item: item["path"])
    return found_roots, entities, scripts


def font(size, bold=False):
    candidates = [
        FILES / "editors" / "templates" / "fonts" / "orbitron bold.ttf",
        FILES / "editors" / "uiv3" / "roboto-medium.ttf",
        Path(r"C:\Windows\Fonts\bahnschrift.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf") if bold else Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try: return ImageFont.truetype(str(path), size)
            except OSError: pass
    return ImageFont.load_default()


def make_card(path: Path, eyebrow: str, title: str, subtitle: str, accent=(79, 218, 231, 255)):
    width, height = 1600, 360
    image = Image.new("RGBA", (width, height), (5, 10, 16, 222))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 13, height), fill=accent)
    draw.rectangle((38, 45, 430, 49), fill=accent)
    draw.text((42, 66), eyebrow, font=font(28, True), fill=(174, 200, 212, 255))
    draw.text((40, 118), title, font=font(72, True), fill=(232, 242, 244, 255))
    draw.text((44, 228), subtitle, font=font(30), fill=(158, 180, 192, 255))
    draw.text((1290, 292), "AEGIS REACH", font=font(22, True), fill=accent)
    image.save(path, optimize=True)


def build_original_cine_assets():
    CINE_IMAGES.mkdir(parents=True, exist_ok=True)
    make_card(
        CINE_IMAGES / "relayfall_location_card.png",
        "OUTER COLONIES // DEFENSE GRID 19",
        "RELAYFALL",
        "AEGIS REACH // 04:17 LOCAL // ORBITAL STRIKE WINDOW OPEN",
        (79, 218, 231, 255),
    )
    make_card(
        CINE_IMAGES / "relayfall_warning_card.png",
        "KESTREL TACTICAL",
        "DEFENSE NETWORK COMPROMISED",
        "RESTORE NORTHSTAR // RESTORE LANTERN // SEIZE AEGIS FIRE CONTROL",
        (241, 165, 82, 255),
    )
    return [
        str((CINE_IMAGES / "relayfall_location_card.png").relative_to(FILES)),
        str((CINE_IMAGES / "relayfall_warning_card.png").relative_to(FILES)),
    ]


def shotlist():
    # Positions are design coordinates for manual placement in MAX. Camera marker
    # rotation should be aimed at target using the editor; CineGuru owns camera motion.
    return {
        "sequence": "RELAYFALL // COLD OPEN",
        "duration_seconds": 11.0,
        "trigger": {
            "type": "Cine-trigger zone",
            "position": [0, 645, -2700],
            "dtime": 0.1,
            "enable_skip": True,
            "disable_if_combat": False,
        },
        "shots": [
            {
                "id": "CG_INTRO_01_DEAD_ORBIT",
                "position": [-1500, 1750, -3380],
                "target": [0, 1200, 3300],
                "filmtime": 3.4,
                "fade": 1.2,
                "fls": 108,
                "fle": 84,
                "purpose": "Establish fortress, broken orbital spine, and Aurelia beyond it.",
                "image_trigger": "imagebank\\aegis_reach\\cine\\relayfall_location_card.png",
            },
            {
                "id": "CG_INTRO_02_INSERTION",
                "position": [760, 980, -3180],
                "target": [0, 760, -2050],
                "filmtime": 2.7,
                "fade": 0,
                "fls": 82,
                "fle": 72,
                "purpose": "Drop beneath the service gantry and reveal the player route.",
            },
            {
                "id": "CG_INTRO_03_WARDENS",
                "position": [-1220, 880, -2370],
                "target": [-800, 690, -2130],
                "filmtime": 2.4,
                "fade": 0,
                "fls": 76,
                "fle": 60,
                "purpose": "Show the opening two-Warden tactical problem before control returns.",
                "image_trigger": "imagebank\\aegis_reach\\cine\\relayfall_warning_card.png",
            },
            {
                "id": "CG_INTRO_04_HANDOFF",
                "position": [0, 790, -2870],
                "target": [0, 760, -1650],
                "filmtime": 2.5,
                "fade": 0.25,
                "fls": 72,
                "fle": 72,
                "purpose": "Match toward the player's first-person heading and hand off cleanly.",
            },
        ],
        "audio": {
            "underscore": "audiobank\\aegis_reach\\reach-underscore.wav",
            "briefing": "audiobank\\aegis_reach\\briefing.wav",
            "subtitle_lines": [
                "KESTREL: Vanguard Seven, Reach is dark.",
                "KESTREL: Three relays stand between us and an orbital strike.",
                "KESTREL: Wake Northstar. Wake Lantern. Then take AEGIS away from them.",
            ],
        },
        "visual_logic": [
            "Cine-trigger zone -> CG_INTRO_01_DEAD_ORBIT",
            "CG_INTRO_01_DEAD_ORBIT -> CG_INTRO_02_INSERTION",
            "CG_INTRO_02_INSERTION -> CG_INTRO_03_WARDENS",
            "CG_INTRO_03_WARDENS -> CG_INTRO_04_HANDOFF",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", help="additional/alternate GameGuru MAX Files root")
    args = parser.parse_args()
    roots = args.root or candidate_roots()
    found_roots, entities, scripts = discover(roots)
    generated = build_original_cine_assets()
    plan = shotlist()
    SHOTLIST.parent.mkdir(parents=True, exist_ok=True)
    SHOTLIST.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    by_kind = {}
    for entity in entities:
        by_kind.setdefault(entity["kind"], []).append(entity)
    report = {
        "searched_roots": [str(path) for path in roots],
        "existing_roots": [str(path) for path in found_roots],
        "cineguru_entities": entities,
        "cineguru_scripts": scripts,
        "by_kind": by_kind,
        "generated_original_assets": generated,
        "shotlist": str(SHOTLIST),
        "camera_candidates": by_kind.get("camera", []),
        "trigger_zone_candidates": by_kind.get("trigger_zone", []),
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("AEGIS REACH // CINEGURU BOOTSTRAP")
    print("MAX roots found:", len(found_roots))
    print("CineGuru entity candidates:", len(entities))
    print("CineGuru script candidates:", len(scripts))
    print("Camera candidates:", len(report["camera_candidates"]))
    print("Trigger-zone candidates:", len(report["trigger_zone_candidates"]))
    print("Original cinematic image assets:", len(generated))
    print("Discovery report:", REPORT)
    print("Shot list:", SHOTLIST)
    if report["camera_candidates"] and report["trigger_zone_candidates"]:
        print("CineGuru detected. Open Design/CINEGURU_OPENING.md for the 4-shot Visual Logic setup.")
    else:
        print("CineGuru was not confidently located. Pass --root with its GameGuru MAX Files directory if needed.")


if __name__ == "__main__":
    main()
