require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT narrative camera coordinator.
-- CineGuru owns camera/player presentation; mission state remains authoritative and
-- every beat fails open so a missing/aborted cinematic can never block progression.
local cine={}
local cameras={
 ARRIVAL='FL CG ARRIVAL',
 MIRA_SIGNAL='FL CG MIRA SIGNAL',
 AEGIS_REVEAL='FL CG AEGIS REVEAL',
 EXTRACTION='FL CG EXTRACTION'
}

local function log(message)
 if fl_log then fl_log('cinematic '..message) end
end

local function finish_active(reason)
 if not cine.active then return end
 log('finish beat='..cine.active..' reason='..tostring(reason))
 cine.active=nil
 cine.active_started=0
 if aegis then
  aegis.cinematic_active=false
  aegis.music_cinematic_duck=false
 end
 if cine.queued then
  local beat=cine.queued
  cine.queued=nil
  aegis.cinematic_request=beat
 end
end

function fl_request_cinematic(beat)
 if not cameras[beat] then return false end
 if not aegis then return false end
 if cine.seen and cine.seen[beat] then return false end
 if cine.active then
  if cine.queued~=beat then cine.queued=beat end
  return true
 end
 if aegis.cinematic_request~=beat then aegis.cinematic_request=beat end
 return true
end

local function begin_beat(beat)
 local camera=cameras[beat]
 if not camera then return end
 cine.seen[beat]=true
 aegis.cinematic_request=nil

 if beat=='AEGIS_REVEAL' and fl_say then
  fl_say('SUIT: FIRING SOLUTION CONFIRMED // SHELTER 12.',
         "KESTREL: The signal under the array matches Mira's survey tone. That is what they were trying to erase.",9)
  fl.discovery_until=g_Time+10000
  fl.discovery_track='discovery_choir'
 end

 if not CG_ActivateCamera then
  log('fallback beat='..beat..' reason=cineguru_unavailable')
  return
 end
 local ok,activated=pcall(CG_ActivateCamera,camera)
 if not ok or not activated then
  log('fallback beat='..beat..' reason=activation_failed')
  return
 end
 cine.active=beat
 cine.active_started=g_Time
 aegis.cinematic_active=true
 aegis.music_cinematic_duck=true
 log('start beat='..beat..' camera='..camera)
end

function firstlight_cinematic_init(e)
 cine={controller=e,seen={},active=nil,active_started=0,queued=nil}
 Hide(e)
 CollisionOff(e)
end

function firstlight_cinematic_main(e)
 if not fl or not fl.started or not aegis then return end

 -- The opening camera is intentionally brief; Kestrel's existing arrival line plays
 -- over it and control returns before the first encounter.
 if not cine.seen.ARRIVAL and g_Time-(fl.born or g_Time)>1200 then
  fl_request_cinematic('ARRIVAL')
 end

 -- AEGIS is the mission's one large visual reveal. Never freeze Seven while hostiles
 -- are actively engaging; once the local pocket is clear, reveal the array/substrate.
 if fl.stage==3 and not cine.seen.AEGIS_REVEAL and not fl.in_contact and
    fl_distance and fl_distance(0,3200)<1350 then
  fl_request_cinematic('AEGIS_REVEAL')
 end

 if cine.active then
  -- Give CineGuru a few frames to transition from triggered -> rolling before treating
  -- a nil active camera as completion. A hard timeout is the second fail-open path.
  if g_Time-cine.active_started>9000 then
   finish_active('timeout')
   return
  end
  if g_Time-cine.active_started>650 and CG_GetActiveCamera then
   local ok,current=pcall(CG_GetActiveCamera)
   if ok and current==nil then finish_active('complete_or_abort') end
  end
  return
 end

 local request=aegis.cinematic_request
 if request and not cine.seen[request] then begin_beat(request) end
end

firstlight_cinematic_init=firstlight_guard('firstlight_cinematic_init',firstlight_cinematic_init)
firstlight_cinematic_main=firstlight_guard('firstlight_cinematic_main',firstlight_cinematic_main)
