# Aegis Reach // GameGuru MAX Ecosystem Strategy

Relayfall should use GameGuru MAX as an integrated production ecosystem rather than treating it as a renderer for custom Lua.

## Engine-native strengths to exploit

- **Visual Logic:** use it for authored relationships that are easier to inspect than hard-coded entity IDs: cinematic triggers, doors, alarms, lights, objective reveals, set-piece activation, and level handoffs.
- **Lua behaviours:** keep systemic combat, mission state, telemetry, enemy-role logic, shield rules, and reusable gameplay systems in Lua.
- **Storyboard:** use it for actual game flow: title/loading, Relayfall, future levels, game-over, and end-state presentation rather than a single loose map.
- **PBR + emissive materials:** reserve bright emissive color for navigation, active machinery, AEGIS technology, and hostile/neutral state communication.
- **Particles and environmental FX:** add sparks, smoke, steam, debris, energy discharge, and controlled weather where they strengthen landmarks or communicate state. Never obscure threat silhouettes just for atmosphere.
- **Object Library / grouping:** turn repeated authored structures (relay crown + machinery + lights + cover language) into reusable groups so later levels inherit a coherent visual vocabulary.
- **Character Creator / AI behaviours:** use stock systems where they are solid; custom Lua should add tactical identity instead of replacing the entire MAX AI stack.
- **Modular HUD:** keep the cyan/amber Aegis tactical language and borrow only useful frames/icons/reticle ideas from installed future HUD packs.

## DLC roles

The repository never redistributes licensed DLC. `tools/ecosystem_scan.py` inventories the local MAX installation and writes `Design/gameguru-ecosystem.json` so authored passes can bind to assets the user actually owns.

### Offworld Station / Offworld Bunker

Best use: primary military-science-fiction architecture.

- corridors and rooms
- animated doors
- relay machinery
- AEGIS-core infrastructure
- storage/service areas
- emissive panels and holographic systems

Use these assets to replace proof-of-concept geometry selectively while preserving the current encounter lanes and sightlines.

### Cyber City Streets

Best use: future-world identity, not literal city streets inside the fortress.

- animated holographic advertising repurposed as tactical/industrial displays
- background buildings for distant settlement/installation silhouette
- street lights and signs as service-infrastructure pieces
- modular facades for exterior support structures

Avoid dense neon clutter. Aegis Reach is military science fiction, not a nightclub.

### CineGuru MAX

Best use: short, purposeful authored sequences.

- cold open / location reveal
- relay activation inserts
- AEGIS-core seizure payoff
- extraction reversal
- future level transitions

Prefer 5–15 second sequences that establish space, stakes, or a changed combat rule, then return control quickly.

### Future characters / robotic creatures

Best use: build one enemy archetype that changes the tactical question.

Priority prototypes:

1. **Aegis Warden / shield-support unit** — creates a protected local formation that must be flanked or disrupted.
2. **Relay drone** — mobile harassment / spotting role that forces the player to look vertically and move.
3. **Area-denial unit** — controls a lane temporarily, creating movement rather than simply increasing enemy health.

### Particles / VFX

Best use: state communication and impact.

- shield break flash
- AEGIS interference arcs
- relay wake-up sparks
- reserve-entry dust/debris
- orbital-strike horizon event
- extraction pad ignition

### Future HUD packs

Use only as a source of components and vocabulary. Preserve Aegis Reach's existing readable HUD hierarchy rather than replacing it wholesale.

## Vertical-slice quality gates

A change earns its place only if it improves at least one of:

1. **Threat read** — can the player identify danger quickly?
2. **Route read** — can the player understand useful movement options?
3. **Landmark memory** — can the player describe where they are after one pass?
4. **Combat decision** — does the sandbox ask a different question?
5. **World scale** — does Relayfall feel like part of a larger conflict?
6. **Presentation** — does the game communicate intention rather than feeling like an editor test map?

## Next production sequence

1. Run `python tools\max_playtest.py deploy --production`.
2. Review `Design/gameguru-ecosystem.json` for installed DLC candidates.
3. Run `python tools\cineguru_bootstrap.py` and use the discovery report to bind the cold open.
4. Playtest the full Relayfall route, not only insertion.
5. Use telemetry to tune combat only after the environment is readable.
6. Selectively replace proof-of-concept architecture with local Offworld/Cyber assets while preserving battle geometry.
7. Add one sci-fi enemy archetype before adding more enemy count.
8. Add AEGIS-core and extraction cinematic payoffs once the cold open is stable.

The creative target is not to reproduce Halo's assets or lore. It is to recover the discipline that made classic combat sandboxes memorable: immediate readability, strong landmarks, meaningful weapon/enemy roles, moments of quiet between pressure spikes, and a world that feels much larger than the current room.
