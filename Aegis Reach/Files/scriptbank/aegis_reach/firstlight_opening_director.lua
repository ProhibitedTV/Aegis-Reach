require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT deterministic opening director.
--
-- The 17 CineGuru camera entities remain the authored physical camera mounts, but this
-- controller owns the actual game camera during insertion. This deliberately avoids
-- relying on CineGuru's follow-on state machine for editorial cuts: every cut is driven
-- from one 50.8 second mission clock, so the camera source cannot silently stretch or
-- stick on the old establishing shot while VO continues.
local director={started=false,finished=false,start_ms=0,shot=0,cameras={},lines={}}

local SHOTS={
 {beat='ARRIVAL_PERIM',name='FL CG ARRIVAL PERIM',stop=2800,fls=88,fle=82},
 {beat='ARRIVAL_NOSE',name='FL CG ARRIVAL NOSE',stop=5800,fls=58,fle=62},
 {beat='ARRIVAL_GATE',name='FL CG ARRIVAL GATE',stop=8400,fls=92,fle=84},
 {beat='ARRIVAL_STBD',name='FL CG ARRIVAL STBD',stop=11400,fls=52,fle=56},
 {beat='ARRIVAL_ISR',name='FL CG ARRIVAL ISR',stop=14500,fls=96,fle=88},
 {beat='ARRIVAL_MAST',name='FL CG ARRIVAL MAST',stop=17500,fls=78,fle=86},
 {beat='ARRIVAL_CONVERT',name='FL CG ARRIVAL CONVERT',stop=20500,fls=48,fle=54},
 {beat='ARRIVAL_BELLY',name='FL CG ARRIVAL BELLY',stop=23500,fls=46,fle=52},
 {beat='ARRIVAL_GEAR',name='FL CG ARRIVAL GEAR',stop=26500,fls=50,fle=54},
 {beat='ARRIVAL_LZ',name='FL CG ARRIVAL LZ',stop=29500,fls=88,fle=80},
 {beat='ARRIVAL_FLARE',name='FL CG ARRIVAL FLARE',stop=32500,fls=72,fle=68},
 {beat='ARRIVAL_TOUCHDOWN',name='FL CG ARRIVAL TOUCHDOWN',stop=35500,fls=62,fle=58},
 {beat='ARRIVAL_RAMP',name='FL CG ARRIVAL RAMP',stop=38500,fls=54,fle=58},
 {beat='ARRIVAL_DEPLOY',name='FL CG ARRIVAL DEPLOY',stop=42700,fls=58,fle=62},
 {beat='ARRIVAL_LIFTOFF',name='FL CG ARRIVAL LIFTOFF',stop=45300,fls=54,fle=58},
 {beat='ARRIVAL_CLIMB',name='FL CG ARRIVAL CLIMB',stop=47800,fls=50,fle=56},
 {beat='ARRIVAL_DEPART',name='FL CG ARRIVAL DEPART',stop=50800,fls=62,fle=72},
}

