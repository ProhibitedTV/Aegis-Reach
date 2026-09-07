# Native review: current candidate is not qualified for main

## Baseline, before the environment rebuild

MAX launched from this feature worktree after fixing external-project registration.
Its native log reached physics initialization, Recast navigation generation and the
main game loop. The mission audit recorded power, records and core completion,
then the beginning of extraction. The user reported a Lua loading error and
untextured ground during that run. The run is therefore **failed**, even though
those mission milestones were recorded. No completion or combat claim is made.

The engine reported all three Suno files loaded and music-state changes. These
are playback-path evidence, not a listening check. The old probe removed enemies
immediately, so it did not qualify animation or navigation.

## Confirmed causes and changes

- Native `load_storyboard` checks local project DAT files before remoteproject.txt.
  A stale Documents storyboard shadowed the checkout. Deployment now preserves
  that conflicting DAT in a local backup and registers the requested checkout.
- First Light used terrain material 287 throughout the landscape. MAX's default
  palette resolves it to mat32, **Square Pattern**. The candidate now uses verified
  native cracked-ground, dry-shore, gravel and cliff materials and retains editable
  native sculpt data. Licensed textures remain in the MAX installation.
- Four custom scenery assets were referenced by main's map but absent from Git.
  They are removed from this mission. The rebuilt structures are purpose-specific
  original assets committed with their model/FPE sources.
- Character initialization is deferred until the entity health/position table is
  populated, as required by masterinterpreter_restart. The verified FPE editor pose
  idle_aim is primed before reveal. Active characters retain the native death path.
- First Light's score now uses its own stable spatial policy and native global
  sound playback, preserving Relayfall. Actual playback flags are logged during QA.
- Mission callbacks preserve a Lua traceback in a local diagnostic log and rethrow
  failures. They do not suppress errors or report false success.

## Revised candidate: outstanding native gate

The revised candidate was launched in MAX but remained before mission startup.
There are no new animation-frame, movement or floor-height samples for it. A
local QA-only title hook did not advance it and was removed. The test process was
closed. The user's exact Lua dialog text is still required; it was not preserved
in the engine log. Do not attribute that reported error to a guessed cause.

**Do not merge yet.** The updated QA probe must complete in the actual engine and
any Lua error must be resolved before this candidate is offered for main playtest.
The new probe leaves enemies alive for frame/movement sampling, then clears them
for objective testing. It still cannot certify combat balance or appearance.

Pending native/human checks: terrain texturing and collision; walking gradients;
all doorways and route continuity; enemy skinning, idle, locomotion, firing and
death; navigation around machinery; audible score and radio balance; pickups;
return reinforcements; extraction completion; prop intersections; vista framing
and lighting. No native screenshots were captured in this session.

## Source basis

Installed `scriptbank/people/character_attack.lua`, its .byc, masterinterpreter.lua,
Characters/Tony - Armed Response.fpe, and scriptbank/global.lua were inspected.
Public MAX source: M-TerrainNew.cpp default palette and LoadTerrainTextureFolder;
GGTerrain.cpp native sculpt/material settings; GridEditB load_storyboard. Source
code establishes API/format intent; the installed engine remains authoritative.
