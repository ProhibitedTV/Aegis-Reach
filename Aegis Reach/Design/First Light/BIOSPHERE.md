# FIRST LIGHT — Vesper Primitive Biosphere

## Intent

Vesper's atmosphere is not scientific proof of life by itself. For Aegis Reach canon, however, Vesper supports a sparse indigenous biosphere adapted to hypersaline residual brine, strong winds, thin soils and thermal niches around human infrastructure.

The goal is not to make the moon lush. The player should notice that the world is biologically alive only after spending a little time in it.

## Environmental language

- **Vesper salt scrub** — low, dense halophile fans on sheltered shoulders and facility outskirts. Grey-green with muted violet growth surfaces so it belongs to Vesper rather than Earth.
- **Brine reeds** — short mineral-fed growth around residual brine pools. They deliberately stay off roads and combat pads.
- **Crust skitters** — hand-sized six-legged grazers that make short looping movements near scrub, brine and warm infrastructure. They are ambient visual objects only: no damage, collision, AI or navmesh ownership.
- **Drift midges** — tiny airborne colonies/spore-like organisms near residual brine, Camp 12's generator and Northstar waste heat. They reuse MAX's installed particle emitter by reference, slowed and recolored until it no longer behaves like sparks.

## Ecology gradient

Life is densest around residual brine, sheltered Camp 12 terrain and waste heat. It becomes deliberately sparse near the AEGIS excavation. This makes the absence of ordinary life around the array part of the environmental storytelling without explaining the Choir.

## Performance / gameplay rules

- Flora has physics disabled.
- Ambient creatures have physics disabled and animate only their render object when the player is nearby.
- Airborne colonies are local native particle emitters that sleep outside a short player radius.
- No biosphere entity can damage the player, own mission state, use combat AI or alter navigation.
- Flora remains at least 300 MAX inches from the authored route centerlines.

## Native review

Automated tests establish geometry validity, route clearance, counts, collision policy and runtime authority boundaries. Native MAX review still needs to judge:

- whether scrub/reed scale reads as alien groundcover rather than oversized props;
- whether drift midges look biological instead of like dim sparks;
- whether skitter movement is subtle and grounded rather than sliding;
- whether the ecology remains visible under Vesper's low-sun grade;
- whether life feels sparse enough that AEGIS becoming barren is perceptible.
