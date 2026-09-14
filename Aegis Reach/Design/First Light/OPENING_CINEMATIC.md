# FIRST LIGHT — Opening Cinematic

## Narrative job

The opening answers one question quickly: **why is Vanguard Seven on Vesper?** Meridian Shelf missed two scheduled check-ins, forty-two colonists are unaccounted for, Mira Sen forced out the fragment `array waking`, and an Iron Warden transponder crossed Gate 07 nine minutes later. Seven is inserted to restore Northstar, recover the evacuation packet, and find the missing colonists.

## Camera doctrine: operational footage, not a movie camera

The opening should feel assembled from footage that could exist inside a real military operation. Every shot must answer **what physical object carries this camera?** Sources are either Kestrel hardware or fixed Meridian infrastructure. There are no invisible crane, drone, dolly, or spectator cameras.

The first attempt at this doctrine still felt static because each camera beat was automatically stretched to the full duration of the VO line assigned to it. A 9–12 second radio line therefore became a 9–12 second shot. That behavior is explicitly retired.

Recorded VO now **continues across edits**. Camera shots are editorial units, not dialogue containers.

## The 50.8-second recut

The opening now contains **17 cuts**, almost all between 2.5 and 3.1 seconds, with one 4.2-second deployment hold. The source changes should be obvious from both composition and the small live-feed identifier rendered at the top of frame.

1. **ARRIVAL_PERIM — M12-PERIM-04** — fixed Camp 12 perimeter security camera; the Kestrel is already a distant moving aircraft when the sequence begins.
2. **ARRIVAL_NOSE — KSTL-01 NOSE EO** — forward hull camera; valley closure and horizon movement establish speed.
3. **ARRIVAL_GATE — M12-GATE-02** — fixed south-approach security camera; Kestrel crosses the frame rather than materializing beside the base.
4. **ARRIVAL_STBD — KSTL-02 STBD SHOULDER** — ship structure anchors frame while terrain moves below.
5. **ARRIVAL_ISR — KSTL-03 VENTRAL ISR** — belly gimbal remains trained on Meridian during the bank.
6. **ARRIVAL_MAST — M12-MAST-01** — survey-mast optical camera sees the aircraft curve around the site.
7. **ARRIVAL_CONVERT — KSTL-03A VENTRAL AFT** — onboard view of the conversion phase.
8. **ARRIVAL_BELLY — KSTL-04 BELLY SERVICE** — underside service feed makes changing attitude and lift hardware readable.
9. **ARRIVAL_GEAR — KSTL-04 STBD GEAR** — gear/belly camera emphasizes ground closure.
10. **ARRIVAL_LZ — LZ07-PERIM-01** — fixed LZ perimeter camera sees the full aircraft entering the pad area.
11. **ARRIVAL_FLARE — LZ07-BEACON-02** — low fixed beacon camera sees powered-lift flare.
12. **ARRIVAL_TOUCHDOWN — LZ07-PAD-03** — pad camera owns the actual settle to ground.
13. **ARRIVAL_RAMP — KSTL-05 RAMP** — rear cargo camera looking out from the aircraft.
14. **ARRIVAL_DEPLOY — KSTL-05 RAMP** — same physical source holds just long enough for the final insertion line and deployment read.
15. **ARRIVAL_LIFTOFF — KSTL-05 RAMP** — ground falls away from the same camera source.
16. **ARRIVAL_CLIMB — KSTL-06 PORT SHOULDER** — opposite-side maintenance camera covers transition back toward cruise.
17. **ARRIVAL_DEPART — KSTL-07 TAIL** — tail feed watches Meridian recede before control returns.

Space skips the entire sequence. The score remains continuous and stays ducked between cuts.

## Continuous aircraft timeline

Camera cuts no longer drive the Kestrel flight path. The aircraft follows one **50.8-second opening clock** from first approach through departure. That means changing camera source cannot restart a spline, teleport the aircraft, or make it reappear from a new origin.

The authored static-mesh states still exist, so their changes are placed on source edits:

- `flight` through 17.5 s,
- `convert` from 17.5–23.5 s,
- `flare` from 23.5–32.5 s,
- `landed` from 32.5–42.7 s,
- `flare` during 42.7–45.3 s liftoff,
- `convert` during 45.3–47.8 s transition,
- `flight` during the 47.8–50.8 s departure.

World-space position remains continuous at those boundaries. The camera edit hides only the geometry-state replacement.

## Feed behavior

- Kestrel hull feeds inherit live aircraft translation, pitch, yaw, roll, and restrained mechanical vibration.
- KSTL-03 VENTRAL ISR is position-attached but target-stabilized.
- Fixed Meridian cameras remain at their authored infrastructure positions.
- A small source label (`KSTL-...`, `M12-...`, or `LZ07-...`) and `MERIDIAN INSERTION // REC` identifier make the source change legible.
- Ramp/deployment/liftoff deliberately reuse the same conceptual KSTL-05 physical camera.

## Gameplay handoff and failure behavior

Only after ARRIVAL_DEPART completes does the coordinator mark insertion complete and return control with `Restore Northstar power` still active. Cinematics never advance mission objectives.

CineGuru startup remains fail-open. If an opening source cannot start, the concise Kestrel fallback briefing is delivered and the mission continues. Aborting any opening cut skips the entire remaining insertion rather than trapping the player in the rest of the edit.

## Native acceptance gate

A successful MAX playtest should now make these differences immediately obvious:

- the opening contains many short cuts rather than four long base views;
- Kestrel is visible at distance from the first infrastructure feed and crosses later fixed-camera frames as a moving aircraft;
- long VO continues naturally while the source changes beneath it;
- world cameras, hull cameras, ISR, gear camera, ramp camera, and tail camera are visually distinguishable;
- the aircraft follows one continuous path regardless of camera changes;
- flight/convert/flare/landed swaps occur on edits rather than as exposed in-shot pops;
- touchdown and liftoff are seen both from infrastructure and onboard perspectives;
- the feed identifier changes with the source;
- player weapon/HUD/camera presentation returns cleanly after the tail feed or after a skip.
