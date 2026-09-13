# FIRST LIGHT — combat / presentation production pass

Branch target: `sol/aaa-combat-director-pass`

This pass does **not** claim that FIRST LIGHT is literally a finished AAA game. It moves the playable slice toward the production qualities that matter most in an FPS: readable threat escalation, authored combat rhythm, player-state feedback, dialogue intelligibility, objective readability, useful combat geometry, and a holdout that builds rather than merely counts down.

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
- Maps authored roles onto MAX's real tactical choices: assault = Get Close, rifle = Use Cover, anchor = Stay Back / Stand Ground, flanker = Wide Flank.
- Uses a shared squad clock so a contact develops as a cell rather than several unrelated entity timers.
- Regular squads use visibility-safe reveals: if a dormant staging point is centered in the player's view, the reveal waits briefly instead of visibly popping an actor into existence. A 3.2 second ceiling prevents progression deadlock.
- Return-route and extraction reserves intentionally bypass the visibility hold because those are authored reinforcement arrivals.
- Uses role-weighted nearby threat plus the director budget to gate only dormant soldiers. Active Wardens retain full agency.
- Gives a newly broken shield a short feed pause before another regular dormant soldier can enter.
- Preserves fixed extraction reserve timing and native death lifecycle.
- QA mode logs held reveals and actual reveal reason/timing.

### Production combat-space layer

`firstlight_combat_geometry.py` / `build_first_light_aaa.py`

The proven baseline world builder remains intact. The normal rebuild path now runs a production wrapper that composes Astra's existing world first, then adds a sparse tactical layer and rewrites the same native MAX archive.

- Adds **24 combat-cover pieces** across the dry channel, Gate 07, Northstar, Operations, AEGIS, the return service road and extraction yard.
- Uses offset cover triangles rather than walls of clutter: a fallback pocket, an advance pocket and a lateral/flank pocket while preserving the main traversal spine.
- Repositions all authored dormant Warden starts onto those encounter pockets so `Use Cover`, `Get Close`, `Stay Back` and `Wide Flank` have spatial meaning.
- Adds **8 restrained contact backlights** behind likely combat silhouettes. Their ranges stay local so they do not flatten Vesper's darker global grade.
- Keeps the extraction pad's central boarding lane clear. Side cover frames the holdout without blocking Kestrel or the terminal.
- Leaves navmesh data absent in the rebuilt archive so MAX regenerates navigation against the changed geometry.
- Emits `combat-geometry.json` plus role/encounter metadata in `layout.json` for post-build review.
- `firstlight_rebuild_if_needed.py` fingerprints the combat layer and automatically rebuilds through `build_first_light_aaa.py` from the normal PLAY FIRST LIGHT path.

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

### Preflight / regression gate

The normal native launch now fails fast if the production combat layer is malformed.

- `test_firstlight.py` verifies stock MAX tactic mappings, authored extraction delay, native death ownership and visibility-safe reveal behavior.
- `test_firstlight_combat_geometry.py` validates cover counts, complete Warden starts, encounter-to-cover proximity, two-sided extraction reserves, local light ranges and a clear LZ center without requiring a MAX installation.
- `firstlight_preflight.py` then validates the generated `combat-geometry.json` and `layout.json` against the encrypted FPM before GameGuru MAX launches.
- Every native-map entity must have a generated-layout counterpart; all Warden starts must be authored by the production layer.

## Native playtest gate

Run the normal FIRST LIGHT native deployment/playtest path. For a diagnostic run, enable `AEGIS_FIRSTLIGHT_QA=1` so the existing observer records traversal and actor samples without changing play.

A pass should explicitly verify:

1. **Opening restraint** — the first 20 seconds remain readable and the first Warden group does not stomp the Kestrel introduction.
2. **Squad cadence / reveal safety** — contacts arrive in readable beats; regular dormant actors do not visibly pop into the center of view; no T-pose/bind-pose reveal occurs.
3. **Native combat** — assault pushes, rifle seeks cover, anchor holds range, flanker takes a wide route; idle, navigation, aim, firing, hit response and death remain native and credible.
4. **Geometry actually helps AI** — the added pockets create lateral choices and recovery cover rather than snagging Recast paths or funneling everyone through one lane.
5. **Pressure fairness** — critically damaged players stop receiving new regular reveals temporarily, while existing enemies continue fighting normally.
6. **Shield loop** — shield collapse is obvious; breaking contact creates a believable recharge window; AEGIS interference delays recharge as intended.
7. **Terminal readability** — current objective cyan, contested amber, completed green, future objectives subdued. No emissive state should wash out the underlying PBR material.
8. **Radio mix** — Kestrel / suit text is never replaced mid-line by a lower-priority tactical bark; music attenuation is noticeable but not a dramatic volume pump.
9. **Combat lighting** — new local backlights silhouette threats without turning the scene flat, overbright or arcade-like.
10. **Northstar → Operations → AEGIS** — objective transition, discovery score state and route guidance remain intact.
11. **Extraction escalation** — reserves still appear around 4/7, 22/25 and 40/43 seconds; callouts feel synchronized with the fight; east/west service-road attacks are readable; the countdown pauses outside the LZ.
12. **LZ traversal** — the pad center and boarding line stay clear despite added side cover.
13. **Completion** — all remaining nearby Wardens must be cleared, boarding still requires a continuous hold, mission completion/debrief fires, and the summary includes peak threat.

## Tuning knobs after the first native run

Do not redesign before seeing a real run. Tune these in order:

- `firstlight_combat_geometry.py`: pocket position/orientation first. If native AI cannot use a pocket, move or delete geometry before touching actor count.
- `firstlight_enemy.lua`: role reveal offsets, 52-degree visibility cone / 3.2-second hold ceiling, role retreat ranges, native `FlankTarget` choice and combat/hearing windows.
- `firstlight_director.lua`: `combat_budget`, pressure thresholds (16 / 42 / 72), shield-recharge delays.
- `firstlight_score.lua`: dialogue duck (-14), combat intensity lift (up to +6), track-change dwell (4.5 s) and minimum identity duration (15 s).
- `firstlight_interact.lua`: emissive strengths and terminal denial radius.

If a native run reports animation or pathfinding regressions, fix the wrapper or map navigation before increasing enemy count. More actors are not a substitute for better encounter geometry.
