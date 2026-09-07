# Aegis Reach: First Light

**First Light is Mission 01.** Relayfall remains the older prototype/reference.
The native GameGuru MAX project is in `Aegis Reach`.

Close an existing MAX run, then double-click **PLAY FIRST LIGHT.cmd** in the main
checkout. The launcher registers this checkout and opens the native project.
Use the FIRST LIGHT mission node in MAX. No standalone export is included.

[Mission and playtest guide](Aegis%20Reach/Design/First%20Light/PLAYTEST.md)

First Light follows Seven across a receded brine sea, through an occupied civilian
survey station, and into an AEGIS excavation. Restore Northstar, recover Mira Sen's
manifest, cancel the strike on Shelter 12, and return to Gate 07 for extraction.

The level uses editable MAX terrain, local licensed MAX assets, original project
geometry, native character_attack behavior, and the three supplied Suno masters.
Licensed packs are local dependencies; authoring tools do not copy their payloads
into this repository. Install the required packs in MAX before building/testing.

For authoring, run `python tools/build_first_light.py`; the route/terrain and three
building shells live in `tools/firstlight_world.py`. `python tools/test_firstlight.py`
automatically locates a Python 3.12 runtime capable of using the vendored Lua 5.1
module. Set `AEGIS_PYTHON` to that interpreter if automatic discovery cannot find it.

Structural tests cannot qualify appearance, audio mixing, or combat. Native QA is
opt-in via `python tools/firstlight_playtest.py qa`: it moves between stations,
observes real enemy animations/movement, and clears enemies to test progression.
Normal play never enables that mode. Native findings and remaining human checks
are recorded in the mission guide.
