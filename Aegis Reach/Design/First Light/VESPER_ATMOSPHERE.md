# FIRST LIGHT // Vesper Atmosphere Pass

Native playtest evidence showed that the recomposed layout is substantially more readable, but Vesper still reads too bright and terrestrial. The old sea shelf is beige/white under a clipped horizon and the landscape has almost no indigenous visual language outside the Choir itself.

## Target

Vesper should read as a cold, dark tidally stressed moon whose old hypersaline seabed has been exposed for a very long time.

The atmosphere pass therefore uses four layers:

1. **Darker global grade.** Lower exposure and sun intensity keep the terrain in dark rust/basalt values and stop the horizon from dominating every frame.
2. **Local human warmth.** Camp 12, maintenance areas and industrial work zones continue to use warm practical lighting so occupied places feel safe by contrast.
3. **Cold technical light.** AEGIS and Meridian technical areas retain cyan/blue accents.
4. **Brineglass geology.** Sparse crystalline mineral blooms create a native Vesper signature and point toward the deeper mystery.

## Brineglass

Brineglass is not a fantasy crystal resource and should not become collectible clutter. It is visual geology: mineral growth left by the old saline environment and exposed by erosion, tidal stress and subsurface disturbance.

The crystals use a dedicated original material rather than the general Aegis atlas. `build_first_light.py` procedurally generates the textures at 1024x1024 during the map build, so the result is deterministic and no binary art payload needs to be stored in Git.

### Energy material language

The intended visual reference is **contained alien energy inside mineral structure**, not ordinary quartz. The material combines:

- deep indigo glass/body color;
- electric blue and cyan internal bands;
- violet interference fields;
- white-hot filament veins and hairline fractures;
- low roughness and high reflectance;
- real native point-light spill onto the surrounding terrain.

This gives the crystal faces an energy-blade-like blue/purple/white character while the actual world glow still comes from MAX lighting rather than a painted halo.

Two related textures create narrative progression:

- `vesper_brineglass_energy.png` — blue/cyan dominant with violet understructure and white energy veins; used through the earlier route.
- `vesper_brineglass_resonant.png` — violet/purple dominant with harder white cores and cyan edge interference; used near AEGIS and the Choir fracture.

The player should initially notice only isolated blue-white blooms on ridges and channel walls. The blooms become larger, more violet, and visually more energetic as the route approaches AEGIS and the Choir fracture. This creates a visual gradient before the story explicitly explains anything.

Rules:

- no crystal forests;
- no crystals inside the Camp 12 core composition;
- no collision or traversal obstruction;
- no loot language;
- use real point-light spill so the crystals affect nearby ground;
- keep early blooms small enough to be discovered rather than announced;
- increase scale and resonant material presence only near the fracture;
- human work lights remain visually distinct from the brineglass color family.

## Current grade

The pass changes First Light's generated visual settings from the washed-out playtest grade to:

- Exposure: `0.93`
- Sun intensity: `0.95`
- Bloom: `0.15`
- Fog nearest: `8200`
- Fog distance: `28000`

These are a first native-playtest target, not sacred values. MAX screenshots remain authoritative. If the terrain becomes unreadably dark, raise exposure incrementally before undoing the overall night-side visual direction.

## Review shots

After rebuilding, inspect:

1. insertion ridge looking toward Camp 12;
2. Camp 12 from outside the protected court;
3. dry tide channel with the first visible blue-white brineglass bloom;
4. Gate 07 silhouette against the horizon;
5. Northstar exterior under amber practical light;
6. Operations-to-AEGIS transition where crystal scale begins increasing;
7. AEGIS/Choir approach with violet resonant brineglass spill.

The intended read is: **human lights are temporary; Vesper's geology is ancient; the Choir is making that ancient geology behave differently.**
