"""Inventory owned GameGuru MAX / Classic entity libraries without copying media.

The scanner is intentionally read-only. It classifies FPE/model pairs so Aegis Reach can
mine a large owned library pack-by-pack while keeping licensed binaries out of Git.
Machine-specific absolute paths are never written unless the caller explicitly asks for
them on stdout with --verbose.
"""
from __future__ import annotations

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json
import os
import re

try:
    from native_format import INSTALL as MAX_FILES
except Exception:
    MAX_FILES = Path(r"C:\Program Files (x86)\Steam\steamapps\common\GameGuru MAX\Files")

USERPROFILE = Path(os.environ.get("USERPROFILE", str(Path.home())))
MAX_USER_FILES = USERPROFILE / "Documents" / "GameGuruApps" / "GameGuruMAX" / "Files"
CLASSIC_CANDIDATES = (
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\Game Guru\Files"),
    Path(r"C:\Program Files (x86)\Steam\steamapps\common\GameGuru\Files"),
    Path(r"C:\Program Files\Steam\steamapps\common\Game Guru\Files"),
    Path(r"C:\Program Files\Steam\steamapps\common\GameGuru\Files"),
)

DEFAULT_SCRIPT_NAMES = {"", "no_behavior_selected.lua", "default.lua", "static.lua"}
CHARACTER_HINTS = {"character", "characters", "people", "zombie", "zombies", "npc", "creature"}
WEAPON_HINTS = {"weapon", "weapons", "gun", "guns", "ammo", "ammunition"}
CHARACTER_CREATOR_HINTS = {"character creator", "charactercreator"}


@dataclass
class EntityRecord:
    source: str
    relative_fpe: str
    model: str
    model_exists: bool
    collisionmode: int | None
    script: str
    is_character: bool
    is_weapon: bool
    is_animated: bool
    is_scripted: bool
    pbr_ready: bool
    risk: str
    category: str
    score: int


def parse_fpe(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith((";", "//")) or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip().lower()] = value.strip().strip('"')
    return data


def _truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in {"", "0", "false", "no", "none"}


def _parts(text: str) -> set[str]:
    normalized = re.sub(r"[_\-/\\]+", " ", text.lower())
    return set(normalized.split())


def _declared_or_sibling_pbr(fpe: Path, data: dict[str, str]) -> bool:
    declared = sum(bool(data.get(k)) for k in ("basecolormap", "normalmap", "surfacemap", "emissivemap"))
    if declared >= 2:
        return True
    stem = fpe.stem.lower()
    names = {p.name.lower() for p in fpe.parent.iterdir() if p.is_file()}
    has_normal = any(n in names for n in (stem + "_normal.dds", stem + "_normal.png", stem + "_n.dds"))
    has_surface = any(n in names for n in (stem + "_surface.dds", stem + "_surface.png"))
    has_color = any(n in names for n in (stem + "_color.dds", stem + "_color.png", stem + "_d.dds"))
    return has_color and (has_normal or has_surface)


def classify(source: str, root: Path, fpe: Path) -> EntityRecord:
    data = parse_fpe(fpe)
    rel = fpe.relative_to(root).as_posix()
    model_name = data.get("model", "")
    model = fpe.parent / model_name.replace("\\", os.sep).replace("/", os.sep) if model_name else None
    model_exists = bool(model_name and model and model.is_file())

    tokens = _parts(rel + " " + model_name + " " + data.get("desc", ""))
    is_character = _truthy(data.get("ischaracter")) or bool(tokens & CHARACTER_HINTS)
    is_weapon = bool(tokens & WEAPON_HINTS) or _truthy(data.get("hasweapon"))
    script = data.get("aimain", data.get("aimain_s", "")).replace("/", "\\").lower()
    is_scripted = bool(script and script not in DEFAULT_SCRIPT_NAMES)
    is_animated = any(key.startswith("anim") or key in {"playanimineditor", "animmax"} for key in data)
    pbr_ready = _declared_or_sibling_pbr(fpe, data)

    collisionmode = None
    try:
        if "collisionmode" in data:
            collisionmode = int(float(data["collisionmode"]))
    except ValueError:
        pass

    path_text = rel.lower()
    if any(h in path_text for h in CHARACTER_CREATOR_HINTS):
        risk, category = "high", "character_creator"
    elif is_character:
        risk, category = "high", "character_or_creature"
    elif is_weapon:
        risk, category = "high", "weapon_or_ammo"
    elif not model_exists:
        risk, category = "high", "missing_model"
    elif is_scripted or is_animated:
        risk, category = "medium", "scripted_or_animated"
    else:
        risk, category = "low", "static_prop"

    score = 0
    if category == "static_prop": score += 60
    if pbr_ready: score += 20
    if collisionmode in (0, 2, 3, 9, 10, 11, 12): score += 8
    if source == "max-user": score += 5
    if source == "classic": score -= 5
    if risk == "high": score -= 100

    return EntityRecord(
        source=source, relative_fpe=rel, model=model_name, model_exists=model_exists,
        collisionmode=collisionmode, script=script, is_character=is_character,
        is_weapon=is_weapon, is_animated=is_animated, is_scripted=is_scripted,
        pbr_ready=pbr_ready, risk=risk, category=category, score=score,
    )


