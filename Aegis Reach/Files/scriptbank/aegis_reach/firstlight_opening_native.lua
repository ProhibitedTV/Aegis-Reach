require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT insertion cinematic v2: one native camera owner, zero CineGuru opening cameras.
--
-- The original hard-replacement proved reliable but overused tiny hull-mounted feeds,
-- leaving the Kestrel itself unreadable against Vesper's night grade.  This pass keeps
-- the same 50.8 second aircraft choreography and 17 story beats, but alternates a few
-- genuine tactical feeds with authored exterior chase/three-quarter views that show the
-- ship, its conversion hardware, touchdown, ramp and departure.  Music cues are also
-- explicit and deterministic instead of merely ducking a free-running adaptive score.
local opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,ship_entity=nil,lines={},logged_wait=false,music_cue=0}

-- fovs/fove are actual camera FOV degrees.  Do not divide them as focal lengths: MAX's
-- SetCameraPanelFOV consumes field-of-view directly.
local SHOTS={
 {beat='ARRIVAL_NOSE',stop=2800,label='KSTL-01 // NOSE EO',carrier='ship',off={0,165,-438},aim={0,-0.025,-1},roll=.55,fovs=67,fove=63},
 {beat='ARRIVAL_PORT_FWD',stop=5600,label='KSTL EXT // PORT THREE-QUARTER',carrier='ship',off={-940,335,510},look={0,105,20},roll=.12,fovs=61,fove=56},
 {beat='ARRIVAL_ISR',stop=8400,label='KSTL EXT // HIGH ISR CHASE',carrier='ship',off={0,910,590},look={0,90,40},roll=.04,fovs=65,fove=58},
 {beat='ARRIVAL_GATE',stop=11400,label='M12-GATE-02 // SECURITY',carrier='world',x=-520,z=-10120,h=210,tx=-1100,tz=-10460,th=600,fovs=69,fove=64},
 {beat='ARRIVAL_STBD',stop=14500,label='KSTL EXT // STBD THREE-QUARTER',carrier='ship',off={900,300,660},look={0,108,35},roll=.10,fovs=58,fove=54},
 {beat='ARRIVAL_TAIL',stop=17500,label='KSTL EXT // ENGINE CHASE',carrier='ship',off={0,285,1240},look={0,105,120},roll=.08,fovs=62,fove=56},
 {beat='ARRIVAL_CONVERT',stop=20500,label='KSTL EXT // CONVERSION PORT',carrier='ship',off={-760,-40,850},look={0,65,80},roll=.06,fovs=55,fove=51},
 {beat='ARRIVAL_BELLY',stop=23500,label='KSTL EXT // VTOL BELLY',carrier='ship',off={650,-70,620},look={0,42,70},roll=.04,fovs=58,fove=53},
 {beat='ARRIVAL_GEAR',stop=26500,label='KSTL EXT // GEAR / LIFT',carrier='ship',off={720,-35,700},look={0,28,105},roll=.03,fovs=57,fove=52},
 {beat='ARRIVAL_LZ',stop=29500,label='LZ07-PERIM-01 // SECURITY',carrier='world',x=880,z=-9800,h=260,tx=-120,tz=-9140,th=120,fovs=72,fove=66},
 {beat='ARRIVAL_GEAR_CLOSE',stop=32500,label='KSTL EXT // FINAL HOVER',carrier='ship',off={-660,150,780},look={0,45,110},roll=.03,fovs=58,fove=54},
 {beat='ARRIVAL_TOUCHDOWN',stop=35500,label='LZ07-PAD-03 // TOUCHDOWN',carrier='world',x=760,z=-9740,h=190,tx=-120,tz=-9140,th=72,fovs=64,fove=58},
 {beat='ARRIVAL_RAMP',stop=38500,label='KSTL EXT // RAMP THREE-QUARTER',carrier='ship',off={-500,210,930},look={0,82,335},roll=.02,fovs=57,fove=52},
 {beat='ARRIVAL_DEPLOY',stop=42700,label='LZ07-PAD-04 // DEPLOY',carrier='world',x=-700,z=-9560,h=125,tx=-120,tz=-9140,th=62,fovs=61,fove=56},
 {beat='ARRIVAL_LIFTOFF',stop=45300,label='KSTL EXT // POWERED LIFT',carrier='ship',off={720,250,980},look={0,95,120},roll=.04,fovs=61,fove=57},
 {beat='ARRIVAL_CLIMB',stop=47800,label='KSTL EXT // CLIMB PORT',carrier='ship',off={-900,390,1120},look={0,105,70},roll=.10,fovs=63,fove=58},
 {beat='ARRIVAL_DEPART',stop=50800,label='KSTL EXT // DEPARTURE CHASE',carrier='ship',off={0,360,1380},look={0,110,160},roll=.12,fovs=65,fove=58},
}

