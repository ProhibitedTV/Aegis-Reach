"""Bind Aegis Reach presentation systems to GameGuru MAX-native Lua/logic hooks.

Runs after environment/world passes. It does not replace MAX Visual Logic; it creates
stable script endpoints that Visual Logic, CineGuru, lights, particles, doors, audio
emitters and other DLC systems can connect to in the editor.

Bindings:
  * hidden global world-state controller -> aegis_world.lua
  * hidden adaptive score controller -> aegis_music.lua
  * horizon beacons -> aegis_beacon.lua
  * existing relay/story scripts expose PerformLogicConnections/ActivateIfUsed
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
from environment_pass import get_suffix, set_suffix

GAME = ROOT / "Aegis Reach"
MAP = GAME / "Files" / "mapbank" / "Aegis Reach - Relayfall.fpm"
REPORT = GAME / "Design" / "native-integration-pass.json"
CONTROLLER_NAME = "NATIVE // WORLD STATE CONTROLLER"
MUSIC_CONTROLLER_NAME = "NATIVE // ADAPTIVE MUSIC"
MUSIC_TRACKS = {
    0: r"aegis_reach\music\salt_moon_drift.wav",
    1: r"aegis_reach\music\moon_outpost_drift.wav",
    2: r"aegis_reach\music\orbital_catacomb.wav",
}


def clean_clone(entity: dict) -> dict:
    clone = copy.deepcopy(entity)
    for key in list(clone):
        suffix = key.split(":", 1)[-1]
        if key.startswith(("319:", "334:")) or "ObjectRelationships" in key:
            clone[key] = "" if isinstance(clone[key], str) else 0
        if suffix in {
            "eleprof.parententityindex", "eleprof.parentlimbindex", "iHasParentIndex",
            "creationOfGroupID", "quatmode", "eleprof.bAutoFlatten",
        }:
            clone[key] = 0
    set_suffix(clone, "quatw", 1.0)
    return clone


def configure_dynamic(entity: dict, script: str) -> None:
    set_suffix(entity, "staticflag", 0)
    set_suffix(entity, "eleprof.aimain_s", script)
    set_suffix(entity, "eleprof.phyalways", 1)
    set_suffix(entity, "eleprof.isimmobile", 1)
    set_suffix(entity, "eleprof.strength", 0)


def clear_payload(entity: dict) -> None:
    for suffix in (
        "eleprof.soundset_s", "eleprof.soundset1_s", "eleprof.soundset2_s",
        "eleprof.soundset3_s", "eleprof.soundset4_s", "eleprof.hasweapon_s",
    ):
        set_suffix(entity, suffix, "")


def patch(map_ele: bytes):
    version, entities = read_ele(map_ele)

    # Deterministic reruns.
    entities = [
        entity for entity in entities
        if str(get_suffix(entity, "eleprof.name_s", "")) not in {CONTROLLER_NAME, MUSIC_CONTROLLER_NAME}
    ]

    mission_controller = None
    beacon_names = []
    for entity in entities:
        name = str(get_suffix(entity, "eleprof.name_s", ""))
        if name == "AEGIS MISSION CONTROLLER":
            mission_controller = entity
        if name.startswith("ENV // BEACON"):
            configure_dynamic(entity, r"aegis_reach\aegis_beacon.lua")
            beacon_names.append(name)

    if mission_controller is None:
        raise RuntimeError("Could not locate AEGIS MISSION CONTROLLER template")

    world = clean_clone(mission_controller)
    set_suffix(world, "eleprof.name_s", CONTROLLER_NAME)
    set_suffix(world, "x", 0.0)
    set_suffix(world, "y", 620.0)
    set_suffix(world, "z", -2850.0)
    configure_dynamic(world, r"aegis_reach\aegis_world.lua")
    clear_payload(world)
    entities.append(world)

    # A single hidden entity owns the three supplied score cues as Sound0..Sound2.
    # aegis_music.lua maps the world controller's semantic music states onto these
    # slots and crossfades using MAX's native non-3D sound controls.
    music = clean_clone(mission_controller)
    set_suffix(music, "eleprof.name_s", MUSIC_CONTROLLER_NAME)
    set_suffix(music, "x", 40.0)
    set_suffix(music, "y", 620.0)
    set_suffix(music, "z", -2850.0)
    configure_dynamic(music, r"aegis_reach\aegis_music.lua")
    clear_payload(music)
    set_suffix(music, "eleprof.soundset_s", MUSIC_TRACKS[0])
    set_suffix(music, "eleprof.soundset1_s", MUSIC_TRACKS[1])
    set_suffix(music, "eleprof.soundset2_s", MUSIC_TRACKS[2])
    entities.append(music)

    result = write_ele(version, entities)
    check_version, check_entities = read_ele(result)
    assert check_version == version
    assert len(check_entities) == len(entities)
    return result, beacon_names, len(entities)


def rewrite_archive(path: Path = MAP, *, dry_run=False, backup=False):
    with zipfile.ZipFile(path) as source:
        source.setpassword(PASSWORD)
        infos = source.infolist()
        payload = {info.filename: source.read(info.filename) for info in infos}
    if "map.ele" not in payload:
        raise RuntimeError("Relayfall archive is missing map.ele")

    patched, beacons, entity_count = patch(payload["map.ele"])
    payload["map.ele"] = patched
    report = {
        "map": str(path),
        "dry_run": dry_run,
        "world_controller": CONTROLLER_NAME,
        "music_controller": MUSIC_CONTROLLER_NAME,
        "music_tracks": {str(slot): path for slot, path in MUSIC_TRACKS.items()},
        "beacons": beacons,
        "entity_count": entity_count,
        "native_apis": [
            "SetActivated", "PerformLogicConnections", "ActivateIfUsed",
            "SetEntityEmissiveColor", "SetEntityEmissiveStrength",
            "GetAmbienceRed/Green/Blue", "SetAmbienceRed/Green/Blue",
            "GetExposure", "SetExposure", "LoopNon3DSound", "StopSound",
            "SetSound", "SetSoundVolume",
        ],
    }
    if dry_run:
        return report

    if backup:
        backup_path = path.with_name(path.stem + ".pre-native-integration.fpm")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            report["backup"] = str(backup_path)

    with tempfile.NamedTemporaryFile(prefix="relayfall-native-integration-", suffix=".fpm", delete=False, dir=path.parent) as handle:
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
    print("AEGIS REACH // MAX-NATIVE INTEGRATION")
    print("World controller:", report["world_controller"])
    print("Adaptive music controller:", report["music_controller"])
    print("Score cues:", len(report["music_tracks"]))
    print("Mission-reactive beacons:", len(report["beacons"]))
    print("Map entities after pass:", report["entity_count"])
    if args.dry_run:
        print("Dry run only; map archive was not replaced.")
    else:
        print("Native integration injected and archive validation passed.")
        print("Report:", REPORT)


if __name__ == "__main__":
    main()
