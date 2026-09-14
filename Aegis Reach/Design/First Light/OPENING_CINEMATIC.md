# FIRST LIGHT — Opening Cinematic

## Narrative job

The opening exists to answer the player's immediate question: **why is Vanguard Seven on Vesper?**

Meridian Shelf has missed two scheduled check-ins. Forty-two colonists are unaccounted for, there is no evacuation beacon, and normal traffic has stopped. Six hours earlier, survey chief Mira Sen transmitted a corrupted burst from Operations containing only fragments: Northstar is offline and an unknown "array" is waking. Nine minutes later, an Iron Warden transponder crossed Gate 07.

Kestrel and Seven are therefore conducting an emergency recovery/investigation mission. The first practical goal is to restore Northstar so the evacuation packet can be recovered and the missing colonists located. The opening should imply danger and contradiction without explaining the Choir or revealing why the Wardens are interested in AEGIS.

## Camera doctrine: military / diegetic, not omniscient

The opening should feel like recovered operational footage from a real campaign. Every opening viewpoint must answer a practical question: **what physical object carries this camera?**

There are no free-floating crane, dolly, drone or invisible "movie" cameras in the insertion sequence. CineGuru still owns presentation, but `firstlight_camera_rig.lua` moves the eight opening camera entities with the live Kestrel object every frame. Fixed hull cameras inherit the aircraft's pitch, yaw, roll and vibration. The ventral reconnaissance camera is a plausible gimbal-stabilized ISR sensor: its position remains attached to the belly while its boresight stays trained on Meridian Shelf.

This makes the cinematic language part of the world rather than a layer floating above it.

## Recorded opening: about 54 seconds

The existing five opening lines are preserved, including the four recorded Kestrel performances. The extra runtime is visual rather than expository: the player experiences the insertion through the aircraft's own camera network.

1. **ARRIVAL_WIDE — KSTL-01 NOSE EO** — forward hull electro-optical feed. Meridian Shelf grows in the frame as the Kestrel crosses the valley and the missed check-ins are introduced.
2. **ARRIVAL_PASS — KSTL-02 STBD SHOULDER** — starboard shoulder maintenance camera aimed back across the aircraft. Hull/wing structure should remain near frame while the outpost and terrain rip past beneath it during the forty-two-colonist line.
3. **ARRIVAL_ORBIT — KSTL-03 VENTRAL ISR** — gimbal-stabilized belly reconnaissance feed. The sensor stays trained on Meridian while the aircraft banks around the site; Mira Sen's "array waking" burst plays here.
4. **ARRIVAL_DESCENT — KSTL-04 STBD GEAR** — landing-gear / belly-side camera. Terrain rises toward the aircraft during the powered-lift descent while the Warden transponder and Northstar objective are delivered.
5. **ARRIVAL_HANDOFF — KSTL-05 RAMP** — rear cargo-door camera looking down/out across the ramp. Touchdown and the confirmation that Seven is down happen from the same practical camera crew would use to monitor deployment.
6. **ARRIVAL_LIFTOFF — KSTL-05 RAMP** — the same physical ramp camera remains in service as the ground drops away beneath the aircraft.
7. **ARRIVAL_CLIMB — KSTL-06 PORT SHOULDER** — opposite-side maintenance camera catches the conversion/climb with the Kestrel structure anchoring the frame.
8. **ARRIVAL_DEPART — KSTL-07 TAIL** — aft observation camera watches Meridian Shelf recede as the Kestrel accelerates away and normal control returns.

Space still skips the entire opening. The Suno score remains continuous and ducks under the cinematic.

## Mechanical-state editing rule

GameGuru MAX currently receives four authored Kestrel geometry states: `flight`, `convert`, `flare`, and `landed`. Those states cannot physically morph into one another, so the opening does not expose the swaps in a continuous feed.

Every major state change happens **on a camera-source edit**:

- `flight` is held through KSTL-01 and KSTL-02.
- the cut to KSTL-03 masks `flight → convert`.
- the cut to KSTL-04 masks `convert → flare`.
- the cut to KSTL-05 masks `flare → landed` and the ramp-open geometry change.
- departure edits similarly mask `landed → flare → convert → flight`.

Within a feed, Kestrel position, altitude, yaw, pitch and roll remain continuously interpolated. The camera mount itself inherits that live transform, so the viewer feels bank, deceleration, hover correction and climb as vehicle motion rather than as a floating camera tracking a ship.

## Mount behavior

- Fixed cameras use a rigid local-space position and boresight rotated by the live Kestrel transform.
- KSTL-03 VENTRAL ISR uses a rigid local-space position but a stabilized world-space target over the Meridian outpost.
- Small deterministic vibration is added per mount to imply real vehicle hardware without turning the shot into handheld shake.
- KSTL-05 is intentionally reused for both touchdown and liftoff so the player recognizes one continuous physical camera source.
- The normal CineGuru camera placements remain as editor/fail-safe transforms only; runtime presentation is owned by the diegetic rig.

## Gameplay handoff

Only after ARRIVAL_DEPART completes does the coordinator mark insertion complete and return normal control with `Restore Northstar power` still active. Cinematics never advance mission objectives themselves.

## Failure behavior

The opening is fail-open by design. CineGuru registration is retried during native MAX startup. A beat is not marked seen until `CG_GetActiveCamera()` proves its camera is actually rolling. If any opening camera cannot start within the grace period, Kestrel delivers a concise in-game version of the premise, the remaining opening beats are marked seen, and the mission continues normally.

Aborting/skipping any opening shot also skips the **entire remaining opening sequence** rather than forcing the player through the remaining feeds.

## Native acceptance gate

A successful native playtest should show all of the following:

- Every opening shot feels physically attached to the Kestrel rather than placed in empty world space.
- KSTL-01 moves with the nose through the initial approach; the horizon reacts to aircraft attitude.
- KSTL-02 visibly retains Kestrel structure near frame while terrain slides past below.
- KSTL-03 remains attached to the belly while its stabilized ISR boresight keeps Meridian readable through the orbit.
- KSTL-04 makes descent speed and ground closure obvious.
- KSTL-05 reads as a real ramp/deployment camera at touchdown and again during liftoff.
- KSTL-06 and KSTL-07 make the departure feel observed by onboard systems rather than an external film crew.
- The flight / conversion / flare / landed geometry changes are not visibly popping on screen because each change occurs on an edit.
- All three story phases remain readable: forty-two missing colonists, Mira's corrupted warning, Warden transponder + Northstar objective.
- The Suno score continues underneath without a restart or pop and audibly ducks during the sequence.
- Player weapon/HUD/camera presentation returns cleanly after the final tail-camera feed or after an abort.
- If CineGuru or the camera rig cannot initialize, the fallback briefing / safe editor transforms leave mission progression unaffected.
- `first-light-runtime.log` records the opening beats as separate `pending`, `activation accepted`, `start`, and `finish` events on a healthy run.
