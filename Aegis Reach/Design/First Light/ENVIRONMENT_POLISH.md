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

## September 10 opening-view correction

The supplied native opening screenshot shows the lab at the far left, a brightly
lit bank behind it, and distant structures dominating the centre. Surface detail
alone did not establish the camp as the first destination. The full desktop image
includes unrelated private applications and is not copied into this public repo.

- Normal insertion moves from (0, -9500) to (-900, -8200), on the existing descent.
  Its marker faces the camp court at 309.32 degrees. The lab is approximately 44 m
  away instead of 82 m. This changes the initial view and shortens the arrival walk;
  it does not move enemies, objectives or the established service-road spine.
- Native terrain directly behind the lab becomes a shallow backed-in bench.
  At X=-2800/Z=-7270 its height drops from 1275.8 to 630.2 inches; the court remains
  at 500. The enclosing ridge returns farther west. No cave or geology props are
  introduced, and existing lab/furniture footing stays level.
- The existing mast moves to (-2145, -6960), on the court's north side. Its practical
  light follows it, with range reduced from 540 to 330 inches and a subdued amber.
  Interior and entrance ranges become 250 and 240. The stock 45-inch marker offset
  is removed for these three lamps so the authored source heights match fixtures.
- The first two small brineglass clusters move alongside the shortened descent,
  outside the camp core. Their small lights also lose the unintended height offset.
  No new formations, props, light sources or asset families are added.

Checks sample the serialized terrain for an unobstructed entrance sightline,
moderate bank grade, grounded mast feet and light offsets. Source comparisons
confirm unchanged road grades and downstream geography/placements. Angular framing
checks measure a larger lab silhouette near the opening centre. These are structural
safeguards; the corrected view still needs native screenshot review.

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
  antenna. It sits at the north edge of the court. Its light marker coincides
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
architecture sources are unchanged. Insertion now starts farther down the existing approach and faces the camp court,
as described above. The Camp 12 ammo pickup remains ground-relative at its existing
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

Current map SHA256: `a93f9f89d8c12d3ab19174f18eacaed65f830060af8a44c7d6e8de9d7cba1a8f`

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

The September 10 native opening image informed this correction. The revised
insertion, bench, mast and light pools have not yet been reviewed in MAX images.
Desktop control/capture is unavailable in this session. No generated render or
test is offered as a substitute for native evidence.

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
