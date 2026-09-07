-- DESCRIPTION: Global Aegis Reach presentation controller.
-- Uses GameGuru MAX's native ambience/exposure and Visual Logic APIs.
-- One hidden Always Active instance is injected by tools/native_integration_pass.py.
-- Also exposes aegis.music_state so authored audio can react without being coupled to
-- combat/director internals. The music files themselves are intentionally supplied later.
local world={}

local function approach(value,target,amount)
 if value<target then return math.min(target,value+amount) end
 if value>target then return math.max(target,value-amount) end
 return value
end

local function target_grade()
 -- The Vesper shelf is colder, clearer and slightly more exposed than the fort.
 if (g_PlayerPosZ or 0)<-3300 then
  return 158,188,218,1.32,"vesper_shelf"
 end
 -- The active AEGIS core subtly suppresses the environment instead of just
 -- making the player's shield numbers worse.
 if aegis and aegis.signal_mode=="interference" then
  return 152,165,202,1.19,"aegis_interference"
 end
 -- After capture, the same infrastructure feels electrically alive and friendly.
 if aegis and aegis.signal_mode=="overcharge" then
  return 168,208,221,1.30,"aegis_overcharge"
 end
 return 176,196,224,1.28,"fortress"
end

local function target_music_state(mode)
 if aegis and aegis.music_sting_until and g_Time<aegis.music_sting_until then
  return aegis.music_sting or "discovery"
 end
 if aegis and aegis.combat_active then
  if aegis.signal_mode=="interference" then return "combat_interference" end
  if aegis.signal_mode=="overcharge" then return "combat_overcharge" end
  return "combat"
 end
 if mode=="vesper_shelf" then return "exploration_vesper" end
 if mode=="aegis_interference" then return "tension_aegis" end
 if mode=="aegis_overcharge" then return "resolution_aegis" end
 return "exploration_fortress"
end

local function pulse_logic(e)
 SetActivated(e,1)
 PerformLogicConnections(e)
 ActivateIfUsed(e)
 SetActivated(e,0)
end

function aegis_world_init(e)
 world[e]={
  r=GetAmbienceRed(),g=GetAmbienceGreen(),b=GetAmbienceBlue(),exposure=GetExposure(),
  mode="",music="",shelf_announced=false,last_update=0
 }
 Hide(e)
 CollisionOff(e)
 SetActivated(e,0)
end

function aegis_world_main(e)
 local w=world[e]
 if not w or not aegis or not aegis.started then return end
 if g_Time-(w.last_update or 0)<60 then return end
 w.last_update=g_Time

 local tr,tg,tb,te,mode=target_grade()
 w.r=approach(w.r,tr,2.5)
 w.g=approach(w.g,tg,2.5)
 w.b=approach(w.b,tb,2.5)
 w.exposure=approach(w.exposure,te,0.008)
 SetAmbienceRed(w.r)
 SetAmbienceGreen(w.g)
 SetAmbienceBlue(w.b)
 SetExposure(w.exposure)

 if mode~=w.mode then
  w.mode=mode
  -- Visual Logic can subscribe to presentation-state changes without coupling
  -- external set pieces to the mission director's implementation.
  pulse_logic(e)
 end

 local music=target_music_state(mode)
 aegis.music_state=music
 if music~=w.music then
  w.music=music
  aegis.music_changed_at=g_Time
  -- This same native endpoint can be wired to future sound/music entities.
  pulse_logic(e)
 end

 if mode=="vesper_shelf" and not w.shelf_announced then
  w.shelf_announced=true
  aegis_message("KESTREL: Vesper shelf. Old sea floor, no roof, long sightlines. Watch the ridges.",5)
  pulse_logic(e)
 end
end
