# First Light: Mission 01 playtest

This pass starts from remote main **a68d5ea**. Relayfall's map and scripts remain
unchanged. First Light is `Files/mapbank/Aegis Reach - First Light.fpm`.

## Play from main

Close MAX before launching. Double-click `PLAY FIRST LIGHT.cmd` in your main
checkout after pulling the merged change. The launcher registers that checkout,
preserving any conflicting old Documents storyboard in a local backup directory.
The storyboard contains no machine-specific project path.

WASD move, mouse aim/fire, RMB aim down sights, R reload, Shift sprint. Hold E for
three seconds at terminals. E reads field records and uses repair crates.

## Intended route and history

1. **Meridian Shelf:** a high insertion shelf looks down onto a broad evaporite
   basin. Descend along the graded survey approach toward Camp 12.
2. **Survey Camp 12:** packed cargo, emergency cots and the evacuation roster tell
   the first story: forty-two workers left; Mira Sen did not. A patrol rifle and
   ammunition reward the detour through the camp.
3. **Dry Tide Channel:** cracked seabed, weathered native rock shoulders and a few
   remnants separate the first fighting positions. Low ground remembers the sea.
4. **Gate 07:** a roofed cut compresses the approach. Beyond it, barriers face both
   the outer road and the civilian compound. The Wardens were containing people.
5. **Northstar:** the taller turbine nave has a lower west maintenance aisle and
   an east service exit. Amber light marks the machinery and restart terminal.
6. **Operations:** an offset, low civilian workplace with archive annex, desks,
   storage, emergency beds, partitions and several doors. Recover the manifest:
   the colony's defenses have been retasked against Shelter 12.
7. **AEGIS Excavation:** pass the armored threshold into a high hall. Its roof
   ends at an open gallery above a deep native-terrain cut. A black buried arch
   rises beyond the railing; mineral lines cross its base below the old sea level.
   Cancel the firing order. Mira may still be alive below the station.
8. **West service route / Gate 07:** a separately graded return road brings the
   player back toward familiar ground. Hold the LZ for sixty seconds, defeat the
   nearby Wardens, then hold E to extract with Kestrel.

## Score

The original Suno WAV masters are retained. Salt Moon Drift accompanies the basin
and quiet human discoveries. Moon Outpost Drift accompanies occupied facilities
and the return. Orbital Catacomb accompanies the excavation and Choir discoveries.
First Light uses a separate spatial score controller with crossfades, a stable
selection delay and a minimum track residence time. Small combat boundaries do
not replace the exploration cue. Temporary synthesized radio remains provisional.

## Validation

Structural tests check Lua mission rules, model imports, encrypted map integrity,
required assets/scripts/audio, portable project binding and native material IDs.
Licensed references resolve against the installed MAX assets rather than requiring
DLC folders in Git. Native QA records actual floor heights, animation frames,
character movement and global-sound playback state in local diagnostics.

Native review results for this pass are recorded in `native-review.md`.
A completed diagnostic route does not prove combat balance or visual quality.

Human checks still required: opening vista and terrain texture appearance;
walking gradients and thresholds; character skinning/animation appearance;
cover and weapon pickup accessibility; audible score/radio mix; every combat
approach, reinforcement reveal, return route and extraction; floating/clipping
props; and readability of the excavation reveal. No screenshots are fabricated
from the layout data. The native screenshot/control tool was unavailable in this
session, so diagram previews are not presented as engine captures.

## Authoring and dependencies

`tools/firstlight_world.py` defines native terrain and architecture.
`tools/build_first_light.py` creates First Light only; it never rewrites Relayfall.
`tools/firstlight_storyboard.py` rebuilds the storyboard and layout previews.
`tools/firstlight_playtest.py` registers and launches this checkout.

Local asset dependencies include the Military Pack, Industrial Collection and
MAX Collection. Their payloads stay in the licensed installation. Original
project meshes/signs and the supplied Suno masters are repository assets.
