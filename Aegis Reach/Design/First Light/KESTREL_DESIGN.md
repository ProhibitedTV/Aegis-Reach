# Vanguard Kestrel // Broadwing airframe

FIRST LIGHT uses an original procedural dropship rather than a licensed or copied
vehicle. The current Kestrel is the **Broadwing-pattern utility dropship**: a compact
lifting-body transport that can approach conventionally, convert to powered lift,
put down on uneven ground, open a rear squad/cargo route, and leave without requiring
a runway.

## Design rules

The ship is built around five readable engineering ideas.

1. **The fuselage carries lift.** The center body is broad and faceted, and the
   shoulder surfaces blend into it instead of reading as giant decorative wings.
   The clean-flight silhouette is roughly 800 MAX inches long by 704 inches wide
   (about 20.3 m by 17.9 m).
2. **Thrust is arranged around the mass center.** Two cruise engines live in the
   shoulders. Four lift sources straddle the center of the airframe fore/aft so the
   landing choreography does not imply all vertical thrust is behind the cargo mass.
3. **Flight hardware changes state.** FIRST LIGHT authors three separate meshes from
   one airframe: `flight`, `flare`, and `landed`. Clean flight hides the lift throats
   and gear. Flare exposes the four lift bays and wide landing gear. Landed removes
   the thrust plumes and opens the rear cargo ramp.
4. **The transport function is visible.** The centerline is kept clear of the engine
   pods and twin tails. The landed state has a framed rear aperture, short vestibule,
   anti-slip cargo floor and a ramp whose tip reaches the authored ground contact
   plane.
5. **Materials follow function.** The lower fuselage and ramp use a dark rough TPS /
   anti-slip material, cruise throats are the hot zone, lift/RCS sources use a cool
   service color, and the cockpit is compact armored glazing. Panel breaks are broad
   and sparse rather than dense ornamental greeble.

The goal is not to copy a particular real aircraft or science-fiction ship. Familiar
aerospace principles are used to make the fictional vehicle self-explanatory.

## Runtime state swap

`firstlight_kestrel.lua` controls six map entities: insertion/extraction multiplied
by the three geometry states. Only two are classified as logical `vehicle` entities
in the layout (the clean-flight representatives); the four alternate meshes are
`vehicle_state` entities. This preserves the existing FIRST LIGHT preflight contract
while allowing visual configuration changes.

### Insertion

During `ARRIVAL`, the Kestrel approaches in clean flight and converts to the flare
state only near the handoff point. During `ARRIVAL_HANDOFF` it begins in flare,
climbs clear, then swaps back to clean flight before accelerating away. The state
swap is visual-only; the cinematic/director remain authoritative.

### Extraction

The extraction ship remains hidden until the existing 36-second arrival gate. From
36-50 seconds it approaches as a clean lifting body. At 50 seconds it converts to
flare; forward motion is mostly arrested during the first half of that phase and
the final descent is primarily vertical. At 60 seconds it swaps to the ramp-open
landed state and sets `aegis.kestrel_landed=true`.

Departure deliberately runs in the opposite order: the landed state holds briefly
for boarding, then the sealed flare mesh lifts the ship vertically clear of the pad, and clean
flight takes over for the accelerating departure. `aegis.kestrel_landed` is cleared
as soon as departure begins.

## Grounding and collision

Kestrel geometry is visual-only (`collisionmode = 11` and runtime `CollisionOff`).
Mission boarding remains controlled by the existing interaction state instead of a
large moving physics body.

The flare gear foot plane is authored at local Y=4. Extraction state entities are
placed at `ground - 4`, so the foot pads meet terrain at touchdown instead of
hovering above it. The landed ramp underside shares that Y=4 contact plane. The visible upper tip
sits four inches above it. The vestibule floor and the ramp hinge both meet at
Y=42. A sealed interior bulkhead hides the unused hull volume; the open rear
sightline and upward ramp normals are regression-tested.

## Generated materials

The builder generates coordinated APBR maps on rebuild:

- `kestrel_broadwing_atlas.png`
- `kestrel_broadwing_normal.png`
- `kestrel_broadwing_surface.png`
- `kestrel_broadwing_emissive.png`

No licensed texture payload is required. The FPEs bind the generated normal,
surface and emissive maps and keep the ship on the standard reloaded APBR shader.

## Native MAX validation

Source regressions verify geometry integrity, minimum span/length, the deployed gear
contact plane, rear-ramp reach, three-state Lua switching and existing story hooks.
Those checks do **not** prove the final presentation. A native GameGuru MAX pass must
still confirm:

- the state swap is visually seamless enough at cinematic distance;
- no alternate state flashes visible for a frame at startup;
- the flare configuration reads as powered lift rather than exposed decoration;
- the landed feet and ramp actually meet the local terrain;
- the ship does not clip nearby LZ geometry during the larger approach path;
- emissive cruise/lift throats remain readable without blowing out the APBR material;
- the rear aperture/ramp is legible during boarding.

If one of those fails, fix the authored geometry/choreography rather than weakening
the regression contract.

## Supplied research and VO integration

The user-supplied Kestrel Dropship Design Research for FIRST LIGHT informed the
boarding aperture, cabin volume, hinge/actuator details, recessed exhaust and
flight-state presentation. The source remains an original mesh; no reference
vehicle geometry or markings are reused. See PRESENTATION_INTEGRATION.md for
implemented changes and the remaining animation, collision, LOD and effects work.
