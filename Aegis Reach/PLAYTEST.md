# Aegis Reach: Relayfall

An original single-player sci-fi infantry mission for GameGuru MAX.

You are **Vanguard Seven**, stranded at a colony defense outpost occupied by the **Iron Wardens**. Restore **Northstar**, **Lantern**, and the **Aegis core**, cancel an orbital strike, then fight back to **Kestrel's landing zone**.

## Recommended playtest workflow

GameGuru MAX expects projects under its own user `Files` area rather than treating the Git checkout as an arbitrary import folder. Keep the Git repository authoritative and deploy the current project into MAX with:

```bat
python tools\max_playtest.py deploy --polish
```

`--polish` applies the current visual-readability pass directly to the Relayfall `.fpm` before copying the authored project files into MAX's user area.

Then:

1. Fully restart GameGuru MAX so scripts and map data reload cleanly.
2. Open **Aegis Reach** from the project list.
3. Open **RELAYFALL**.
4. Use **Normal Single Level** / Test Game for the fastest gameplay iteration.
5. For title/menu flow, use **Standalone Test All Levels** when available.

After the run, collect telemetry back into the repo:

```bat
python tools\max_playtest.py collect
python tools\summarize_playtest.py
```

For machine-readable output:

```bat
python tools\summarize_playtest.py --json
```

The actual mission file is:

`Files\mapbank\Aegis Reach - Relayfall.fpm`

The authoritative storyboard is `Files\projectbank\Aegis Reach\project203.dat`. A copy of the initial blank storyboard is preserved in `Design\initial-project203.dat`.

## Controls and objectives

| Action | Control |
|---|---|
| Move / aim | WASD / mouse |
| Fire / aim down sights | Left / right mouse button |
| Reload / sprint / jump | R / Shift / Space |
| Select weapons | Number keys or mouse wheel |
| Relay override / extraction | Hold E for 3 seconds |
| Field repair | E near the marked repair crate |
| Pause and controls | Escape |

You begin with a compact assault rifle and reserve ammunition. The first combat area contains a shotgun; a later supply cache holds a marksman rifle. Grenades and rifle ammunition are placed along the route.

**Your suit has 100 armour and 100 shield.** Damage drains shield first. In normal sectors, breaking contact for 5.5 seconds starts recharging. Armour needs the single-use field repair crate. The AEGIS core changes that rule: while its countermeasure field is active nearby, recharge is slower and takes longer to begin; after the core is captured, the uplink accelerates shield recovery for the return to Kestrel. Cyan terminals must be activated in order. After overriding the core, return to the cyan insertion pad and clear hostiles within the landing-zone perimeter. Hold E to board, then E again to debrief.

This prototype runs in one session. Save/load menu controls are omitted because persistent mission-state restoration has not been implemented.

## Combat-loop pass 1

The mission currently includes a deliberate combat-pacing layer:

- Iron Wardens have deterministic tactical roles: **flanker, anchor, hunter, skirmisher**, plus two reserve jobs: direct **assault** and alerted **shock flank**.
- Standing troops remain visible, but their full combat AI wakes only when the player reaches the appropriate encounter phase and local radius. This keeps Relayfall from becoming one fortress-wide firefight.
- Reserve pairs remain hidden until their authored mission beat. The first pushes directly; the second follows about 1.1 seconds later on a wide route, creating a readable reinforcement pincer instead of simultaneous pop-in.
- The AEGIS core has a gameplay role. Near the live core during phase 3, its countermeasure field degrades shield recharge. Capturing the core flips the network into a faster recharge mode for extraction.
- The HUD reports close tactical contact, shield collapse, recharge mode, and the hostile/boosted AEGIS field state.
- Runtime telemetry records encounter starts/clears, duration, kills, armour loss, shield breaks, and AEGIS signal transitions.

The intended encounter structure is documented in `Design\COMBAT_PILLARS.md`.

## Visual-readability pass 2

The first real MAX playtest proved that the game systems were running, but also exposed a major presentation failure: the fortress was so dark that playable geometry and enemies frequently collapsed into near-black silhouettes.

Pass 2 treats lighting as combat design rather than decoration.

`tools\polish_relayfall.py` directly patches the playable `.fpm` and:

- restores the built-in `highcloud` sky instead of the previous black void;
- raises stable exposure and ambient fill without using auto-exposure;
- shifts shadow fill toward blue-grey rather than pure black;
- adds warmer directional light to separate hard-surface shapes;
- uses restrained blue atmospheric fog to improve depth and horizon separation;
- reduces bloom so emissives remain crisp instead of washing out the scene;
- enlarges the six existing cyan/amber authored light pools so important lanes and objective areas read at combat distance.

The visual target and guardrails are documented in `Design\VISUAL_DIRECTION.md`.

### Visual quality gate

During the next screenshot/video review, verify:

