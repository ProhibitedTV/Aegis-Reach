require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT native CineGuru graph initializer.
-- The map owns PERIM->...->DEPART as real entity relationships. This controller waits
-- until all seventeen CineGuru cameras have registered, asks the installed graph parser
-- to resolve nextcam links, then verifies every edge before publishing ready.
local chain={processed=false,retry_at=0,ids={}}
local ORDER={
 'FL CG ARRIVAL PERIM','FL CG ARRIVAL NOSE','FL CG ARRIVAL GATE','FL CG ARRIVAL STBD',
 'FL CG ARRIVAL ISR','FL CG ARRIVAL MAST','FL CG ARRIVAL CONVERT','FL CG ARRIVAL BELLY',
 'FL CG ARRIVAL GEAR','FL CG ARRIVAL LZ','FL CG ARRIVAL FLARE','FL CG ARRIVAL TOUCHDOWN',
 'FL CG ARRIVAL RAMP','FL CG ARRIVAL DEPLOY','FL CG ARRIVAL LIFTOFF','FL CG ARRIVAL CLIMB',
 'FL CG ARRIVAL DEPART'
}

local function entity_name(e)
 if not e or not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e);if ok then return name end
end

local function scan_registered()
 if not g_Entity or not CG_IsCamera then return false end
 local found={}
 for id,_ in pairs(g_Entity) do
  local name=entity_name(id)
  if name then found[name]=id end
 end
 local ids={}
 for i,name in ipairs(ORDER) do
  local id=found[name];if not id then return false end
  local ok,registered=pcall(CG_IsCamera,id);if not ok or not registered then return false end
  ids[i]=id
 end
 chain.ids=ids;return true
end

local function verify_graph()
 if not CG_GetCamera then return false end
 for i,id in ipairs(chain.ids) do
  local ok,cam=pcall(CG_GetCamera,id);if not ok or not cam then return false end
  if i<#chain.ids then
   if cam.nextcam~=chain.ids[i+1] then return false end
  elseif cam.nextcam~=nil then
   return false
  end
 end
 return true
end

local function process_graph()
 if chain.processed or not CG_ProcessCamera or not scan_registered() then return false end
 local parsed=pcall(CG_ProcessCamera,chain.ids[1],nil);if not parsed or not verify_graph() then return false end
 chain.processed=true
 if aegis then aegis.cineguru_native_chain_ready=true end
 if fl_log then fl_log('cinematic native CineGuru chain ready cameras='..tostring(#chain.ids)) end
 return true
end

function firstlight_cineguru_chain_init(e)
 chain={processed=false,retry_at=0,ids={}}
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
