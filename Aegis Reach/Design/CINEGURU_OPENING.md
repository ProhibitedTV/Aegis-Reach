# CineGuru sequence: RELAYFALL // COLD OPEN

## Why this exists

Relayfall currently starts as a playable prototype. This sequence turns the first ten seconds into a game opening: establish the world, show the objective space, reveal the immediate threat, then hand the same heading back to the player.

The sequence is intentionally short. It should make the world feel larger without delaying the 30-seconds-of-fun combat loop.

## Required CineGuru pieces

Run from the repository root:

```bat
python tools\cineguru_bootstrap.py
```

This scans the user's licensed GameGuru MAX install for CineGuru camera / trigger entities and scripts. It writes:

- `Design\cineguru-discovery.json`
- `Design\cineguru-shotlist.json`
- `Files\imagebank\aegis_reach\cine\relayfall_location_card.png`
- `Files\imagebank\aegis_reach\cine\relayfall_warning_card.png`

CineGuru itself is not copied into this repository.

## Trigger

Place a **Cine-trigger zone** over the insertion spawn.

- position: `X 0 / Y 645 / Z -2700`
- Dtime: `0.100`
- Enable Skip: `ON`
- Disable If Combat: `OFF`

Connect the trigger zone to camera `CG_INTRO_01_DEAD_ORBIT` in MAX Visual Logic.

## Camera chain

### CG_INTRO_01_DEAD_ORBIT

**Purpose:** world-scale reveal.

- position: `X -1500 / Y 1750 / Z -3380`
- target: fortress centre / broken orbital spine / Aurelia
- Filmtime: `3.4`
- Fade: `1.2`
- Fls: `108`
- Fle: `84`

Start almost black. Let the outpost, Aurelia, and broken defense structure emerge during the fade.

Trigger the location card during this shot:

`imagebank\aegis_reach\cine\relayfall_location_card.png`

Composition rule: Aurelia should occupy part of the sky but never dominate the frame. The broken orbital spine is the sharper silhouette. The fortress is the subject.

### CG_INTRO_02_INSERTION

**Purpose:** translate the huge establishing view into the player's physical space.

- position: `X 760 / Y 980 / Z -3180`
- target: `X 0 / Y 760 / Z -2050`
- Filmtime: `2.7`
- Fade: `0`
- Fls: `82`
- Fle: `72`

Use a simple moving camera or a short nodal path if desired. Move forward and slightly down under the insertion service gantry. The shot should visually explain where the player will run next.

### CG_INTRO_03_WARDENS

**Purpose:** establish the opening combat problem before control returns.

- position: `X -1220 / Y 880 / Z -2370`
- target: first Warden near `X -800 / Z -2130`
- Filmtime: `2.4`
- Fade: `0`
- Fls: `76`
- Fle: `60`

Do not present the Wardens as boss characters. The shot says: *this space is occupied and you need to break their line.*

Optional image trigger:

`imagebank\aegis_reach\cine\relayfall_warning_card.png`

### CG_INTRO_04_HANDOFF

**Purpose:** cut back toward the player's actual combat heading so control feels continuous.

- position: `X 0 / Y 790 / Z -2870`
- target: `X 0 / Y 760 / Z -1650`
- Filmtime: `2.5`
- Fade: `0.25`
- Fls: `72`
- Fle: `72`

End as close as practical to the first-person view direction. The transition should feel like the cinematic camera simply became the player's eyes.

## Visual Logic

Connect the sequence:

```text
Cine-trigger zone
    -> CG_INTRO_01_DEAD_ORBIT
    -> CG_INTRO_02_INSERTION
    -> CG_INTRO_03_WARDENS
    -> CG_INTRO_04_HANDOFF
```

If image or sound trigger entities are used, connect them from the relevant active camera rather than creating separate gameplay triggers.

## Audio / subtitles

Existing mission assets are suitable for the first cut:

- `audiobank\aegis_reach\reach-underscore.wav`
- `audiobank\aegis_reach\briefing.wav`

Suggested subtitle timing:

1. **KESTREL:** `Vanguard Seven, Reach is dark.`
2. **KESTREL:** `Three relays stand between us and an orbital strike.`
3. **KESTREL:** `Wake Northstar. Wake Lantern. Then take AEGIS away from them.`

Keep the language terse. Do not explain the entire setting in the opening.

## Direction rules

- Total opening cinematic target: **10–12 seconds**.
- Skip must be enabled.
- No camera should hide the player's immediate route.
- Never begin combat while the player is trapped in the cinematic.
- Do not use excessive shake. Save impact shake for explosions, heavy weapons, or the orbital-defense system.
- Cutscenes should reveal tactical information whenever possible.
- Favor wide-to-medium compositions over face closeups until Aegis Reach has bespoke character art worth featuring.

## Later CineGuru beats

Once this cold open is proven in-engine, the next two cinematics should be:

### AEGIS CORE SEIZURE

A 5–7 second in-engine sequence after the third relay completes:

- core machinery wakes;
- lights flip from hostile amber to cyan;
- camera looks upward to the orbital spine;
- distant defense energy / sky event implies the strike solution changing;
- control returns immediately into the extraction run.

### KESTREL EXTRACTION

A 7–10 second mission-ending sequence:

- final reserve collapses;
- extraction gantry and pad lights come alive;
- camera rises over the outpost;
- orbital debris / Aurelia frame the victory image;
- transition to mission results.

These should be authored as rewards for gameplay, not interruptions to it.
