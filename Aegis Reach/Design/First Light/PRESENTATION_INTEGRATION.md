# First Light: Kestrel VO and presentation integration

Baseline for this continuation: remote main `24cfe622`, September 14. The Broadwing,
CineGuru, M-17, biosphere, recorded Kestrel VO integration, landed-only boarding
collision and inertial flight-dynamics pass are retained. This pass does not alter
the orbital sky, terrain, Camp 12, mission objectives or authored enemy starts.

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
20 m Broadwing airframe now has four authored hardware silhouettes: clean flight,
conversion, full VTOL flare and landed/ramp-open. The aft hull meets an actual cargo
aperture instead of leaving holes around a rectangular door or intersecting the ramp
with the belly. A closed bulkhead, short floor, benches, lights, hinge details and
paired actuators create a compact boarding vestibule. Ramp upper-face winding and
recessed engine-core winding are corrected. Ramp underside and landing feet share
the authored contact plane.

The landed extraction state has a separate low-poly polygon collision proxy covering
only the rear ramp and vestibule floor. Its controller keeps collision off until
`aegis.kestrel_landed=true`, then clears it again immediately when departure starts.
That makes the visible boarding route physically walkable without leaving an
invisible ship-sized collider on the LZ during approach.

### Mechanical conversion pass

The previous flight-to-flare swap skipped directly from a clean cruise silhouette to
fully open lift doors and fully deployed landing gear. The procedural asset author now
builds an intermediate `convert` mesh for both insertion and extraction. In that state,
the four lift-bay split doors are only part-way open, recessed lift throats are visible
without established downward plumes, the gear doors are splayed, and the four-point
landing gear is only partially extended. Cruise thrust remains present through the
conversion state, so the propulsion read transitions before the full powered-lift
flare takes over.

The runtime controller now stages all eight visual entities as
flight -> convert -> flare -> landed on arrival, and reverses that hardware sequence
on departure. The opening insertion uses the same conversion silhouette during the
last portion of its approach and again while leaving the handoff hover. Extraction
enters conversion before the full flare, then completes the final mostly vertical
settle on the flare mesh. Departure first gains vertical clearance on full lift,
retracts through the conversion state above the LZ, and only then commits to the
clean flight configuration.

This remains a deliberately stepped mesh-state solution, not a claim of skeletal or
rigged continuous animation. It materially reduces the single large hardware pop while
staying inside the existing deterministic MAX-safe pipeline and preserving the landed
ramp/collision contract.

### Flight-dynamics presentation pass

The Kestrel controller adds deterministic inertial motion around the mission-safe
state swaps. Approach paths carry shallow coordinated bank, yaw and pitch rather than
moving a rigid airframe along a position spline. The VTOL phases use low-amplitude
multi-frequency corrections that fade as the ship settles or commits to cruise.
Opening handoff hover remains restrained enough that the craft continues to read as
a heavy powered-lift transport rather than a helicopter.

Extraction unloads its cruise bank into conversion and deceleration flare, damps
powered-lift corrections through final descent, holds the landed state completely
rigid while the ramp collision is active, then transitions from vertical clearance
through hardware retraction into a banked, nose-down accelerating departure. The
landed geometry is intentionally excluded from hover noise so visual ramp, collision
proxy and interaction volume cannot drift apart under the player.

Mission authority, boarding state, collision lifecycle and confirmed cinematic clocks
remain unchanged. Opening skip removes all insertion variants. Departure still waits
for the boarding camera and fits its actual duration.

Remaining Kestrel presentation work is true continuous rigged hardware animation,
LODs, downwash and state-dependent engine audio. Those should follow native MAX review
rather than being guessed from headless tests. The conversion timings and flight
dynamics also require native review for perceived mass, camera framing and motion
comfort before their amplitudes are treated as final.

## Other integration corrections

Skitters pause where they are, resume without snapping home, and sample native terrain
while moving. Rotated M-17 engine, panels and cargo use transformed mesh contact points
when placed on terrain instead of assuming an origin at the feet. The counterpart's
wreck geometry, four collision cores and effects are preserved.

## Verification and handoff

Preflight compiles every First Light script in actual Lua 5.2 when run in the repo's
normal build environment. The story-delivery regression now constructs all four
Broadwing mesh states, rejects degenerate faces, confirms the conversion hardware does
not reach the landed contact plane early, and drives the real Kestrel Lua through the
eight-entity flight -> convert -> flare -> landed -> flare -> convert -> flight
lifecycle. The landed-only boarding collision remains governed by the existing
separate regression and preflight checks.

Start a NEW GAME. Watch both opening shots, then test Space skip on a fresh run.
Listen for all four complete spoken lines with matching captions. Circle M-17 and read
its recorder. Observe a skitter pause. Finish the mission and inspect the Kestrel from
the side during extraction: the lift doors and landing gear should now visibly pass
through a partial deployment state before full flare. Walk from terrain into the
landed vestibule, then board and watch departure. Confirm that the ramp remains rigid
while boardable, disappears from collision immediately on liftoff, and that hardware
retraction occurs only after the ship has gained clearance from the LZ.

During both approaches, specifically watch whether the banking reads as inertia rather
than camera-relative wobble, whether the intermediate conversion state reduces the old
configuration pop at the existing shot distance, and whether the VTOL corrections feel
heavy rather than busy. Native MAX appearance, sound balance, performance and collision
feel remain the final acceptance gate.

Native review attempt from the preceding pass: MAX launched the registered candidate
on September 13. The Computer Use capture API failed twice after fresh window selection
with `SetIsBorderRequired failed: No such interface supported (0x80004002)`. No native
screenshot or audiovisual approval is claimed here. The current branch is prepared for
the next player review and the repository regression path has been updated to cover the
new conversion state.