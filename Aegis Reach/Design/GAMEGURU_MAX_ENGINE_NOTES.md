# AEGIS REACH // GAMEGURU MAX ENGINE NOTES

This document is the working technical map for building Aegis Reach *with* GameGuru MAX instead of accidentally building a parallel engine around it.

Primary technical reference: the current public `Dark-Basic-Software-Limited/GameGuruMAX` source tree plus the official MAX Terrain Generator / Terrain Editing tutorials.

## 1. Terrain is a native Wicked/MAX system

Current MAX terrain lives under:

```text
GameGuru Core/Guru-WickedMAX/GGTerrain/
```

The terrain system is not a legacy 512x512 GameGuru Classic height field. The current editable sculpt field is:

```cpp
#define GGTERRAIN_HEIGHTMAP_EDIT_SIZE 4096
```

MAX exposes native sculpt modes:

```text
RAISE
LOWER
LEVEL
BLEND
RAMP
PICK
WRITE
RANDOM
RESTORE
```

It also has separate terrain edit modes for sculpt, paint, trees and grass.

### Aegis rule

Use native terrain for macro geology and traversal. Do not use large box meshes as replacement landscape.

## 2. MAX coordinate scale

The source explicitly defines:

```cpp
GGTerrain_UnitsToMeters(units) = units * 0.0254
```

Therefore:

```text
1 MAX world unit = 1 inch
100 units = 2.54 m
500 units = 12.7 m
1000 units = 25.4 m
```

All future encounter, terrain and camera designs should use this conversion consciously.

## 3. What an FPM actually saves for terrain

`M-MapFile.cpp` writes current terrain state into the FPM archive.

Important members include:

```text
ggterrain.dat
<sculpt-size>.dat
<paint-size>.ptd
heightmapdata.raw       (when a main imported heightmap exists)
tt*/                    terrain geometry / virtual-texture cache nodes
grass_coloronly.dds
```

### Sculpt payload

`GGTerrain_GetSculptDataSize()` returns:

```text
4096 * 4096 * (sizeof(float) + sizeof(uint8_t))
= 83,886,080 bytes
```

Serialization order:

```text
first  4096*4096 uint8 values  -> pHeightMapEditType
then   4096*4096 float values  -> pHeightMapEdit
```

MAX restores the same block with `GGTerrain_SetSculptData()` and invalidates/rebuilds terrain.

Aegis Reach now writes this native payload in `tools/native_terrain_pass.py`.

## 4. Native sculpt coordinates

MAX maps world X/Z into the 4096 edit grid using its editable half-extent:

```text
normalized = world / editable_size
terrain_grid = (normalized * 0.5 + 0.5) * 4096
```

The default `editable_size` is 50000 units, meaning roughly a 100000-unit / 2540 m wide editable square before project-specific changes.

The player-control code can query the runtime editable boundary through:

```lua
GetTerrainEditableArea(dimension)
```

## 5. Replace-mode height edits

MAX's sculpt data supports edit modes. Type `1` is replace mode.

In replace mode, the stored float is a normalized height. MAX later scales positive values by the terrain `height` parameter, negative values by `minHeight`, and adds `offset_y`.

This is why Aegis Reach can author a deterministic landform directly into the FPM and still leave it editable in MAX afterward.

## 6. Main heightmap import is separate from sculpting

MAX can also own a base imported heightmap (`heightmapdata.raw`). The Terrain Generator supports heightmap import and the engine exposes:

```cpp
GGTerrain_LoadHeightMap(...)
GGTerrain_SetHeightMap(...)
```

The heightmap is unsigned 16-bit data normalized against 65535. MAX supports endian selection for RAW import; Aegis Reach's optional generated source uses **16-bit Little Endian RAW**.

The production project does not need to regenerate the whole level from a heightmap on every pass. We use native sculpt edits for iterative level work and keep RAW generation as an optional Terrain Generator starting point.

## 7. Terrain paint is also native data

MAX's editable material map is another fixed 4096 x 4096 `uint8` field.

```text
GGTerrain_GetPaintDataSize() = 4096 * 4096 bytes
```

A zero paint value means MAX can use automatic height/slope material selection; explicit painted values select material indices.

### Aegis rule

Do not programmatically paint arbitrary material IDs until the actual terrain material palette for the project has been inventoried. Geometry first, material mapping second.

## 8. Height fields cannot make true caves

The native terrain is a height field. It cannot represent a ceiling over another terrain surface at the same X/Z.

Therefore:

```text
native terrain -> basins, slopes, ridges, valleys, escarpments, shelves
geometry       -> caves, tunnels, overhangs, buildings, bridges, alien interiors
```

This is ideal for Aegis Reach's desired rhythm: terrain provides the exterior alien world, while modular geometry creates enclosed military/Choir spaces embedded into it.

