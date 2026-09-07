# AEGIS REACH // GAMEGURU MAX NATIVE TERRAIN HANDOFF

## Correction

The earlier Aegis Reach terrain experiments treated broad collision meshes and a generic 16-bit image as if they were equivalent to authoring GameGuru MAX terrain. They are not.

GameGuru MAX has two complementary native terrain workflows:

1. **Terrain Generator** — procedural generation / biome starting points / RAW heightmap import.
2. **Terrain Editing inside the Level Editor** — native sculpting, painting, trees and grass.

Aegis Reach production now writes the same editable **4096 x 4096 sculpt field** that MAX's Terrain Editing system uses. Broad landforms are terrain. Meshes are architecture, overhangs, bridges, caves, props and deliberate hard-surface formations.

## Production workflow

Pull `main`, then:

```bat
python tools\test_native_integration.py
python tools\max_playtest.py deploy --production
```

`deploy --production` now writes Vesper into Relayfall's native terrain sculpt payload before deploying the map to MAX. It also removes the old slab/ridge entities that were temporarily substituting for landscape.

The terrain remains editable in MAX after deployment.

## What MAX is actually storing

The current Wicked/MAX terrain implementation uses a fixed 4096 x 4096 editable sculpt field.

The FPM contains:

- `ggterrain.dat` — terrain settings JSON inside GameGuru's memblock wrapper;
- `83886080.dat` — native sculpt data when sculpting exists;
- a `.ptd` terrain-paint payload;
- optional `heightmapdata.raw` when a main imported heightmap exists;
- `tt*` terrain cache/node folders used for generated geometry/virtual textures.

The native sculpt block is exactly:

```text
16,777,216 bytes  uint8 edit type
67,108,864 bytes  float32 edit height
----------------
83,886,080 bytes total
```

Aegis Reach writes **edit type 1 (Replace)** for its owned terrain region and leaves the rest of the terrain edit field untouched.

## MAX world scale

GameGuru MAX source defines:

```text
1 world unit = 1 inch
1 world unit = 0.0254 meters
```

This matters. A 500-unit ridge is about 12.7 m tall, not 500 m.

Our previous terrain-source script mixed conceptual meter coordinates with MAX world coordinates. That has been corrected.

## Vesper's native landform composition

Relayfall now uses a low-frequency macro shape rather than a flat plane:

1. **Relayfall graded footprint** — terrain stays just beneath modeled fortress floors.
2. **South breach tongue** — ground rises to meet the fortress and rolls naturally into the exterior.
3. **Evaporite basin** — lower exposed brine-sea floor.
4. **West basalt shoulder** — broad high flank.
5. **East basalt shoulder** — opposing high ground and long-range position.
6. **Dried brine channel** — genuine lowered terrain, not a texture strip.
7. **Outer shelf** — lower quiet release space beyond the first fight.
8. **East tidal fracture** — real depression leading toward future Undertide content.
9. **North escarpment** — geology frames Relayfall instead of an infinite tabletop.
10. **Far south rim** — the playable landscape resolves into a geological horizon.

Terrain noise is intentionally subordinate. The player should read the big shapes from combat distance.

## Editing it manually in MAX

After `deploy --production`:

1. Restart MAX and open Relayfall.
2. Open the terrain tools in the Level Editor.
3. Walk/view the level from gameplay height before sculpting.
4. Use **Level** or **Write** around architectural interfaces.
5. Use **Ramp** for deliberate traversable transitions.
6. Use **Raise/Lower** for macro silhouette changes.
7. Use **Blend** to remove accidental sharp brush artifacts while preserving authored ridges.
8. Paint materials after the geometry reads correctly.
9. Rebuild/test AI navigation after meaningful terrain changes.
10. Save the level.

Bring the editor-authored FPM back to the repo with:

```bat
python tools\sync_max_map.py pull --dry-run
python tools\sync_max_map.py pull
```

That editor-saved FPM then becomes the new terrain authority for the next iteration.

## Optional Terrain Generator import

If we want to regenerate Vesper from the Terrain Generator rather than the direct native sculpt pass:

```bat
python tools\vesper_terrain_source.py --size 2048
```

The primary output is now correctly:

```text
Aegis Reach\Design\terrain-source\vesper_relayfall_height_16le.raw
```

It is unsigned 16-bit **Little Endian RAW**. The preview PNG is only a visual aid.

In MAX Terrain Generator use the RAW heightmap importer, set the exact dimensions from the generated manifest, choose **Little Endian**, then adjust Heightmap Scale / Max Height and generate the terrain into the Level Editor.

For Aegis Reach's normal build loop, direct native sculpting is preferred because it preserves the current level instead of asking the editor to regenerate the world.

## Indoor / outdoor design rule

MAX terrain is a height field. It is excellent for:

- hills and escarpments;
- ravines and basins;
- shelves and terraces;
- roads/approaches;
- exterior combat elevation;
- geological transitions.

It is not the right representation for true overhangs or volumetric caves.

Use modular geometry for:

- fortress interiors;
- service tunnels;
- Undertide caves/catacombs;
- bridges/causeways;
- cliff overhangs;
- Choir architecture;
- retaining walls where civilization cuts into geology.

The mission should repeatedly compress and release:

**open shelf -> breach -> service interior -> relay courtyard -> maintenance tunnel -> major exterior vista -> buried structure -> exterior return**

That gives us the CE-like indoor/outdoor rhythm without fighting MAX's terrain representation.

## AI/navmesh implication

MAX uses Recast/Detour navigation. Terrain shape therefore affects AI for real. Broad slopes and clear shoulders are preferable to noisy micro-terrain. Keep encounter spaces connected by readable walkable surfaces, then use MAX navmesh limits/encounter scripting to keep AI local rather than expecting one giant path corridor to solve the entire moon.

## Terrain/material sequencing

Do this in order:

1. macro landform silhouette;
2. player traversal;
3. AI traversal;
4. architecture-to-ground interfaces;
5. terrain materials;
6. geological decals/weathering;
7. vegetation/particles where appropriate;
8. small story clutter.

Do **not** decorate a terrain layout that has not yet proven fun to move through.

## The story rule remains

Vesper's low ground remembers the vanished sea. High basalt stays dark. Civilian Meridian infrastructure responds to the geology. AEGIS construction overlays it. Warden occupation is temporary and tactical.

If a terrain feature does not improve navigation, combat, silhouette, history, or discovery, it probably should not exist.
