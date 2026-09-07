require 'scriptbank\\aegis_reach\\firstlight_audit'
-- DESCRIPTION: Robust adaptive Aegis Reach score controller for GameGuru MAX.
--
-- The previous version depended on three entity Sound slots. That was fragile: the
-- large Suno masters are staged locally at deploy time, so a missing slot produced a
-- completely silent game. MAX has a simpler native path for persistent music:
-- LoadGlobalSound / LoopGlobalSound / SetGlobalSoundVolume.
--
-- This controller loads the three authored cues directly and ALWAYS loads the small
-- checked-in reach-underscore.wav as a fallback. If any Suno master is absent, the
-- game still has music instead of failing silently.
local music={}

local TRACK_SALT=0
local TRACK_OUTPOST=1
local TRACK_CATACOMB=2
local TRACK_COUNT=3

local GLOBAL_IDS={
 [TRACK_SALT]=211,
 [TRACK_OUTPOST]=212,
 [TRACK_CATACOMB]=213
}
local FALLBACK_ID=214

local audit_paths={}
local userprofile=os.getenv and os.getenv("USERPROFILE") or nil
if userprofile and userprofile~="" then
 table.insert(audit_paths,userprofile.."/Documents/GameGuruApps/GameGuruMAX/Files/aegis-native-runtime.log")
end
table.insert(audit_paths,"aegis-native-runtime.log")
table.insert(audit_paths,"../Design/native-runtime.log")
table.insert(audit_paths,"Design/native-runtime.log")

local function audit(message)
 pcall(function()
  for _,path in ipairs(audit_paths) do
   local file=io.open(path,"a")
   if file then
    file:write(os.date("%Y-%m-%d %H:%M:%S")," ",message,"\n")
    file:close()
    return
   end
  end
 end)
end

local function track_name(slot)
 if slot==TRACK_SALT then return "salt_moon_drift" end
 if slot==TRACK_OUTPOST then return "moon_outpost_drift" end
 if slot==TRACK_CATACOMB then return "orbital_catacomb" end
 return "unknown"
end

local function track_for_state(state)
 if state=="exploration_vesper" then return TRACK_SALT,52 end
 if state=="discovery_human" then return TRACK_SALT,58 end
 if state=="exploration_fortress" then return TRACK_OUTPOST,48 end
 if state=="combat" then return TRACK_OUTPOST,66 end
 if state=="combat_overcharge" then return TRACK_OUTPOST,70 end
 if state=="resolution_aegis" then return TRACK_OUTPOST,62 end
 if state=="tension_aegis" then return TRACK_CATACOMB,56 end
 if state=="combat_interference" then return TRACK_CATACOMB,66 end
 if state=="discovery_choir" then return TRACK_CATACOMB,62 end
 return TRACK_SALT,46
end

local function delete_if_loaded(id)
 if GetGlobalSoundExist and GetGlobalSoundExist(id)==1 then DeleteGlobalSound(id) end
end

local function load_score()
 for slot=0,TRACK_COUNT-1 do delete_if_loaded(GLOBAL_IDS[slot]) end
 delete_if_loaded(FALLBACK_ID)

 -- Keep these calls literal. MAX's standalone collector scans Lua for literal
 -- LoadGlobalSound references and can therefore package the score correctly.
 LoadGlobalSound("audiobank\\aegis_reach\\music\\salt_moon_drift.wav",GLOBAL_IDS[TRACK_SALT])
 LoadGlobalSound("audiobank\\aegis_reach\\music\\moon_outpost_drift.wav",GLOBAL_IDS[TRACK_OUTPOST])
 LoadGlobalSound("audiobank\\aegis_reach\\music\\orbital_catacomb.wav",GLOBAL_IDS[TRACK_CATACOMB])
 LoadGlobalSound("audiobank\\aegis_reach\\reach-underscore.wav",FALLBACK_ID)
end

local function exists(id)
 return GetGlobalSoundExist and GetGlobalSoundExist(id)==1
end

local function resolved_id(slot)
 local id=GLOBAL_IDS[slot]
 if exists(id) then return id,false end
 if exists(FALLBACK_ID) then return FALLBACK_ID,true end
 return -1,true
end

local function ensure_looping(id)
 if id<0 or not exists(id) then return end
 if GetGlobalSoundPlaying and GetGlobalSoundPlaying(id)==0 then
  LoopGlobalSound(id)
 end
end

local function set_volume(id,volume)
 if id<0 or not exists(id) then return end
 SetGlobalSoundVolume(id,math.max(0,math.min(100,math.floor(volume))))
