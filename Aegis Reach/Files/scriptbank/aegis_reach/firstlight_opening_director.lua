require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Compatibility controller only.
--
-- Native MAX repeatedly rendered the legacy external establishing view even when this
-- entity owned a validated 17-cut timeline. The actual insertion camera now runs from
-- firstlight_hud.lua -> firstlight_opening_native.lua, a mission path already proven to
-- execute every frame. Keep this entity only so old maps/build metadata fail gracefully;
-- it must never touch camera 0, dialogue, or opening elapsed time.
local announced=false

function firstlight_opening_director_init(e)
 Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_opening_director_main(e)
 if not announced and fl and fl.started then
  announced=true
  if fl_log then fl_log('opening-director compatibility entity delegated to HUD-native owner') end
 end
end

firstlight_opening_director_init=firstlight_guard('firstlight_opening_director_init',firstlight_opening_director_init)
firstlight_opening_director_main=firstlight_guard('firstlight_opening_director_main',firstlight_opening_director_main)
