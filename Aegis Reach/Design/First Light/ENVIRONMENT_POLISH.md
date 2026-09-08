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
  coarse stone and dark strata. No terrain textures or DLC models are copied.
- Camp 12 uses the existing Cyberpunk Streets wall/entrance/window family to
  enclose one small lab. Placement uses measured mesh extents and the roof's
  elevated local origin. Seven shell modules replace five disconnected pieces.
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
objective placements, and the Gate 07 / Northstar / Operations / AEGIS architecture
sources are unchanged. The Camp 12 ammo pickup keeps its X/Z and 28-inch ground
offset; it moves down 12.90 inches with the court edge. Downstream terrain is
unchanged from a fresh build of the baseline source.

The baseline source rebuild contains 198 entities, 68 asset types and 26 lights;
this candidate contains 195 entities, 67 asset types and 26 lights. Camp 12 has
18 environment entities including seven lab modules and its existing route beacon.

## Verification and build provenance

- Existing mission/content validation: 27 checks passed.
- Lua 5.2 compatibility, composition and launch preflight checks passed.
- Encrypted native map CRC, entity roundtrip and referenced resources passed.
- A local comparison against a freshly rebuilt main checked unchanged route
  control points, unchanged downstream terrain samples, unchanged non-camp
  architecture transforms and unchanged mission placements, with only the
  explicitly ground-relative Camp 12 pickup adjustment described above.
- MAX launched this candidate and its log reached the native title page.
  That is startup evidence only: no in-level visual or collision result is claimed.

Candidate map SHA256:
`14d234c9a740651c36d85a86e5acd14ea05c5cf85ebd0bc012150e807e0b9cc3`

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

No native screenshots were captured for this candidate. Desktop control and
capture were unavailable in the authoring session. Do not substitute generated
previews, asset thumbnails, map diagrams or passing tests for these missing views.
The next step is native screenshot -> adjustment -> screenshot, deleting weak
placements before adding anything. Native collision, visual fit, fog and lighting
must be resolved before this branch is eligible for main.
