"""Headless structural test for the Vesper open-space/story pass.

Does not replace the checked-in .fpm. It patches the decoded map payload in memory and
verifies the breach, generated world entities, and story-script bindings before MAX
gets involved.
"""
from __future__ import annotations

import zipfile

from max_archive import PASSWORD
from world_story_pass import MAP, PLACEMENTS, build_assets, patch_world
from world_story_logic_pass import patch as patch_story_logic, STORY_NAMES
from native_format import read_ele
from environment_pass import get_suffix


def main():
    build_assets()
    with zipfile.ZipFile(MAP) as source:
        source.setpassword(PASSWORD)
        map_ele = source.read("map.ele")
        map_ent = source.read("map.ent")

    patched_ele, patched_ent, added, removed_gate, entity_count, bank_count = patch_world(map_ele, map_ent)
    assert removed_gate == 4, f"expected 4 south-gate wall segments removed, got {removed_gate}"
    assert len(added) == len(PLACEMENTS), (len(added), len(PLACEMENTS))

    version, entities = read_ele(patched_ele)
    names = {str(get_suffix(e, "eleprof.name_s", "")) for e in entities}
    for placement in PLACEMENTS:
        assert placement[0] in names, placement[0]

    logic_ele, bound = patch_story_logic(patched_ele)
    assert set(bound) == STORY_NAMES, (bound, STORY_NAMES)
    version2, entities2 = read_ele(logic_ele)
    assert version2 == version
    assert len(entities2) == len(entities)

    print("AEGIS REACH // VESPER WORLD TEST PASS")
    print("Map entities:", entity_count)
    print("Bank entries:", bank_count)
    print("World placements:", len(added))
    print("South breach segments removed:", removed_gate)
    print("Story triggers bound:", len(bound))
    print("Binary .ele round-trip: OK")


if __name__ == "__main__":
    main()
