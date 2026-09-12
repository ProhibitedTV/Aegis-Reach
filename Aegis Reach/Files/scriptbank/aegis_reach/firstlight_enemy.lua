require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Native MAX infantry, authored encounter groups and concealed reinforcements.
-- The mission director controls reveal cadence; native character_attack owns locomotion,
-- firing, cover behavior and death once a soldier enters the fight.
require 'scriptbank\\people\\character_attack'
local soldiers={}

local function role_for(index)
 local slot=(index-1)%4
 if slot==0 then return 'assault' end
 if slot==1 then return 'rifle' end
 if slot==2 then return 'anchor' end
 return 'flanker'
end

function firstlight_enemy_init_name(e,name)
 local group,index=string.match(name,'FL ENEMY (%d+) (%d+)')
 group=tonumber(group);index=tonumber(index)
 soldiers[e]={group=group,index=index,role=role_for(index),active=false,registered=false,queued=0,eligible_since=0}
 -- Dormant MAX characters can otherwise remain visible in their bind/T pose until
 -- character_attack_main takes ownership. First Light reveals each encounter locally.
 Hide(e)
 CollisionOff(e)
end

local function prime_native_character(e,w)
 -- The interpreter reads health/position in masterinterpreter_restart. Defer until
 -- MAX has populated the entity table, then initialize exactly once.
 character_attack_init_file(e,'people\\character_attack')

 -- Use the stock MAX tactical choices deliberately rather than replacing its AI:
 -- FlankTarget 1=Stay Back, 2=Get Close, 3=Wide Flank, 4=Use Cover.
 local canretreat=w.role=='anchor' and 0 or 1
 local retreatrange=400
 local standground=0
 local flanktarget=4
 if w.role=='assault' then retreatrange=260;flanktarget=2 end
 if w.role=='flanker' then retreatrange=430;flanktarget=3 end
 if w.role=='anchor' then retreatrange=520;standground=1;flanktarget=1 end
 local alerted=w.group>=6 and 1 or 0
 local combattime=(w.group>=5 or w.role=='anchor') and 16000 or 14000
 local hearingrange=w.role=='anchor' and 1750 or 1500
 character_attack_properties(e,0,canretreat,retreatrange,standground,0,flanktarget,alerted,1,combattime,1,hearingrange,0,0)

 if SetAnimationName then SetAnimationName(e,'idle_aim');SetAnimationSpeed(e,1);LoopAnimation(e) end
 firstlight_audit('enemy_init e='..e..' group='..w.group..' role='..w.role..' tactic='..flanktarget..' bytecode='..tostring(g_character_attack_behavior_count))
 w.primed=true
end

local function required_stage(group)
 return group<=3 and 1 or (group==4 and 2 or (group==5 and 3 or 4))
end

local function fixed_reserve_delay(w)
 if w.group==7 then return ({4000,7000,22000,25000,40000,43000})[w.index] or 0 end
 if w.group==6 then return w.index*1500 end
 return nil
end

local function ready_to_reveal(e,w)
 if fl.stage<required_stage(w.group) then w.eligible_since=0;return false end
 if w.group==1 and g_Time-fl.born<22000 then return false end

 local fixed=fixed_reserve_delay(w)
 if w.group==7 then
  if fl.evac_start==0 or g_Time-fl.evac_start<fixed then return false end
 elseif w.group==6 then
  if w.queued==0 then w.queued=g_Time end
  if g_Time-w.queued<fixed then return false end
 elseif GetPlayerDistance(e)>(w.group==1 and 1550 or 1250) then
  w.eligible_since=0
  return false
 end

 -- Authored squads enter in readable beats instead of materializing as one blob.
 if w.eligible_since==0 then w.eligible_since=g_Time end
 local cadence=(w.index-1)*600
 if w.group>=6 then cadence=math.min(900,(w.index-1)*250) end
 if g_Time-w.eligible_since<cadence then return false end

 -- Adaptive budget only gates NEW reveals. Once a Warden is active the stock MAX
 -- combat behavior keeps full agency; the director never despawns or cheats a kill.
 local budget=fl.combat_budget or (fl.stage==4 and 5 or 4)
 local nearby=fl_hostiles(g_PlayerPosX,g_PlayerPosZ,2200)
 if nearby>=budget then return false end
 return true
end

function firstlight_enemy_main(e)
 local w=soldiers[e]
 if not w or not fl or not fl.started or fl.won then return end
 if not g_Entity[e] then return end
 if not w.primed then prime_native_character(e,w) end
 if not w.registered then fl.enemies[e]=w;w.registered=true end
 if g_Entity[e] and g_Entity[e].health<=0 then
  if w.active then character_attack_main(e) end -- Let the native death state finish.
  return
 end

 if not w.active then
  if not ready_to_reveal(e,w) then return end
  w.active=true
  -- Prime a valid named pose before revealing the character. The stock MAX
  -- character behavior takes over immediately afterward.
  if SetAnimationName and LoopAnimation then
   SetAnimationName(e,'idle_aim')
   SetAnimationSpeed(e,1)
   LoopAnimation(e)
  end
  Show(e)
  CollisionOn(e)
  fl_log('enemy_activated group='..w.group..' index='..w.index..' role='..w.role..' entity='..e..' budget='..tostring(fl.combat_budget))
 end

 character_attack_main(e)
 if os.getenv('AEGIS_FIRSTLIGHT_QA')=='1' and (not w.audit_at or g_Time-w.audit_at>1000) then
  w.audit_at=g_Time
  local actor=g_Entity[e]
  firstlight_audit('actor e='..e..' group='..w.group..' role='..w.role..' frame='..GetObjectFrame(actor.obj)..' x='..actor.x..' y='..actor.y..' z='..actor.z..' behavior='..tostring(g_character_attack_behavior_count))
 end
end

firstlight_enemy_init_name=firstlight_guard('firstlight_enemy_init_name',firstlight_enemy_init_name)
firstlight_enemy_main=firstlight_guard('firstlight_enemy_main',firstlight_enemy_main)
