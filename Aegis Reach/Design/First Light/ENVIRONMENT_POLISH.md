# First Light environment rebuild - native review pending

Baseline: remote main `0fbb6960c94168367c50c34692d6a2fb084d2e8b`.
This branch changes the actual First Light map. There is no showroom or separate
prototype map. It is not qualified for merge until the new native views pass.

## Why the previous camp was rejected

The supplied September 8 native screenshot, compared with the concept reference,
shows the wrong scale and material hierarchy: a small concrete hut in a uniformly
rocky basin, exposed equipment, unrelated pools of light, and conspicuous blue
crystals in the foreground. Moving one barrier or tuning exposure did not address
the main architecture or the missing service-road surface.

## Current production candidate

- One original Meridian field lab replaces the six street-wall/roof pieces. Its
  shell measures 420 x 260 MAX inches (10.67 x 6.60 metres), with a chamfered crown,
  structural ribs, transport rails, roof service equipment and recessed entrance.
  The shell contains 884 triangles; its opening is approximately 100 x 101 inches.
  There is no generated floor or entrance step over the native terrain.
- The lab uses an original ivory/graphite/teal material atlas with seam wear,
  fasteners, Meridian identifiers, restrained cyan trim and amber practical strips.
  The coordinated 4096 x 512 albedo, normal, surface and emission atlases are
  deterministic outputs of `meridian_fieldkit.py`. Paint remains matte and
  dielectric; alloy ribs and exposed fasteners use a restrained metallic response.
  Surface seams and fasteners now sit inside the UV islands instead of outside
  the sampled crop. Printed Meridian labels stay flat. Lamps retain smooth normals.
  Upper end-panel UVs have nonzero area for stable normal-map tangent frames.
  No third-party model or DLC texture is embedded in this kit.
- The lab upper end panels now have separate inward and outward faces. The prior
  outward-only fans could disappear from an interior view under backface culling.
  New sightline checks reproduced that defect and pass after the repair. The
  ceiling strip now has a housing that meets the ceiling, without adding a light.
- The original mast is now a narrow braced truss with two lamp housings and an
  antenna. It sits at the back corner of the court. Its light marker coincides
  with the fixture height; the other two camp lights serve the lab and doorway.
- Existing installed desk/chair, generator, cable reel, cargo container, supply
  crate, two survey instruments and one barrier remain. They form work, power and
  logistics groups around the larger lab. Camp 12 now contains 12 environment
  objects including its existing route beacon, down from 17 in the prior draft.
- The court pad extends west to support the complete shell. Terrain height at
  the lab corners and mast base is 500 inches. Existing low terrain shoulders
  protect the site, and the insertion shoulder cut retains its facade sightline.
- The insertion-to-Gate service route and Camp 12 court are painted in native
  terrain data: installed mat23 mineral fines, with narrow mat16 wheel bands.
  There are 4,949 painted cells. Rocky slope materials remain outside the road.
  No snow material, coplanar floor, road mesh or decal overlay is used.
- The first brineglass exposure moves off the near foreground to the descending
  route. The first five mineral light sources have less spill. Ten formations,
  including three later violet formations and their two existing procedural
  texture artworks, remain. No crystal forest or additional light array is added.
- The roster remains on the lab wall and retains the missing-person clue.

## Gameplay and build verification

Current build: 189 entities, 67 asset types, 26 lights. Mission/score Lua, all three
music masters, combat/objective positions, route control points and downstream
architecture sources are unchanged. Insertion yaw retains the earlier 30-degree
turn toward camp. The Camp 12 ammo pickup remains ground-relative at its existing
X/Z. Downstream terrain heights remain unchanged; the road's material is authored
through the scoped native paint mask.

Passed: 27 mission/content checks, Lua 5.2 compatibility, composition safeguards,
installed Assimp import, encrypted map CRC/resource references, the local baseline
scope comparison, and field-kit checks covering actual door clearance, triangle
winding, paint row orientation and preservation outside the owned route.

MAX has launched this candidate and reached its title page. Startup is not an
in-level visual or collision pass. New original art files are intentional game
content; runtime caches, testmap state, savegames, logs and local references are
excluded from Git.

Current map SHA256: `13ab59b02ab5e6489cb2b70e7cbeb2e3c09b57b2d1cd9ec8d6bc9e81db411ad3`

## Original-art load freshness

The launcher now hashes the original First Light X/FPE/PNG source bundle before
native launch. On a changed or previously unverified bundle it removes only the
compiled DBO siblings of those original meshes. Unchanged bundles keep their
compiled copies. Installed DLC and unrelated caches are not touched. The local
stamp is ignored by Git; the launch manifest records its content signature.

This supplements MAX's timestamp freshness checks. Older compiled files were
present beside newer source meshes, but this is not proof that MAX displayed
stale meshes in the supplied images. Six temporary-file tests cover first launch,
reuse, content changes with preserved timestamps, texture/material changes,
unowned files and invalid/missing model references. Native appearance and
collision still require the views below.

## Meridian material provenance and limits

MAX's [surface shader](https://github.com/Dark-Basic-Software-Limited/GameGuruMAX/blob/3e21f674d84b6e631f6e026cf23fbc7e1854ca61/GameGuru%20Core/Guru-WickedMAX/GGTerrain/CustomShaders/brdf.hlsli#L269)
multiplies roughness by G, metalness by B and reflectance by A; R supplies primary
occlusion when enabled. Original field-kit surface maps keep R/A at 255 and encode
roughness/metalness locally. The FPE multipliers are 1, reflectance remains 0.04,
and normal strength is 0.65. No painted shadows or baked occlusion are fabricated.

Channel checks cover every normal's length/direction, emission restricted to light
tiles, paint/alloy distinction, visible detail within UV margins, noncollapsed UV
triangles, reproducible generation and deployed FPE references. An authoring-only
channel preview was inspected. It is not a native render or visual approval.
Native material response, tangent orientation at runtime, glare and distant mip
behavior remain review requirements. This material pass changes the existing
lab/mast treatment; it adds no props, lights, terrain or gameplay systems.

## Native paint provenance

The format is taken from MAX's own `GGTerrain_GetMaterialIndex`,
`GGTerrain_GetPaintData` and `GGTerrain_SetPaintData` in
[the engine source](https://github.com/TheGameCreators/GameGuruMAX/blob/main/GameGuru%20Core/Guru-WickedMAX/GGTerrain/GGTerrain.cpp).
Paint is a 4096 x 4096 byte map. Zero selects height/slope materials; nonzero values
are one-based material IDs. Paint uses ordinary Z rows, unlike the existing
reversed sculpt buffer. Tests guard this difference and check untouched samples
outside the authored route. Installed terrain texture payloads remain local.

## Outstanding native gate

The supplied images document the rejected earlier version. No native screenshot
of this new field-lab/road build has been captured yet. Desktop control/capture
is unavailable in this session. No generated render or test is offered as a
substitute for native evidence.

Required next views:

1. Insertion ridge and descent: lab silhouette, brineglass restraint and road read.
2. Camp court at player height: field-lab scale, panels, ground transitions and light.
3. Walk through the lab doorway and look back: collision, roof/wall fit and work area.
4. Camp exit toward Gate 07 / Northstar: uninterrupted service-route continuity.
5. Dusk skyline and mineral close view: exposure, material response and atmosphere.

Reject or revise any broken material, overlap, floating object, unreadable route,
or toy-like shell. The present work is a concrete art-direction rebuild to review;
it is not a claim that the concept's finish has been achieved. Downstream landmark
finish and further terrain silhouette work require later native evidence.
