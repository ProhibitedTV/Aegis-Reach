-- DESCRIPTION: Aegis Reach mission director. One instance; Always Active enabled.
-- Original scenario and code. Uses GameGuru MAX's local combat assets.
aegis = aegis or {}

-- Runtime audit is deliberately best-effort. Relayfall is commonly copied into
-- GameGuru MAX's user Files directory for testing, so try that known writable
-- location before project-relative development paths. This keeps telemetry alive
-- whether the mission runs from the repo or from MAX's Documents deployment.
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

function aegis_director_init(e)
 audit("director_init entity="..e)
 aegis = {phase=1, relays={}, enemies={}, active_enemies={}, reserves={}, reserve_announced={}, extracted=false, started=false,
   message="", message_until=0, last_health=200, last_hit=0, shield=100, armour=100,
   next_regen=0, regen_announced=false, born=0, kills=0, hold=0, hold_last=0, radio=-1, score=0,
   combat_active=false, combat_last=0, combat_contacts=0, signal_mode="standard", signal_announced="",
   shield_breaks=0, encounter_seq=0, encounter_started=0, encounter_phase=0, encounter_start_kills=0,
   encounter_start_armour=100, encounter_breaks=0}
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

function aegis_nearby_hostiles(radius)
 local alive=0
 local rr=radius*radius
 for id,_ in pairs(aegis.active_enemies) do
  local n=g_Entity[id]
  if n and n.health>0 then
   local dx=(n.x or 0)-g_PlayerPosX
   local dz=(n.z or 0)-g_PlayerPosZ
   if dx*dx+dz*dz<=rr then alive=alive+1 end
  end
 end
 return alive
end

-- Recharge cadence is part of the mission arc, not just a health setting.
-- The live AEGIS core fights the player's suit near the final objective; once
-- captured, Vanguard Seven rides the same network home with a temporary boost.
function aegis_recharge_profile()
 if aegis.phase==3 and aegis_distance(0,2870)<1650 then
  return 7600,1,120,"interference"
 end
 if aegis.phase>=4 then
  return 3600,3,70,"overcharge"
 end
 return 5500,2,80,"standard"
end

local function update_signal_state()
 local delay,amount,interval,mode=aegis_recharge_profile()
 if aegis.signal_mode~=mode then
  aegis.signal_mode=mode
  if mode=="interference" then
   aegis_message("SUIT: AEGIS COUNTERMEASURE FIELD // shield recharge degraded",5)
   audit("signal_mode interference phase="..aegis.phase)
  elseif mode=="overcharge" then
   aegis_message("SUIT: AEGIS UPLINK CAPTURED // shield recharge accelerated",5)
   audit("signal_mode overcharge phase="..aegis.phase)
  elseif aegis.signal_announced~="" then
   aegis_message("SUIT: Countermeasure field cleared // recharge nominal",4)
   audit("signal_mode standard phase="..aegis.phase)
  end
  aegis.signal_announced=mode
 end
 return delay,amount,interval,mode
end

local function start_encounter(nearby)
 aegis.encounter_seq=aegis.encounter_seq+1
 aegis.encounter_started=g_Time
 aegis.encounter_phase=aegis.phase
 aegis.encounter_start_kills=aegis.kills
 aegis.encounter_start_armour=aegis.armour
 aegis.encounter_breaks=0
 audit("encounter_start id="..aegis.encounter_seq.." phase="..aegis.phase.." contacts="..nearby.." armour="..math.floor(aegis.armour).." shield="..math.floor(aegis.shield))
end

local function finish_encounter()
 local duration=math.floor((g_Time-aegis.encounter_started)/100)/10
 local eliminations=math.max(0,aegis.kills-aegis.encounter_start_kills)
 local armour_loss=math.max(0,math.floor(aegis.encounter_start_armour-aegis.armour))
 audit("encounter_clear id="..aegis.encounter_seq.." phase="..aegis.encounter_phase.." duration="..duration.."s kills="..eliminations.." armour_loss="..armour_loss.." shield_breaks="..aegis.encounter_breaks)
end

