AEGIS REACH // ADAPTIVE SCORE RUNTIME FILES

Expected local masters:

salt_moon_drift.wav
  Sound0
  states: exploration_vesper, discovery_human

moon_outpost_drift.wav
  Sound1
  states: exploration_fortress, combat, combat_overcharge, resolution_aegis

orbital_catacomb.wav
  Sound2
  states: tension_aegis, combat_interference, discovery_choir

Stage the user's supplied 48 kHz stereo WAV masters with:

  python tools\import_music.py --strict

Production deploy also stages them automatically when the source files are present in
common Downloads/Desktop/Music locations.
