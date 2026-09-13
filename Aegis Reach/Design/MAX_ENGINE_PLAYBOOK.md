# Aegis Reach — GameGuru MAX Engine Playbook

This file records engine knowledge that is actionable for the project. It is deliberately separate from the story bible: these are production constraints, native APIs, migration rules, and review gates.

## Source hierarchy

1. **Native GameGuru MAX behavior/source shipped by TheGameCreators** is the API truth.
2. **Blood Moon Interactive** is our primary behavior/design field guide:
   - https://www.bloodmooninteractive.com/
   - https://www.bloodmooninteractive.com/articles/loop3dsound.html
   - https://www.bloodmooninteractive.com/articles/lighting-in-game-design.html
   - https://www.bloodmooninteractive.com/articles/level-design-fundamentals.html
   - https://www.bloodmooninteractive.com/articles/performance-optimization.html
   - https://www.bloodmooninteractive.com/articles/juice.html
3. GameGuru forum / official update notes are useful for engine quirks and migration history, but anything performance- or bug-sensitive still requires a native playtest.
4. A source/static test never establishes native visual quality.

## Behavior patterns we will use

### Spatial sound

MAX's `effects\loop3dsound.lua` establishes the native pattern:
- `GetPlayerDistance(e)` determines audibility.
- `LoopSound(e,0)` owns the 3D emitter.
- `SetSoundVolume(...)` applies smooth distance falloff.
- sounds are stopped outside useful range instead of burning runtime work everywhere.
- activation state can gate the emitter.

FIRST LIGHT already follows this pattern for the M-17 rupture. Future machinery, brine pockets, warning beacons, and interior ambience should use one localized emitter per meaningful source, not a global wall of ambience.

### Dynamic light control

MAX's `effects\lightcontrol.lua` demonstrates the supported runtime light API:
- `GetEntityLightNumber(e)`
- `GetLightRange(...)` / `SetLightRange(...)`
- `GetLightRGB(...)` / `SetLightRGB(...)`
- optional emissive coupling through `SetEntityEmissiveStrength(...)`
- player-range sensing and throttled flicker/ramp logic.

FIRST LIGHT uses these APIs in `firstlight_practical_light.lua` for the two M-17 fire practicals. The purpose is responsive firelight, not a new lighting system.

**Budget rule:** tactical/backlight practicals remain local (currently <= 550 MAX units). Do not solve darkness by adding giant overlapping dynamic lights. Use composition, contrast, emissive surfaces, fog/sky grade and a small number of motivated lights.

### Particles and environmental feedback

Native MAX particle markers remain the emitter owner. Mission Lua only controls lifecycle and parameters:
- start/stop by distance and mission stage;
- configure once, then tick at a coarse cadence;
- burst particles are event-driven;
- ambient particles must not gain combat or navigation authority.

This keeps "juice" proportional: important events can flare, spark or smoke, while idle spaces remain readable and performant.

## Collision policy

Use the cheapest collision that matches player expectations.

| Mode | Project use |
|---|---|
| 0 box | simple blockers and authored proxy volumes |
| 1 polygon | only when the player truly needs detailed surface traversal |
| 2 sphere | spherical props where appropriate |
| 3 cylinder | barrel/pillar-like blockers |
| 8 external OBJ polygon mesh | candidate for deliberate custom collision after native audition |
| 9 convex hull | irregular simple solid props |
| 10 hull decomposition | complex solids when a box/hull is inadequate |
| 11 no physics | foliage, particles, cosmetic wreck pieces, most ambient life |
| 12 no physics / queryable | detection-only cases when IntersectAll behavior is desired |
| 22 pass-through animal pattern | evaluate only for native creatures that need terrain following |

The M-17 render shell is collisionmode 11 and uses four hidden box proxies. This is intentional: render art and gameplay collision are separate contracts. A mode-8 custom collision OBJ is a possible later replacement, but only after a controlled native test; do not destabilize a working wreck just because the engine supports another mode.

## MAX + Classic owned-asset policy

Jeremy owns GameGuru MAX and GameGuru Classic plus a large purchased/installed library. That means we should aggressively **use** compatible local media, but ownership is not a reason to redistribute licensed binaries through Git.

Production rules:
- Never bulk-copy the entire Classic entitybank into the repository.
- Never commit DLC/marketplace media just because it exists locally.
- Migrate **one pack at a time** into the MAX user entitybank and audition it.
- Static props are the first-choice Classic migration candidates.
- Characters, Character Creator assemblies, weapons, and heavily scripted/animated Classic entities are high-risk until proven in MAX.
- Re-author PBR maps/material response when a useful legacy prop looks visually dated.
- Once an asset is accepted, the map references the locally installed/user-media path.
- Build/preflight should fail clearly when a required local dependency is missing.

Run:

```bat
python tools\max_asset_library_audit.py --no-max-core
```

to scan the MAX user library plus detected Classic installations without copying anything. Add `--json <path>` only when you want a portable relative-path report. The auditor deliberately ranks low-risk static props first and quarantines characters, weapons and missing-model entries.

## FIRST LIGHT level-design rules

Blood Moon's level-design guidance maps well to the Halo-CE-inspired target:
- sightlines communicate the next meaningful space;
- landmarks own orientation (Camp 12, Northstar, Operations, AEGIS, Kestrel LZ);
- lighting/color establish hierarchy instead of waypoint spam;
- combat pockets have cover but preserve a traversal spine;
- exploration and revelation beats interrupt combat rhythm;
- environmental storytelling should answer "what happened here?" before exposition does.

The current opening gives one concrete task and one mystery. Do not dump Choir lore at the player before they have physically seen evidence.

## Performance rules

- Cull particle/audio logic by distance.
- Throttle environmental Lua; 10–15 Hz is plenty for fire flicker and ambient decisions.
- No physics on decorative foliage/fauna/debris unless interaction requires it.
- Prefer a few local dynamic lights over broad overlapping ranges.
- Treat shadows as a budgeted presentation feature.
- Large/complex collision must be intentional, never the default for clutter.
- Test native MAX often; source correctness does not prove frame time or appearance.

## Asset-audition workflow

1. Run `max_asset_library_audit.py`.
2. Pick one coherent pack/category, not hundreds of unrelated props.
3. Copy/import that pack into the MAX user library if needed.
4. Open representative assets in MAX and inspect scale, material response, origin, collision, animation/script behavior and shadow cost.
5. Promote only successful assets into world-generation references.
6. Rebuild FIRST LIGHT and run preflight.
7. Native walk-through before calling the asset production-safe.

## Near-term engine backlog

- Native-test the new M-17 fire-light response and hidden collision proxies.
- Use the asset auditor to identify a first Classic industrial/sci-fi prop pack for Camp 12 / Northstar dressing.
- Add more spatial audio only when we have identified the actual owned sound assets; never guess filenames.
- Evaluate mode-8 custom collision for future large wrecks/architecture after the M-17 proxy approach has been playtested.
- Continue using CineGuru for sparse authored shots, with fail-open mission progression.
