-- DESCRIPTION: Adaptive Aegis Reach score controller using GameGuru MAX native sound APIs.
-- One hidden instance is injected by tools/native_integration_pass.py with three Sound slots:
-- Sound0 = Salt Moon Drift, Sound1 = Moon Outpost Drift, Sound2 = Orbital Catacomb.
--
-- MAX's shipped fadeinsound.lua demonstrates LoopNon3DSound + SetSoundVolume. We use
-- SetSound to select each slot before changing volume so the score can crossfade instead
-- of hard-cutting every time the world controller changes aegis.music_state.
local music={}

local TRACK_SALT=0
local TRACK_OUTPOST=1
local TRACK_CATACOMB=2
local TRACK_COUNT=3

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
 if state=="exploration_vesper" then return TRACK_SALT,48 end
 if state=="discovery_human" then return TRACK_SALT,54 end
 if state=="exploration_fortress" then return TRACK_OUTPOST,46 end
 if state=="combat" then return TRACK_OUTPOST,64 end
 if state=="combat_overcharge" then return TRACK_OUTPOST,68 end
 if state=="resolution_aegis" then return TRACK_OUTPOST,62 end
 if state=="tension_aegis" then return TRACK_CATACOMB,52 end
 if state=="combat_interference" then return TRACK_CATACOMB,62 end
 if state=="discovery_choir" then return TRACK_CATACOMB,58 end
 return TRACK_SALT,42
end

local function set_slot_volume(e,slot,volume)
 SetSound(e,slot)
 SetSoundVolume(math.max(0,math.min(100,math.floor(volume))))
end

local function ensure_playing(e,m,slot)
 if m.playing[slot] then return end
 set_slot_volume(e,slot,0)
 LoopNon3DSound(e,slot)
 m.playing[slot]=true
end

local function stop_slot(e,m,slot)
 if not m.playing[slot] then return end
 set_slot_volume(e,slot,0)
 StopSound(e,slot)
 m.playing[slot]=false
end

function aegis_music_init(e)
 music[e]={
  target=-1,pending=-1,pending_since=0,
  volumes={[0]=0,[1]=0,[2]=0},playing={[0]=false,[1]=false,[2]=false},
  last_state="",last_update=0,target_volume=46
 }
 Hide(e)
 CollisionOff(e)
 SetActivated(e,0)
 for slot=0,TRACK_COUNT-1 do set_slot_volume(e,slot,0) end
 audit("music_init entity="..e)
end

function aegis_music_main(e)
 local m=music[e]
 if not m or not aegis or not aegis.started then return end
 if g_Time-(m.last_update or 0)<50 then return end
 local elapsed=math.max(1,g_Time-(m.last_update or g_Time))
 m.last_update=g_Time

 local state=aegis.music_state or "exploration_fortress"
 local desired,desired_volume=track_for_state(state)

 -- Discovery cues should answer the player's action immediately. Normal tactical state
 -- changes wait briefly so stepping across a boundary or a two-second combat lull does
 -- not constantly restart the score.
 local immediate=(state=="discovery_choir" or state=="discovery_human")
 if desired~=m.target then
  if desired~=m.pending then
   m.pending=desired
   m.pending_since=g_Time
  end
  if immediate or g_Time-m.pending_since>=1200 then
   m.target=desired
   m.target_volume=desired_volume
   m.pending=-1
   ensure_playing(e,m,m.target)
   aegis.music_track=m.target
   aegis.music_track_changed_at=g_Time
   audit("music_state state="..state.." track="..track_name(m.target).." volume="..math.floor(desired_volume))
  end
 else
  m.target_volume=desired_volume
  m.pending=-1
 end
 m.last_state=state

 -- Crossfade in roughly 2.2 seconds. Music stays deliberately below full volume so
 -- weapons, Kestrel and environmental detail retain headroom.
 local step=elapsed*0.032
 for slot=0,TRACK_COUNT-1 do
  local goal=(slot==m.target) and m.target_volume or 0
  local v=m.volumes[slot] or 0
  if v<goal then v=math.min(goal,v+step) end
  if v>goal then v=math.max(goal,v-step) end
  m.volumes[slot]=v
  if v>0.1 then
   ensure_playing(e,m,slot)
   set_slot_volume(e,slot,v)
  elseif slot~=m.target then
   stop_slot(e,m,slot)
  end
 end
end
