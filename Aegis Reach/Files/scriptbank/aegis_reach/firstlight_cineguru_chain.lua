require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT retired CineGuru insertion graph compatibility marker.
--
-- The opening is now driven directly by firstlight_opening_native.lua from the
-- mission HUD tick.  The seventeen old ARRIVAL cameras are quarantined out of the
-- map, so this entity intentionally performs no camera discovery, graph parsing or
-- activation.  It remains only to preserve stable authoring/entity expectations.

function firstlight_cineguru_chain_init(e)
 if aegis then aegis.cineguru_native_chain_ready=false end
 Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_cineguru_chain_main(e)
 -- Intentionally inert. Later MIRA / AEGIS / EXTRACTION cameras are owned by the
 -- normal story coordinator and do not depend on an insertion relationship graph.
end

firstlight_cineguru_chain_init=firstlight_guard('firstlight_cineguru_chain_init',firstlight_cineguru_chain_init)
firstlight_cineguru_chain_main=firstlight_guard('firstlight_cineguru_chain_main',firstlight_cineguru_chain_main)