local function update_combat_state()
 local nearby=aegis_nearby_hostiles(1850)
 aegis.combat_contacts=nearby
 if nearby>0 then
  aegis.combat_last=g_Time
  if not aegis.combat_active then
   aegis.combat_active=true
   start_encounter(nearby)
   if g_Time-aegis.born>7000 then
    aegis_message("TACTICAL: Contact. Break their line, flank, then finish the survivors.",4)
   end
  end
 elseif aegis.combat_active and g_Time-aegis.combat_last>2200 then
  aegis.combat_active=false
  finish_encounter()
  if not aegis.extracted then aegis_message("TACTICAL: Local sector clear. Reload and move before the next push.",4) end
 end
 return nearby
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
  TextCenterOnX(50,54,2,"ARMOUR "..math.floor(aegis.armour).."    SHIELD BREAKS "..aegis.shield_breaks)
  TextCenterOnX(50,61,2,"Press E to debrief")
  if g_Time>aegis.completed_at+2000 and g_KeyPressE==1 then WinGame() end
  return
 end

 local regen_delay,regen_amount,regen_interval,signal_mode=update_signal_state()

 -- Health is split into 100 armour and 100 shield. Damage drains shield first.
 local shield_before=aegis.shield
 local damage=math.max(0,aegis.last_health-g_PlayerHealth)
 if damage>0 then
  aegis.last_hit=g_Time
  aegis.regen_announced=false
  local absorb=math.min(aegis.shield,damage)
  aegis.shield=aegis.shield-absorb
  aegis.armour=math.max(0,aegis.armour-(damage-absorb))
  if shield_before>0 and aegis.shield<=0 then
   aegis.shield_breaks=aegis.shield_breaks+1
   if aegis.combat_active then aegis.encounter_breaks=aegis.encounter_breaks+1 end
   aegis_message("SUIT: SHIELD COLLAPSE // break line of sight now",4)
   audit("shield_break total="..aegis.shield_breaks.." phase="..aegis.phase.." armour="..math.floor(aegis.armour))
  end
 end

 if g_Time-aegis.last_hit>regen_delay and g_Time>=aegis.next_regen and aegis.shield<100 then
  if not aegis.regen_announced then
   aegis.regen_announced=true
   if signal_mode=="interference" then
    aegis_message("SUIT: Weak recharge lock acquired // hold cover",3)
   elseif signal_mode=="overcharge" then
    aegis_message("SUIT: AEGIS-assisted recharge engaged",3)
   else
    aegis_message("SUIT: Shield recharge engaged",3)
   end
  end
  aegis.shield=math.min(100,aegis.shield+regen_amount)
  aegis.next_regen=g_Time+regen_interval
  SetPlayerHealth(math.floor(aegis.armour+aegis.shield))
 end
 aegis.last_health=g_PlayerHealth

 local alive=aegis_remaining()
 aegis.kills=0
 for id,_ in pairs(aegis.enemies) do if not g_Entity[id] or g_Entity[id].health<=0 then aegis.kills=aegis.kills+1 end end
 local nearby=update_combat_state()

 local objectives={"01 // Restore NORTHSTAR relay", "02 // Restore LANTERN relay", "03 // Override AEGIS fire control", "04 // Return to the cyan extraction pad"}
 TextColor(3,4,3,"AEGIS REACH : RELAYFALL",88,224,236)
 TextColor(3,9,2,objectives[math.min(aegis.phase,4)],222,232,237)
 local locations={{-700,-1100},{800,850},{0,2870},{0,-2510}}
 local target=locations[math.min(aegis.phase,4)]
 TextColor(3,13,2,"OBJECTIVE "..math.floor(aegis_distance(target[1],target[2])*.0254).."m   /   HOSTILES "..alive,245,183,89)

 TextColor(72,4,2,"SHIELD "..math.floor(aegis.shield).." / 100",88,224,236)
 TextColor(72,8,2,"ARMOUR "..math.floor(aegis.armour).." / 100",224,232,235)
 if nearby>0 then
  TextColor(72,12,1,"CONTACT // "..nearby.." close hostile"..(nearby==1 and "" or "s"),255,177,89)
 else
  TextColor(72,12,1,"TACTICAL CLEAR // recharge in "..(regen_delay/1000).."s",192,208,220)
 end
 if signal_mode=="interference" then
  TextColor(72,16,1,"AEGIS FIELD // RECHARGE DEGRADED",255,137,94)
 elseif signal_mode=="overcharge" then
  TextColor(72,16,1,"AEGIS UPLINK // RECHARGE BOOSTED",91,239,214)
 end

 if aegis.shield<25 then TextCenterOnXColor(50,79,2,"SHIELD LOW // FIND COVER",255,117,80) end
 if g_Time<aegis.message_until then TextCenterOnXColor(50,21,2,aegis.message,234,218,175) end
 if g_Time-aegis.born<22000 then
  TextCenterOnX(50,88,2,"WASD move  |  Mouse aim/fire  |  R reload  |  Shift sprint  |  E interact")
  TextCenterOnX(50,92,1,"Assault rifle controls space. Shotgun punishes pushes. Marksman rifle breaks distant anchors.")
 end
end
