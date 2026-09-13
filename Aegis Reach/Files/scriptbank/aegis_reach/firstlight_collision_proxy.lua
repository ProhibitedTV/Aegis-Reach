require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Invisible gameplay collision for authored wreck proxy volumes.
-- Hide() affects rendering only; physics stays enabled by the map entity. Deliberately
-- never call CollisionOff here. Re-hide every tick because MAX can restore visibility
-- when an always-active entity transitions through native streaming/state updates.

function firstlight_collision_proxy_init(e)
 Hide(e)
end

function firstlight_collision_proxy_main(e)
 Hide(e)
end

firstlight_collision_proxy_init=firstlight_guard('firstlight_collision_proxy_init',firstlight_collision_proxy_init)
firstlight_collision_proxy_main=firstlight_guard('firstlight_collision_proxy_main',firstlight_collision_proxy_main)