1. A standing enemy at useful rifle range is visible without zooming into the image.
2. Foreground weapon, cover, enemy silhouette, and background architecture occupy distinguishable value ranges.
3. The sky produces a real horizon and readable structure silhouettes.
4. Main movement lanes are visible even between local light fixtures.
5. Cyan objective/navigation light and amber industrial light guide the eye without turning the fortress into a neon city.
6. Shadows still exist and preserve depth, but they no longer swallow major playable surfaces.

## Combat checks for the next run

1. **Insertion:** Wardens 01–02 should be the only immediate combat problem. They should engage naturally as you leave the cyan pad.
2. **Enemy roles:** some soldiers should attempt wider movement, some should hold a position, and some should close distance. Note any role that looks broken or gets stuck on the MAX navmesh.
3. **Encounter boundaries:** later enemies should not begin fighting from across the entire fortress. They should wake as you enter their local space.
4. **Northstar to Lantern:** the blast-wall side gates should provide meaningful flanking routes rather than decorative openings.
5. **Core reserve:** after Lantern, Reserve 01 should enter aggressively and Reserve 02 should follow shortly on a wider line.
6. **AEGIS interference:** the core combat space should report `AEGIS FIELD // RECHARGE DEGRADED`. The slower recharge should be noticeable but fair.
7. **Core capture reversal:** after the third override, the HUD should switch to `AEGIS UPLINK // RECHARGE BOOSTED` and the return trip should feel more confident.
8. **LZ reserve:** Reserve 03 should pressure directly and Reserve 04 should follow on the wider route.
9. **Shield rhythm:** shield collapse should be obvious; recharge state should be legible without becoming UI spam.
10. **Reserve arrival:** authored reserve `Hide/Show` should eventually receive stronger audiovisual arrival cues if the current pop-in remains noticeable.

For balance feedback, useful human observations are: weapon used, whether an enemy role looked intelligent or broken, whether a route felt useful, whether shield pressure felt fair, and whether you ever felt forced to stand still and trade damage.

## Telemetry

The mission now first attempts to write runtime telemetry to the MAX user Files area as:

`%USERPROFILE%\Documents\GameGuruApps\GameGuruMAX\Files\aegis-native-runtime.log`

with project-relative fallbacks for development runs.

Use:

```bat
python tools\max_playtest.py collect
```

to copy the newest deployed log back to `Design\native-runtime.log` before summarizing it.

The summary reports completed encounters, combat seconds, eliminations, armour loss, shield breaks, phase totals, and AEGIS field transitions. Logs are append-only; archive or remove the deployed log when you want one clean session.

## What is included

- Native MAX map with 130 entity placements and 16 enemy soldiers, including staged reserves.
- Nine original modular station assets: deck, bastion wall, infantry cover, supply crate, relay terminal, signal spire, extraction pad, bunker and antenna arc.
- Five original Lua behaviors for the mission, relays, enemies, field repair and extraction.
- Custom title, briefing, loading, pause, victory and defeat presentation; stock ammunition readout plus mission and suit readouts.
- Original title artwork, relay chime and electronic underscore; a locally synthesized radio briefing.
- A tactical map and editable object layout in `Design`.

## Validation and playtest focus

**Completed before the combat-loop pass:** 17 headless mission-logic checks; real MAX soldier-interpreter initialization (493 behavior instructions) under Lua 5.1; original meshes imported through the installed MAX Assimp library; native archive CRC, entity-format roundtrip and referenced-file checks. Details are saved in `Design`.

**Combat logic:** the headless harness covers tactical role configuration, encounter gating, reserve staggering, relay split capture, shield-break telemetry, AEGIS interference, and post-capture recharge boost. These checks do not substitute for a real engine run.

**Visual pass:** `polish_relayfall.py` validates the rewritten MAX-encrypted archive and round-trips the modified `.ele` entity data before replacing the playable map. Actual appearance must still be judged in-engine.

**Still needs in-engine playtesting:** lighting/readability, NPC navigation and weapon balance, audio levels, role movement, reserve arrival quality, AEGIS recharge feel, and complete menu-to-win flow.

Prefer screenshots or short gameplay recordings for geometry, lighting, combat readability, and AI problems.

## Editing

The map is a native editable `.fpm`. The original behavior scripts are under `Files\scriptbank\aegis_reach`; the original modular assets and atlas are under `Files\entitybank\Aegis Reach`.

`build_game.py` replaces the generated mission map and original modular meshes. After a full rebuild, rerun `polish_relayfall.py` (or deploy with `max_playtest.py deploy --polish`) before testing so the current visual pass is re-applied.

Stock soldiers, weapons, sounds and supporting files were copied from the installed GameGuru MAX environment for this local project. This is an original scenario, with no Halo characters, maps, music or branding. The supplied title artwork is concept art, not a gameplay screenshot. See `Design\ART.md` for its provenance.
