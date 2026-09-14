require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT insertion: one native camera owner, zero CineGuru opening cameras.
--
-- The ownership model stays native/HUD-driven because that path is deterministic in
-- MAX, but the film language now deliberately follows CineGuru's strengths: composed
-- tracking shots, movement within a shot, focal progression and restrained vibration.
-- The Kestrel is the subject; the environment supplies scale and context.
local opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,ship_entity=nil,lines={},logged_wait=false}

-- Ship-relative cameras remain outside the Broadwing's ~800 x 704 inch envelope.
-- off -> off2 and look -> look2 form a smooth virtual camera move during each shot.
-- Fixed infrastructure cameras can also creep along a short rail while auto-tracking.
local SHOTS={
 {beat='ARRIVAL_NOSE',stop=2800,label='KSTL-01 FORWARD CHASE // LIVE',carrier='ship',off={520,280,-1350},off2={250,330,-1150},look={0,90,-40},look2={0,108,-105},clear=120,roll=.14,shake=2.4,fls=62,fle=54},
 {beat='ARRIVAL_PORT_FWD',stop=5600,label='KSTL-02 PORT FORMATION // LIVE',carrier='ship',off={-1250,240,-420},off2={-980,310,-210},look={0,95,0},look2={0,110,-80},clear=100,roll=.16,shake=2.0,fls=60,fle=52},
 {beat='ARRIVAL_ISR',stop=8400,label='KSTL-03 HIGH TRACK // LIVE',carrier='ship',off={0,1050,-850},off2={260,900,-520},look={0,70,0},look2={0,85,-110},clear=180,roll=.08,shake=.8,fls=68,fle=58},
 {beat='ARRIVAL_GATE',stop=11400,label='M12-GATE-02 // AUTO TRACK',carrier='world',x=-520,z=-10120,h=260,x2=-430,z2=-10040,h2=285,trackship=true,look={0,80,0},fls=72,fle=60},
 {beat='ARRIVAL_STBD',stop=14500,label='KSTL-04 STBD FORMATION // LIVE',carrier='ship',off={1250,220,-260},off2={1020,300,-80},look={0,95,0},look2={0,108,-70},clear=100,roll=.18,shake=2.0,fls=60,fle=52},
 {beat='ARRIVAL_TAIL',stop=17500,label='KSTL-05 REAR CHASE // LIVE',carrier='ship',off={0,300,1450},off2={300,255,1200},look={0,95,80},look2={0,108,20},clear=120,roll=.18,shake=2.2,fls=62,fle=52},
 {beat='ARRIVAL_CONVERT',stop=20500,label='KSTL-06 CONVERSION OBS // LIVE',carrier='ship',off={980,210,980},off2={760,165,790},look={0,70,0},look2={0,45,65},clear=100,roll=.12,shake=3.2,fls=58,fle=48},
 {beat='ARRIVAL_BELLY',stop=23500,label='KSTL-07 LOWER PORT OBS // LIVE',carrier='ship',off={-920,-320,760},off2={-760,-210,620},look={0,20,0},look2={0,5,40},clear=70,roll=.08,shake=2.2,fls=56,fle=46},
 {beat='ARRIVAL_GEAR',stop=26500,label='KSTL-08 GEAR OBS // LIVE',carrier='ship',off={820,-240,820},off2={650,-150,600},look={0,-25,0},look2={0,-35,55},clear=55,roll=.06,shake=1.5,fls=54,fle=44},
 {beat='ARRIVAL_LZ',stop=29500,label='LZ07-PERIM-01 // AUTO TRACK',carrier='world',x=610,z=-9420,h=190,x2=540,z2=-9360,h2=210,trackship=true,look={0,70,0},fls=68,fle=56},
 {beat='ARRIVAL_GEAR_CLOSE',stop=32500,label='KSTL-08 GEAR CLOSE // LIVE',carrier='ship',off={600,-150,610},off2={520,-90,520},look={0,-20,0},look2={0,-32,70},clear=45,roll=.05,shake=1.0,fls=50,fle=42},
 {beat='ARRIVAL_TOUCHDOWN',stop=35500,label='LZ07-PAD-03 // AUTO TRACK',carrier='world',x=260,z=-9270,h=95,x2=300,z2=-9220,h2=108,trackship=true,look={0,65,0},fls=64,fle=54},
 {beat='ARRIVAL_RAMP',stop=38500,label='KSTL-09 REAR RAMP OBS // LIVE',carrier='ship',off={0,190,1350},off2={250,175,1200},look={0,60,245},look2={0,55,300},clear=80,roll=.06,shake=.7,fls=56,fle=48},
 {beat='ARRIVAL_DEPLOY',stop=42700,label='KSTL-10 PORT REAR OBS // DEPLOY',carrier='ship',off={-900,130,1100},off2={-650,165,850},look={0,60,230},look2={0,52,315},clear=70,roll=.04,shake=.6,fls=54,fle=46},
 {beat='ARRIVAL_LIFTOFF',stop=45300,label='LZ07-LIFT CAM // AUTO TRACK',carrier='world',x=520,z=-9300,h=85,x2=570,z2=-9250,h2=105,trackship=true,look={0,80,0},fls=64,fle=54},
 {beat='ARRIVAL_CLIMB',stop=47800,label='KSTL-11 PORT CHASE // CLIMB',carrier='ship',off={-1150,320,950},off2={-900,390,650},look={0,90,50},look2={0,115,-60},clear=120,roll=.16,shake=2.6,fls=60,fle=50},
 {beat='ARRIVAL_DEPART',stop=50800,label='KSTL-12 LONG REAR CHASE // DEPART',carrier='ship',off={0,420,1850},off2={300,510,1450},look={0,110,80},look2={0,125,-20},clear=160,roll=.18,shake=2.2,fls=66,fle=56},
}

