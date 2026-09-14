# FIRST LIGHT — Opening Cinematic

## Narrative job

The opening exists to answer the player's immediate question: **why is Vanguard Seven on Vesper?**

Meridian Shelf has missed two scheduled check-ins. Forty-two colonists are unaccounted for, there is no evacuation beacon, and normal traffic has stopped. Six hours earlier, survey chief Mira Sen transmitted a corrupted burst from Operations containing only fragments: Northstar is offline and an unknown "array" is waking. Nine minutes later, an Iron Warden transponder crossed Gate 07.

Kestrel and Seven are therefore conducting an emergency recovery/investigation mission. The first practical goal is to restore Northstar so the evacuation packet can be recovered and the missing colonists located. The opening should imply danger and contradiction without explaining the Choir or revealing why the Wardens are interested in AEGIS.

## Recorded opening: about 44 seconds

1. **Human stakes** — high establishing view over the dead Meridian service corridor toward Camp 12. Kestrel states that Meridian missed two check-ins: forty-two colonists, no beacon, no traffic.
2. **Mystery** — Mira Sen's corrupted final burst is presented as recovered signal text: "...Northstar offline... array waking..." The source is Operations; the rest is lost.
3. **Threat + action** — Kestrel notes that a Warden transponder crossed Gate 07 nine minutes after the burst. Seven's order is simple: restore Northstar, recover the evacuation packet, find the missing people.

ARRIVAL lasts 18.53 seconds and ARRIVAL_HANDOFF lasts 25.61 seconds. The first four lines use the supplied WAV performances; the fifth remains text-only. Camera timing comes from the dialogue catalog and measured audio lengths. Space skips the entire opening. The Suno score remains continuous and ducks under the cinematic.

## Gameplay handoff

When CineGuru returns control, Kestrel confirms touchdown and points Seven toward Northstar. The normal FIRST LIGHT objective remains `Restore Northstar power`; cinematics never advance mission state themselves.

## Failure behavior

The opening is fail-open by design. CineGuru registration is retried during native MAX startup. The beat is not marked seen until `CG_GetActiveCamera()` proves the ARRIVAL camera is actually rolling. If the camera cannot start within the grace period, Kestrel delivers a concise in-game version of the same premise and the mission continues normally.

## Native acceptance gate

A successful native playtest should show all of the following:

- ARRIVAL takes camera ownership shortly after level start instead of silently disappearing.
- The shot clearly establishes Vesper / Meridian Shelf and the abandoned approach to Camp 12.
- All three story phases are readable: forty-two missing colonists, Mira's corrupted warning, Warden transponder + Northstar objective.
- The Suno score continues underneath without a restart or pop and audibly ducks during the beat.
- Player weapon/HUD/camera presentation returns cleanly after CineGuru completes or is aborted.
- The handoff message appears and normal movement begins with `Restore Northstar power` still active.
- If CineGuru cannot start, the fallback Kestrel briefing appears and mission progression is unaffected.
- `first-light-runtime.log` records `pending`, `activation accepted`, `start`, and `finish` for ARRIVAL on a healthy run; a failed run records the explicit fallback reason.
