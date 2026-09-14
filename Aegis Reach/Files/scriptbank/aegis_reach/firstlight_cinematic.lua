require 'scriptbank\aegis_reach\firstlight_audit'
-- FIRST LIGHT narrative camera coordinator. CineGuru owns presentation; mission fails open.
local cine={}
local cameras={ARRIVAL_WIDE="FL CG ARRIVAL WIDE",ARRIVAL_PASS="FL CG ARRIVAL PASS",ARRIVAL_ORBIT="FL CG ARRIVAL ORBIT",ARRIVAL_DESCENT="FL CG ARRIVAL DESCENT",ARRIVAL_HANDOFF="FL CG ARRIVAL HANDOFF",ARRIVAL_LIFTOFF="FL CG ARRIVAL LIFTOFF",ARRIVAL_CLIMB="FL CG ARRIVAL CLIMB",ARRIVAL_DEPART="FL CG ARRIVAL DEPART",MIRA_SIGNAL="FL CG MIRA SIGNAL",AEGIS_REVEAL="FL CG AEGIS REVEAL",EXTRACTION="FL CG EXTRACTION"}
local opening_order={"ARRIVAL_WIDE","ARRIVAL_PASS","ARRIVAL_ORBIT","ARRIVAL_DESCENT","ARRIVAL_HANDOFF","ARRIVAL_LIFTOFF","ARRIVAL_CLIMB","ARRIVAL_DEPART"}
local profiles={ARRIVAL_WIDE={seconds=8.99,fade=0.24,fls=54,fle=72},ARRIVAL_PASS={seconds=10.19,fade=0.12,fls=58,fle=82},ARRIVAL_ORBIT={seconds=9.64,fade=0.14,fls=62,fle=86},ARRIVAL_DESCENT={seconds=12.67,fade=0.14,fls=66,fle=88},ARRIVAL_HANDOFF={seconds=4.6,fade=0.18,fls=70,fle=84},ARRIVAL_LIFTOFF={seconds=2.6,fade=0.12,fls=62,fle=78},ARRIVAL_CLIMB={seconds=2.4,fade=0.12,fls=60,fle=76},ARRIVAL_DEPART={seconds=3.0,fade=0.16,fls=56,fle=72},MIRA_SIGNAL={seconds=9.95,fade=0.35,fls=70,fle=84},AEGIS_REVEAL={seconds=10.75,fade=0.35,fls=58,fle=90},EXTRACTION={seconds=7.75,fade=0.35,fls=62,fle=82}}
local RETRY_MS=250;local STARTUP_GRACE_MS=7000
local function log(m)if fl_log then fl_log('cinematic '..m) end end
local function entity_name(e)if not e or not GetEntityName then return nil end;local ok,n=pcall(GetEntityName,e);if ok then return n end end
local function resolve_registered_camera(name)
 if not g_Entity or not GetEntityName then return nil end
 for id,_ in pairs(g_Entity) do if entity_name(id)==name then if not CG_IsCamera then return id end;local ok,registered=pcall(CG_IsCamera,id);if ok and registered then return id end end end
end
local function active_camera()if not CG_GetActiveCamera then return nil end;local ok,current=pcall(CG_GetActiveCamera);if ok then return current end end
local function camera_matches(beat,id)if not id then return false end;if cine.pending_camera and id==cine.pending_camera then return true end;return entity_name(id)==cameras[beat] end
local function configure_camera(beat,id)
 local p=profiles[beat];if not p or not id or not CG_GetCamera then return false end;local ok,cam=pcall(CG_GetCamera,id);if not ok or not cam then return false end
 cam.filmtime=math.floor(p.seconds*1000);cam.fadeTime=math.floor(p.fade*1000);cam.data=cam.data or {};cam.data.fls=p.fls;cam.data.fle=p.fle;return true
end
local function say(id,a,b,seconds)if fl_dialogue and fl_dialogue(id) then return end;if fl_say then fl_say(a,b,seconds) end end
local function opening_index(beat)
 for i,name in ipairs(opening_order) do if beat==name then return i end end
 return nil
end
local function is_opening(beat)return opening_index(beat)~=nil end
local function next_opening_beat(beat)
 local i=opening_index(beat);if i and i<#opening_order then return opening_order[i+1] end
end
local function mark_opening_seen()
 cine.seen=cine.seen or {}
 for _,beat in ipairs(opening_order) do cine.seen[beat]=true end
end
local function opening_fallback(reason)
 if cine.opening_fallback then return end;cine.opening_fallback=true;log('opening fallback reason='..tostring(reason));say('FL01_KES_004','KESTREL: Meridian Shelf missed two check-ins. Forty-two colonists are unaccounted for.','Restore Northstar. Recover the evacuation packet. Find our people.',8);if fl then fl.objective_pulse_until=g_Time+3500 end
