# First Light: Kestrel VO and presentation integration

Baseline: remote main `592822b`, September 14. The Broadwing, CineGuru, M-17,
biosphere, recorded Kestrel VO integration and landed-only boarding collision are
retained. This pass does not alter the orbital sky, terrain, Camp 12, mission
objectives or authored enemy starts.

## Voice and story

The user's original four WAVs are bound as `FL01_KES_001` through `004`.
They remain unmodified mono, 44.1 kHz, 16-bit PCM. Measured lengths are
7.837, 9.038, 8.490 and 11.520 seconds. The remaining 17 lines use text;
no additional voice performances are claimed.

The full catalog matches the user's supplied 21-line transcript and voice
assignments. The M-17 pilot line is preserved exactly. The source is
`tools/firstlight_dialogue.py`; it generates the Lua catalog and export manifest.
Every available WAV contributes its measured duration plus a 150 ms caption tail.
Cinematic cue schedules and shot durations derive from that same catalog.
ARRIVAL is 18.53 s and ARRIVAL_HANDOFF is 25.61 s. No audio is time-stretched.
Replacing a WAV, even with an equal-size file, invalidates the build fingerprint.

The old dialogue script used Lua's reserved word `until` as a field name and
could not load. That is corrected. Complete captions now wrap; previous voice
playback stops on interruption or skip. Space skips both opening shots.
Zone/radio observations wait behind existing story text. Missing cameras still
allow the mission to continue and deliver the shelter warning.

## Broadwing implementation

The supplied Kestrel research informed the functional boarding pass. The incoming
20 m Broadwing airframe and its flight/flare/landed variants remain the basis.
The aft hull now meets an actual cargo aperture instead of leaving holes around
a rectangular door or intersecting the ramp with the belly. A closed bulkhead,
short floor, benches, lights, hinge details and paired actuators create a compact
boarding vestibule. Ramp upper-face winding and recessed engine-core winding
are corrected. Ramp underside and landing feet share the authored contact plane.

Flight, flare and landed are still discrete visual mesh swaps, not a rigged
animation. The moving airframe remains visual-only, but the landed extraction
state has a separate low-poly polygon collision proxy covering only the rear
ramp and vestibule floor. Its controller keeps collision off until
`aegis.kestrel_landed=true`, then clears it again immediately when departure starts.
That makes the visible boarding route physically walkable without leaving an
invisible ship-sized collider on the LZ during approach.

### Flight-dynamics presentation pass

The Kestrel controller now adds deterministic inertial motion around the existing
mission-safe state swaps. Approach paths carry shallow coordinated bank, yaw and
pitch rather than moving a rigid airframe along a position spline. The VTOL phases
use low-amplitude multi-frequency corrections that fade as the ship settles or
commits to cruise. Opening handoff hover remains restrained enough that the craft
continues to read as a heavy powered-lift transport rather than a helicopter.

Extraction now unloads its cruise bank into a deceleration flare, damps powered-lift
corrections through final descent, holds the landed state completely rigid while the
ramp collision is active, then transitions from vertical clearance into a banked,
nose-down accelerating departure. The landed geometry is intentionally excluded
from hover noise so visual ramp, collision proxy and interaction volume cannot drift
apart under the player.

This is a presentation/choreography improvement only. Mission authority, boarding
state, collision lifecycle and the confirmed cinematic clocks are unchanged.

The ship follows the confirmed camera clock. Opening skip removes all insertion
variants. Departure waits for the boarding camera and fits its actual duration.
The ship first holds for boarding, lifts in flare configuration, then accelerates
in flight configuration.

Remaining Kestrel presentation work is true continuous hardware animation between
the discrete meshes, LODs, downwash and state-dependent engine audio. Those should
follow native MAX review rather than being guessed from headless tests. The new
flight dynamics also require native review for perceived mass, camera framing and
motion comfort before their amplitudes are treated as final.

## Other integration corrections

Skitters pause where they are, resume without snapping home, and sample native
terrain while moving. Rotated M-17 engine, panels and cargo use transformed mesh
contact points when placed on terrain instead of assuming an origin at the feet.
The counterpart's wreck geometry, four collision cores and effects are preserved.

## Verification and handoff

Preflight compiles every First Light script in actual Lua 5.2. Runtime tests drive
caption expiry, voice interruption, camera activation/skip/fallback, Kestrel state
selection/departure, landed-only boarding collision and a full skitter movement
cycle. Geometry checks cover the open boarding sightline, ramp winding, ramp
collision slope, contact plane and rotated wreck debris. The map and all active
original generated assets are rebuilt as one candidate. No new DLC payloads, DBO
caches, savegames or testmap/editor state are included.

Start a NEW GAME. Watch both opening shots, then test Space skip on a fresh run.
Listen for all four complete spoken lines with matching captions. Circle M-17 and
read its recorder. Observe a skitter pause. Finish the mission and inspect the
landed ramp, walk from the terrain into the vestibule, then board and watch
departure. Confirm that no invisible ramp collision is present before the ship lands
or after liftoff starts. During both Kestrel approaches, specifically watch whether
the banking reads as inertia rather than camera-relative wobble and whether the VTOL
corrections feel heavy at the existing shot distance. Native MAX appearance, sound
balance, performance and collision feel remain the final acceptance gate.

Native review attempt: MAX launched the registered candidate on September 13.
The Computer Use capture API failed twice after fresh window selection with
`SetIsBorderRequired failed: No such interface supported (0x80004002)`.
No native screenshot or audiovisual approval is claimed. The automated source and
runtime contracts are ready for the next player review.