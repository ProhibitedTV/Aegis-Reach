require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Native MAX infantry, authored encounter groups and concealed reinforcements.
require 'scriptbank\\people\\character_attack'
local soldiers={}

function firstlight_enemy_init_name(e,name)
 local group,index=string.match(name,'FL ENEMY (%d+) (%d+)')
 group=tonumber(group);index=tonumber(index)
 soldiers[e]={group=group,index=index,active=false,registered=false,queued=0}
 -- Dormant MAX characters can otherwise remain visible in their bind/T pose until
 -- character_attack_main takes ownership. First Light intentionally reveals each
 -- encounter locally, so keep every inactive soldier concealed and non-colliding.
 Hide(e)
 CollisionOff(e)
end

local function prime_native_character(e,w)
 -- The interpreter reads health/position in masterinterpreter_restart. Defer until
 -- MAX has populated the entity table, then initialize exactly once.
 character_attack_init_file(e,'people\\character_attack')
 local index=w.index
 local anchor=index%3==0
 character_attack_properties(e,0,anchor and 0 or 1,anchor and 450 or 300,anchor and 1 or 0,0,index%2==0 and 3 or 2,0,1,14000,1,1500,0,0)

 if SetAnimationName then SetAnimationName(e,'idle_aim');SetAnimationSpeed(e,1);LoopAnimation(e) end
 firstlight_audit('enemy_init e='..e..' bytecode='..tostring(g_character_attack_behavior_count))
 w.primed=true
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
  local stage=w.group<=3 and 1 or (w.group==4 and 2 or (w.group==5 and 3 or 4))
  if fl.stage<stage then return end
  if w.group==1 and g_Time-fl.born<22000 then return end

  if w.group==7 then
   if fl.evac_start==0 then return end
   local delay=({4000,7000,22000,25000,40000,43000})[w.index]
   if g_Time-fl.evac_start<delay then return end
  elseif w.group==6 then
   if w.queued==0 then w.queued=g_Time end
   if g_Time-w.queued<w.index*1700 then return end
  elseif GetPlayerDistance(e)>(w.group==1 and 1550 or 1250) then
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
  fl_log('enemy_activated group='..w.group..' index='..w.index..' entity='..e)
 end

 character_attack_main(e)
 if os.getenv('AEGIS_FIRSTLIGHT_QA')=='1' and (not w.audit_at or g_Time-w.audit_at>1000) then
  w.audit_at=g_Time
  local actor=g_Entity[e]
  firstlight_audit('actor e='..e..' group='..w.group..' frame='..GetObjectFrame(actor.obj)..' x='..actor.x..' y='..actor.y..' z='..actor.z..' behavior='..tostring(g_character_attack_behavior_count))
 end
end

firstlight_enemy_init_name=firstlight_guard('firstlight_enemy_init_name',firstlight_enemy_init_name)

firstlight_enemy_main=firstlight_guard('firstlight_enemy_main',firstlight_enemy_main)
