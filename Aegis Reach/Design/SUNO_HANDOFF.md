# AEGIS REACH // SUNO MUSIC HANDOFF

## Why separate cues

Aegis Reach now exposes a runtime `aegis.music_state` from the MAX world controller. That lets music follow exploration, combat, AEGIS interference, discovery, and resolution instead of behaving like one long background track.

For the first useful music upload, generate **separate cues** rather than one continuous score.

## Requested first batch

### 1. `vesper_exploration`

Purpose: the player first sees the old sea floor and understands how remote Vesper is.

Target feeling:
- isolation without horror;
- enormous landscape;
- restrained wonder;
- old human work layered over something much older.

Musical language:
- processed cello or low bowed texture;
- distant metallic resonance;
- sparse analog pulse;
- very light wordless breath/choir texture only if it feels human, not religious;
- no giant trailer drums.

Length: 2–4 minutes.

Should be able to loop without a huge ending cadence.

### 2. `warden_pressure`

Purpose: standard combat state.

Target feeling:
- forward motion;
- tactical urgency;
- confidence rather than panic;
- enough rhythmic identity to make the rifle/shotgun loop feel physical.

Musical language:
- industrial percussion;
- short low string figures;
- analog pulse derived from the exploration cue;
- avoid nonstop maximal intensity.

Length: 2–3 minutes.

### 3. `choir_discovery`

Purpose: short discovery cue when the player finds `RESONANCE CUT 03` or later Choir evidence.

Target feeling:
- recognition before explanation;
- beautiful but wrong;
- a physical resonance rather than “alien magic.”

Musical language:
- glass/crystalline overtones;
- bowed metal;
- subharmonic drone;
- one simple melodic cell that can later reappear in a larger form.

Length: 30–60 seconds.

No percussion required.

### 4. `aegis_resolution`

Purpose: AEGIS capture / power reversal / return toward extraction.

Target feeling:
- systems coming alive;
- earned momentum;
- emotional lift without becoming a superhero anthem.

Musical language:
- return of the exploration motif in clearer harmony;
- stronger pulse;
- warmer midrange;
- restrained industrial rhythm.

Length: 1–2 minutes.

## Optional fifth cue

### `meridian_memory`

Purpose: Mira's wreck, Shelter 12, or other human-history discovery.

This should be intimate rather than mysterious: the emotional reminder that survey crews lived and worked here before the fighting.

Length: 30–90 seconds.

## File delivery

Best upload format:

- WAV if available;
- 48 kHz preferred, 44.1 kHz acceptable;
- stereo;
- no extreme loudness limiting;
- leave a little headroom;
- one cue per file;
- upload the files directly to ChatGPT and identify which cue each one is.

Do not worry about final GameGuru filenames. Once the audio is uploaded, the integration pass can normalize names, convert if needed, place the files under `Files/audiobank/aegis_reach/music/`, and wire them to the runtime states.

## Current runtime state names

The world controller currently emits these state labels:

- `exploration_vesper`
- `exploration_fortress`
- `combat`
- `combat_interference`
- `combat_overcharge`
- `tension_aegis`
- `resolution_aegis`
- `discovery_human`
- `discovery_choir`

The first music integration does not need a unique track for every label. We can map several states to the same cue and layer/transition more aggressively later.

## Score rule

The score should reveal the same world the environment does.

Vesper = space and weight.
Meridian = human warmth and fragility.
AEGIS = machinery and control.
The Choir = resonance and impossible regularity.

If a cue could be dropped into any generic sci-fi shooter unchanged, it needs another pass.
