require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT opening camera owner.
--
-- This module is intentionally called from firstlight_hud.lua, a mission path that is
-- already proven to execute every frame in native MAX. It does not activate CineGuru
-- and it does not read the 17 authored camera entities. World/security shots are
-- computed directly; Kestrel shots are derived directly from the live insertion
-- airframe. One clock, one camera writer, no entity scheduling dependency.
local opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,lines={},logged_wait=false}

local SHOTS={
 {beat='ARRIVAL_PERIM',stop=2800,label='M12-PERIM-04 // LIVE',carrier='world',x=-1050,z=-10350,h=165,tx=-2350,tz=-11320,th=760,fls=88,fle=82},
 {beat='ARRIVAL_NOSE',stop=5800,label='KSTL-01 NOSE EO // LIVE',carrier='ship',off={0,154,-378},aim={0,-0.08,-1},roll=1.0,fls=58,fle=62},
 {beat='ARRIVAL_GATE',stop=8400,label='M12-GATE-02 // LIVE',carrier='world',x=-520,z=-10120,h=115,tx=-1100,tz=-10460,th=560,fls=92,fle=84},
 {beat='ARRIVAL_STBD',stop=11400,label='KSTL-02 STBD SHOULDER // LIVE',carrier='ship',off={360,112,20},aim={-1,-0.10,0.32},roll=1.0,fls=52,fle=56},
 {beat='ARRIVAL_ISR',stop=14500,label='KSTL-03 VENTRAL ISR // TRACK',carrier='ship',off={0,48,-60},target={-240,-8750,120},roll=0.12,fls=96,fle=88},
 {beat='ARRIVAL_MAST',stop=17500,label='M12-MAST-01 // LIVE',carrier='world',x=-2230,z=-7300,h=190,tx=610,tz=-9510,th=520,fls=78,fle=86},
 {beat='ARRIVAL_CONVERT',stop=20500,label='KSTL-03A VENTRAL AFT // LIVE',carrier='ship',off={0,54,235},aim={0,-0.22,-1},roll=0.78,fls=48,fle=54},
 {beat='ARRIVAL_BELLY',stop=23500,label='KSTL-04 BELLY SERVICE // LIVE',carrier='ship',off={-125,46,90},aim={0.34,-0.58,-1},roll=0.72,fls=46,fle=52},
 {beat='ARRIVAL_GEAR',stop=26500,label='KSTL-04 STBD GEAR // LIVE',carrier='ship',off={250,42,110},aim={-0.18,-1,0.20},roll=0.75,fls=50,fle=54},
 {beat='ARRIVAL_LZ',stop=29500,label='LZ07-PERIM-01 // LIVE',carrier='world',x=610,z=-9420,h=120,tx=80,tz=-9020,th=320,fls=88,fle=80},
 {beat='ARRIVAL_FLARE',stop=32500,label='LZ07-BEACON-02 // LIVE',carrier='world',x=-620,z=-8990,h=55,tx=-120,tz=-9140,th=190,fls=72,fle=68},
 {beat='ARRIVAL_TOUCHDOWN',stop=35500,label='LZ07-PAD-03 // LIVE',carrier='world',x=260,z=-9270,h=24,tx=-120,tz=-9140,th=82,fls=62,fle=58},
 {beat='ARRIVAL_RAMP',stop=38500,label='KSTL-05 RAMP // LIVE',carrier='ship',off={0,138,410},aim={0,-0.18,1},roll=0.35,fls=54,fle=58},
 {beat='ARRIVAL_DEPLOY',stop=42700,label='KSTL-05 RAMP // DEPLOY',carrier='ship',off={0,138,410},aim={0,-0.22,1},roll=0.35,fls=58,fle=62},
 {beat='ARRIVAL_LIFTOFF',stop=45300,label='KSTL-05 RAMP // LIVE',carrier='ship',off={0,138,410},aim={0,-0.22,1},roll=0.40,fls=54,fle=58},
 {beat='ARRIVAL_CLIMB',stop=47800,label='KSTL-06 PORT SHOULDER // LIVE',carrier='ship',off={-360,112,30},aim={1,-0.08,0.25},roll=1.0,fls=50,fle=56},
 {beat='ARRIVAL_DEPART',stop=50800,label='KSTL-07 TAIL // LIVE',carrier='ship',off={0,158,420},aim={0,-0.05,1},roll=1.0,fls=62,fle=72},
}