end
local function mark_line(key,id,a,b,seconds) cine.lines=cine.lines or {};if cine.lines[key] then return end;cine.lines[key]=true;say(id,a,b,seconds) end
local function update_story_timeline(beat,elapsed)
 if beat=="ARRIVAL_WIDE" then
  if elapsed>=350 then mark_line("FL01_KES_001","FL01_KES_001","KESTREL: Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.","",7.987) end
 elseif beat=="ARRIVAL_PASS" then
  if elapsed>=350 then mark_line("FL01_KES_002","FL01_KES_002","KESTREL: Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.","",9.189) end
 elseif beat=="ARRIVAL_ORBIT" then
  if elapsed>=350 then mark_line("FL01_KES_003","FL01_KES_003","KESTREL: Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.","",8.64) end
 elseif beat=="ARRIVAL_DESCENT" then
  if elapsed>=350 then mark_line("FL01_KES_004","FL01_KES_004","KESTREL: A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.","",11.67) end
 elseif beat=="ARRIVAL_HANDOFF" then
  if elapsed>=350 then mark_line("FL01_KES_005","FL01_KES_005","KESTREL: You are down. I will stay high and dark until you call for extraction.","",3.6) end
 elseif beat=="ARRIVAL_LIFTOFF" then
 elseif beat=="ARRIVAL_CLIMB" then
 elseif beat=="ARRIVAL_DEPART" then
 elseif beat=="MIRA_SIGNAL" then
  if elapsed>=350 then mark_line("FL01_MIR_001","FL01_MIR_001","MIRA SEN: Seven... Shelter Twelve. We are below the array. Do not let them fire.","",4.8) end
  if elapsed>=5500 then mark_line("FL01_KES_009","FL01_KES_009","KESTREL: Copy. AEGIS is targeting the shelter. Get to the core.","",3.8) end
 elseif beat=="AEGIS_REVEAL" then
  if elapsed>=350 then mark_line("FL01_MIR_002","FL01_MIR_002","MIRA SEN: It is not a foundation. The black ribs continue below the old waterline. It answers the calibration tone.","",5.5) end
  if elapsed>=6200 then mark_line("FL01_KES_010","FL01_KES_010","KESTREL: Whatever it is, save the people first. Kill the firing order.","",3.9) end
 elseif beat=="EXTRACTION" then
  if elapsed>=350 then mark_line("FL01_KES_016","FL01_KES_016","KESTREL: Seven, you are on. Strap in.","",2.4) end
  if elapsed>=3100 then mark_line("FL01_KES_017","FL01_KES_017","KESTREL: Lifting. Shelter Twelve is alive. Mira is still transmitting.","",4.0) end
 end
 if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end
end
local function finish_opening_handoff()if aegis then aegis.insertion_complete=true end;if fl then fl.objective_pulse_until=g_Time+3500 end end
local function clear_pending(reason,failed)
 local beat=cine.pending;if not beat then return end;log('pending finish beat='..beat..' reason='..tostring(reason));if failed then cine.failed[beat]=true end
 if failed and is_opening(beat) then opening_fallback(reason);mark_opening_seen();finish_opening_handoff() end
 if failed and beat=='MIRA_SIGNAL' then say('FL01_MIR_001','MIRA SEN: Shelter Twelve. We are below the array.','Do not let them fire.',8) end
 if failed and beat=='AEGIS_REVEAL' then say('FL01_MIR_002','MIRA SEN: The black ribs continue below the old waterline.','It answers the calibration tone.',8) end
 if failed and beat=='EXTRACTION' and fl_finish_extraction then fl_finish_extraction() end
 cine.pending=nil;cine.pending_camera=nil;cine.pending_started=0;cine.last_activation=0
 if aegis then aegis.cinematic_request=nil;aegis.cinematic_active=false;aegis.cinematic_beat=nil;aegis.music_cinematic_duck=false end
 if cine.queued then local q=cine.queued;cine.queued=nil;if aegis then aegis.cinematic_request=q end end
end
local function finish_active(reason)
 if not cine.active then return end
 local beat=cine.active
 if reason=='timeout' and CG_GetCamera and cine.active_camera then local ok,cam=pcall(CG_GetCamera,cine.active_camera);if ok and cam then cam.state='abort' end end
 local skipped=reason=='aborted';local nextbeat=(not skipped and is_opening(beat)) and next_opening_beat(beat) or nil
 if skipped and fl_dialogue_cancel then fl_dialogue_cancel() end
 log('finish beat='..beat..' reason='..tostring(reason));cine.active=nil;cine.active_camera=nil;cine.active_started=0
 if aegis then aegis.cinematic_active=false;aegis.cinematic_beat=nil;aegis.music_cinematic_duck=nextbeat~=nil end
 if skipped and is_opening(beat) then mark_opening_seen();finish_opening_handoff()
 elseif is_opening(beat) then if nextbeat then if aegis then aegis.cinematic_request=nextbeat end else finish_opening_handoff() end
 elseif beat=='EXTRACTION' and fl_finish_extraction then fl_finish_extraction() end
 if cine.queued then local q=cine.queued;cine.queued=nil;if aegis then aegis.cinematic_request=q end end
