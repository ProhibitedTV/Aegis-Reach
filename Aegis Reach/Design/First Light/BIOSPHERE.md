# FIRST LIGHT — Vesper Biosphere Visual Language

## Intent

Vesper's atmosphere is not evidence of life by itself. In Aegis Reach canon, however, the moon supports a sparse indigenous biosphere adapted to hypersaline residual brine, strong winds, exposed mineral shelves and warm niches around human infrastructure.

The first implementation proved the gameplay/performance concept but looked assembled from unrelated primitives: stick-like plants, boxy fauna and legacy Earth-desert shrubs. This pass establishes one shared science-fiction biology instead.

The world should still feel mostly barren. The player notices life in sheltered margins and brine pockets, then notices its absence as AEGIS becomes dominant.

## Shared biological language

Vesper organisms are built around three repeated materials/forms:

- **Dark mineral root/chitin** — charcoal teal to violet-black structural tissue, plated rather than woody.
- **Pressure membranes** — broad cyan/violet leathery-glass surfaces supported by internal conductive veins. They catch low-angle light and create readable alien silhouettes without neon saturation.
- **Salt tissue / cold ocelli** — pale mineral interiors and tiny restrained blue-green luminous organs. Bioluminescence is punctuation, not a glowing-forest effect.

Generated assets share coordinated albedo, normal, surface and emission atlases so flora and fauna read as one ecosystem instead of unrelated props.

## Organisms

### Vesper glass fan

A low halophile rooted in a mineral bulb. Seven broad pressure membranes overlap into one fan/rosette silhouette. The membranes carry visible internal veins and curl under prevailing wind rather than sprouting disconnected Earth-like leaves.

### Vesper brine cup

A colonial organism found at residual brine margins. Several open, asymmetric cups share a mineral base. Pale inner tissue gathers brine/aerosols while fine central filaments act as sensory or reproductive structures. Its silhouette is closer to coral/anemone architecture than grass or reeds.

### Vesper salt lace

A creeping surface colony that spreads broad branching membranes over protected mineral crust. Small luminous nodules occur at the ends of mature branches. This gives Vesper a third growth strategy and fills close-to-ground negative space without adding traversal clutter.

### Crust skitter

A hand-sized mineral-chitin grazer with a segmented body, eight hooked legs, paired sensory ocelli and antennae. It moves in short scuttling bursts, then pauses to graze, avoiding the old constant-sliding-prop motion.

### Veilwing

Small atmospheric grazer with a narrow spindle body and four broad pressure sails rather than terrestrial insect wings. It drifts/orbits slowly around brine and thermal niches with bank/pitch changes, providing actual mesh-based airborne life.

### Microscopic spore colonies

Native MAX particles remain only as a subtle secondary layer: dim, slow suspended microbial/spore haze. They no longer carry the burden of representing visible insects.

## Ecology gradient

Life follows:

1. residual brine;
2. wind shelter;
3. waste heat / human infrastructure;
4. stable mineral shelves.

Life becomes deliberately sparse toward the AEGIS excavation. The barren zone is environmental storytelling, not proof that the Choir and Vesper's native biosphere are the same phenomenon.

## Legacy-media policy

The eight stock `Desert Bush - Form A` placements from the earlier world pass are retired at build time. They remain in the historical base composition but render at zero scale so FIRST LIGHT has one biosphere visual owner. No licensed media is copied or redistributed by this pass.

## Performance / gameplay rules

- Every custom biosphere asset uses collision mode 11.
- Flora and ambient fauna are authored physics-off.
- Mesh fauna animate only their render object and only near the player.
- Skitters update at roughly 11 Hz; veilwings at roughly 14 Hz; microscopic particles at roughly 5.5 Hz.
- No biosphere entity can damage the player, own mission state, use combat AI or alter navigation.
- Authored flora remains at least 300 MAX inches from route centerlines.
- AEGIS remains intentionally biologically sparse.

## Native review gate

Automated tests can establish geometry validity, complexity, material-map presence, collision policy, route clearance and authority boundaries. Native MAX must still answer the artistic questions:

- Do glass fans read as layered living membranes rather than cards or crystals?
- Do brine cups feel organic/mineral rather than like procedural pipes?
- Does salt lace sit naturally on terrain without obvious floating or clipping?
- Do skitters read as small animals at gameplay distance, and do their pause/scuttle rhythms kill the sliding-prop look?
- Do veilwings feel like atmospheric organisms instead of flying geometry?
- Are the luminous details visible enough to unify the biology without turning Vesper into a neon fantasy biome?
- Does the ecology become noticeably quieter/barren near AEGIS?