local EVENTS={
 {at=200,id='FL01_KES_001',speaker='KESTREL',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.',seconds=7.987},
 {at=8550,id='FL01_KES_002',speaker='KESTREL',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.',seconds=9.189},
 {at=17800,id='FL01_KES_003',speaker='KESTREL',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=8.64},
 {at=26600,id='FL01_KES_004',speaker='KESTREL',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.',seconds=11.67},
 {at=38700,id='FL01_KES_005',speaker='KESTREL',text='You are down. I will stay high and dark until you call for extraction.',seconds=3.6},
}

local rad=math.rad
local deg=math.deg
local sin=math.sin
local cos=math.cos
local sqrt=math.sqrt
local atan=math.atan2

local function log(msg)if fl_log then fl_log('opening-native '..tostring(msg)) end end
local function ground(x,z)
 if GetGroundHeight then local ok,h=pcall(GetGroundHeight,x,z);if ok and type(h)=='number' then return h end end
 return 0
end
local function look_angles(cx,cy,cz,tx,ty,tz,roll)
 local dx,dy,dz=tx-cx,ty-cy,tz-cz;local flat=math.max(0.001,sqrt(dx*dx+dz*dz))
 return -deg(atan(dy,flat)),deg(atan(dx,dz)),roll or 0
end
local function rotate_local(x,y,z,rx,ry,rz)
 local cr,sr=cos(rad(rz)),sin(rad(rz));local x1,y1,z1=x*cr-y*sr,x*sr+y*cr,z
 local cp,sp=cos(rad(rx)),sin(rad(rx));local x2,y2,z2=x1,y1*cp-z1*sp,y1*sp+z1*cp
 local cy,sy=cos(rad(ry)),sin(rad(ry));return x2*cy+z2*sy,y2,-x2*sy+z2*cy
end
local function entity_name(e)
 if not e or not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e);if ok then return name end
end
local function find_ship()
 if opening.ship_obj and GetObjectPosAng then
  local ok,x=pcall(function()local px=GetObjectPosAng(opening.ship_obj);return px end)
  if ok and x then return true end
 end
 if not g_Entity then return false end
 for id,ent in pairs(g_Entity) do
  if ent and ent.obj and entity_name(id)=='FL KESTREL INSERTION FLIGHT' then opening.ship_obj=ent.obj;return true end
 end
 return false
end
local function shot_for(ms)
 for i,s in ipairs(SHOTS) do if ms<s.stop then return i,s end end
 return #SHOTS,SHOTS[#SHOTS]
end
local function shot_start(i)return i<=1 and 0 or SHOTS[i-1].stop end
local function world_pose(s)
 local x,z=s.x,s.z;local y=ground(x,z)+s.h
 local tx,tz=s.tx,s.tz;local ty=ground(tx,tz)+s.th
 local rx,ry,rz=look_angles(x,y,z,tx,ty,tz,0);return x,y,z,rx,ry,rz
end
local function ship_pose(s)
 if not find_ship() or not GetObjectPosAng then return nil end
 local sx,sy,sz,srx,sry,srz=GetObjectPosAng(opening.ship_obj);if not sx then return nil end
 srx,sry,srz=srx or 0,sry or 0,srz or 0
 local dx,dy,dz=rotate_local(s.off[1],s.off[2],s.off[3],srx,sry,srz)
 local cx,cy,cz=sx+dx,sy+dy,sz+dz;local tx,ty,tz
 if s.target then
  tx,tz=s.target[1],s.target[2];ty=ground(tx,tz)+s.target[3]
 else
  local ax,ay,az=rotate_local(s.aim[1],s.aim[2],s.aim[3],srx,sry,srz)
  tx,ty,tz=cx+ax*1000,cy+ay*1000,cz+az*1000
 end
 local rx,ry,rz=look_angles(cx,cy,cz,tx,ty,tz,srz*(s.roll or 1));return cx,cy,cz,rx,ry,rz
end
local function pose_for(s)if s.carrier=='world' then return world_pose(s) end;return ship_pose(s) end
local function say(ev)
 if opening.lines[ev.id] then return end;opening.lines[ev.id]=true
 if fl_dialogue and fl_dialogue(ev.id) then return end
 if fl_say then fl_say(ev.speaker..': '..ev.text,'',ev.seconds) end
end
local function draw_source(s,i)
 if Panel then Panel(2,2,34,9) end
 if TextCenterOnXColor then
  TextCenterOnXColor(18,3.0,1,s.label,103,220,230)
  TextCenterOnXColor(18,6.1,1,'MERIDIAN INSERTION // REC  '..string.format('%02d/17',i),144,165,178)
 end
 if aegis then aegis.camera_feed_label=s.label end
end
local function release(skipped)
 if opening.finished then return end;opening.finished=true
 if SetCameraOverride then SetCameraOverride(0) end
 if UnFreezePlayer then UnFreezePlayer() end
 if SetCameraPanelFOV and opening.orig_fov then SetCameraPanelFOV(opening.orig_fov) end
 if SetPostMotionIntensity and opening.orig_pmi then SetPostMotionIntensity(opening.orig_pmi) end
 if SetPlayerWeapons then SetPlayerWeapons(1) end
 if ChangePlayerWeaponID and opening.orig_weapon and opening.orig_weapon>0 then ChangePlayerWeaponID(opening.orig_weapon) end
 if SetFlashLightKeyEnabled and opening.orig_flash~=nil then SetFlashLightKeyEnabled(opening.orig_flash) end
 if ShowHuds then ShowHuds() end
 if radar_showallsprites then radar_showallsprites() end
 if fl_dialogue_cancel and skipped then fl_dialogue_cancel() end
 if aegis then
  aegis.opening_native_active=false;aegis.opening_director_active=false;aegis.insertion_complete=true
  aegis.opening_started_at=nil;aegis.opening_elapsed_ms=50800;aegis.cinematic_active=false;aegis.cinematic_beat=nil
  aegis.cinematic_started_at=nil;aegis.cinematic_duration_ms=nil;aegis.music_cinematic_duck=false
  aegis.cinematic_request='OPENING_NATIVE_DONE'
 end
 if fl then fl.objective_pulse_until=(g_Time or 0)+3500 end
 log(skipped and 'skip complete' or 'opening complete')
end
local function begin()
 if opening.started or opening.finished then return end
 if not find_ship() then
  if not opening.logged_wait then log('waiting for FL KESTREL INSERTION FLIGHT');opening.logged_wait=true end
  return
 end
 opening.started=true;opening.start_ms=g_Time or 0;opening.shot=0;opening.lines={}
 opening.orig_fov=GetGamePlayerStateCameraFov and GetGamePlayerStateCameraFov() or 60
 opening.orig_pmi=GetPostMotionIntensity and GetPostMotionIntensity() or 0
 opening.orig_weapon=GetPlayerWeaponID and GetPlayerWeaponID() or 0
 opening.orig_flash=GetGamePlayerStateFlashlightKeyEnabled and GetGamePlayerStateFlashlightKeyEnabled() or 1
 if fl then fl.message_until=0;fl.zone_until=0;fl.radio_queue={} end
 if aegis then
  aegis.opening_native_active=true;aegis.opening_director_active=false;aegis.insertion_complete=false
  aegis.cinematic_request='OPENING_NATIVE_LOCK';aegis.cinematic_active=true;aegis.opening_started_at=opening.start_ms
  aegis.opening_elapsed_ms=0;aegis.music_cinematic_duck=true
 end
 if FreezePlayer then FreezePlayer() end
 if SetCameraOverride then SetCameraOverride(3) end
 if SetPostMotionIntensity then SetPostMotionIntensity(0) end
 if SetFlashLightKeyEnabled then SetFlashLightKeyEnabled(0) end
 if SetPlayerWeapons then SetPlayerWeapons(0) end
 if HideHuds then HideHuds() end
 if radar_hideallsprites then radar_hideallsprites() end
 log('begin HUD-owned 17-shot insertion')
end

function fl_opening_native_reset()
 opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,lines={},logged_wait=false}
end

function fl_opening_native_tick()
 if opening.finished or not fl or not fl.started or not aegis then return false end
 if not opening.started then
  -- Claim the narrative request before the legacy cinematic coordinator can launch.
  if not aegis.insertion_complete then aegis.cinematic_request='OPENING_NATIVE_LOCK' end
  if (g_Time or 0)-(fl.born or (g_Time or 0))>=80 then begin() end
  if not opening.started then return false end
 end
 local ms=(g_Time or 0)-opening.start_ms;aegis.opening_elapsed_ms=ms
 if g_KeyPressSPACE==1 and ms>250 then release(true);return false end
 if ms>=50800 then release(false);return false end
 local i,s=shot_for(ms)
 if i~=opening.shot then opening.shot=i;log('cut '..tostring(i)..'/17 '..s.beat..' '..s.label) end
 local x,y,z,rx,ry,rz=pose_for(s)
 if x then
  -- Reassert override every frame; this is the same pattern used by MAX's stock
  -- security-camera/camera-override scripts and prevents player-camera logic from
  -- taking the view back between Lua ticks.
  if SetCameraOverride then SetCameraOverride(3) end
  if SetCameraPosition then SetCameraPosition(0,x,y,z) end
  if SetCameraAngle then SetCameraAngle(0,rx,ry,rz) end
  local start=shot_start(i);local span=math.max(1,s.stop-start);local t=math.max(0,math.min(1,(ms-start)/span))
  local focal=s.fls+(s.fle-s.fls)*t;if SetCameraPanelFOV then SetCameraPanelFOV(focal/2) end
 else
  log('camera pose unavailable beat='..s.beat)
 end
 aegis.opening_native_active=true;aegis.cinematic_active=true;aegis.cinematic_beat=s.beat
 aegis.cinematic_started_at=opening.start_ms+shot_start(i);aegis.cinematic_duration_ms=s.stop-shot_start(i);aegis.music_cinematic_duck=true
 for _,ev in ipairs(EVENTS) do if ms>=ev.at then say(ev) end end
 draw_source(s,i)
 if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end
 return true
end