end
function fl_request_cinematic(beat)
 if not cameras[beat] or not aegis then return false end;if cine.seen and cine.seen[beat] then return false end;if cine.failed and cine.failed[beat] then return false end
 if cine.active or cine.pending then if cine.active==beat or cine.pending==beat then return true end;if cine.queued~=beat then cine.queued=beat end;return true end
 if aegis.cinematic_request~=beat then aegis.cinematic_request=beat end;return true
end
local function activate_pending()
 local beat=cine.pending;if not beat then return end
 if not CG_ActivateCamera then if g_Time-cine.pending_started>STARTUP_GRACE_MS then clear_pending('cineguru_unavailable',true) end;return end
 local name=cameras[beat];local id=resolve_registered_camera(name);if id then cine.pending_camera=id;configure_camera(beat,id) end
 local ok,accepted=pcall(CG_ActivateCamera,id or name);cine.last_activation=g_Time;if not ok then log('activation error beat='..beat) elseif accepted then log('activation accepted beat='..beat..' camera='..name) end
end
local function confirm_pending()
 local beat=cine.pending;if not beat then return false end;local current=active_camera()
 if current and camera_matches(beat,current) then configure_camera(beat,current);cine.active=beat;cine.active_camera=current;cine.active_started=g_Time;cine.lines={};cine.seen[beat]=true;cine.pending=nil;cine.pending_camera=nil;cine.pending_started=0;cine.last_activation=0;aegis.cinematic_request=nil;aegis.cinematic_active=true;aegis.cinematic_beat=beat;aegis.cinematic_started_at=g_Time;aegis.cinematic_duration_ms=math.floor(profiles[beat].seconds*1000);aegis.music_cinematic_duck=true;if fl then fl.message_until=0;fl.zone_until=0 end;log('start beat='..beat..' camera='..cameras[beat]..' entity='..tostring(current));return true end
 return false
end
local function begin_pending(beat)
 cine.pending=beat;cine.pending_camera=nil;cine.pending_started=g_Time;cine.last_activation=-RETRY_MS
 if not is_opening(beat) then aegis.music_cinematic_duck=false end
 log('pending beat='..beat..' camera='..cameras[beat])
end
local function active_timeout_ms(beat)local p=profiles[beat];return p and math.floor(p.seconds*1000+3500) or 9000 end
function firstlight_cinematic_init(e)cine={controller=e,seen={},failed={},active=nil,active_camera=nil,active_started=0,pending=nil,pending_camera=nil,pending_started=0,last_activation=0,queued=nil,opening_fallback=false,lines={}};Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end end
function firstlight_cinematic_main(e)
 if not fl or not fl.started or not aegis then return end
 if not cine.seen.ARRIVAL_WIDE and not cine.failed.ARRIVAL_WIDE and not cine.active and not cine.pending and not aegis.cinematic_request and g_Time-(fl.born or g_Time)>350 then fl_request_cinematic('ARRIVAL_WIDE') end
 if fl.stage==3 and not cine.seen.AEGIS_REVEAL and not cine.failed.AEGIS_REVEAL and not fl.in_contact and fl_distance and fl_distance(0,3200)<1350 then fl_request_cinematic('AEGIS_REVEAL') end
 if cine.active then local elapsed=g_Time-cine.active_started;update_story_timeline(cine.active,elapsed);if elapsed>active_timeout_ms(cine.active) then finish_active('timeout');return end;if elapsed>650 then local current=active_camera();if not current or (cine.active_camera and current~=cine.active_camera) then finish_active(elapsed<profiles[cine.active].seconds*1000-450 and 'aborted' or 'complete') end end;return end
 if cine.pending then if confirm_pending() then return end;if g_Time-cine.pending_started>STARTUP_GRACE_MS then clear_pending('start_timeout',true);return end;if g_Time-cine.last_activation>=RETRY_MS then activate_pending() end;return end
 local request=aegis.cinematic_request;if request and cameras[request] and not cine.seen[request] and not cine.failed[request] then begin_pending(request) end
end
firstlight_cinematic_init=firstlight_guard('firstlight_cinematic_init',firstlight_cinematic_init)
firstlight_cinematic_main=firstlight_guard('firstlight_cinematic_main',firstlight_cinematic_main)
