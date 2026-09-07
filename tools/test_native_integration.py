"""Headless structural test for the integrated Relayfall production pipeline.

Exercises the map-transform sequence in memory: environment -> Vesper world -> layered
terrain story -> story bindings -> optional shelf combat -> native MAX presentation and
adaptive music bindings. It never replaces the checked-in .fpm.
"""
from __future__ import annotations

import zipfile

from max_archive import PASSWORD
from native_format import read_ele
from environment_pass import MAP, build_assets as build_environment_assets, patch_environment, get_suffix
from world_story_pass import build_assets as build_world_assets, patch_world
from terrain_story_pass import build_assets as build_terrain_assets, patch_terrain, PLACEMENTS as TERRAIN_PLACEMENTS
from world_story_logic_pass import patch as patch_story_logic, STORY_NAMES
from shelf_encounter_pass import patch_encounter
from native_integration_pass import (
    patch as patch_native,
    CONTROLLER_NAME,
    MUSIC_CONTROLLER_NAME,
    MUSIC_TRACKS,
)


def name_set(data: bytes) -> set[str]:
    _, entities = read_ele(data)
    return {str(get_suffix(entity, "eleprof.name_s", "")) for entity in entities}


def main():
    build_environment_assets()
    build_world_assets()
    build_terrain_assets()

    with zipfile.ZipFile(MAP) as source:
        source.setpassword(PASSWORD)
        map_ele = source.read("map.ele")
        map_ent = source.read("map.ent")

    env_ele, env_ent, env_added, _, _ = patch_environment(map_ele, map_ent)
    assert len(env_added) >= 15, len(env_added)

    world_ele, world_ent, world_added, removed_gate, _, _ = patch_world(env_ele, env_ent)
    assert removed_gate == 4, removed_gate
    assert len(world_added) >= 10, len(world_added)

    terrain_ele, terrain_ent, terrain_added, _, _ = patch_terrain(world_ele, world_ent)
    assert len(terrain_added) == len(TERRAIN_PLACEMENTS), (len(terrain_added), len(TERRAIN_PLACEMENTS))

    story_ele, story_bound = patch_story_logic(terrain_ele)
    assert set(story_bound) == STORY_NAMES, story_bound

    shelf_ele, shelf_ent, shelf_added, _ = patch_encounter(story_ele, terrain_ent)
    shelf_enemies = [item for item in shelf_added if item["kind"] == "enemy"]
    assert len(shelf_enemies) == 4, len(shelf_enemies)

    native_ele, beacons, entity_count = patch_native(shelf_ele)
    assert len(beacons) == 4, beacons

    names = name_set(native_ele)
    assert CONTROLLER_NAME in names
    assert MUSIC_CONTROLLER_NAME in names
    for expected in STORY_NAMES:
        assert expected in names
    for placement in TERRAIN_PLACEMENTS:
        assert placement[0] in names, placement[0]
    for i in range(21, 25):
        assert any(f"SHELF WARDEN {i}" in name for name in names), i

    _, entities = read_ele(native_ele)
    by_name = {
        str(get_suffix(entity, "eleprof.name_s", "")): entity
        for entity in entities
    }
    scripts = {
        name: str(get_suffix(entity, "eleprof.aimain_s", ""))
        for name, entity in by_name.items()
    }
    assert scripts[CONTROLLER_NAME].lower().endswith(r"aegis_reach\aegis_world.lua")
    assert scripts[MUSIC_CONTROLLER_NAME].lower().endswith(r"aegis_reach\aegis_music.lua")
    for name in beacons:
        assert scripts[name].lower().endswith(r"aegis_reach\aegis_beacon.lua")
    for name in STORY_NAMES:
        assert scripts[name].lower().endswith(r"aegis_reach\aegis_story.lua")

    music = by_name[MUSIC_CONTROLLER_NAME]
    assert str(get_suffix(music, "eleprof.soundset_s", "")) == MUSIC_TRACKS[0]
    assert str(get_suffix(music, "eleprof.soundset1_s", "")) == MUSIC_TRACKS[1]
    assert str(get_suffix(music, "eleprof.soundset2_s", "")) == MUSIC_TRACKS[2]

    print("AEGIS REACH // MAX-NATIVE PIPELINE TEST PASS")
    print("Environment placements:", len(env_added))
    print("Vesper base placements:", len(world_added))
    print("Layered terrain placements:", len(terrain_added))
    print("Shelf enemies:", len(shelf_enemies))
    print("Story bindings:", len(story_bound))
    print("Mission-reactive beacons:", len(beacons))
    print("Adaptive score slots:", len(MUSIC_TRACKS))
    print("Final map entities:", entity_count)
    print("Binary .ele round-trip: OK")


if __name__ == "__main__":
    main()