def source_roots(include_core: bool = True) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    if include_core:
        roots.append(("max-core", MAX_FILES / "entitybank"))
    roots.append(("max-user", MAX_USER_FILES / "entitybank"))
    roots.extend(("classic", p / "entitybank") for p in CLASSIC_CANDIDATES)
    result=[];seen=set()
    for label,path in roots:
        key=str(path).lower()
        if path.is_dir() and key not in seen:
            result.append((label,path));seen.add(key)
    return result


def scan(roots: list[tuple[str, Path]], limit: int | None = None) -> list[EntityRecord]:
    records=[]
    for label,root in roots:
        for fpe in root.rglob("*.fpe"):
            try: records.append(classify(label,root,fpe))
            except (OSError,UnicodeError): continue
            if limit and len(records)>=limit: return records
    return records


def summarize(records: list[EntityRecord]) -> dict:
    counts=Counter(r.category for r in records)
    risks=Counter(r.risk for r in records)
    by_source=Counter(r.source for r in records)
    candidates=sorted((r for r in records if r.risk=="low" and r.model_exists),key=lambda r:(-r.score,r.source,r.relative_fpe.lower()))
    return {
        "entity_count":len(records),
        "by_source":dict(sorted(by_source.items())),
        "by_category":dict(sorted(counts.items())),
        "by_risk":dict(sorted(risks.items())),
        "top_static_candidates":[{
            "source":r.source,"relative_fpe":r.relative_fpe,"pbr_ready":r.pbr_ready,
            "collisionmode":r.collisionmode,"score":r.score,
        } for r in candidates[:100]],
        "policy":{
            "copy_media_into_git":False,
            "migration":"pack-by-pack",
            "production_dependency":"reference installed/user media only after native audition",
            "high_risk":["characters","weapons","character-creator assemblies","missing models"],
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap=ArgumentParser(description=__doc__)
    ap.add_argument("--no-max-core",action="store_true",help="skip the stock MAX entitybank")
    ap.add_argument("--limit",type=int,default=0,help="stop after N FPE files (0 = no limit)")
    ap.add_argument("--json",type=Path,help="write a portable relative-path report")
    ap.add_argument("--verbose",action="store_true",help="print discovered source roots")
    args=ap.parse_args(argv)

    roots=source_roots(include_core=not args.no_max_core)
    if not roots:
        print("No GameGuru MAX/Classic entitybank roots found.");return 2
    if args.verbose:
        for label,root in roots: print(f"{label}: {root}")

    records=scan(roots,args.limit or None)
    report=summarize(records)
    print("AEGIS REACH // OWNED ASSET LIBRARY AUDIT")
    print("Entities:",report["entity_count"])
    print("Sources:",", ".join(f"{k}={v}" for k,v in report["by_source"].items()))
    print("Categories:",", ".join(f"{k}={v}" for k,v in report["by_category"].items()))
    print("Low-risk static candidates:",report["by_risk"].get("low",0))
    print("Top candidates:")
    for item in report["top_static_candidates"][:20]:
        pbr="PBR" if item["pbr_ready"] else "legacy-material"
        print(f"  [{item['source']}] {item['relative_fpe']} // {pbr} // collision {item['collisionmode']}")
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(report,indent=2));print("Portable report:",args.json)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
