# FIRST LIGHT — Opening Cinematic

## Narrative job

The opening exists to answer the player's immediate question: **why is Vanguard Seven on Vesper?**

Meridian Shelf has missed two scheduled check-ins. Forty-two colonists are unaccounted for, there is no evacuation beacon, and normal traffic has stopped. Six hours earlier, survey chief Mira Sen transmitted a corrupted burst from Operations containing only fragments: Northstar is offline and an unknown "array" is waking. Nine minutes later, an Iron Warden transponder crossed Gate 07.

Kestrel and Seven are therefore conducting an emergency recovery/investigation mission. The first practical goal is to restore Northstar so the evacuation packet can be recovered and the missing colonists located. The opening should imply danger and contradiction without explaining the Choir or revealing why the Wardens are interested in AEGIS.

## Recorded opening: about 54 seconds

The existing five opening lines are preserved, including the four recorded Kestrel performances. The extra runtime is visual rather than expository: the player gets enough time to understand the Kestrel as a real vehicle entering, surveying, landing at, and leaving Meridian Shelf.

1. **ARRIVAL_WIDE — distant approach** — a high valley view establishes the dead shelf and lets the Kestrel enter as a small moving silhouette while Meridian's missed check-ins are introduced.
2. **ARRIVAL_PASS — close shelf crossing** — the aircraft makes a fast lateral pass across the abandoned outpost as the forty-two missing colonists / no-beacon condition is stated.
3. **ARRIVAL_ORBIT — reconnaissance arc** — the Kestrel curves around the facility rather than flying a single straight spline. Mira Sen's "array waking" burst plays here.
4. **ARRIVAL_DESCENT — conversion and powered-lift approach** — the aircraft commits to the landing site while the Warden transponder and Northstar objective are delivered.
5. **ARRIVAL_HANDOFF — touchdown / ramp** — a low hero angle owns touchdown and the line confirming Seven is down.
6. **ARRIVAL_LIFTOFF — vertical clearance** — the Kestrel clears the pad on lift thrust.
7. **ARRIVAL_CLIMB — transition** — a new angle catches the aircraft unloading vertical lift and beginning forward acceleration.
8. **ARRIVAL_DEPART — valley exit** — a final wide shot watches the Kestrel accelerate out before normal control returns.

Space still skips the entire opening. The Suno score remains continuous and ducks under the cinematic.

## Mechanical-state editing rule

GameGuru MAX currently receives four authored Kestrel geometry states: `flight`, `convert`, `flare`, and `landed`. Those states cannot physically morph into one another, so the opening no longer exposes the swaps in a continuous shot.

Instead, every major state change happens **under a CineGuru edit**:

- `flight` is held through ARRIVAL_WIDE and ARRIVAL_PASS.
- the cut to ARRIVAL_ORBIT masks `flight → convert`.
- the cut to ARRIVAL_DESCENT masks `convert → flare`.
- the cut to ARRIVAL_HANDOFF masks `flare → landed` and the ramp-open geometry change.
- the departure edits similarly mask `landed → flare → convert → flight`.

Within each shot, position, altitude, yaw, pitch and roll are continuously interpolated with curved paths and coordinated bank. The camera edit hides only the mechanical mesh replacement, not a teleport. Adjacent path endpoints are authored to meet exactly.

## Gameplay handoff

Only after ARRIVAL_DEPART completes does the coordinator mark insertion complete and return normal control with `Restore Northstar power` still active. Cinematics never advance mission objectives themselves.

## Failure behavior

The opening is fail-open by design. CineGuru registration is retried during native MAX startup. A beat is not marked seen until `CG_GetActiveCamera()` proves its camera is actually rolling. If any opening camera cannot start within the grace period, Kestrel delivers a concise in-game version of the premise, the remaining opening beats are marked seen, and the mission continues normally.

Aborting/skipping any opening shot also skips the **entire remaining opening sequence** rather than forcing the player through the remaining edits.

## Native acceptance gate

A successful native playtest should show all of the following:

- ARRIVAL_WIDE takes camera ownership shortly after level start.
- The Kestrel is visible at distance before the first close pass.
- ARRIVAL_PASS reads as a fast aircraft pass with coordinated bank rather than a rigid linear slide.
- ARRIVAL_ORBIT visibly curves around the outpost and gives the facility geographic context.
- ARRIVAL_DESCENT looks like a decelerating powered-lift approach.
- The flight / conversion / flare / landed geometry changes are not visibly popping on screen because each change occurs on an edit.
- Touchdown, ramp, liftoff, climb and departure each receive a readable authored shot.
- All three story phases remain readable: forty-two missing colonists, Mira's corrupted warning, Warden transponder + Northstar objective.
- The Suno score continues underneath without a restart or pop and audibly ducks during the sequence.
- Player weapon/HUD/camera presentation returns cleanly after the final departure shot or after an abort.
- If CineGuru cannot start, the fallback Kestrel briefing appears and mission progression is unaffected.
- `first-light-runtime.log` records the opening beats as separate `pending`, `activation accepted`, `start`, and `finish` events on a healthy run.
