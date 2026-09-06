# Aegis Reach: Relayfall

An original single-player sci-fi infantry mission for GameGuru MAX.

You are **Vanguard Seven**, stranded at a colony defense outpost occupied by the **Iron Wardens**. Restore **Northstar**, **Lantern**, and the **Aegis core**, cancel an orbital strike, then fight back to **Kestrel's landing zone**.

## Start your playtest

1. **Restart GameGuru MAX and reopen Aegis Reach.** The project was edited on disk while MAX was open. Do not save the old blank storyboard over these files before reopening it. If MAX asks to save that old blank view, choose not to save it.
2. The storyboard should show **RELAYFALL** in place of **Level 1**. Open that level, then use **Normal Single Level** / Test Game. The first load may take longer while MAX converts the original `.x` meshes and builds navigation data.
3. For the title screen and full screen flow, use **Standalone Test All Levels** from the storyboard when available. A distributable standalone executable has not been exported.

If the hub does not pick up the refreshed storyboard, the mission file is:

`Files\mapbank\Aegis Reach - Relayfall.fpm`

Use the project's **Add Existing Level** control to select it. The authoritative storyboard is `Files\projectbank\Aegis Reach\project203.dat`. A copy of the initial blank storyboard is preserved in `Design\initial-project203.dat`.

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

This first prototype runs in one session. Save/load menu controls are omitted because persistent mission-state restoration has not been implemented.

## Combat-loop pass 1

The current branch adds a deliberate combat-pacing layer without changing the map archive:

- Iron Wardens now have deterministic tactical roles: **flanker, anchor, hunter, skirmisher**, plus two reserve jobs: direct **assault** and alerted **shock flank**.
- Standing troops remain visible, but their full combat AI wakes only when the player reaches the appropriate encounter phase and local radius. This keeps Relayfall from becoming one fortress-wide firefight.
- Reserve pairs remain hidden until their authored mission beat. The first pushes directly; the second follows about 1.1 seconds later on a wide route, creating a readable reinforcement pincer instead of simultaneous pop-in.
- The AEGIS core now has a gameplay role. Near the live core during phase 3, its countermeasure field degrades shield recharge. Capturing the core flips the network into a faster recharge mode for extraction.
- The HUD reports close tactical contact, shield collapse, recharge mode, and the hostile/boosted AEGIS field state.
- The runtime audit uses project-relative paths and now records encounter starts/clears, duration, kills, armour loss, shield breaks, and AEGIS signal transitions.

The intended encounter structure is documented in `Design\COMBAT_PILLARS.md`.

### What to watch for in this pass

1. **Insertion:** Wardens 01–02 should be the only immediate combat problem. They should engage naturally as you leave the cyan pad.
2. **Enemy roles:** some soldiers should attempt wider movement, some should hold a position, and some should close distance. Note any role that looks broken or gets stuck on the MAX navmesh.
3. **Encounter boundaries:** later enemies should not begin fighting from across the entire fortress. They should wake as you enter their local space.
4. **Northstar to Lantern:** the blast-wall side gates should provide meaningful flanking routes rather than decorative openings.
5. **Core reserve:** after Lantern, Reserve 01 should enter aggressively and Reserve 02 should follow shortly on a wider line. This should feel like a quick-response pincer, not two actors becoming visible on the same frame.
6. **AEGIS interference:** when you enter the core combat space, the HUD should report `AEGIS FIELD // RECHARGE DEGRADED`. The slower recharge should be noticeable but not make the fight feel hopeless.
7. **Core capture reversal:** after the third override, the HUD should switch to `AEGIS UPLINK // RECHARGE BOOSTED`. The return trip should feel more confident and aggressive without becoming invulnerable.
8. **LZ reserve:** Reserve 03 should pressure directly and Reserve 04 should follow on the wider route. The final fight should be shorter and sharper than the core battle.
9. **Shield rhythm:** shield collapse should be obvious; recharge state should be legible without becoming UI spam.
10. **Pop-in:** ordinary Wardens are never hidden by encounter gating. Only authored reserve troops use `Hide/Show`; note whether their arrival still needs a stronger visual/audio cue.

For balance feedback, the most useful human observations are: weapon used, whether an enemy role looked intelligent or broken, whether a route felt useful, and whether you ever felt forced to stand still and trade damage.

## After the playtest: summarize the run

The director appends balancing events to `Design\native-runtime.log`. From the repository root, run:

```bat
python tools\summarize_playtest.py
```

For machine-readable output that can be pasted back into ChatGPT or Codex:

```bat
python tools\summarize_playtest.py --json
```

The summary reports completed encounters, combat seconds, eliminations, armour loss, shield breaks, phase totals, and AEGIS field transitions. The log is append-only, so if you want one clean session, rename or delete `Design\native-runtime.log` before launching MAX.

## What is included

- Native MAX map with 130 entity placements and 16 enemy soldiers, including staged reserves.
- Nine original modular station assets: deck, bastion wall, infantry cover, supply crate, relay terminal, signal spire, extraction pad, bunker and antenna arc.
- Five original Lua behaviors for the mission, relays, enemies, field repair and extraction.
- Custom title, briefing, loading, pause, victory and defeat presentation; stock ammunition readout plus mission and suit readouts.
- Original title artwork, relay chime and electronic underscore; a locally synthesized radio briefing.
- A tactical map and editable object layout in `Design`.

## Validation and playtest focus

**Completed before the combat-loop pass:** 17 headless mission-logic checks; real MAX soldier-interpreter initialization (493 behavior instructions) under Lua 5.1; original meshes imported through the installed MAX Assimp library; native archive CRC, entity-format roundtrip and referenced-file checks. Details are saved in `Design`.

**Current branch:** the headless harness has been expanded for tactical role configuration, encounter gating, reserve staggering, relay split capture, shield-break telemetry, AEGIS interference, and post-capture recharge boost. These checks still do not substitute for a real engine run.

**Still needs your in-engine playtest:** rendering and lighting, player spawn and collision, NPC navigation and weapon balance, audio levels, role movement, reserve arrival quality, AEGIS recharge feel, and the complete menu-to-win flow. Codex's Windows screenshot capture failed with `SetIsBorderRequired: No such interface supported (0x80004002)`, so these have not been visually verified in GameGuru MAX.

Useful first observations: can you spawn on the cyan pad, see the mission HUD, fire and reload, fight the first two guards, activate Northstar, and reach the other relays? If something fails, note the exact on-screen error and the action just before it. Prefer screenshots or a short gameplay recording for geometry and lighting problems.

## Editing

The map is a native editable `.fpm`. The original behavior scripts are under `Files\scriptbank\aegis_reach`; the original modular assets and atlas are under `Files\entitybank\Aegis Reach`. Build scripts are in the parent workspace's `tools` directory. Running `build_game.py` replaces the generated mission map and original modular meshes, so preserve your later hand edits before rebuilding.

Stock soldiers, weapons, sounds and supporting files were copied from your installed GameGuru MAX for this local project. This is an original scenario, with no Halo characters, maps, music or branding. The supplied title artwork is concept art, not a gameplay screenshot. See `Design\ART.md` for its provenance.
