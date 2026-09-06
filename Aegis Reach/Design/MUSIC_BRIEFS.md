# AEGIS REACH // MUSIC BRIEFS

These briefs are written so Jeremy can use Suno or another composition workflow to generate stems/cues that support the game's pacing rather than wallpapering every scene.

The musical identity should avoid imitating Halo melodies or instrumentation directly. The inspiration to preserve is **space, restraint, memorable motif, and strong contrast between solitude and combat**.

## Core palette

Use a limited recurring palette so the score feels authored:

- low bowed metal / processed cello texture;
- distant mixed choir used as atmosphere, not heroic anthem;
- glassy FM/synthetic bell tones associated with Vesper/the Choir;
- restrained analog synth pulse;
- deep tom / frame-drum / industrial percussion for combat;
- distorted radio/noise beds for occupied AEGIS systems;
- one simple 4–6 note melodic cell that can survive in ambient, combat, and emotional arrangements.

Avoid:
- nonstop trailer braams;
- generic cyberpunk arpeggios;
- wall-to-wall percussion;
- fake "epic choir" in every cue;
- obvious Halo-style Gregorian imitation.

## 01 — VESPER // OPEN SHELF

**Use:** player spawn / quiet exterior traversal before first combat.

**Length:** 2:30–4:00 loopable.

**Emotion:** remote, cold, enormous, beautiful, slightly mournful.

**Structure:**
- 0:00–0:30 almost no pulse; windlike tonal bed + sparse bell motif;
- 0:30–1:30 low harmonic motion appears as Aurelia/fortress enter view;
- 1:30 onward subtle pulse but never full combat energy.

**Suno prompt seed:**

> cinematic ambient science fiction score for a lonely moon orbiting a gas giant, sparse processed cello, distant wordless choir texture, crystalline synthetic bells, huge negative space, cold mineral landscape, subtle emotional melancholy, slow evolving harmony, no heroic fanfare, no EDM beat, immersive game soundtrack, loop-friendly

## 02 — RELAYFALL // FIRST CONTACT

**Use:** opening Warden fight / general low-intensity combat layer.

**Length:** 1:30–2:30 loopable.

**Emotion:** precise, dangerous, mobile—not apocalyptic.

**Structure:**
- restrained 90–105 BPM pulse;
- syncopated low drums and metallic impacts;
- motif appears in short fragments;
- leave room for weapon audio.

**Suno prompt seed:**

> tactical military science fiction combat score, restrained industrial percussion, low synth pulse, processed cello ostinato, short crystalline motif fragments, tense but controlled, 100 BPM, designed to sit under gunfire, no giant trailer drums, no EDM drop, dynamic game combat loop

## 03 — NORTHSTAR RESTORED

**Use:** 4–8 second relay activation sting.

**Length:** short sting.

**Emotion:** relief + forward momentum.

**Sound:**
- one clean rising harmonic gesture;
- cyan system tone integrated into music;
- motif resolves upward but not fully.

## 04 — LANTERN // GEOTHERMAL YARD

**Use:** Lantern area exploration/combat transition.

**Length:** 2:00–3:00.

**Emotion:** warmer, mechanical, human.

Use rhythmic steam-like breath, low machinery resonance, and a more tactile percussion palette. This area should remind the player that people lived and worked here.

## 05 — THE CHOIR BENEATH

**Use:** first discovery of clearly impossible subsurface resonance.

**Length:** 45–75 seconds non-looping.

**Emotion:** awe before fear.

**Rule:** do not telegraph "evil alien thing." The first response should be curiosity.

**Suno prompt seed:**

> mysterious science fiction discovery cue, resonant glass tones, subharmonic drones, slowly aligning harmonic overtones, almost geological rhythm, no percussion for first half, awe and intellectual curiosity before unease, intimate but vast, strange acoustic resonance, cinematic game score

## 06 — AEGIS CORE // INTERFERENCE

**Use:** core fight while shield recharge is degraded.

**Length:** 2:00–3:00 loopable.

**Emotion:** pressure, system instability.

Add rhythmic interruptions/dropouts that feel like the music itself is being interfered with. Avoid random glitch spam; the interruptions should land musically.

## 07 — AEGIS FLIPS

**Use:** core capture / defense network changes allegiance.

**Length:** 20–35 seconds.

**Emotion:** earned power reversal.

This is the first time the main motif should arrive confidently in a full register.

## 08 — KESTREL RUN

**Use:** extraction return.

**Length:** 1:30–2:30.

**Emotion:** momentum, competence, release.

Faster pulse than the opening combat cue but cleaner harmony. The player should feel stronger because the world state changed, not because the score became bombastic.

## 09 — MIRA SEN // FIELD TRACE

**Use:** optional environmental-story discoveries.

**Length:** 30–60 second modular fragments.

**Emotion:** human absence.

Use one intimate acoustic/electroacoustic element that never appears in combat—soft piano preparation, bowed glass, or close-mic metal resonance. It should make abandoned survey spaces feel personal without sentimental dialogue.

## Implementation notes

Whenever possible export:
- full mix WAV;
- percussion stem;
- tonal stem;
- texture/choir stem;
- short sting variants.

That lets us use GameGuru/CineGuru/Visual Logic to change musical density by game state instead of hard-cutting between unrelated songs.

Keep loop tails clean. Leave 3–6 dB of headroom because MAX weapon audio can get dense.
