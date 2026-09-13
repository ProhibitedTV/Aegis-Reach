# First Light: aftermath and damaged infrastructure

This pass uses six native MAX particle markers and three original, human-scale
props. It tells the same story as the mission: an interrupted evacuation, civilian
power isolated by the Wardens, records deliberately destroyed, and AEGIS retasked
against the shelter. It does not imply the intact Northstar generators exploded.

| Location | Visible evidence | Mission consequence |
| --- | --- | --- |
| Camp 12, beside the survey mast | Open junction, pulled wiring, short cool electrical bursts | Fault emission stops once the Northstar override restores safe routing |
| Gate 07, behind the inspection office | Ruptured cargo case, detached lid, low smoke and occasional warm embers | Residual aftermath of the forced freight turnaround |
| Northstar, first stack | Thin exhaust from the actual stack opening | Starts only after power returns |
| Operations, rear service court | Burned electronics case, low dark smoke | Physical evidence purged beside the personnel archive |
| AEGIS, west relay cabinet | Brief blue electrical discharge at its front panel | Active only while the firing bus is armed; stops after cancellation |

Camp 12 remains a refuge. There is no large fire, smoke curtain, additional global
fog, camera shake, particle damage or new mission stage. Emission is distance
limited (starts within 53 m, stops beyond 61 m) with hysteresis; bursts are staggered
and separated by 2.2-3.1 seconds. Win/death disables emission and exit stops it.
The native engine owns emitter allocation and cleanup.

## Authoring and installed dependencies

- `tools/firstlight_story_effects.py`: three grounded prop placements, original
  junction/case mesh geometry, emitter positions/scales and semantic roles.
- `Files/scriptbank/aegis_reach/firstlight_effects.lua`: opacity, speed, tint,
  lifespan, burst cadence, proximity and mission-state response.
- `tools/build_first_light_aaa.py`: applies this layer after existing combat
  placement, then writes the same production First Light map.
- Native `_markers/Particles.fpe`, with an explicit custom behavior replacing its
  missing legacy particle.lua. The canonical map stores `newparticle.emittername`.
- Installed presets `particlesbank/embers2`, `smoke_billowy` and `camp smoke`.
  Their ARX/textures stay in the local MAX installation; no licensed payload copied.

Native API/serialization contracts were inspected in installed global.lua,
scriptbank/effects/particleeffect.lua and the repository's MAX-Entity.cpp reference.
The implementation uses EffectStart/Stop, EffectFireBurst and EffectSet* commands,
not the obsolete ParticlesAddEmitter interface. Static preview and show-at-start
are disabled so mission state owns activation.

The original case uses darkened existing Meridian material tiles and exposed
internal modules; the junction has a still-hinged open door and pulled wiring.
The Northstar and AEGIS emitters attach to exact original-mesh coordinates.
Camp 12 adds one meaningful prop (15 total); the court/road remain open.

## Native review

The user-approved September 13 sky remains unchanged. This is an effects candidate,
not native-approved particle art. The native control runtime now loads and finds
MAX, but screenshot capture fails with `SetIsBorderRequired: 0x80004002` on both
the initial attempt and a fresh window lookup. Candidate cbcc078 was launched
normally (PID 25388); no blind input was sent. The full preflight passed. Comparing
the encrypted map contents confirmed all 235 existing entity records, terrain and
sky payloads are unchanged; only nine new entities and their bank entries differ.
Tests can verify marker serialization, dependencies, native-ground contact, stage
transitions and rate limits; they cannot judge plume size, opacity or spark motion.

Start a new game and inspect the junction at Camp 12, then the small damaged case
behind Gate 07. Restore power: the camp fault should quiet and Northstar's first
stack should vent. Inspect the data case behind Operations. At AEGIS, compare the
west cabinet before and after cancelling the firing order. Check the effects from
player height and the incoming road; they must not obscure enemies or landmarks.

Dial native emitter scale in EFFECTS first if smoke is too large. Reduce opacity
in the Lua role config if it reads as a solid cloud. Reject any effect that lacks
physical alignment, looks like magical fire, or hurts performance. No extra
particle categories are needed before these six are inspected.