## 9. Architecture should meet terrain deliberately

At outdoor/indoor interfaces:

- flatten/level only the footprint that logically needed grading;
- use ramps for roads/service approaches;
- use retaining walls where construction cuts into a slope;
- let cliffs or terrain hide the back/sides of embedded interiors;
- avoid floating buildings and giant artificial foundation slabs;
- avoid accidental terrain poking through floors.

Fortress geometry should look constructed *into* Vesper, not dropped onto a tabletop.

## 10. Navigation is Recast/Detour

MAX includes its Recast/Detour navigation implementation.

Implications:

- terrain slope and discontinuity affect AI navigation;
- broad traversable terrain is safer than noisy micro-sculpting;
- MAX supports `NAVMESH LIMIT` areas for controlling navigation scope;
- long-distance crowd/path behavior should not be treated as one unlimited path problem;
- encounter scripting should activate local tactical spaces instead of waking half the map.

Aegis Reach's existing local enemy activation architecture aligns well with this.

## 11. Lua is not a toy layer

MAX's `scriptbank/global.lua` exposes a large engine-facing API including:

- entity activation/state;
- sound playback and volume;
- terrain height queries;
- entity/object manipulation;
- lighting/emissive controls;
- prompts/HUD text;
- player state;
- logic connections;
- raycasts and surface queries;
- AI control helpers.

### Aegis architecture rule

**Lua describes systemic truth; Visual Logic stages authored consequences.**

Example:

```text
Lua: NORTHSTAR relay becomes captured
  -> Visual Logic: blast door unlocks
  -> lights switch cyan
  -> sparks/steam event fires
  -> CineGuru camera insert can trigger
  -> music state changes
  -> next enemy group becomes eligible
```

## 12. Visual Logic is useful for authored set pieces

Do not hard-code every cinematic/environment reaction into one giant director Lua file.

Use Lua for:

- mission state;
- combat state;
- player systems;
- systemic AI rules;
- adaptive score state;
- world state.

Use Visual Logic for inspectable local choreography:

- door opens;
- machine activates;
- light group changes;
- CineGuru sequence begins;
- particle effect starts;
- alarm/stinger plays;
- hologram appears;
- one-shot environmental event occurs.

## 13. CineGuru is a presentation layer, not the mission state machine

CineGuru is best used for:

- short arrival/reveal shots;
- actor blocking;
- camera pans/tracking;
- subtitles;
- fades;
- image/audio triggers;
- light choreography;
- brief in-engine narrative beats.

Aegis Reach should keep cutscenes short and return control quickly. The environment and player action carry most of the story.

## 14. Terrain Generator vs Level Editor Terrain Editing

These are different stages.

### Terrain Generator

Use for:

- initial procedural world shape;
- biome-style starting points;
- RAW heightmap import;
- editable area / broad height-range setup;
- generating a base world before entering the Level Editor.

### Level Editor Terrain Editing

Use for:

- Raise/Lower;
- Level/Write;
- Blend;
- Ramp;
- material painting;
- vegetation;
- gameplay-specific local fixes.

Aegis Reach production currently modifies the latter's native sculpt state directly, which is the correct iterative path for an already-authored map.

## 15. Environment production doctrine

Build Relayfall in this order:

1. native terrain silhouette;
2. traversal and sightlines;
3. AI navigation;
4. fortress/terrain interfaces;
5. combat encounters;
6. terrain material palette;
7. large architectural landmarks;
8. environmental FX and sound;
9. story props and decals;
10. small clutter.

The project got this order wrong initially by jumping from flat ground to story objects. The current native-terrain rework corrects that foundation.

## 16. What we should exploit next

After the first native-terrain playtest:

- inventory the actual terrain material IDs/palette in Relayfall;
- paint pale evaporite floors and dark basalt high ground natively;
- use terrain normals/material queries for context-sensitive particles/footsteps if useful;
- create embedded Offworld/Cyber interiors in hillsides instead of freestanding boxes;
- define NAVMESH LIMIT regions around major encounter spaces;
- use terrain height queries when spawning/placing exterior scripted events;
- connect Relay/Story outputs to Visual Logic and CineGuru;
- add weather/salt-drift/vent particles that respect terrain rather than floating in world space.

## Source paths worth revisiting

```text
GameGuru Core/Guru-WickedMAX/GGTerrain/GGTerrain.h
GameGuru Core/Guru-WickedMAX/GGTerrain/GGTerrain.cpp
GameGuru Core/Guru-WickedMAX/GGTerrain/GGTerrainFile.cpp
GameGuru Core/GameGuru/Source/M-MapFile.cpp
GameGuru Core/GameGuru/Source/M-Game.cpp
Scripts/scriptbank/global.lua
```

When a MAX-specific behavior is unclear, inspect the engine/source convention first, then build around it.
