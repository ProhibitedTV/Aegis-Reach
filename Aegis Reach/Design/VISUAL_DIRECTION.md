# Aegis Reach visual direction

## Target

Relayfall should read as a remote military-science-fiction relay fortress at blue hour: severe architecture, cold atmospheric fill, bright signal infrastructure, warm warning light, and a huge readable skyline.

The reference standard is the **clarity and confidence of classic arena shooters**, not imitation of another franchise's assets, silhouettes, architecture, or lore. The player should understand the fight before stopping to admire the scenery.

## Visual hierarchy

Every combat view should resolve in this order:

1. **Enemy silhouette** — the threat must separate from the background.
2. **Cover and route** — the player should immediately see where movement is possible.
3. **Objective landmark** — relay, spire, bunker, or extraction geometry should orient the player without depending entirely on HUD text.
4. **Atmosphere and detail** — fog, emissives, cables, clutter, decals, and distant scenery enrich the space only after the first three reads work.

If environmental detail harms one of the first three reads, remove or relocate the detail.

## Palette

### World fill

- deep steel blue and slate rather than pure black;
- cool sky and ambient fill keep shadowed architecture readable;
- distant geometry should fade toward blue-grey atmospheric perspective.

### Navigation / friendly system language

- cyan/teal marks relay infrastructure, extraction, suit systems, and routes the player is meant to understand;
- cyan should be bright enough to guide, but not sprayed uniformly across every surface.

### Threat / industrial language

- amber is used for machinery, warning fixtures, exposed power, and combat-pocket contrast;
- red should be rare and reserved for genuine danger or enemy-specific language later.

## Lighting rules

1. **Never use darkness as the primary source of difficulty.** Difficulty comes from enemy behavior, angles, timing, and resource decisions.
2. A standing enemy at useful rifle range must not disappear into the wall behind them.
3. Main movement lanes need ambient fill even when no local light is nearby.
4. Local lights should create alternating cool/warm pools that help divide a large arena into remembered spaces.
5. Objective structures get brighter edge light than generic walls.
6. Avoid flat fullbright. Shadows remain important for depth, but their floor should remain readable.
7. Auto-exposure stays off unless testing proves it is necessary; consistent combat readability matters more than cinematic adaptation.

## Sky and horizon

The previous prototype disabled the skybox entirely, producing a black void and poor silhouette separation. Visual pass 2 restores a built-in high-cloud sky and moves the mission toward morning blue-hour lighting.

The horizon should eventually carry one memorable original landmark beyond the fortress — mountains, orbital infrastructure, distant colony lights, or an enormous communications structure. The purpose is scale and orientation, not a ringworld analogue.

## Combat-space landmarks

Relayfall already has a useful structure. Each major beat should become visually recognizable before additional geometry is added:

- **Insertion / Kestrel pad:** clean cyan landing-zone language, open view into the fortress.
- **Northstar:** first strong signal-spire silhouette, cyan-heavy treatment.
- **Lantern:** warmer industrial pocket with crossing lanes and more amber machinery.
- **AEGIS core:** tallest and most electrically intense space; hostile signal state should feel oppressive without becoming darker.
- **Return to Kestrel:** familiar spaces read differently because the player is moving against the original flow.

## Cyberpunk DLC usage

Cyberpunk assets are valuable as a detail library, especially for:

- cable runs and exposed conduits;
- maintenance gantries and catwalks;
- antenna components and relay machinery;
- server/power cabinets;
- emissive signage and industrial light fixtures;
- vents, junction boxes, barriers, and believable service clutter.

Do **not** turn the fortress into a neon city. Aegis Reach is military infrastructure. Use cyberpunk props as functional technological detail layered over a restrained hard-surface base.

## Enemy readability

The current Iron Wardens all share a stock human silhouette. Until bespoke enemies exist, combat roles should gain subtle but readable visual identifiers where practical:

- flanker: cool accent;
- anchor: warm/heavier accent;
- hunter: brighter forward-facing threat accent;
- skirmisher: neutral baseline;
- reserve assault: distinct warning/accent treatment.

These should eventually be visible before the role acts. Behavior that can only be learned after taking damage is weaker than behavior communicated by silhouette, color, sound, or posture.

## Weapon presentation

Weapons need to communicate role through sound, recoil, muzzle event, animation cadence, and impact response — not damage numbers alone.

The current sandbox should remain compact:

- assault rifle = mobile default;
- shotgun = close-range space control;
- marksman rifle = deliberate long-range problem solver;
- grenade = positional disruption.

Future weapons should be rejected unless they add a genuinely new tactical verb.

## Visual pass 2 implementation

`tools/polish_relayfall.py` patches the current `.fpm` directly and:

- restores a real skybox (`highcloud`);
- raises stable exposure and ambient fill;
- shifts the environment toward cool blue atmospheric fill;
- adds warmer directional sunlight for shape separation;
- reduces the black-void look with stronger zenith and fog color;
- reduces excessive bloom while preserving emissive punch;
- enlarges the six existing cyan/amber authored light pools;
- preserves the existing geometry and encounter layout.

Run it directly or deploy with:

```bat
python tools\max_playtest.py deploy --polish
```

## Review test

A screenshot passes the first visual-quality gate when:

- the player can identify enemies without zooming into the image;
- foreground weapon, midground cover, enemy, and background architecture occupy distinguishable value ranges;
- the sky produces a clear horizon/silhouette;
- black pixels still exist, but major playable surfaces are not swallowed by them;
- cyan and amber accents guide the eye instead of dominating the entire frame.
