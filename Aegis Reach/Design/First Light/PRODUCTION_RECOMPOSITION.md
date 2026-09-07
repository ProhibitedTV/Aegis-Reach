# FIRST LIGHT // Production Recomposition

This pass exists because First Light's gameplay/runtime systems matured faster than its environment composition. Native playtests showed the mission could boot, run encounters, drive objectives and play the score while the authored spaces still read as blockout geometry, overlapping prop layers or disconnected labels.

## What the project already has

First Light already has a usable systems spine:

- native GameGuru MAX terrain and navmesh rebuild workflow;
- four-stage mission progression: Northstar power -> Operations manifest -> AEGIS core -> extraction;
- local encounter activation and delayed reserves;
- shield/armour logic and objective interaction gating;
- semantic score states using the supplied Suno masters;
- non-destructive QA, runtime logging, load-safety checks and preflight;
- a substantial installed local MAX asset library covering construction, modular sci-fi/cyberpunk, military, industrial and medical/office dressing.

The production problem is therefore not lack of content. It is ownership, composition and restraint.

## Single-owner environment rule

Every visible layer now has one job:

1. **Native terrain owns grounded space.** Roads, shelves, pads, bowls, slopes and walking surfaces come from the MAX terrain sculpt. No generated floor planes are allowed over terrain.
2. **Installed modular kits own ordinary human architecture.** Walls, entries, windows, roof pieces, overpasses, steps and technical trims should come from coherent local asset families.
3. **Industrial/construction/military props explain function.** These assets are used in small clusters: power, survey, storage, occupation, maintenance and excavation.
4. **Bespoke meshes require a reason.** They are limited to unique silhouettes or forms the installed kits cannot express cleanly: the Camp 12 survey mast, Northstar stack silhouette, AEGIS arrival frame, sparse route beacon, Choir object and fracture bridge.
5. **Story signs confirm place; they do not create place.** A location must read before its HUD or sign text is noticed.

The old pattern of building a complete primitive shell in `firstlight_world.py` and then adding a second independent dressing pass in `build_first_light.py` is prohibited.

## Space recipes

### Survey Camp 12

**Read:** compact Meridian field laboratory on a protected old-seabed work pad.

- one small modular field-lab frontage backed toward the terrain bank;
- one survey mast;
- one survey instrument cluster;
- one generator/cable cluster;
- one compact logistics edge;
- one open court and unobstructed road exit toward Gate 07;
- warm practical light with a limited cyan technical pool.

No camping aesthetic. No tent/cot scatter. No snow/Arctic geology. No giant poles in the approach sightline.

### Gate 07

**Read:** the civilian service road entering a militarized threshold.

- one coherent overpass/entry modular family;
- asymmetric Warden roadblocks and logistics;
- cold cyan light;
- the road remains visually continuous through the opening.

### Northstar

**Read:** industrial power yard visible by its twin stacks.

- bespoke stack pair only as skyline identity;
- modular service span and supports;
- generators, storage tanks, stairs, control boxes and maintenance clutter;
- amber industrial lighting;
- enough open ground to preserve combat lanes.

### Operations

**Read:** a lower, human-scale Meridian workplace requisitioned by the Wardens.

- one wall/entry/window modular family;
- restrained roof/overhang language;
- desks, terminals, lockers and storage in functional groups;
- one emergency cot as evacuation evidence, not a barracks layer;
- neutral/cool practical lighting.

### AEGIS Excavation

**Read:** clean defense infrastructure becoming larger and stranger near the fracture.

- one sparse arrival-frame silhouette;
- coherent modular entry/steps/technical trim;
- construction and control equipment around the work edge;
- cyan light and a clear sightline toward the nonhuman excavation reveal.

### Choir / fracture

The Choir remains deliberately outside the human modular vocabulary. Its bespoke geometry is allowed because visual incompatibility is the point.

## Asset policy

Licensed MAX/DLC assets are referenced from the local installation only. Their payloads are never copied into Git.

Prefer a small coherent family over a large inventory. If a modular asset renders at the wrong scale, origin or material quality in native MAX, remove or rescale it; do not hide the problem by adding more props.

## Regression gates

`tools/test_firstlight_composition.py` protects against structural mistakes that native screenshots already exposed:

- return of the giant legacy bespoke room shells;
- return of recurring custom Floodlight/Revetment geometry;
- return of Camp 12's second tent/cot/desk dressing layer;
- runaway Camp 12 prop count;
- excessive route markers;
- expansion of bespoke architecture without an explicit reason.

This test is wired into `firstlight_preflight.py` before native MAX launch.

## Native review gate

Structural tests cannot prove that a scene looks good. Native GameGuru MAX remains authoritative.

After this pass, inspect these views in order:

1. insertion descent toward Camp 12;
2. 15–20 m outside Camp 12;
3. camp center toward the field lab;
4. camp exit toward Gate 07;
5. Gate 07 threshold;
6. Northstar arrival and flank lane;
7. Operations entrance/interior circulation;
8. AEGIS arrival and Choir reveal.

For each view ask:

- Is the route understandable without trusting the HUD arrow?
- Is there one dominant visual anchor?
- Do the assets look intentionally related?
- Is any asset floating, buried, oversized, intersecting or visually broken?
- Is there any z-fighting or unstable surface?
- Does the space explain its function?
- Can the next location be anticipated from the current one?

Delete and reposition before adding new asset categories.

## Next development order

1. Validate this recomposed environment in native MAX and correct scale/origin/material failures.
2. Tune cover and encounter positions only after the new architecture is visually stable.
3. Improve world-story details and faction identity inside proven compositions.
4. Replace any remaining placeholder bespoke forms only when a better tested modular or original solution exists.
5. Polish lighting, audio transitions and final environmental storytelling after the spatial language holds up without labels.
