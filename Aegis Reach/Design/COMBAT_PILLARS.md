# Aegis Reach combat pillars

## North star

Aegis Reach should feel like a high-tempo science-fiction infantry sandbox built around a repeatable **30-second combat loop**:

1. Read the battlefield and identify the dangerous role.
2. Commit with the right weapon or route.
3. Take pressure, lose shield, and decide whether to finish the push or break contact.
4. Reposition through cover or a flank gate while the enemy reacts.
5. Collapse the local group, reload, recharge, and immediately see the next problem.

The goal is not maximum enemy count. The goal is a small number of enemies creating a changing tactical problem that is easy to understand and satisfying to solve repeatedly.

## What the prototype already has

The Relayfall map is a useful vertical slice rather than a throwaway proof of concept. It already contains:

- a regenerating 100-point shield over persistent 100-point armour;
- a compact assault rifle at spawn;
- shotgun, marksman rifle, grenade and ammunition pickups;
- hard-cover pieces and blast-wall flank gates;
- three sequential objectives followed by a return-to-LZ fight;
- twelve standing Iron Wardens plus four reserve soldiers;
- a mission director, objective scripts, field repair and extraction logic.

These systems are enough to tune the core loop before adding more levels.

## Enemy combat language

Pass 1 gives the stock MAX soldier behavior four readable roles. The role is deterministic from the Iron Warden number, so the current map does not need to be rebuilt.

### Flanker

Moves wide around the player and punishes tunnel vision. The player should notice a threat leaving the main firing line and decide whether to intercept or finish the current target.

### Anchor

Defends a firing position and holds space. Anchors make the marksman rifle and grenades useful and give the player a reason to change angles instead of simply walking forward.

### Hunter

Closes distance aggressively. Hunters put pressure on shield recovery and make the shotgun valuable.

### Skirmisher

Uses less predictable movement and supports the other roles. This is the baseline rifleman rather than the star of the encounter.

### Reserve assault

Reserve troops spawn only at authored mission beats and enter already alerted. They exist to reverse the emotional direction of a fight: the player thinks an area is nearly solved, then has to react to a fresh push.

## Encounter cadence for Relayfall

### Beat 1 — Insertion breach

**Actors:** Iron Wardens 01–02.

Purpose: teach movement, rifle feel, shields and cover without overwhelming the player. This should become the benchmark encounter. If repeatedly fighting these two soldiers is not fun, do not add more content yet.

Desired duration: roughly 20–35 seconds for a first-time player.

### Beat 2 — Northstar yard

**Actors:** Wardens 03–05 around the Northstar approach.

Purpose: introduce the first multi-angle fight and make the blast-wall side gates matter. A player walking straight up the center should feel pressured; a player who changes angle should feel smart.

Reward: Northstar completion, a short tactical reset, nearby ammunition and access to the shotgun route.

### Beat 3 — Lantern crossfire

**Actors:** Wardens 06–08.

Purpose: force weapon choice. Hunters should make close range dangerous while an anchor or distant rifleman asks the player to use cover and the marksman rifle.

The field repair crate belongs near this middle beat because armour damage now has an opportunity cost rather than automatically healing.

### Beat 4 — AEGIS core

**Actors:** Wardens 09–12 plus Reserve 01–02.

Purpose: the largest offensive fight in the slice. The standing defenders establish the problem; the reserve assault pair changes it after the player reaches the core phase. This should feel like a deliberate quick-response force, not enemies appearing randomly.

The core override should happen after the player has earned a short moment of control.

### Beat 5 — Kestrel LZ reversal

**Actors:** Reserve 03–04 plus any surviving pursuers.

Purpose: turn the level back on itself. The player returns through familiar space with a new objective and an aggressive pursuit squad. Extraction remains blocked until nearby enemies are dead.

This beat should be shorter and more desperate than the core fight.

## Weapon roles

Keep the sandbox small enough that each pickup changes how the player thinks.

- **Compact assault rifle:** flexible default; wins through tracking, bursts and controlled movement.
- **Shotgun:** space-maker against hunters and enemies crossing a gate.
- **Marksman rifle:** removes anchors and rewards sight-line awareness.
- **Grenades:** break static positions and force movement; placement should encourage using them rather than hoarding them.

Do not add five nearly identical rifles. Add a weapon only when it creates a new tactical decision.

## Shield and armour rhythm

The shield is the primary pacing clock.

- Damage first removes shield.
- Shield collapse should be unmistakable.
- Breaking contact for 5.5 seconds starts regeneration.
- Armour loss persists and makes the field-repair crate meaningful.

A good encounter repeatedly asks: **Can I finish this target before my shield breaks, or should I disengage now?**

## Visual direction

The current teal/amber fortified relay aesthetic is a workable foundation, but the final game should have a stronger proprietary science-fiction identity.

The cyberpunk DLC is potentially useful for:

- antenna machinery and relay internals;
- industrial catwalks, cable runs and power conduits;
- holographic or emissive signage;
- maintenance clutter and believable lived-in infrastructure;
- silhouette-breaking props around the otherwise simple procedural walls.

Use those assets as detail layers, not as an excuse to make every surface noisy. Combat cover and routes must remain readable at a glance.

## Rules for future iteration

1. Tune the first encounter before adding a second level.
2. Every combat arena needs at least two viable movement routes.
3. Never solve difficulty only by increasing enemy health.
4. Prefer role mixtures over raw enemy count.
5. Reinforcements should have an authored reason and readable arrival beat.
6. Recovery time is part of combat; do not keep the player under constant undifferentiated fire.
7. Weapon pickups should foreshadow the problem they are good at solving.
8. Preserve the one-session mission state until save restoration is deliberately implemented.
9. Keep scripts compatible with Lua 5.1 and stock GameGuru MAX behavior APIs.
10. Validate every gameplay change in-engine; headless tests only protect mission logic.

## Next high-value tasks for Codex

After an in-engine test of this combat pass:

1. Collect a short recording of the insertion breach and Northstar fight.
2. Tune enemy accuracy, damage and wake radius from observed time-to-kill and shield pressure.
3. Give the four combat roles visual silhouettes or color accents so behavior can be read before it happens.
4. Add authored reinforcement arrival cues (door, lift, dropship audio, alarm light, or visible gate) instead of relying only on `Show()` for reserves.
5. Replace some procedural cover with cyberpunk DLC props while preserving the tactical layout.
6. Build one bespoke science-fiction enemy archetype that changes the sandbox rather than another rifleman.
7. Improve weapon/audio impact: firing report, hit confirmation, shield-collapse cue and enemy reaction barks.
8. Only then expand Relayfall or start a second mission.

## Success metric

The project is ready to grow when the first 30 seconds can be replayed several times and still produce small variations in movement, threat priority and weapon choice while remaining readable and fair.
