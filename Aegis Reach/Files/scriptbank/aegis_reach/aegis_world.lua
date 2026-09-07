-- DESCRIPTION: Global Aegis Reach presentation controller.
-- Uses GameGuru MAX's native ambience/exposure and Visual Logic APIs.
-- One hidden Always Active instance is injected by tools/native_integration_pass.py.
-- Also exposes aegis.music_state so authored audio can react without being coupled to
-- combat/director internals.
local world={}

local function approach(value,target,amount)
 if value<target then return math.min(target,value+amount) end
 if value>target then return math.max(target,value-amount) end
 return value
end

local function target_grade()
 -- Readability floor: Relayfall is dramatic blue-hour sci-fi, not a horror game.
 -- The earlier values looked acceptable in static screenshots but became muddy once
 -- weapon/viewmodel exposure and dark modular assets were all on screen together.
 if (g_PlayerPosZ or 0)<-3300 then
  return 170,198,225,1.46,"vesper_shelf"
 end
 if aegis and aegis.signal_mode=="interference" then
  return 165,180,210,1.30,"aegis_interference"
 end
 if aegis and aegis.signal_mode=="overcharge" then
  return 178,214,230,1.43,"aegis_overcharge"
 end
 return 188,205,228,1.40,"fortress"
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
 SetActivated(e,1)
end

function aegis_world_init(e)
 world[e]={
  r=GetAmbienceRed(),g=GetAmbienceGreen(),b=GetAmbienceBlue(),exposure=GetExposure(),
  mode="",music="",shelf_announced=false,last_update=0
 }
 Hide(e)
 CollisionOff(e)
 SetActivated(e,1)
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
  pulse_logic(e)
 end

 local music=target_music_state(mode)
 aegis.music_state=music
 if music~=w.music then
  w.music=music
  aegis.music_changed_at=g_Time
  pulse_logic(e)
 end

 if mode=="vesper_shelf" and not w.shelf_announced then
  w.shelf_announced=true
  aegis_message("KESTREL: Vesper shelf. Old sea floor, no roof, long sightlines. Watch the ridges.",5)
  pulse_logic(e)
 end
end