end

local function stop_if_silent(id,volume,keep)
 if id<0 or not exists(id) or keep then return end
 if volume<=0.1 and StopGlobalSound then StopGlobalSound(id) end
end

function firstlight_score_init(e)
 load_score()

 music[e]={
  target=TRACK_SALT,pending=-1,pending_since=0,
  volumes={[211]=0,[212]=0,[213]=0,[214]=0},
  last_state="",last_update=g_Time or 0,target_volume=46,
  fallback_announced=false
 }

 Hide(e)
 CollisionOff(e)
 -- Do not deactivate the controller. Always Active is supplied by the map entity and
 -- this script must keep ticking even when no Visual Logic connection is firing.
 SetActivated(e,1)

 -- MAX may also start visuals.ini's ambient track. The adaptive controller owns music
 -- from this point onward so there is never a doubled loop.
 if StopAmbientMusicTrack then StopAmbientMusicTrack() end

 local first,fallback=resolved_id(TRACK_SALT)
 if first>=0 then
  ensure_looping(first)
  set_volume(first,34)
  music[e].volumes[first]=34
 end

 audit(
  "FIRST_LIGHT music_init salt="..tostring(exists(GLOBAL_IDS[TRACK_SALT]))..
  " outpost="..tostring(exists(GLOBAL_IDS[TRACK_OUTPOST]))..
  " catacomb="..tostring(exists(GLOBAL_IDS[TRACK_CATACOMB]))..
  " fallback="..tostring(exists(FALLBACK_ID))
 )
end

function firstlight_score_main(e)
 local m=music[e]
 if not m then return end
 if not aegis or not aegis.started then return end
 if g_Time-(m.last_update or 0)<50 then return end
 local elapsed=math.max(1,g_Time-(m.last_update or g_Time))
 m.last_update=g_Time

 local state=aegis.music_state or "exploration_fortress"
 local desired,desired_volume=track_for_state(state)
 local immediate=false -- Spatial music has stable identity; brief combat does not replace it.

 if desired~=m.target then
  if desired~=m.pending then
   m.pending=desired
   m.pending_since=g_Time
  end
  if (immediate or g_Time-m.pending_since>=4500) and g_Time-(m.changed_at or -20000)>=15000 then
   m.changed_at=g_Time
   m.target=desired
   m.target_volume=desired_volume
   m.pending=-1
   aegis.music_track=m.target
   aegis.music_track_changed_at=g_Time
   local id,fallback=resolved_id(m.target)
   if id>=0 then ensure_looping(id) end
   audit("music_state state="..state.." track="..track_name(m.target).." fallback="..tostring(fallback).." volume="..math.floor(desired_volume))
  end
 else
  m.target_volume=desired_volume
  m.pending=-1
 end
 m.last_state=state
 if os.getenv('AEGIS_FIRSTLIGHT_QA')=='1' and g_Time-(m.audit_at or 0)>5000 then
  m.audit_at=g_Time
  audit('FIRST_LIGHT score target='..track_name(m.target)..' playing='..tostring(GetGlobalSoundPlaying(GLOBAL_IDS[m.target]))..' volume='..math.floor(m.target_volume))
 end

 local target_id,fallback=resolved_id(m.target)
 if fallback and not m.fallback_announced then
  m.fallback_announced=true
  audit("music_fallback active=true requested="..track_name(m.target))
 end

 -- Crossfade global music in roughly two seconds. Multiple authored cues can overlap
 -- briefly, but if several semantic tracks resolve to the same fallback sound there is
 -- only one actual global sound instance.
 local step=elapsed*0.035
 local ids={GLOBAL_IDS[TRACK_SALT],GLOBAL_IDS[TRACK_OUTPOST],GLOBAL_IDS[TRACK_CATACOMB],FALLBACK_ID}
 for _,id in ipairs(ids) do
  local goal=(id==target_id) and m.target_volume or 0
  local v=m.volumes[id] or 0
  if v<goal then v=math.min(goal,v+step) end
  if v>goal then v=math.max(goal,v-step) end
  m.volumes[id]=v
  if v>0.1 then
   ensure_looping(id)
   set_volume(id,v)
  else
   set_volume(id,0)
   stop_if_silent(id,v,id==target_id)
  end
 end
end

firstlight_score_init=firstlight_guard('firstlight_score_init',firstlight_score_init)

firstlight_score_main=firstlight_guard('firstlight_score_main',firstlight_score_main)