local EVENTS={
 {at=200,id='FL01_KES_001',speaker='KESTREL',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.',seconds=7.987},
 {at=8550,id='FL01_KES_002',speaker='KESTREL',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.',seconds=9.189},
 {at=17800,id='FL01_KES_003',speaker='KESTREL',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=8.64},
 {at=26600,id='FL01_KES_004',speaker='KESTREL',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.',seconds=11.67},
 {at=38700,id='FL01_KES_005',speaker='KESTREL',text='You are down. I will stay high and dark until you call for extraction.',seconds=3.6},
}

-- Exact score edits for the opening.  The score controller restarts each requested
-- master when cue_serial advances, then performs the crossfade itself.
local MUSIC_CUES={
 {at=0,track='salt_moon_drift',volume=60},
 {at=8400,track='moon_outpost_drift',volume=64},
 {at=23500,track='orbital_catacomb',volume=62},
 {at=42700,track='salt_moon_drift',volume=60},
}

local rad,deg=math.rad,math.deg
local sin,cos,sqrt=math.sin,math.cos,math.sqrt
local atan=math.atan2
local function log(msg)if fl_log then fl_log('opening-native '..tostring(msg)) end end
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

-- MAX's g_Entity can behave like an engine-backed sparse table.  Walk numeric IDs
-- and cache the FLIGHT object; that hidden state follows the continuous insertion
-- trajectory even while CONVERT/FLARE/LANDED is the visible mesh.
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
local function shot_for(ms)for i,s in ipairs(SHOTS) do if ms<s.stop then return i,s end end;return #SHOTS,SHOTS[#SHOTS] end
local function shot_start(i)return i<=1 and 0 or SHOTS[i-1].stop end
local function world_pose(s)
 local x,z=s.x,s.z;local y=ground(x,z)+s.h;local tx,tz=s.tx,s.tz;local ty=ground(tx,tz)+s.th
 local rx,ry,rz=look_angles(x,y,z,tx,ty,tz,0);return x,y,z,rx,ry,rz
end
local function ship_pose(s)
 if not find_ship() or not GetObjectPosAng then return nil end
 local sx,sy,sz,srx,sry,srz=GetObjectPosAng(opening.ship_obj);if not sx then return nil end
 srx,sry,srz=srx or 0,sry or 0,srz or 0
 local dx,dy,dz=rotate_local(s.off[1],s.off[2],s.off[3],srx,sry,srz)
 local cx,cy,cz=sx+dx,sy+dy,sz+dz;local tx,ty,tz
 if s.look then
  local lx,ly,lz=rotate_local(s.look[1],s.look[2],s.look[3],srx,sry,srz)
  tx,ty,tz=sx+lx,sy+ly,sz+lz
 elseif s.target then
  tx,tz=s.target[1],s.target[2];ty=ground(tx,tz)+s.target[3]
 else
  local ax,ay,az=rotate_local(s.aim[1],s.aim[2],s.aim[3],srx,sry,srz)
  tx,ty,tz=cx+ax*1000,cy+ay*1000,cz+az*1000
 end
 local rx,ry,rz=look_angles(cx,cy,cz,tx,ty,tz,srz*(s.roll or 0));return cx,cy,cz,rx,ry,rz
end
local function pose_for(s)if s.carrier=='world' then return world_pose(s) end;return ship_pose(s) end
local function say(ev)
 if opening.lines[ev.id] then return end;opening.lines[ev.id]=true
 if fl_dialogue and fl_dialogue(ev.id) then return end
 if fl_say then fl_say(ev.speaker..': '..ev.text,'',ev.seconds) end
end
local function update_music(ms)
 if not aegis then return end
 for i,cue in ipairs(MUSIC_CUES) do
  if ms>=cue.at and opening.music_cue<i then
   opening.music_cue=i
   aegis.cinematic_music_track=cue.track
   aegis.cinematic_music_volume=cue.volume
   aegis.cinematic_music_cue_serial=(aegis.cinematic_music_cue_serial or 0)+1
   log('music cue '..tostring(i)..' '..cue.track..' @ '..tostring(ms)..'ms')
  end
 end
end
local function draw_source(s,i)
 if Panel then Panel(1.7,1.7,40,11.4) end
 if TextCenterOnXColor then
  TextCenterOnXColor(20.5,3.1,2,s.label,104,224,232)
  TextCenterOnXColor(20.5,7.0,1,'MERIDIAN INSERTION  //  REC '..string.format('%02d',i)..' / 17',145,166,178)
  TextCenterOnXColor(91,96.2,1,'SPACE // SKIP',150,166,176)
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
  aegis.cinematic_music_track=nil;aegis.cinematic_music_volume=nil
  aegis.cinematic_music_cue_serial=(aegis.cinematic_music_cue_serial or 0)+1
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
 opening.started=true;opening.start_ms=g_Time or 0;opening.shot=0;opening.lines={};opening.music_cue=0
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
 update_music(0)
 log('begin cinematic-v2 17-shot insertion')
end

function fl_opening_native_reset()
 opening={started=false,finished=false,start_ms=0,shot=0,ship_obj=nil,ship_entity=nil,lines={},logged_wait=false,music_cue=0}
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
 update_music(ms)
 local i,s=shot_for(ms)
 if i~=opening.shot then opening.shot=i;log('cut '..tostring(i)..'/17 '..s.beat..' '..s.label) end
 local x,y,z,rx,ry,rz=pose_for(s)
 if x then
  if SetCameraOverride then SetCameraOverride(3) end
  if SetCameraPosition then SetCameraPosition(0,x,y,z) end
  if SetCameraAngle then SetCameraAngle(0,rx,ry,rz) end
  local start=shot_start(i);local span=math.max(1,s.stop-start);local t=math.max(0,math.min(1,(ms-start)/span))
  local fov=s.fovs+(s.fove-s.fovs)*t;if SetCameraPanelFOV then SetCameraPanelFOV(fov) end
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
