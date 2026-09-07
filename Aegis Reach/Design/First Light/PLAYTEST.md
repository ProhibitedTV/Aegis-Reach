# First Light — playable Mission 01

The new level is `Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm`.
The previous Relayfall prototype remains intact. This branch builds from remote
revision 70efa63 and preserves Sol's native terrain codec, MAX combat interpreter,
three supplied Suno masters, and established Vesper/Mira/Kestrel setting.

## Play

Double-click `PLAY FIRST LIGHT.cmd` in this working copy. Close an existing MAX
run first. The launcher registers this copy of Aegis Reach and starts MAX's normal
native project play mode. In the editor, the mission node is FIRST LIGHT.

WASD move, mouse aim/fire, RMB aim down sights, R reload, Shift sprint. Hold E for
three seconds at mission terminals; E reads records and uses field repair crates.

## The playable story

Forty-two survey workers escaped Relayfall. Mira Sen did not. Seven arrives on the
exposed seabed to restore a blackout, finds a camp packed for an evacuation that
never finished, and discovers that the Wardens are pointing the colony's own
defense network at the missing team's shelter.

1. **Meridian Shelf:** quiet arrival, a view toward Aurelia and the distant station.
2. **Survey Camp 12:** packed crates, abandoned cots, a missing name on the roster.
   The optional marksman rifle rewards investigation before the first fight.
3. **Dry Tide Channel:** basalt cover and offset ridges offer a direct crossing or
   a wider firing position. Three Wardens activate locally after the arrival beat.
4. **Gate 07:** barricades face into the compound. A checkpoint shotgun and ammo
   cache support a closer approach. The gate becomes the later extraction arena.
5. **Northstar:** a generator court with maintenance cover and an open side aisle.
   Restoring its terminal reconnects the civilian distress channel.
6. **Operations:** a roofed records building with two side approaches, desks,
   lockers and emergency beds. The recovered manifest reveals Mira's distress call.
7. **AEGIS Excavation:** heavy security surrounds the core and exposed black ribs.
   Cancelling its firing order saves Shelter 12 and accelerates shield recovery.
8. **Service Yard / Gate 07:** four pursuers pressure the return route. Reaching
   the LZ starts a 60-second holdout with three reinforcement pairs. Stay within
   the defended area, clear nearby enemies, and hold E to board Kestrel.

The ending resolves the strike while leaving a concrete next-mission question:
Mira is alive beneath the station, and something there answers her instruments.

## Scope and review

This is a playable first-level build, not a finished commercial release. Temporary
radio dialogue uses local Windows speech synthesis. Lighting, prop scale, encounter
balance and navigation need a human playthrough. The optional native QA mode
teleports between stations and removes active enemies to exercise loading,
physics and progression; it does not qualify combat feel.

Run `tools/test_firstlight.py` for Lua 5.1 progression checks, installed Assimp model
imports, required references and encrypted archive validation. Run
`tools/firstlight_playtest.py qa` for the opt-in native MAX smoke test. The runtime
log is in Documents/GameGuruApps/GameGuruMAX/Files/first-light-runtime.log.

## Authoring

`tools/build_first_light.py` owns this mission's layout, terrain and asset placement.
It creates the separate First Light FPM and never rewrites Relayfall.
`tools/firstlight_storyboard.py` binds this mission and refreshes the native menus.
`tools/make_firstlight_radio.ps1` regenerates the temporary radio performances.
The three Suno files remain original full-quality masters imported by
`tools/import_music.py`; they are not replaced by procedural music.

The original local checkout and its unsaved maps remain untouched. The external
MAX project registration now points to this isolated working copy so the actual
engine tests the version being developed here.
