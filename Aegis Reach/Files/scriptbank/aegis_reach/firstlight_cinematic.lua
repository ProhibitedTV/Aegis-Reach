require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT narrative camera coordinator.
-- CineGuru owns camera/player presentation; mission state remains authoritative.
-- Native MAX can initialise scripted entities over several frames, so a requested
-- beat is not consumed until CineGuru proves that the camera is actually rolling.
local cine={}
local cameras={
 ARRIVAL='FL CG ARRIVAL',
 MIRA_SIGNAL='FL CG MIRA SIGNAL',
 AEGIS_REVEAL='FL CG AEGIS REVEAL',
 EXTRACTION='FL CG EXTRACTION'
}
local profiles={
 ARRIVAL={seconds=9.5,fade=0.65,fls=54,fle=82},
 MIRA_SIGNAL={seconds=5.0,fade=0.25,fls=70,fle=82},
 AEGIS_REVEAL={seconds=6.0,fade=0.35,fls=58,fle=88},
 EXTRACTION={seconds=5.0,fade=0.35,fls=66,fle=82}
}
local RETRY_MS=250
local STARTUP_GRACE_MS=7000

local function log(message)
 if fl_log then fl_log('cinematic '..message) end
end

local function entity_name(e)
 if not e or not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e)
 if ok then return name end
 return nil
end

local function resolve_registered_camera(name)
 if not g_Entity or not GetEntityName then return nil end
 for id,_ in pairs(g_Entity) do
  if entity_name(id)==name then
   if not CG_IsCamera then return id end
   local ok,registered=pcall(CG_IsCamera,id)
   if ok and registered then return id end
  end
 end
 return nil
end

local function active_camera()
 if not CG_GetActiveCamera then return nil end
 local ok,current=pcall(CG_GetActiveCamera)
 if ok then return current end
 return nil
end

local function camera_matches(beat,id)
 if not id then return false end
 if cine.pending_camera and id==cine.pending_camera then return true end
 local name=entity_name(id)
 return name~=nil and name==cameras[beat]
end

local function configure_camera(beat,id)
 local profile=profiles[beat]
 if not profile or not id or not CG_GetCamera then return false end
 local ok,cam=pcall(CG_GetCamera,id)
 if not ok or not cam then return false end
 cam.filmtime=math.floor(profile.seconds*1000)
 cam.fadeTime=math.floor(profile.fade*1000)
 cam.data=cam.data or {}
 cam.data.fls=profile.fls
 cam.data.fle=profile.fle
 return true
end

local function play_arrival_fallback(reason)
 if cine.opening_fallback then return end
 cine.opening_fallback=true
 log('arrival fallback reason='..tostring(reason))
 if fl_say then
  fl_say('KESTREL: Meridian Shelf missed two check-ins. Forty-two colonists are unaccounted for.',
         "Mira's last burst died with Northstar. Restore the relay, recover the evacuation packet, find our people.",10)
 end
 if fl then fl.objective_pulse_until=g_Time+3500 end
end

local function caption(title,line1,line2)
 if Panel then Panel(7,76,93,93) end
 if TextCenterOnXColor then
  TextCenterOnXColor(50,78,1,title,103,220,230)
  TextCenterOnXColor(50,83,2,line1,228,225,209)
  TextCenterOnXColor(50,88,1,line2,196,210,218)
 end
end

local function draw_arrival_briefing(elapsed)
 if TextCenterOnXColor then
  TextCenterOnXColor(50,8,1,'VANGUARD RECOVERY // VESPER // MERIDIAN SHELF',176,195,202)
 end
 if elapsed<2800 then
  caption('KESTREL // INSERTION BRIEF',
          'Meridian Shelf missed two scheduled check-ins.',
          'Forty-two colonists. No beacon. No traffic.')
 elseif elapsed<5700 then
  caption('MIRA SEN // LAST BURST // 6 HOURS AGO',
          '"...Northstar offline... array waking..."',
          'SIGNAL LOST // SOURCE: OPERATIONS')
 else
  caption('KESTREL // PRIORITY RECOVERY',
          'A Warden transponder crossed Gate 07 nine minutes later.',
          'Restore Northstar. Recover the evacuation packet. Find our people.')
 end
end

local function clear_pending(reason,failed)
 local beat=cine.pending
 if not beat then return end
 log('pending finish beat='..beat..' reason='..tostring(reason))
 if failed then cine.failed[beat]=true end
 if beat=='ARRIVAL' and failed then play_arrival_fallback(reason) end
 cine.pending=nil
 cine.pending_camera=nil
 cine.pending_started=0
 cine.last_activation=0
 if aegis then
  aegis.cinematic_request=nil
  aegis.cinematic_active=false
  aegis.music_cinematic_duck=false
 end
 if cine.queued then
  local queued=cine.queued
  cine.queued=nil
  if aegis then aegis.cinematic_request=queued end
 end
end

local function finish_active(reason)
 if not cine.active then return end
 local beat=cine.active
 log('finish beat='..beat..' reason='..tostring(reason))
 cine.active=nil
 cine.active_camera=nil
 cine.active_started=0
 if aegis then
  aegis.cinematic_active=false
  aegis.music_cinematic_duck=false
 end
 if beat=='ARRIVAL' and fl_say then
  fl_say('KESTREL: Touchdown confirmed. Northstar is ahead.',
         'Bring the relay back. Then we find the forty-two.',6)
  if fl then fl.objective_pulse_until=g_Time+3500 end
 end
 if cine.queued then
  local queued=cine.queued
  cine.queued=nil
  aegis.cinematic_request=queued
 end
