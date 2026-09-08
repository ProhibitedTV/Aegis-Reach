# First Light environment polish - native review pending

This is an unapproved production-level candidate, not a completed visual pass.
It starts from remote main `0fbb6960c94168367c50c34692d6a2fb084d2e8b`.
No showroom or separate map is part of this change. Do not merge until the
native views below have been captured, personally inspected and iterated.

## Authored changes

- Local native-terrain shoulders and low banks frame the insertion descent and
  Camp 12. The approach road has a narrower graded shoulder; the smaller court
  lets terrain shelter the lab. Relief fades out before the first encounter.
- Terrain layers use installed dark mineral gravel, rust-stained low ground,
  dark strata. The opening screenshot prompted removal of the pale coarse-stone layer and the broad orange lowland layer. No terrain textures or DLC models are copied.
- Camp 12 uses the existing Cyberpunk Streets wall/entrance/window family to
  enclose one small lab. Placement uses measured mesh extents and the roof's
  elevated local origin. Six shell modules form a covered service bay. The solid decorative entrance panel has been removed for physical access.
  These measurements establish a candidate fit, not native collision approval.
- The mast is smaller; one cargo unit, one case and one power cluster remain.
  A desk and chair sit inside the lab. An exit pole/lamp, second cargo unit,
  spare crate, cylinder and second camp barrier are removed. The evacuation
  roster becomes a smaller wall-mounted sign instead of a freestanding frame.
- Three existing camp lights form an indoor amber pool, an amber court pool,
  and a small cyan entrance accent. Their ranges are reduced. Total light count
  remains 26.
- The first five brineglass blooms move nearer route edges and grow from small
  early exposures toward larger later formations. All ten clusters remain,
  including the three violet clusters. Bases are embedded more deeply, with
  slight tilt; light spill is lower and early ranges are smaller. Both existing
  procedural energy textures are retained and also used as weak emissive maps.
- Exposure and bloom are reduced, with a cool overcast sky and shorter fog range.
  Sun RGB is explicitly in MAX's native 0..255 range; DeSaturate=1 preserves color.
  Final brightness, texture response and horizon balance still need native review.

## Deliberately stable

Mission and score Lua, the three Suno masters, route control points, enemy and
objective positions, and the Gate 07 / Northstar / Operations / AEGIS architecture
sources are unchanged. The Camp 12 ammo pickup keeps its X/Z and 28-inch ground
offset and follows the court edge vertically. The player keeps the same position
and loadout, with the starting yaw turned 30 degrees toward the Camp 12 descent. Downstream terrain is
unchanged from a fresh build of the baseline source.

The baseline source rebuild contains 198 entities, 68 asset types and 26 lights;
this candidate contains 194 entities, 67 asset types and 26 lights. Camp 12 has
17 environment entities including six lab modules and its existing route beacon.

## Verification and build provenance

- Existing mission/content validation: 27 checks passed.
- Lua 5.2 compatibility, composition and launch preflight checks passed.
- Encrypted native map CRC, entity roundtrip and referenced resources passed.
- A local comparison against a freshly rebuilt main checked unchanged route
  control points, unchanged downstream terrain samples, unchanged non-camp
  architecture transforms and unchanged mission placements, with only the
  ground-relative Camp 12 pickup adjustment and insertion yaw described above.
- MAX launched this candidate and its log reached the native title page.
  That is startup evidence only: no in-level visual or collision result is claimed.

Candidate map SHA256:
`70c788c8b487a94b14d42c10f52ab627c395df51c94b0b81457678f296ab0847`

Committed map/layout reports on the baseline lag behind its authoring source.
The generated artifact refresh therefore also includes original project meshes
already produced by main (arrival frame, Northstar stacks, route beacon and
brineglass), and the existing source's six-inch bridge deck lift. These are
source/build synchronization, not new downstream design changes. All installed
DLC remains referenced by path. Runtime logs, caches, registrations, testmap
state and local comparison files are excluded from the commit.

## Required native review - all pending

