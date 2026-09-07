# First Light: next production passes

First Light is now at the point where native MAX behavior must drive development.
The next improvements are intentionally ordered so visual/content work does not
hide runtime regressions.

## Gate 1 — boot and runtime reliability

Do not add more encounters or scenery until this gate is green.

Acceptance criteria:

- no Lua dialog during load or mission start
- preflight passes against the exact runtime map
- no stock `weapon.lua` loose pickup entities
- mission director starts and HUD appears
- no missing-script / missing-asset errors
- the three score masters are present and referenced
- a native run report can be collected after every test

## Gate 2 — animation, AI and audio

Acceptance criteria:

- every visible Warden is animated before reveal
- dormant groups remain hidden and non-colliding
- first combat activates locally rather than map-wide
- character navigation produces real movement samples
- death animations/lifecycle complete through stock MAX behavior
- Salt Moon Drift is audible in the exterior
- Moon Outpost Drift is audible in occupied infrastructure / return route
- Orbital Catacomb is audible in the AEGIS / Choir spaces
- transitions do not restart or spam cues at small boundaries
- radio is intelligible without masking score or weapon audio

Use `PLAY FIRST LIGHT QA.cmd` for the instrumented route, then
`COLLECT FIRST LIGHT.cmd` after MAX exits.

## Gate 3 — environment composition

Once Gates 1–2 are green, make the map look authored rather than generated.

Priority review frames:

1. insertion vista over Meridian Shelf
2. Survey Camp 12
3. first tide-channel fight
4. Gate 07 compression point
5. Northstar turbine hall
6. Operations workplace
7. AEGIS excavation / Choir reveal
8. west return route
9. extraction holdout

For each frame inspect:

- silhouette and focal point
- terrain/structure intersection
- readable traversal path
- lighting contrast and enemy readability
- repeated prefab patterns
- floating or clipping props
- whether civilian / military / buried-Choir history reads without text

Delete weak generated geometry instead of preserving it by default.

## Gate 4 — combat sandbox

Only tune damage after visibility, animation and navigation are proven.

Review:

- encounter duration
- cover height and spacing
- intentional flank routes
- enemy reveal direction
- reinforcement timing
- line-of-sight breaks
- recovery space between fights
- whether return-route combat feels different from the outbound route

Preserve the existing shield/armour model until native playtests show a real
balance problem.

## Gate 5 — mission polish

After the full route works:

- replace temporary radio where needed
- add tested custom weapon rewards rather than stock loose pickups
- improve Iron Warden faction identity
- add small environmental motion / machinery only where it supports a space
- tighten objective feedback and extraction presentation
- capture a stable screenshot set and final native QA report

## Rule for future AI passes

A pass is not complete because entity count increased or a Python test passed.
A pass is complete when the corresponding native acceptance gate above is green.