end

function fl_request_cinematic(beat)
 if not cameras[beat] or not aegis then return false end
 if cine.seen and cine.seen[beat] then return false end
 if cine.failed and cine.failed[beat] then return false end
 if cine.active or cine.pending then
  if cine.active==beat or cine.pending==beat then return true end
  if cine.queued~=beat then cine.queued=beat end
  return true
 end
 if aegis.cinematic_request~=beat then aegis.cinematic_request=beat end
 return true
end

local function activate_pending()
 local beat=cine.pending
 if not beat then return end
 if not CG_ActivateCamera then
  if g_Time-cine.pending_started>STARTUP_GRACE_MS then
   clear_pending('cineguru_unavailable',true)
  end
  return
 end

 local camera_name=cameras[beat]
 local camera_id=resolve_registered_camera(camera_name)
 if camera_id then
  cine.pending_camera=camera_id
  configure_camera(beat,camera_id)
 end
 local target=camera_id or camera_name
 local ok,accepted=pcall(CG_ActivateCamera,target)
 cine.last_activation=g_Time
 if not ok then
  log('activation error beat='..beat)
 elseif accepted then
  log('activation accepted beat='..beat..' camera='..camera_name)
 end
end

local function confirm_pending()
 local beat=cine.pending
 if not beat then return false end
 local current=active_camera()
 if current and camera_matches(beat,current) then
  configure_camera(beat,current)
  cine.active=beat
  cine.active_camera=current
  cine.active_started=g_Time
  cine.seen[beat]=true
  cine.pending=nil
  cine.pending_camera=nil
  cine.pending_started=0
  cine.last_activation=0
  aegis.cinematic_request=nil
  aegis.cinematic_active=true
  aegis.music_cinematic_duck=true
  if beat=='ARRIVAL' and fl then
   -- Ordinary mission radio is a fallback. Once CineGuru is visibly rolling, the
   -- cinematic subtitle layer owns the briefing and the regular message is cleared.
   fl.message_until=0
   fl.zone_until=0
  end
  log('start beat='..beat..' camera='..cameras[beat]..' entity='..tostring(current))
  return true
 end
 return false
end

local function begin_pending(beat)
 cine.pending=beat
 cine.pending_camera=nil
 cine.pending_started=g_Time
 cine.last_activation=-RETRY_MS
 aegis.music_cinematic_duck=false
 log('pending beat='..beat..' camera='..cameras[beat])
end

local function active_timeout_ms(beat)
 local p=profiles[beat]
 return p and math.floor(p.seconds*1000+3500) or 9000
end

function firstlight_cinematic_init(e)
 cine={controller=e,seen={},failed={},active=nil,active_camera=nil,active_started=0,
       pending=nil,pending_camera=nil,pending_started=0,last_activation=0,queued=nil,
       opening_fallback=false}
 Hide(e)
 CollisionOff(e)
end

function firstlight_cinematic_main(e)
 if not fl or not fl.started or not aegis then return end

 -- Director may start before CineGuru has registered this entity. Keep requesting the
 -- opening until an actual camera starts or the fail-open timer deliberately gives up.
 if not cine.seen.ARRIVAL and not cine.failed.ARRIVAL and
    not cine.active and not cine.pending and not aegis.cinematic_request and
    g_Time-(fl.born or g_Time)>350 then
  fl_request_cinematic('ARRIVAL')
 end

 -- AEGIS is the mission's one large visual reveal. Never freeze Seven while hostiles
 -- are actively engaging; once the local pocket is clear, reveal the array/substrate.
 if fl.stage==3 and not cine.seen.AEGIS_REVEAL and not cine.failed.AEGIS_REVEAL and
    not fl.in_contact and fl_distance and fl_distance(0,3200)<1350 then
  fl_request_cinematic('AEGIS_REVEAL')
 end

 if cine.active then
  local elapsed=g_Time-cine.active_started
  if cine.active=='ARRIVAL' then draw_arrival_briefing(elapsed) end
  if elapsed>active_timeout_ms(cine.active) then
   finish_active('timeout')
   return
  end
  if elapsed>650 then
   local current=active_camera()
   if not current or (cine.active_camera and current~=cine.active_camera) then
    finish_active('complete_or_abort')
   end
  end
  return
 end

 if cine.pending then
  if confirm_pending() then return end
  if g_Time-cine.pending_started>STARTUP_GRACE_MS then
   clear_pending('start_timeout',true)
   return
  end
  if g_Time-cine.last_activation>=RETRY_MS then activate_pending() end
  return
 end

 local request=aegis.cinematic_request
 if request and cameras[request] and not cine.seen[request] and not cine.failed[request] then
  begin_pending(request)
 end
end

firstlight_cinematic_init=firstlight_guard('firstlight_cinematic_init',firstlight_cinematic_init)
firstlight_cinematic_main=firstlight_guard('firstlight_cinematic_main',firstlight_cinematic_main)
