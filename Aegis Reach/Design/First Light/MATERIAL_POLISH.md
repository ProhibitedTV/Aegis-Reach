# First Light material polish

This pass raises material fidelity without changing mission authority, collision, cinematic timing, or the authored geometry contracts.

The source atlases in `tools/texture_sources/first_light/` are original project art inputs. `tools/firstlight_material_polish.py` converts them into GameGuru MAX APBR assets while preserving the existing eight-tile UV layout used by the Kestrel, Meridian field kit, and Vesper biosphere. Surface maps use the project convention R=occlusion, G=roughness, B=metalness, A=reflectance.

## Asset families

- **Broadwing Kestrel:** graphite/titanium hull breakup, maintenance panels, vents, hazard trim, engine heat detail, and a dedicated interior/ramp tile. Existing flight/conversion/flare/landed meshes and FPE names are unchanged.
- **Meridian / Northstar:** the existing field-kit texture names now receive higher-frequency industrial paneling, salt-weathered paint, vents, conduits, utility detail, and status-light material variation. Existing environment UVs and FPE bindings remain unchanged.
- **M-17 wreck:** visible wreck, detached engine, and torn panel now bind a dedicated scorched aircraft material set while hidden collision proxies remain on the ordinary field-kit material.
- **Vesper biosphere:** the existing eight-tile biosphere contract now uses fibrous, translucent-looking saline flora detail with mineral color breakup and restrained bioluminescent tiles.
- **Brineglass:** calm and resonant mineral materials gain higher-frequency crystalline detail plus normal maps. Existing emissive identity is retained, with teal calm energy and violet-blue resonant energy.

The material pass runs after `build_first_light_aaa.py`, because several upstream builders deliberately emit deterministic fallback textures. Source images participate in the First Light build signature, and the pass keeps its own source/output manifest at `Aegis Reach/Design/First Light/material-polish.json`.

Native GameGuru MAX review remains required for final texel-density, roughness, normal-strength, emissive-balance, and mip/readability tuning.
