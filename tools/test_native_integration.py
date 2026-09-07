"""Headless structural test for the integrated Relayfall production pipeline.

Exercises the map transform sequence in memory and validates the GameGuru MAX-native
terrain assumptions without allocating the full 80 MiB sculpt payload. Actual FPM
sculpt serialization is validated by native_terrain_pass.py during production deploy.
"""
from __future__ import annotations

import zipfile

from max_archive import PASSWORD
from native_format import read_ele
from environment_pass import MAP, build_assets as build_environment_assets, patch_environment, get_suffix
from world_story_pass import build_assets as build_world_assets, patch_world
from terrain_story_pass import build_assets as build_terrain_assets, patch_terrain
from shelf_encounter_pass import patch_encounter
from native_terrain_pass import (
    GRID,
    SCULPT_BYTES,
    TYPE_BYTES,
    DEPRECATED_GROUND_NAMES,
    patch_entities as patch_native_terrain_entities,
    vesper_height_units,
    world_to_grid,
    sculpt_index,
)
from world_story_logic_pass import patch as patch_story_logic, STORY_NAMES
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
    assert terrain_added, "terrain story pass should still add architectural/story props"

    shelf_ele, shelf_ent, shelf_added, _ = patch_encounter(terrain_ele, terrain_ent)
    shelf_enemies = [item for item in shelf_added if item["kind"] == "enemy"]
    assert len(shelf_enemies) == 4, len(shelf_enemies)

    # This is the production correction: mesh substitutes disappear and generated
    # exterior entities move onto the same analytic shape written into MAX's native
    # 4096x4096 terrain sculpt buffer.
    native_terrain_ele, terrain_entity_report = patch_native_terrain_entities(shelf_ele)
    names_after_terrain = name_set(native_terrain_ele)
    for deprecated in DEPRECATED_GROUND_NAMES:
        assert deprecated not in names_after_terrain, deprecated
    assert len(terrain_entity_report["removed_mesh_ground"]) >= 10
    assert len(terrain_entity_report["snapped_entities"]) >= 10

    story_ele, story_bound = patch_story_logic(native_terrain_ele)
    assert set(story_bound) == STORY_NAMES, story_bound

    native_ele, beacons, entity_count = patch_native(story_ele)
    assert len(beacons) == 4, beacons

    names = name_set(native_ele)
    assert CONTROLLER_NAME in names
    assert MUSIC_CONTROLLER_NAME in names
    for expected in STORY_NAMES:
        assert expected in names
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

    # Engine-source invariants for the Wicked/MAX terrain system.
    assert GRID == 4096
    assert TYPE_BYTES == 4096 * 4096
    assert SCULPT_BYTES == 4096 * 4096 * 5
    assert sculpt_index(2048, 2048) >= 0
    assert world_to_grid(0, 50000) == 2048

    # Composition sanity: the terrain is no longer a flat plane.
    fortress = vesper_height_units(0, 0)
    basin = vesper_height_units(0, -5200)
    west_ridge = vesper_height_units(-2350, -5000)
    east_ridge = vesper_height_units(2450, -5700)
    fracture = vesper_height_units(3300, -6500)
    south_rim = vesper_height_units(0, -11500)
    assert fortress > basin
    assert west_ridge > basin + 250
    assert east_ridge > basin + 300
    assert fracture < east_ridge - 200
    assert south_rim > basin + 500

    print("AEGIS REACH // MAX-NATIVE PIPELINE TEST PASS")
    print("Environment placements:", len(env_added))
    print("Vesper story placements:", len(world_added) + len(terrain_added))
    print("Prototype mesh ground removed:", len(terrain_entity_report["removed_mesh_ground"]))
    print("Terrain-snapped entities:", len(terrain_entity_report["snapped_entities"]))
    print("Shelf enemies:", len(shelf_enemies))
    print("Story bindings:", len(story_bound))
    print("Mission-reactive beacons:", len(beacons))
    print("Adaptive score slots:", len(MUSIC_TRACKS))
    print("Native MAX sculpt layout:", GRID, "x", GRID, "/", SCULPT_BYTES, "bytes")
    print("Terrain samples (units):", {"fort": round(fortress), "basin": round(basin), "west": round(west_ridge), "east": round(east_ridge), "fracture": round(fracture), "rim": round(south_rim)})
    print("Final map entities:", entity_count)
    print("Binary .ele round-trip: OK")


if __name__ == "__main__":
    main()
