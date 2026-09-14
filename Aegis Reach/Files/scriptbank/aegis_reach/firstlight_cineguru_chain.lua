require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT native CineGuru graph initializer.
-- The map owns PERIM->...->DEPART as real entity relationships. This controller waits
-- until CineGuru has registered the first camera, then asks its existing graph parser
-- to resolve nextcam links. No camera transform, timing or mission authority lives here.
local chain={processed=false,first=nil,retry_at=0}
local FIRST='FL CG ARRIVAL PERIM'

local function entity_name(e)
 if not e or not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e);if ok then return name end
end

local function find_first()
 if not g_Entity then return nil end
 for id,_ in pairs(g_Entity) do if entity_name(id)==FIRST then return id end end
end

local function process_graph()
 if chain.processed or not CG_ProcessCamera or not CG_IsCamera then return false end
 local id=chain.first or find_first();chain.first=id
 if not id then return false end
 local ok,registered=pcall(CG_IsCamera,id);if not ok or not registered then return false end
 local parsed=pcall(CG_ProcessCamera,id,nil)
 if not parsed then return false end
 if CG_GetCamera then
  local got,cam=pcall(CG_GetCamera,id)
  if not got or not cam or not cam.nextcam then return false end
 end
 chain.processed=true
 if aegis then aegis.cineguru_native_chain_ready=true end
 if fl_log then fl_log('cinematic native CineGuru chain ready first='..tostring(id)) end
 return true
end

function firstlight_cineguru_chain_init(e)
 chain={processed=false,first=nil,retry_at=0}
 if aegis then aegis.cineguru_native_chain_ready=false end
 Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_cineguru_chain_main(e)
 if chain.processed then return end
 if (g_Time or 0)<chain.retry_at then return end
 chain.retry_at=(g_Time or 0)+100
 process_graph()
end

firstlight_cineguru_chain_init=firstlight_guard('firstlight_cineguru_chain_init',firstlight_cineguru_chain_init)
firstlight_cineguru_chain_main=firstlight_guard('firstlight_cineguru_chain_main',firstlight_cineguru_chain_main)