local EVENTS={
 {at=200,id='FL01_KES_001',speaker='KESTREL',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.',seconds=7.987},
 {at=8550,id='FL01_KES_002',speaker='KESTREL',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.',seconds=9.189},
 {at=17800,id='FL01_KES_003',speaker='KESTREL',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=8.64},
 {at=26600,id='FL01_KES_004',speaker='KESTREL',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.',seconds=11.67},
 {at=38700,id='FL01_KES_005',speaker='KESTREL',text='You are down. I will stay high and dark until you call for extraction.',seconds=3.6},
}

local function log(msg)if fl_log then fl_log('opening-director '..tostring(msg)) end end
local function entity_name(e)
 if not e or not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e);if ok then return name end
end
local function scan()
 if not g_Entity then return false end
 local by_name={}
 for id,ent in pairs(g_Entity) do
  if ent and ent.obj then local name=entity_name(id);if name then by_name[name]=ent.obj end end
 end
 local count=0
 for i,s in ipairs(SHOTS) do director.cameras[i]=by_name[s.name];if director.cameras[i] then count=count+1 end end
 return count==#SHOTS
end
local function say(ev)
 if director.lines[ev.id] then return end;director.lines[ev.id]=true
 if fl_dialogue and fl_dialogue(ev.id) then return end
 if fl_say then fl_say(ev.speaker..': '..ev.text,'',ev.seconds) end
end
local function shot_for(ms)
 for i,s in ipairs(SHOTS) do if ms<s.stop then return i,s end end
 return #SHOTS,SHOTS[#SHOTS]
end
local function shot_start(i)return i<=1 and 0 or SHOTS[i-1].stop end
local function camera_pose(obj)
 if not obj or not GetObjectPosAng then return nil end
 local x,y,z,rx,ry,rz=GetObjectPosAng(obj);if not x then return nil end
 return x,y,z,rx or 0,ry or 0,rz or 0
end
local function begin()
 if director.started then return end
 if not scan() then return end
 director.started=true;director.start_ms=g_Time;director.shot=0;director.lines={}
 if aegis then
  aegis.opening_director_active=true
  aegis.cinematic_request='OPENING_DIRECTOR_LOCK'
  aegis.cinematic_active=true
  aegis.opening_started_at=g_Time
  aegis.opening_elapsed_ms=0
  aegis.music_cinematic_duck=true
 end
 director.orig_fov=GetGamePlayerStateCameraFov and GetGamePlayerStateCameraFov() or 60
 director.orig_pmi=GetPostMotionIntensity and GetPostMotionIntensity() or 0
 director.orig_weapon=GetPlayerWeaponID and GetPlayerWeaponID() or 0
 director.orig_flash=GetGamePlayerStateFlashlightKeyEnabled and GetGamePlayerStateFlashlightKeyEnabled() or 1
 if SetPostMotionIntensity then SetPostMotionIntensity(0) end
 if SetCameraOverride then SetCameraOverride(3) end
 if SetFlashLightKeyEnabled then SetFlashLightKeyEnabled(0) end
 if SetPlayerWeapons then SetPlayerWeapons(0) end
 if HideHuds then HideHuds() end
 if radar_hideallsprites then radar_hideallsprites() end
 log('begin 17-shot deterministic insertion')
end
local function restore(skipped)
 if director.finished then return end;director.finished=true
 if SetCameraOverride then SetCameraOverride(0) end
 if SetCameraPanelFOV and director.orig_fov then SetCameraPanelFOV(director.orig_fov) end
 if SetPostMotionIntensity and director.orig_pmi then SetPostMotionIntensity(director.orig_pmi) end
 if SetPlayerWeapons then SetPlayerWeapons(1) end
 if ChangePlayerWeaponID and director.orig_weapon then ChangePlayerWeaponID(director.orig_weapon) end
 if SetFlashLightKeyEnabled and director.orig_flash~=nil then SetFlashLightKeyEnabled(director.orig_flash) end
 if ShowHuds then ShowHuds() end
 if radar_showallsprites then radar_showallsprites() end
 if fl_dialogue_cancel and skipped then fl_dialogue_cancel() end
 if aegis then
  aegis.opening_director_active=false
  aegis.insertion_complete=true
  aegis.opening_started_at=nil
  aegis.opening_elapsed_ms=50800
  aegis.cinematic_active=false
  aegis.cinematic_beat=nil
  aegis.cinematic_started_at=nil
  aegis.cinematic_duration_ms=nil
  aegis.music_cinematic_duck=false
  -- Keep a harmless non-camera request in place so the legacy coordinator cannot
  -- re-launch ARRIVAL_PERIM after this director hands control back to the player.
  aegis.cinematic_request='OPENING_DIRECTOR_DONE'
 end
 if fl then fl.objective_pulse_until=g_Time+3500 end
 log(skipped and 'skip complete' or 'opening complete')
end

function firstlight_opening_director_init(e)
 director={started=false,finished=false,start_ms=0,shot=0,cameras={},lines={}}
 Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
 if aegis then aegis.opening_director_active=false end
end

function firstlight_opening_director_main(e)
 if director.finished or not fl or not fl.started or not aegis then return end
 if not director.started then
  -- Reserve the opening immediately, even if camera entities are still finishing their
  -- first-frame registration. This closes the race where the legacy coordinator could
  -- launch ARRIVAL_PERIM while this director was still scanning its 17 source mounts.
  if not aegis.insertion_complete then aegis.cinematic_request='OPENING_DIRECTOR_LOCK' end
  if g_Time-(fl.born or g_Time)>=120 then begin() end
  return
 end
 local ms=g_Time-director.start_ms
 aegis.opening_elapsed_ms=ms
 if g_KeyPressSPACE==1 and ms>250 then restore(true);return end
 if ms>=50800 then restore(false);return end
 local i,s=shot_for(ms);local obj=director.cameras[i]
 if i~=director.shot then
  director.shot=i
  log('cut '..tostring(i)..'/17 '..s.beat..' source='..s.name)
 end
 local x,y,z,rx,ry,rz=camera_pose(obj)
 if x then
  if SetCameraPosition then SetCameraPosition(0,x,y,z) end
  if SetCameraAngle then SetCameraAngle(0,rx,ry,rz) end
  local start=shot_start(i);local span=math.max(1,s.stop-start);local t=math.max(0,math.min(1,(ms-start)/span))
  local focal=s.fls+(s.fle-s.fls)*t
  if SetCameraPanelFOV then SetCameraPanelFOV(focal/2) end
 end
 aegis.cinematic_active=true;aegis.cinematic_beat=s.beat;aegis.cinematic_started_at=director.start_ms+shot_start(i);aegis.cinematic_duration_ms=s.stop-shot_start(i);aegis.music_cinematic_duck=true
 for _,ev in ipairs(EVENTS) do if ms>=ev.at then say(ev) end end
 if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end
end

function firstlight_opening_director_exit(e)
 if director.started and not director.finished then restore(true) end
end

firstlight_opening_director_init=firstlight_guard('firstlight_opening_director_init',firstlight_opening_director_init)
firstlight_opening_director_main=firstlight_guard('firstlight_opening_director_main',firstlight_opening_director_main)
firstlight_opening_director_exit=firstlight_guard('firstlight_opening_director_exit',firstlight_opening_director_exit)
