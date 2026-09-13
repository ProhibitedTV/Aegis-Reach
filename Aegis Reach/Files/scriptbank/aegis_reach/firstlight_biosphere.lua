require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Primitive Vesper biosphere presentation. Ambient only: no combat, damage or nav AI.
local bio={}

local function distance(e)
 if GetPlayerDistance then
  local ok,d=pcall(GetPlayerDistance,e)
  if ok and d then return d end
 end
 return 0
end

function firstlight_biosphere_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or nil
 if string.find(name,'FL BIO SKITTER',1,true) then
  bio[e]={kind='skitter',x=ent and ent.x or 0,y=ent and ent.y or 0,z=ent and ent.z or 0,
          phase=(e%19)*0.71,radius=15+(e%5)*4,speed=.46+(e%4)*.07}
  if CollisionOff then CollisionOff(e) end
 elseif string.find(name,'FL BIO MIDGES',1,true) then
  bio[e]={kind='midges',configured=false,active=false,next_check=0}
  if CollisionOff then CollisionOff(e) end
  if EffectStop then EffectStop(e) end
 else
  bio[e]={kind='static'}
  if CollisionOff then CollisionOff(e) end
 end
end

local function update_midges(e,s)
 if not EffectStart then return end
 if g_Time<s.next_check then return end
 s.next_check=g_Time+140
 if not s.configured then
  -- Reuse the native ember sprite at tiny scale, but remove its hot/spark behavior.
  -- At runtime this reads as a sparse cloud of dull airborne organisms/spores.
  if EffectSetOpacity then EffectSetOpacity(e,24) end
  if EffectSetSpeed then EffectSetSpeed(e,13) end
  if EffectSetColor then EffectSetColor(e,132,159,142) end
  if EffectSetLifespan then EffectSetLifespan(e,115) end
  if EffectSetBurstMode then EffectSetBurstMode(e,0) end
  s.configured=true
 end
 local d=distance(e)
 local on=fl and fl.started and not fl.won and g_PlayerHealth>0 and d<1700
 if on and not s.active then EffectStart(e);s.active=true
 elseif not on and s.active then EffectStop(e);s.active=false end
end

local function update_skitter(e,s)
 if not PositionObject or not g_Entity or not g_Entity[e] or not g_Entity[e].obj then return end
 if distance(e)>1600 then return end
 local t=g_Time*.001*s.speed+s.phase
 local dx=math.sin(t)*s.radius+math.sin(t*2.31)*s.radius*.18
 local dz=math.cos(t*.87)*s.radius+math.cos(t*1.73)*s.radius*.16
 local lift=math.abs(math.sin(t*3.4))*.45
 PositionObject(g_Entity[e].obj,s.x+dx,s.y+lift,s.z+dz)
end

function firstlight_biosphere_main(e)
 local s=bio[e];if not s then return end
 if s.kind=='midges' then update_midges(e,s)
 elseif s.kind=='skitter' then update_skitter(e,s) end
end

function firstlight_biosphere_exit(e)
 local s=bio[e]
 if s and s.kind=='midges' and s.active and EffectStop then EffectStop(e) end
 bio[e]=nil
end

firstlight_biosphere_init_name=firstlight_guard('firstlight_biosphere_init_name',firstlight_biosphere_init_name)
firstlight_biosphere_main=firstlight_guard('firstlight_biosphere_main',firstlight_biosphere_main)
firstlight_biosphere_exit=firstlight_guard('firstlight_biosphere_exit',firstlight_biosphere_exit)