local EVENTS={
 {at=200,id='FL01_KES_001',speaker='KESTREL',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.',seconds=7.987},
 {at=8550,id='FL01_KES_002',speaker='KESTREL',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.',seconds=9.189},
 {at=17800,id='FL01_KES_003',speaker='KESTREL',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=8.64},
 {at=26600,id='FL01_KES_004',speaker='KESTREL',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.',seconds=11.67},
 {at=38700,id='FL01_KES_005',speaker='KESTREL',text='You are down. I will stay high and dark until you call for extraction.',seconds=3.6},
}

local rad,deg=math.rad,math.deg
local sin,cos,sqrt=math.sin,math.cos,math.sqrt
local atan=math.atan2
local function log(msg)if fl_log then fl_log('opening-native '..tostring(msg)) end end
local function clamp01(t)if t<0 then return 0 elseif t>1 then return 1 end;return t end
local function smooth(t)t=clamp01(t);return t*t*(3-2*t) end
local function lerp(a,b,t)return a+(b-a)*t end
local function lerp3(a,b,t)
 b=b or a
 return {lerp(a[1],b[1],t),lerp(a[2],b[2],t),lerp(a[3],b[3],t)}
end
local function ground(x,z)
 if GetGroundHeight then local ok,h=pcall(GetGroundHeight,x,z);if ok and type(h)=='number' then return h end end
 return 0
end
local function look_angles(cx,cy,cz,tx,ty,tz,roll)
 local dx,dy,dz=tx-cx,ty-cy,tz-cz;local flat=math.max(.001,sqrt(dx*dx+dz*dz))
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
 return nil
end

-- MAX's g_Entity can behave like an engine-backed sparse table. Do not rely on
-- pairs() discovering every entity. Walk numeric IDs and cache the FLIGHT object;
-- every visual Kestrel state follows the same authored pose, so this hidden object is
-- a stable transform parent even while another state mesh is visible.
local function find_ship()
 if opening.ship_obj and GetObjectPosAng then
  local ok,x=pcall(function()local px=GetObjectPosAng(opening.ship_obj);return px end)
  if ok and x then return true end
 end
 if not g_Entity then return false end
 for id=1,4096 do
  local ent=g_Entity[id]
  if ent and ent.obj then
   local name=entity_name(id)
   if name=='FL KESTREL INSERTION FLIGHT' then
    opening.ship_entity=id;opening.ship_obj=ent.obj
    log('acquired Kestrel entity='..tostring(id)..' object='..tostring(ent.obj))
    return true
   end
  end
 end
 return false
end
local function ship_transform()
 if not find_ship() or not GetObjectPosAng then return nil end
 local sx,sy,sz,srx,sry,srz=GetObjectPosAng(opening.ship_obj);if not sx then return nil end
 return sx,sy,sz,srx or 0,sry or 0,srz or 0
end
local function shot_for(ms)for i,s in ipairs(SHOTS) do if ms<s.stop then return i,s end end;return #SHOTS,SHOTS[#SHOTS] end
local function shot_start(i)return i<=1 and 0 or SHOTS[i-1].stop end
local function tracked_ship_target(s,t)
 local sx,sy,sz,srx,sry,srz=ship_transform();if not sx then return nil end
 local look=lerp3(s.look or {0,80,0},s.look2,t);local lx,ly,lz=rotate_local(look[1],look[2],look[3],srx,sry,srz)
 return sx+lx,sy+ly,sz+lz,srz
end
local function world_pose(s,t)
 local x=lerp(s.x,s.x2 or s.x,t);local z=lerp(s.z,s.z2 or s.z,t);local h=lerp(s.h,s.h2 or s.h,t);local y=ground(x,z)+h
 local tx,ty,tz,shiproll
 if s.trackship then tx,ty,tz,shiproll=tracked_ship_target(s,t) end
 if not tx then
  tx=s.tx or x;tz=s.tz or (z+100);ty=ground(tx,tz)+(s.th or 80);shiproll=0
 end
 local rx,ry,rz=look_angles(x,y,z,tx,ty,tz,(shiproll or 0)*(s.roll or 0));return x,y,z,rx,ry,rz
end
local function ship_pose(s,t,ms)
 local sx,sy,sz,srx,sry,srz=ship_transform();if not sx then return nil end
 local off=lerp3(s.off,s.off2,t);local look=lerp3(s.look or {0,80,0},s.look2,t)
 local amp=s.shake or 0
 if amp>0 then
  local phase=(ms or 0)*.001
  off[1]=off[1]+sin(phase*13.1+s.stop*.001)*amp
  off[2]=off[2]+sin(phase*17.7+s.stop*.0007)*amp*.45
  off[3]=off[3]+sin(phase*11.3+s.stop*.0003)*amp*.35
 end
 local dx,dy,dz=rotate_local(off[1],off[2],off[3],srx,sry,srz)
 local cx,cy,cz=sx+dx,sy+dy,sz+dz
 local floor=ground(cx,cz)+(s.clear or 60);if cy<floor then cy=floor end
 local lx,ly,lz=rotate_local(look[1],look[2],look[3],srx,sry,srz)
 local tx,ty,tz=sx+lx,sy+ly,sz+lz
 local rigroll=srz*(s.roll or 0)
 if amp>0 then rigroll=rigroll+sin((ms or 0)*.017+s.stop*.001)*amp*.035 end
 local rx,ry,rz=look_angles(cx,cy,cz,tx,ty,tz,rigroll);return cx,cy,cz,rx,ry,rz
end
local function pose_for(s,t,ms)if s.carrier=='world' then return world_pose(s,t) end;return ship_pose(s,t,ms) end
local function say(ev)
 if opening.lines[ev.id] then return end;opening.lines[ev.id]=true
 if fl_dialogue and fl_dialogue(ev.id) then return end
 if fl_say then fl_say(ev.speaker..': '..ev.text,'',ev.seconds) end
end
local function draw_source(s,i)
 if Panel then Panel(1.5,1.5,33,7.8) end
 if TextCenterOnXColor then
  TextCenterOnXColor(17.2,2.7,1,s.label,103,220,230)
  TextCenterOnXColor(17.2,5.6,1,'VANGUARD KESTREL // INSERTION FEED',144,165,178)
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
  aegis.opening_started_at=nil;aegis.opening_elapsed_ms=50800;aegis.opening_shot_progress=nil;aegis.cinematic_active=false;aegis.cinematic_beat=nil
  aegis.cinematic_started_at=nil;aegis.cinematic_duration_ms=nil;aegis.music_cinematic_duck=false
  aegis.cinematic_request='OPENING_NATIVE_DONE'
 end
 if fl then fl.objective_pulse_until=(g_Time or 0)+3500 end
 log(skipped and 'skip complete' or 'opening complete')
end
local function begin()
 if opening.started or opening.finished then return end
 if not find_ship() then
  if not opening.logged_wait then log('waiting for numeric Kestrel entity scan');opening.logged_wait=true end
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
  aegis.opening_elapsed_ms=0;aegis.opening_shot_progress=0;aegis.music_cinematic_duck=true
 end
 if FreezePlayer then FreezePlayer() end
 if SetCameraOverride then SetCameraOverride(3) end
 if SetPostMotionIntensity then SetPostMotionIntensity(0) end
 if SetFlashLightKeyEnabled then SetFlashLightKeyEnabled(0) end
 if SetPlayerWeapons then SetPlayerWeapons(0) end
 if HideHuds then HideHuds() end
 if radar_hideallsprites then radar_hideallsprites() end
 log('begin CineGuru-inspired Kestrel-subject 17-shot insertion')
end

function fl_opening_native_reset()
 opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,ship_entity=nil,lines={},logged_wait=false}
end

function fl_opening_native_tick()
 if opening.finished or not fl or not fl.started or not aegis then return false end
 if not opening.started then
  if not aegis.insertion_complete then aegis.cinematic_request='OPENING_NATIVE_LOCK' end
  if (g_Time or 0)-(fl.born or (g_Time or 0))>=40 then begin() end
  if not opening.started then return false end
 end
 local ms=(g_Time or 0)-opening.start_ms;aegis.opening_elapsed_ms=ms
 if g_KeyPressSPACE==1 and ms>250 then release(true);return false end
 if ms>=50800 then release(false);return false end
 local i,s=shot_for(ms)
 if i~=opening.shot then opening.shot=i;log('cut '..tostring(i)..'/17 '..s.beat..' '..s.label) end
 local start=shot_start(i);local span=math.max(1,s.stop-start);local t=smooth((ms-start)/span);aegis.opening_shot_progress=t
 local x,y,z,rx,ry,rz=pose_for(s,t,ms)
 if x then
  if SetCameraOverride then SetCameraOverride(3) end
  if SetCameraPosition then SetCameraPosition(0,x,y,z) end
  if SetCameraAngle then SetCameraAngle(0,rx,ry,rz) end
  -- SetCameraPanelFOV consumes degrees directly. Do not halve authored CineGuru-style
  -- FOV values; doing so turned a normal ~60 degree shot into a telephoto ~30 degree view.
  local focal=lerp(s.fls,s.fle,t);if SetCameraPanelFOV then SetCameraPanelFOV(focal) end
 else
  log('camera pose unavailable beat='..s.beat)
 end
 aegis.opening_native_active=true;aegis.cinematic_active=true;aegis.cinematic_beat=s.beat
 aegis.cinematic_started_at=opening.start_ms+start;aegis.cinematic_duration_ms=s.stop-start;aegis.music_cinematic_duck=true
 for _,ev in ipairs(EVENTS) do if ms>=ev.at then say(ev) end end
 draw_source(s,i)
 if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end
 return true
end
