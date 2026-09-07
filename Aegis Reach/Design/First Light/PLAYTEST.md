# First Light: Mission 01 playtest

First Light is `Files/mapbank/Aegis Reach - First Light.fpm`. Relayfall remains the
older prototype/reference and is not rewritten by the First Light authoring tools.

## Normal play from main

Close MAX before launching. Pull `main`, then run:

```bat
call "PLAY FIRST LIGHT.cmd"
```

The launcher now performs three steps before MAX starts:

1. applies the narrow load-safety patch for any legacy stock `weapon.lua` pickups
2. runs the Lua 5.2 compatibility and First Light structural tests
3. validates the exact runtime map and all three authored score masters

It then registers the current checkout as MAX's external Aegis Reach project and
records the git commit, runtime map hash and score-file metadata in local launch
state. If preflight fails, MAX does not launch.

WASD move, mouse aim/fire, RMB aim down sights, R reload, Shift sprint. Hold E for
three seconds at terminals. E reads field records and uses repair crates.

## Instrumented native QA

Run:

```bat
call "PLAY FIRST LIGHT QA.cmd"
```

The QA route moves through the major authored spaces and records floor-height,
enemy-animation/movement and score-controller evidence. It is a diagnostic run,
not proof that combat balance or visual composition is good.

After either normal play or QA, run:

```bat
call "COLLECT FIRST LIGHT.cmd"
```

or:

```bat
python tools\firstlight_collect.py
```

A timestamped report is written under `Design/First Light/runtime-reports/` and
summarizes Lua errors, score initialization/transitions, enemy activations, native
QA actor samples and mission/QA completion evidence. These reports remain local.

## Intended route and history

1. **Meridian Shelf:** a high insertion shelf looks down onto a broad evaporite
   basin. Descend along the graded survey approach toward Camp 12.
2. **Survey Camp 12:** packed cargo, emergency cots and the evacuation roster tell
   the first story: forty-two workers left; Mira Sen did not. Ammunition and the
   field record reward the detour without relying on MAX's unstable loose-weapon
   pickup path.
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

The playtest is not considered audio-clean until all three cues are heard in their
intended spaces at useful levels and the native report contains score evidence.

## Current acceptance gates

### Gate 1: boot/runtime

- no Lua dialog during load or mission start
- First Light HUD appears and stage 1 begins
- no missing asset/script errors
- no stock `weapon.lua` pickup crash
- preflight passes before launch

### Gate 2: animation/AI/audio

- no visible T-pose on dormant or activating Wardens
- activation happens locally and deliberately
- enemies navigate in native MAX rather than remaining stationary
- death lifecycle completes through stock character behavior
- score is audible and transitions without spam/restarts

### Gate 3: visual composition

Capture and review these nine frames:

1. insertion vista
2. Survey Camp 12
3. first tide-channel fight
4. Gate 07
5. Northstar interior
6. Operations
7. AEGIS excavation / Choir reveal
8. west return route
9. extraction holdout

Inspect terrain/structure interfaces, lighting hierarchy, enemy readability,
repeated prefab patterns, floating/clipping geometry and whether the civilian,
military and buried-Choir history reads visually.

### Gate 4: combat

Only tune damage after visibility, animation and navigation are proven. Review
cover spacing, flank routes, reveal directions, reinforcement timing, encounter
duration and recovery space between fights.

The detailed order of work is in `NEXT_PASS.md`.

## Validation and dependencies

Structural tests check Lua mission rules, model imports, encrypted map integrity,
required assets/scripts/audio, portable project binding and native material IDs.
Licensed references resolve against installed MAX assets rather than requiring DLC
folders in Git.

`tools/firstlight_world.py` defines native terrain and architecture.
`tools/build_first_light.py` creates First Light only and no longer authors loose
stock weapon pickups. `tools/firstlight_storyboard.py` rebuilds the storyboard and
layout previews. `tools/firstlight_playtest.py` owns launch/preflight registration.

Local asset dependencies include the Military Pack, Industrial Collection and MAX
Collection. Their payloads stay in the licensed installation. Original project
meshes/signs and the supplied Suno masters are repository assets.
