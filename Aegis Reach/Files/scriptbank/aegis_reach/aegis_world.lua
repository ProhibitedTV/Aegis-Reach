-- DESCRIPTION: Global Aegis Reach presentation controller.
-- Uses GameGuru MAX's native ambience/exposure and Visual Logic APIs.
-- One hidden Always Active instance is injected by tools/native_integration_pass.py.
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

function aegis_world_init(e)
 world[e]={
  r=GetAmbienceRed(),g=GetAmbienceGreen(),b=GetAmbienceBlue(),exposure=GetExposure(),
  mode="",shelf_announced=false,last_update=0
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
  SetActivated(e,1)
  PerformLogicConnections(e)
  ActivateIfUsed(e)
  SetActivated(e,0)
 end

 if mode=="vesper_shelf" and not w.shelf_announced then
  w.shelf_announced=true
  aegis_message("KESTREL: Vesper shelf. Old sea floor, no roof, long sightlines. Watch the ridges.",5)
  SetActivated(e,1)
  PerformLogicConnections(e)
  ActivateIfUsed(e)
  SetActivated(e,0)
 end
end
