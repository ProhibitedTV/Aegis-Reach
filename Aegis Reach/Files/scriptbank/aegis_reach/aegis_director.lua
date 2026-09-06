-- DESCRIPTION: Aegis Reach mission director. One instance; Always Active enabled.
-- Original scenario and code. Uses GameGuru MAX's local combat assets.
aegis = aegis or {}

-- Local runtime evidence: written by MAX, not the offline test harness.
local audit_path = "C:/Users/RhythmicCarnage/Desktop/Astra Game Test/Aegis Reach/Design/native-runtime.log"
local function audit(message)
 local ok = pcall(function()
  local file=io.open(audit_path,"a")
  if file then file:write(os.date("%Y-%m-%d %H:%M:%S")," ",message,"\n");file:close() end
 end)
end

function aegis_director_init(e)
 audit("director_init entity="..e)
 aegis = {phase=1, relays={}, enemies={}, reserves={}, extracted=false, started=false,
   message="", message_until=0, last_health=200, last_hit=0, shield=100, armour=100,
   next_regen=0, born=0, kills=0, hold=0, hold_last=0, radio=-1, score=0}
 Hide(e)
 CollisionOff(e)
end

function aegis_message(text,seconds)
 aegis.message=text
 aegis.message_until=g_Time+(seconds or 6)*1000
end

function aegis_distance(x,z)
 return math.sqrt((g_PlayerPosX-x)^2+(g_PlayerPosZ-z)^2)
end

function aegis_remaining()
 local alive=0
 for id,_ in pairs(aegis.enemies) do
  if g_Entity[id] and g_Entity[id].health>0 then alive=alive+1 end
 end
 return alive
end

function aegis_director_main(e)
 if not aegis.started then
  aegis.started=true; aegis.born=g_Time; aegis.last_hit=g_Time
  aegis.last_health=g_PlayerHealth
  aegis.shield=100; aegis.armour=100
  SetPlayerHealth(200)
  aegis_message("KESTREL: Restore NORTHSTAR, LANTERN, then the AEGIS core. Stop the orbital strike.",12)
  PlaySound(e,0)
  LoopSound(e,1)
  audit("mission_started health="..tostring(g_PlayerHealth).." player="..tostring(g_PlayerPosX)..","..tostring(g_PlayerPosY)..","..tostring(g_PlayerPosZ))
 end
 if not aegis.audit_next or g_Time>aegis.audit_next then
  aegis.audit_next=g_Time+15000
  local count=0;for _,v in pairs(g_Entity) do if type(v)=="table" then count=count+1 end end
  audit("tick entities="..count.." hostiles="..aegis_remaining().." phase="..aegis.phase.." health="..tostring(g_PlayerHealth).." player="..tostring(g_PlayerPosX)..","..tostring(g_PlayerPosY)..","..tostring(g_PlayerPosZ))
 end
 if g_PlayerHealth<=0 then return end
 if aegis.extracted then
  TextCenterOnXColor(50,35,5,"AEGIS REACH // MISSION COMPLETE",88,231,239)
  TextCenterOnX(50,43,3,"Strike cancelled. The colony survives.")
  TextCenterOnX(50,49,3,"TIME "..aegis.final_time.."s    ELIMINATIONS "..aegis.kills.."    SCORE "..aegis.score)
  TextCenterOnX(50,58,2,"Press E to debrief")
  if g_Time>aegis.completed_at+2000 and g_KeyPressE==1 then WinGame() end
  return
 end
 -- Health is split into 100 armour and 100 shield. Damage drains shield first.
 local damage=math.max(0,aegis.last_health-g_PlayerHealth)
 if damage>0 then
  aegis.last_hit=g_Time
  local absorb=math.min(aegis.shield,damage)
  aegis.shield=aegis.shield-absorb; aegis.armour=math.max(0,aegis.armour-(damage-absorb))
 end
 if g_Time-aegis.last_hit>5500 and g_Time>=aegis.next_regen and aegis.shield<100 then
  aegis.shield=math.min(100,aegis.shield+2);aegis.next_regen=g_Time+80
  SetPlayerHealth(math.floor(aegis.armour+aegis.shield))
 end
 aegis.last_health=g_PlayerHealth
 local alive=aegis_remaining();aegis.kills=0
 for id,_ in pairs(aegis.enemies) do if not g_Entity[id] or g_Entity[id].health<=0 then aegis.kills=aegis.kills+1 end end
 local objectives={"01 // Restore NORTHSTAR relay", "02 // Restore LANTERN relay", "03 // Override AEGIS fire control", "04 // Return to the cyan extraction pad"}
 TextColor(3,4,3,"AEGIS REACH : RELAYFALL",88,224,236)
 TextColor(3,9,2,objectives[math.min(aegis.phase,4)],222,232,237)
 local locations={{-700,-1100},{800,850},{0,2870},{0,-2510}}
 local target=locations[math.min(aegis.phase,4)]
 TextColor(3,13,2,"OBJECTIVE "..math.floor(aegis_distance(target[1],target[2])*.0254).."m   /   HOSTILES "..alive,245,183,89)
 TextColor(72,4,2,"SHIELD "..math.floor(aegis.shield).." / 100",88,224,236)
 TextColor(72,8,2,"ARMOUR "..math.floor(aegis.armour).." / 100",224,232,235)
 TextColor(72,12,1,"Recharge: break contact for 5.5 seconds",192,208,220)
 if aegis.shield<25 then TextCenterOnXColor(50,79,2,"SHIELD LOW // FIND COVER",255,117,80) end
 if g_Time<aegis.message_until then TextCenterOnXColor(50,21,2,aegis.message,234,218,175) end
 if g_Time-aegis.born<22000 then
  TextCenterOnX(50,88,2,"WASD move  |  Mouse aim/fire  |  R reload  |  Shift sprint  |  E interact")
  TextCenterOnX(50,92,1,"Follow the cyan terminals. Gates on either side of each blast wall provide flanking routes.")
 end
end
