# FIRST LIGHT — combat / presentation production pass

Branch target: `sol/aaa-combat-director-pass`

This pass does **not** claim that FIRST LIGHT is literally a finished AAA game. It moves the playable slice toward the production qualities that matter most in an FPS: readable threat escalation, authored combat rhythm, player-state feedback, dialogue intelligibility, objective readability, and a holdout that builds rather than merely counts down.

The north star remains the broad combat readability and encounter rhythm of a classic arena FPS such as *Halo: Combat Evolved*, while keeping Aegis Reach's own Vesper / Warden / brineglass identity.

## What changed

### Adaptive combat director

`firstlight_director.lua`

- Tracks a 0–100 hidden pressure value from nearby contacts, recent damage, shield/armour loss and extraction escalation.
- Exposes LOW / ELEVATED / HIGH / CRITICAL threat bands to the combat HUD.
- Maintains a new-enemy reveal budget (normally four, five during extraction) and tightens it when the player is shieldless or critically damaged.
- Never despawns, kills, freezes or otherwise cheats already-active enemies.
- Adds shield-collapse and armour-critical feedback.
- Queues tactical barks behind story dialogue so combat chatter cannot interrupt mission-critical lines.
- Adds staged extraction callouts that align with the authored reserve timings.
- Adds readable shield/armour and extraction progress meters.
- Logs pressure and reveal budget in the existing native runtime audit.

### Authored squad reveal rhythm

`firstlight_enemy.lua`

- Keeps GameGuru MAX `character_attack` responsible for actual locomotion, combat and death.
- Gives each authored squad a light role pattern: assault / rifle / anchor.
- Staggers reveal cadence so a group reads as an encounter instead of a simultaneous spawn dump.
- Uses the director's reveal budget only for dormant soldiers. Active Wardens retain full agency.
- Preserves fixed extraction reserve timing and native death lifecycle.

### Diegetic objective language

`firstlight_interact.lua`

Mission terminals now communicate state through emissive color before the player is standing on top of them:

- dim steel — future / locked objective
- cyan — current actionable objective
- bright cyan — interaction in progress
- amber — waiting / contested
- green — completed
- violet — optional field record

Hold interactions expose a real progress meter. A terminal denied by nearby enemies can issue a rate-limited suit bark. Field repair clears the critical-armour warning state.

### Adaptive score mix

`firstlight_score.lua`

- Combat loudness now follows director intensity without hard-cutting the spatial score identity on every brief contact.
- Dialogue automatically ducks the score, then restores it smoothly.
- AEGIS interference and extraction overcharge retain their authored semantic states.
- Native audit logging records ducking and intensity.

## Native playtest gate

Run the normal FIRST LIGHT native deployment/playtest path. For a diagnostic run, enable `AEGIS_FIRSTLIGHT_QA=1` so the existing observer records traversal and actor samples without changing play.

A pass should explicitly verify:

1. **Opening restraint** — the first 20 seconds remain readable and the first Warden group does not stomp the Kestrel introduction.
2. **Squad cadence** — groups arrive in beats; no visible T-pose/bind-pose reveal; no dormant visible characters.
3. **Native combat** — idle, navigation, aim, firing, hit response and death all remain native and credible.
4. **Pressure fairness** — critically damaged players stop receiving new reveals temporarily, while existing enemies continue fighting normally.
5. **Shield loop** — shield collapse is obvious; breaking contact creates a believable recharge window; AEGIS interference delays recharge as intended.
6. **Terminal readability** — current objective cyan, contested amber, completed green, future objectives subdued. No emissive state should wash out the underlying PBR material.
7. **Radio mix** — Kestrel / suit text is never replaced mid-line by a lower-priority tactical bark; music attenuation is noticeable but not a dramatic volume pump.
8. **Northstar → Operations → AEGIS** — objective transition, discovery score state and route guidance remain intact.
9. **Extraction escalation** — reserves still appear around 4/7, 22/25 and 40/43 seconds; callouts feel synchronized with the fight; the countdown pauses outside the LZ.
10. **Completion** — all remaining nearby Wardens must be cleared, boarding still requires a continuous hold, mission completion/debrief fires, and the summary includes peak threat.

## Tuning knobs after the first native run

Do not redesign before seeing a real run. Tune these in order:

- `firstlight_director.lua`: `combat_budget`, pressure thresholds (16 / 42 / 72), shield-recharge delays.
- `firstlight_enemy.lua`: regular reveal cadence (600 ms), reserve cadence, assault/rifle/anchor stand-off values.
- `firstlight_score.lua`: dialogue duck (-14), combat intensity lift (up to +6), track-change dwell (4.5 s) and minimum identity duration (15 s).
- `firstlight_interact.lua`: emissive strengths and terminal denial radius.

If a native run reports animation or pathfinding regressions, fix the wrapper or map navigation before increasing enemy count. More actors are not a substitute for better encounter geometry.