| View | Acceptance questions | Status |
| --- | --- | --- |
| Insertion ridge toward Camp 12 | Does terrain frame a recognizable lab without hiding the route? | Pending |
| Descent toward Camp 12 | Are road shoulders traversable and geological, with readable small brineglass? | Pending |
| Camp court looking toward lab | Is the shell joined and grounded; is the sign readable; is warmth restrained? | Pending |
| Lab entrance looking across court | Are desk/chair collision, doorway clearance and open court believable? | Pending |
| Camp exit toward route | Is the outbound road visibly open without the removed pole? | Pending |
| Route toward Gate 07 / Northstar | Do fog, road cues and terrain preserve landmark recognition? | Pending |
| Brineglass in terrain context | Does it emerge from geology with subtle light, rather than resemble decoration? | Pending |
| Dusk skyline | Is the sky subordinate, with readable ground and no washed-out lighting? | Pending |

The user supplied a native opening screenshot of the initial candidate. It was
inspected and rejected as final visual approval for the reasons below. No revised
opening screenshot or other required views have been captured yet. Desktop
control and capture remain unavailable in the authoring session. Do not substitute generated
previews, asset thumbnails, map diagrams or passing tests for these missing views.
The next step is native screenshot -> adjustment -> screenshot, deleting weak
placements before adding anything. Native collision, visual fit, fog and lighting
must be resolved before this branch is eligible for main.


## Opening screenshot iteration (7 September 2026)

The supplied native image shows pale gravel dominating the foreground and ridge
slopes, broad orange ground, Camp 12 mostly outside the left edge, and a saturated
blue foreground crystal with a conspicuous white pool. The skyline is calmer
than earlier versions but the lab is not the opening's primary visual anchor.
This image does not qualify the environment for main.

The next revision makes five targeted corrections:

1. Turn the starting yaw from 0 to 330 degrees, keeping spawn position and loadout.
2. Lower a broad inner descent shoulder that obstructed the lab. Source-height
   ray samples from insertion eye height to the front facade and roof are now
   clear (minimum sampled margins 13.6 and 39.1 inches). These checks explain the
   edit; rendered terrain and actual player movement remain authoritative.
3. Replace pale upper-slope gravel with installed dark strata and the orange
   lowland layer with the existing mineral base. Reduce sun intensity 1.8 to 1.45;
   retain the current sky, fog and exposure for a controlled comparison.
4. Reduce the first two brineglass footprints and vertical proportions, contract
   their light radii from 150/180 to 65/90 inches, and soften the light color.
   Raise shared surface roughness and reduce reflectance and weak emission.
   The procedural blue/cyan and violet texture artwork is unchanged.
5. Contract the amber work-court pool from 390 to 310 inches and soften its orange
   tint. No extra lights or props are added.

All other viewpoints remain pending. The next required image is the revised
opening, followed by descent and an eye-height Camp 12 court view.


## Camp access and grounding correction (8 September 2026)

A source geometry audit found a functional flaw in the enclosed lab: the installed
`Cyberpunk Streets Booster Pack\Buildings\CS_Wall_01_Entry_01.fpe` is a closed
facade. Across-door triangle intersections blocked every sampled X position from
-90 to +90 at local heights 5, 40, 80, 103, 115, 145 and 180. Naming the asset an
entrance had concealed the lack of physical passage. A compatible static variant
was also closed; no replacement DLC or scripted door system was introduced.

The closed facade panel is removed, leaving one open service bay beneath the
existing roof. Walls, roof, workstation and lighting retain their positions.
This exposes the indoor work area to the court and eliminates the known blockage;
native player collision and the final shelter silhouette still need review.

The single camp Roadblock2 previously straddled the outbound slope: measured
lowest mesh vertices were up to 13.39 inches below and 6.96 inches above terrain.
It moves from (-1220,-6600) to (-1350,-6910), on the flat court edge. A conservative
76-inch footprint is checked against native terrain height. It remains one small
perimeter cue beside the route, with no new terrain pad or barrier ring.

The existing wall roster now says MERIDIAN / CAMP 12, retaining the 42-of-43
missing-person clue. Its geometry, placement and size are unchanged. No gameplay,
score, encounter, new asset family or new lighting changes accompany this fix.
The updated candidate must be checked from inside the court and while walking
through the service bay before merge.
