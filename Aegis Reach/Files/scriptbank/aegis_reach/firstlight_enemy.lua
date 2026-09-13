require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Native MAX infantry, authored encounter groups and concealed reinforcements.
-- The mission director controls reveal cadence; native character_attack owns locomotion,
-- firing, cover behavior and death once a soldier enters the fight.
require 'scriptbank\\people\\character_attack'
local soldiers={}
local squad_clock={}
local squad_epoch=-1

-- Each four-person cell has a readable battlefield job. The first contact is a rifleman
-- rather than an instant rusher; pressure then builds through assault, anchor and flank.
local function role_for(index)
 local slot=(index-1)%4
 if slot==0 then return 'rifle' end
 if slot==1 then return 'assault' end
 if slot==2 then return 'anchor' end
 return 'flanker'
end

local ROLE_DELAY={anchor=0,rifle=350,assault=750,flanker=1250}
local ROLE_WEIGHT={anchor=1.15,rifle=1.0,assault=1.15,flanker=1.10}

function firstlight_enemy_init_name(e,name)
 local group,index=string.match(name,'FL ENEMY (%d+) (%d+)')
 group=tonumber(group);index=tonumber(index)
 soldiers[e]={
  group=group,index=index,role=role_for(index),active=false,registered=false,queued=0,
  eligible_since=0,watch_since=0,reveal_reason='',reveal_wait=0
 }
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

local function angle_delta(a,b)
 return (a-b+540)%360-180
end

local function player_is_watching(e)
 local actor=g_Entity[e]
 if not actor then return false end
 local dx=actor.x-g_PlayerPosX;local dz=actor.z-g_PlayerPosZ
 local distance=math.sqrt(dx*dx+dz*dz)
 if distance<420 then return false end -- close-range reveals must not deadlock an encounter
 local bearing=math.deg(math.atan2(dx,dz))
 return math.abs(angle_delta(bearing,g_PlayerAngY or 0))<52
end

local function active_threat_weight(radius)
 local total=0
 local rr=radius*radius
 for id,state in pairs(fl.enemies or {}) do
  local actor=g_Entity[id]
  if state.active and actor and actor.health>0 then
   local dx=actor.x-g_PlayerPosX;local dz=actor.z-g_PlayerPosZ
   if dx*dx+dz*dz<rr then total=total+(ROLE_WEIGHT[state.role] or 1) end
  end
 end
 return total
end

local function stage_gate(e,w)
 if fl.stage<required_stage(w.group) then w.eligible_since=0;return false end
 if w.group==1 and g_Time-fl.born<22000 then return false end

 local fixed=fixed_reserve_delay(w)
 if w.group==7 then
  if fl.evac_start==0 or g_Time-fl.evac_start<fixed then return false end
  w.reveal_reason='extraction_wave'
 elseif w.group==6 then
  if w.queued==0 then w.queued=g_Time end
  if g_Time-w.queued<fixed then return false end
  w.reveal_reason='return_ambush'
 elseif GetPlayerDistance(e)>(w.group==1 and 1550 or 1250) then
  w.eligible_since=0;w.watch_since=0
  return false
 else
  w.reveal_reason='proximity'
 end
 return true
end

local function reveal_choreography(e,w)
 local epoch=fl.born or 0
 if squad_epoch~=epoch then squad_clock={};squad_epoch=epoch end
 if w.eligible_since==0 then w.eligible_since=g_Time end
 if not squad_clock[w.group] then squad_clock[w.group]=g_Time end

 -- One shared clock turns a group into a squad beat instead of N independent pop-ins.
 local cadence=ROLE_DELAY[w.role] or ((w.index-1)*600)
 if w.group>=6 then cadence=math.floor(cadence*.55) end
 if g_Time-squad_clock[w.group]<cadence then return false end

 -- Dormant regular squads should not materialize in the center of the player's view.
 -- If the player watches a staging point continuously, release after a short ceiling so
 -- progression cannot deadlock. Extraction/return reserves are authored arrivals and
 -- intentionally bypass this rule.
 if w.group<=5 and player_is_watching(e) then
  if w.watch_since==0 then w.watch_since=g_Time end
  w.reveal_wait=g_Time-w.watch_since
  if w.reveal_wait<3200 then return false end
  w.reveal_reason='visibility_timeout'
 else
  w.watch_since=0
 end

 return true
end

local function ready_to_reveal(e,w)
 if not stage_gate(e,w) then return false end
 if not reveal_choreography(e,w) then return false end

 -- Adaptive budget only gates NEW reveals. Once a Warden is active the stock MAX
 -- combat behavior keeps full agency; the director never despawns or cheats a kill.
 local budget=fl.combat_budget or (fl.stage==4 and 5 or 4)
 local threat=active_threat_weight(2200)
 if threat>=budget then return false end

 -- Give a newly broken shield a short recovery beat before feeding another dormant
 -- regular squad member into the fight. Authored extraction waves retain their timing.
 if w.group<=5 and fl.shield<=0 and g_Time-fl.last_hit<1700 then return false end
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
  if not ready_to_reveal(e,w) then
   if os.getenv('AEGIS_FIRSTLIGHT_QA')=='1' and w.watch_since>0 and (not w.hold_audit_at or g_Time-w.hold_audit_at>1000) then
    w.hold_audit_at=g_Time
    firstlight_audit('reveal_held e='..e..' group='..w.group..' role='..w.role..' watched_ms='..math.floor(w.reveal_wait or 0)..' distance='..math.floor(GetPlayerDistance(e)))
   end
   return
  end
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
  fl_log('enemy_activated group='..w.group..' index='..w.index..' role='..w.role..' reason='..w.reveal_reason..' wait='..math.floor(w.reveal_wait or 0)..' entity='..e..' budget='..tostring(fl.combat_budget))
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
