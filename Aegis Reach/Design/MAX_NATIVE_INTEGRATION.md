# Aegis Reach // GameGuru MAX native integration

Aegis Reach should remain a GameGuru MAX project that can be understood and extended from the editor. Custom Lua owns systemic rules; MAX Visual Logic and DLC entities own authored presentation/set-piece relationships.

## Native APIs now used directly

These are taken from the shipped GameGuru MAX scripts already present in this project, including `effects/ambience.lua`, `effects/emission_control.lua`, `effects/event_manager.lua`, and `objects/add_fx.lua`.

- `SetActivated`
- `PerformLogicConnections`
- `PerformLogicConnectionNumber`
- `ActivateIfUsed`
- `SetEntityEmissiveColor`
- `SetEntityEmissiveStrength`
- `GetAmbienceRed / Green / Blue`
- `SetAmbienceRed / Green / Blue`
- `GetExposure / SetExposure`
- `Hide / Show`
- `CollisionOff / CollisionOn`
- `SetPosition / Rotate*`
- `GetGroundHeight`

The rule is: if MAX already exposes a good runtime system, use it before creating a parallel framework.

## Stable gameplay -> editor event endpoints

### Relay terminals

`aegis_relay.lua` now:

1. communicates relay state through emissive color/intensity;
2. charges visually while the player holds E;
3. flips to cyan when captured;
4. calls `PerformLogicConnections(e)` and `ActivateIfUsed(e)` once capture completes.

This lets any relay drive editor-authored downstream actions without hard-coded entity IDs.

Good connections:

- CineGuru insert shot;
- Offworld/Cyber animated door;
- warning lights -> friendly cyan lights;
- particle burst / sparks;
- machinery animation;
- hologram / sign change;
- localized audio sting;
- delayed event manager sequence.

### Environmental story props

`aegis_story.lua` fires one Visual Logic/IfUsed event after its quiet proximity reaction.

Good connections:

- short CineGuru detail insert;
- directional field recording;
- holographic survey trace;
- dormant equipment waking briefly;
- optional subtitle / image trigger.

Do not turn every prop into an exposition terminal.

### World-state controller

`aegis_world.lua` is a hidden Always Active controller injected by `tools/native_integration_pass.py`.

It owns presentation state rather than combat state:

- Vesper exterior grade;
- fortress grade;
- AEGIS interference grade;
- captured AEGIS overcharge grade;
- first arrival on the brine shelf.

On state changes it fires MAX logic outputs, so editor-authored set pieces can react to the world state.

### Horizon beacons

`aegis_beacon.lua` gives existing environment beacons mission-reactive emissive behavior:

- standard: slow cyan breathing;
- AEGIS interference: unstable amber flicker;
- captured uplink: stronger clean cyan pulse.

Each mission-phase change also emits a Visual Logic event.

## DLC usage doctrine

The user's installed DLC is part of the production palette. Do not merely scatter pack assets around the map.

### CineGuru MAX

Use for short spatial/story payoffs connected to gameplay events. Prefer 5-12 second sequences and preserve skip/control flow.

### Cyber / future-world packs

Use for:

- emissive machinery;
- holo displays;
- cable/service infrastructure;
- industrial signage;
- animated doors;
- distant installation silhouettes;
- authored props that can visibly change state.

Avoid generic neon clutter.

### Sci-fi/offworld architecture packs

Use to selectively replace greybox shell pieces after sightlines and collision are proven. Keep encounter geometry readable and rebuild around the existing tactical purpose rather than around whatever model looks coolest in the browser.

### Effects / particles

Use for state communication:

- relay wake-up;
- AEGIS interference;
- vent plumes;
- distant orbital failures;
- reserve entry;
- shield break accents;
- extraction ignition.

Particles never get to obscure enemies just to look expensive.

## Production pipeline order

`python tools\max_playtest.py deploy --production`

applies:

1. local ecosystem scan;
2. original skyline/environment pass;
3. Vesper brine-shelf world pass;
4. sparse environmental-story bindings;
5. optional shelf recon encounter;
6. MAX-native event/presentation bindings;
7. generated story art;
8. CineGuru presentation assets;
9. visual/lighting polish;
10. validated copy into MAX.

## Design rule

**Lua describes the systemic truth. Visual Logic stages the authored consequence.**

Examples:

- Lua decides that NORTHSTAR is captured; Visual Logic decides which doors/lights/camera/audio sequence responds.
- Lua decides the player crossed onto Vesper's shelf; Visual Logic can stage a distant vent eruption or camera event.
- Lua decides AEGIS is hostile/captured; MAX emissive/ambience systems visibly transform the same space.

This keeps Aegis Reach both programmable and editable.
