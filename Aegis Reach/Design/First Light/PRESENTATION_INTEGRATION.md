# First Light: integrated presentation pass

Baseline: remote main `34dbebe` (September 13). This pass preserves the counterpart's
CineGuru, M-17 wreck, Kestrel and alien biosphere work. It does not replace the
approved orbital sky, mission objectives, encounter starts, terrain or Camp 12.

## Player-facing corrections

- Dialogue now loads in native Lua 5.2. The previous `until` field was a syntax
  error that static source-contract tests did not catch.
- One authoring catalog owns subtitle text, dialogue export and cinematic timing.
  Every shot leaves room for its complete lines and a short breath between them.
  The opening is about 25 seconds and Space skips the entire insertion sequence.
- Captions wrap without deleting the ends of sentences. Optional voice playback
  stops the previous voice before starting another. Zone observations wait behind
  story/record text. Missing cameras still deliver the shelter warning.
- The M-17 recorder explicitly identifies filters, medical packs and security
  ammunition. It remains an optional discovery and does not advance objectives.
- Kestrel has closed nose/aft ends, wing edges, an aft rescue hatch and step,
  Vanguard identification, higher-resolution surface detail and coordinated normal
  and material maps. Its landed low point meets the pad. Liftoff waits for the
  boarding camera, with flight duration following the actual shot duration.
- Skitters hold their current position while grazing, resume without snapping
  home, and sample native ground while moving across slopes.
- M-17's rotated detached engine, panels and cargo find contact using their whole
  transformed mesh. They are no longer placed solely by their central origin.

## Verification

Preflight now compiles every First Light Lua file in Lua 5.2 and executes dialogue,
cinematic activation/skip/fallback, Kestrel boarding departure, and a full skitter
move/pause/resume cycle. Ground-contact checks evaluate the rotated debris vertices.
The tests establish runtime and geometry contracts, not native artistic acceptance.

The incoming main contained authoring sources without several regenerated original
assets. The canonical map and active original assets are rebuilt together for this
candidate. Installed MAX/CineGuru dependencies remain referenced as already configured;
no new licensed payloads, compiled DBOs, saves or editor/testmap state are included.

## Native review and remaining work

Start a new game. Watch ARRIVAL and ARRIVAL_HANDOFF once, then restart and test
Space skip. Check caption pacing and clean restoration of the weapon/HUD. At the
M-17 wreck, circle the loose panels and listen near the damaged engine. Read the
recorder. Observe a skitter until it pauses, especially on sloping ground. Complete
the mission and check Kestrel's pad contact and boarding/liftoff transition.

There are currently **zero recorded dialogue WAVs bound**. Text and the Suno music
work without them; the authored voice export is ready for a later recording pass.
Native camera framing, collision feel, effects density and material response still
need MAX review. Further visual work should use those views before adding content.
