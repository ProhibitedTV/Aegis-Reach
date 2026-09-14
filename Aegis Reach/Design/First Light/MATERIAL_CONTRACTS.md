# First Light material contracts

The authored texture-polish pass may derive high-frequency detail from source art, but engine-facing APBR semantics stay deterministic.

- Surface packing remains **R = occlusion, G = roughness, B = metalness, A = reflectance**.
- **Brineglass is dielectric**: calm and resonant brineglass surface maps must have metalness B = 0 everywhere.
- Brineglass roughness is constrained to the established crystal-response window of 45–110 in the packed G channel.
- The contract pass runs after material generation, including cache-restoration builds, and updates `material-polish.json` hashes after any semantic correction.

This layer exists so generated/detail-rich source art can evolve without silently changing the physical material identity expected by GameGuru MAX and the Meridian material regression suite.
