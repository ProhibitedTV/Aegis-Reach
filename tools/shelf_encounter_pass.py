"""Add the first optional outdoor combat pocket to Vesper's brine shelf.

Run after world_story_pass.py. The encounter remains optional: shelf patrols are
visible in the landscape but aegis_enemy.lua does not register or wake them until the
player intentionally crosses the south breach. This preserves the quiet world reveal
and keeps the original fortress mission flow intact while the new exterior is tested.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from max_archive import PASSWORD, convert
from native_format import ROOT, read_ele, write_ele
from environment_pass import parse_bank, write_bank, get_suffix, set_suffix

GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"
MAP = FILES / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "shelf-encounter-pass.json"
PREFIX = "SHELF //"


def bank_path(entity: dict, bank: list[str]) -> str:
    idx = int(get_suffix(entity, "bankindex", 0) or 0)
    return bank[idx - 1] if 0 < idx <= len(bank) else ""


def find_template(entities: list[dict], bank: list[str], needle: str) -> dict:
    needle = needle.lower()
    for entity in entities:
        if needle in bank_path(entity, bank).lower():
            return entity
    raise RuntimeError(f"Could not find template entity for {needle!r}")


def clone_clean(template: dict) -> dict:
    entity = copy.deepcopy(template)
    for key in list(entity):
        suffix = key.split(":", 1)[-1]
        if key.startswith(("319:", "334:")) or "ObjectRelationships" in key:
            entity[key] = "" if isinstance(entity[key], str) else 0
        if suffix in {
            "eleprof.parententityindex", "eleprof.parentlimbindex", "iHasParentIndex",
            "creationOfGroupID", "quatmode", "eleprof.bAutoFlatten",
        }:
            entity[key] = 0
    set_suffix(entity, "quatw", 1.0)
    return entity


def place(entity: dict, name: str, x: float, y: float, z: float, ry: float = 0.0) -> None:
    set_suffix(entity, "x", x)
    set_suffix(entity, "y", y)
    set_suffix(entity, "z", z)
    set_suffix(entity, "rx", 0.0)
    set_suffix(entity, "ry", ry)
    set_suffix(entity, "rz", 0.0)
    set_suffix(entity, "eleprof.name_s", name)


def configure_enemy(entity: dict, *, name: str, x: float, y: float, z: float, ry: float,
                    weapon: str, strength: int = 100, accuracy: int = 125) -> None:
    place(entity, name, x, y, z, ry)
    set_suffix(entity, "staticflag", 0)
    set_suffix(entity, "eleprof.isimmobile", 0)
    set_suffix(entity, "eleprof.phyalways", 1)
    set_suffix(entity, "eleprof.strength", strength)
    set_suffix(entity, "eleprof.hasweapon_s", weapon)
    set_suffix(entity, "eleprof.quantity", 36)
    set_suffix(entity, "eleprof.damage", 8)
    set_suffix(entity, "eleprof.accuracy", accuracy)
    set_suffix(entity, "eleprof.conerange", 1400.0)
    set_suffix(entity, "eleprof.weapondamagemultiplier", 0.3)
    set_suffix(entity, "eleprof.aimain_s", r"aegis_reach\aegis_enemy.lua")
    set_suffix(entity, "eleprof.soundset4_s", "")


def configure_pickup(entity: dict, *, name: str, x: float, y: float, z: float, quantity: int) -> None:
    place(entity, name, x, y, z, 22.0)
    set_suffix(entity, "eleprof.quantity", quantity)


def patch_encounter(map_ele: bytes, map_ent: bytes):
    version, entities = read_ele(map_ele)
    bank = parse_bank(map_ent)

    # Deterministic reruns: remove only entities authored by this pass.
    entities = [
        entity for entity in entities
        if not str(get_suffix(entity, "eleprof.name_s", "")).startswith(PREFIX)
    ]

    enemy_template = find_template(entities, bank, r"Characters\Tony - Armed Response.fpe")
    rifle_template = find_template(entities, bank, r"Max Collection\Weapons\Patrol Rifle.fpe")
    grenade_template = find_template(entities, bank, r"Max Collection\Weapons\Frag Grenade.fpe")

    added: list[dict] = []

    # Index 21..24 deliberately maps through aegis_enemy.lua to flanker, anchor,
    # hunter, skirmisher. Their geometry creates a broad outdoor crossfire rather
    # than another corridor encounter.
    enemy_specs = [
        # west-side angle: should tempt the player to use the western basalt mass.
        ("SHELF // SHELF WARDEN 21", -1180, 586, -4470, 18, r"enhanced\MK18", 100, 125),
        # elevated long-range anchor: starts above the east ridge and settles onto collision.
        ("SHELF // SHELF WARDEN 22", 1500, 760, -5650, 195, r"enhanced\AR", 110, 135),
        # central pressure: makes simply running straight across the old sea floor expensive.
        ("SHELF // SHELF WARDEN 23", 280, 586, -4870, 176, r"enhanced\MK18", 100, 120),
        # deeper contact: prevents the first kill pair from ending the whole outdoor decision.
        ("SHELF // SHELF WARDEN 24", 920, 586, -6180, 205, r"enhanced\MK18", 100, 122),
    ]
    for name, x, y, z, ry, weapon, strength, accuracy in enemy_specs:
        entity = clone_clean(enemy_template)
        configure_enemy(
            entity, name=name, x=x, y=y, z=z, ry=ry,
            weapon=weapon, strength=strength, accuracy=accuracy,
        )
        entities.append(entity)
        added.append({"name": name, "kind": "enemy", "x": x, "y": y, "z": z, "weapon": weapon})

    # Exploration reward: Mira's wreck gives the player a tool that naturally
    # recontextualizes the shelf into a longer-range fight.
    rifle = clone_clean(rifle_template)
    configure_pickup(
        rifle,
        name="SHELF // MERIDIAN CACHE // MARKSMAN RIFLE",
        x=-1510, y=610, z=-5415, quantity=60,
    )
    entities.append(rifle)
    added.append({"name": "SHELF // MERIDIAN CACHE // MARKSMAN RIFLE", "kind": "weapon", "x": -1510, "y": 610, "z": -5415})

    grenade = clone_clean(grenade_template)
    configure_pickup(
        grenade,
        name="SHELF // MERIDIAN CACHE // FRAG PAIR",
        x=-1440, y=610, z=-5380, quantity=2,
    )
    entities.append(grenade)
    added.append({"name": "SHELF // MERIDIAN CACHE // FRAG PAIR", "kind": "weapon", "x": -1440, "y": 610, "z": -5380})

    result_ele = write_ele(version, entities)
    check_version, check_entities = read_ele(result_ele)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result_ele, write_bank(bank), added, len(entities)


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False):
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}

    if "map.ele" not in payload or "map.ent" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele or map.ent")

    patched_ele, patched_ent, added, entity_count = patch_encounter(payload["map.ele"], payload["map.ent"])
    payload["map.ele"] = patched_ele
    payload["map.ent"] = patched_ent

    report = {
        "map": str(path),
        "dry_run": dry_run,
        "placements": added,
        "entity_count": entity_count,
        "enemy_count": sum(1 for item in added if item["kind"] == "enemy"),
        "reward_count": sum(1 for item in added if item["kind"] == "weapon"),
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-shelf-encounter.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-shelf-encounter-", suffix=".fpm", delete=False, dir=path.parent) as handle:
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
    print("AEGIS REACH // VESPER SHELF ENCOUNTER")
    print("Map:", report["map"])
    print("Enemies:", report["enemy_count"])
    print("Exploration rewards:", report["reward_count"])
    print("Map entities after pass:", report["entity_count"])
    if args.dry_run:
        print("Dry run only; map archive was not replaced.")
    else:
        print("Shelf encounter injected and MAX archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
