# First Light: facility candidate handoff

This candidate is on `codex/vesper-environment-polish`, PR #23. It is not merged
or native-approved. Start a NEW GAME; saved games can retain old positions/state.
The registered MAX project currently points to this worktree candidate, not main.

## Latest integration

Remote Sol combat work through `14c6bee` is now merged into this candidate. Enemy
starts, cover, tactical pacing, objective feedback and score ducking therefore
need a complete playthrough. The earlier facility-only position-preservation note
is not a claim about this integrated version. Use `COLLECT FIRST LIGHT QA.cmd`
after a run for the incoming encounter-tuning report.

The original `vesper_orbital` sky replaces sunset. Check west/northwest for the
planet, scan every horizon join, and inspect shadow readability and water
reflections. Light shafts and procedural clouds are disabled. Sky packaging:
`tools/build_vesper_sky.py`; source/settings: `Sky/README.md` and the atmosphere
block in `tools/build_first_light.py`.

## Load and verify

Close an existing MAX session normally before launching the revised project.
From the checkout root run `PLAY FIRST LIGHT.cmd`, or:

```powershell
python -B tools/firstlight_playtest.py play
```

The launcher rebuilds changed geometry, validates references, invalidates only
compiled copies of original art and registers this checkout with MAX.

1. Gate 07: view the office from the road. The small sign should be beside the
   office, clear of the route. Walk both sides of the replacement barriers.
2. Northstar: use the standing-height power console. Confirm the hold prompt,
   combat gate and progression still work.
3. Operations: enter the archive, use records, traverse the link, then enter the
   crew room. Inspect desks/monitors and cot/lockers. Confirm the crew-room
   defender can fight and navigate; new walls may affect AI.
4. AEGIS: approach the pavilion between the relay cabinets; enter and use CORE.
   Check cabinet feet, antenna silhouettes and ceiling/door collision.
5. Return to LZ 07 and finish extraction. Inspect smaller signs at player height.
6. Compare HUD at 1080p: objective text within panel, readable compass labels,
   shield depletion/recharge and armour at the bottom right.

Capture real MAX images from each facility approach and inside both rooms. Report
floating geometry, intersections, dark text, doorway snags and obstructed enemies
before approving a merge. Structural tests are not visual or collision proof.

## Where to tune

| Change | Authoring source |
| --- | --- |
| Facility centers, yaw, furniture, barriers | `tools/firstlight_world.py`, `architecture()` |
| Shell, canopy, console, link, antenna geometry | `tools/meridian_fieldkit.py` |
| Fixture light colors, ranges and heights | `tools/build_first_light.py`, `light_locations` / `fixture_heights` |
| Sign sizes, supports and positions | `tools/build_first_light.py`, `sign()` |
| Compass/panels/vital bars | `Aegis Reach/Files/scriptbank/aegis_reach/firstlight_hud.lua` |
| Mission interaction behavior | `firstlight_director.lua`; unchanged in this pass |

Coordinates are engine inches, X/Z horizontal, Y vertical. MAX yaw rotates local
+Z toward +X. Modules face local -Z; the doorway center is local X=72, Z=-130.
Archive is (1250,1080,1050), yaw 0; crew room (1935,1080,1000), yaw 90;
AEGIS pavilion (-72,1540,3210), yaw 0. Consoles remain at original objective points.
Modules use native terrain as their floor. Do not raise them without considering
footing, doorway clearance and objective position.

Make persistent changes in these sources: a generator rebuild overwrites edits
made only to the generated map or meshes. Rebuild using:

```powershell
python -B tools/firstlight_playtest.py deploy
```

Commit the authored sources, original assets and canonical `.fpm`; omit testmap,
logs, saves, editor config, compiled DBOs and installed DLC. Avoid `git add .`.

## Next art priorities

After native review: terrain silhouette/rock-scale breakup, contact detail around
facility feet, better cabinet/console surface detail, skyline depth and precise
warm/cool balance. Assess puddle reflections, crystal clarity and scrub from the
prior pass in native MAX before adding more. Keep Camp 12's established footprint
and the readable service road. The current material/geometry pass is a candidate,
not a claim of concept-art or AAA finish.
