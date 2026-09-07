# AEGIS REACH // ADAPTIVE SCORE SYSTEM

## Supplied cue set

The first three Suno masters form a usable score vocabulary rather than one looping background track.

| Cue | Master length | Primary role | Runtime slot |
| --- | ---: | --- | ---: |
| **Salt Moon Drift** | 179.640 s | Vesper exterior, quiet human discovery | Sound0 |
| **Moon Outpost Drift** | 142.608 s | fortress traversal, normal combat pressure, AEGIS resolution | Sound1 |
| **Orbital Catacomb** | 154.512 s | AEGIS interference, Choir discovery, deep interior | Sound2 |

All supplied masters are stereo 48 kHz / 16-bit PCM WAV.

### Why these mappings

**Salt Moon Drift** has the broadest gradual rise in energy across its runtime. It is the landscape cue: the score can begin comparatively open and accumulate weight as the player moves farther onto Vesper.

**Moon Outpost Drift** carries the strongest sustained energy of the three and therefore does the most work during occupied-fortress traversal and the current provisional combat state. It is not intended to become permanent battle music; a dedicated Warden pressure cue can replace that mapping later without changing the music-state API.

**Orbital Catacomb** has more dramatic interior/revelation weight. It belongs around the active AEGIS field, Choir evidence, and future subterranean/orbital spaces rather than routine rifle fights.

## Runtime architecture

`aegis_world.lua` describes semantic score states:

- `exploration_vesper`
- `exploration_fortress`
- `combat`
- `combat_interference`
- `combat_overcharge`
- `tension_aegis`
- `resolution_aegis`
- `discovery_human`
- `discovery_choir`

`aegis_music.lua` translates those states into one of the three actual Sound slots and target volumes.

The music entity is injected by `tools/native_integration_pass.py` as:

`NATIVE // ADAPTIVE MUSIC`

with:

- Sound0 -> `aegis_reach\music\salt_moon_drift.wav`
- Sound1 -> `aegis_reach\music\moon_outpost_drift.wav`
- Sound2 -> `aegis_reach\music\orbital_catacomb.wav`

The controller uses GameGuru MAX-native `LoopNon3DSound`, `StopSound`, `SetSound`, and `SetSoundVolume`. The implementation crossfades over roughly two seconds rather than hard-cutting on every state change, and ordinary state changes are debounced so a short combat lull does not restart the score.

Discovery states are intentionally immediate.

## Mix rule

Music is deliberately capped well below MAX volume 100:

- quiet exploration ~46-48;
- discoveries ~54-58;
- standard pressure ~64;
- overcharge peak ~68.

Weapons, Kestrel dialogue, shield feedback, wind, machinery, and environmental sound must remain intelligible. The score is part of the world, not a blanket over it.

## Source-master workflow

Large WAV attachments are staged locally with:

```bat
python tools\import_music.py --strict
```

The importer searches the repo, current directory, Downloads, Desktop, Music, and common OneDrive equivalents. It recognizes the supplied Suno filenames, copies them to canonical GameGuru paths, records WAV metadata, and verifies the exact uploaded revisions by SHA-256 when available.

Production deployment also runs this importer automatically in non-strict mode:

```bat
python tools\max_playtest.py deploy --production
```

If one of the masters is missing, deployment continues but prints exactly which cue must be supplied.

## Future score expansion

The next highest-value cue is a dedicated **Warden pressure** track. When it arrives, standard `combat` should move off Moon Outpost Drift, leaving that piece more space to represent occupied human infrastructure and the post-AEGIS power reversal.

After that, consider short one-shot stings rather than additional long tracks:

- relay restoration;
- first sight of Aurelia;
- first entrance into true Choir architecture;
- Kestrel extraction arrival;
- mission-complete release.

The goal is thematic recurrence, not a huge playlist.
