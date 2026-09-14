require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Vesper ambient biosphere presentation. Visual only: no damage, combat AI, nav or physics.
local bio={}

local function distance(e)
 if GetPlayerDistance then
  local ok,d=pcall(GetPlayerDistance,e)
  if ok and d then return d end
 end
 return 99999
end
local function object_of(e)
 if not g_Entity or not g_Entity[e] then return nil end
 return g_Entity[e].obj
end

function firstlight_biosphere_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or nil
 local common={x=ent and ent.x or 0,y=ent and ent.y or 0,z=ent and ent.z or 0,next_tick=0,phase=(e%23)*.61,motion=0,clock=0,last_motion=0}
 if string.find(name,'FL BIO SKITTER',1,true) then
  common.kind='skitter';common.radius=16+(e%5)*3;common.speed=.56+(e%4)*.06;common.lastx=common.x;common.lastz=common.z
 elseif string.find(name,'FL BIO VEILWING',1,true) then
  common.kind='veilwing';common.radius=28+(e%4)*5;common.speed=.48+(e%3)*.05
 elseif string.find(name,'FL BIO SPORES',1,true) then
  common.kind='spores';common.configured=false;common.active=false
 else
  common.kind='static'
 end
 bio[e]=common
 if CollisionOff then CollisionOff(e) end
 if common.kind=='spores' and EffectStop then EffectStop(e) end
end

local function update_spores(e,s)
 if g_Time<s.next_tick then return end;s.next_tick=g_Time+180
 if not s.configured then
  -- The old prototype asked ember particles to read as insects. They are now only a
  -- faint microbial/spore haze behind real mesh fauna, so keep them slow and dim.
  if EffectSetOpacity then EffectSetOpacity(e,12) end
  if EffectSetSpeed then EffectSetSpeed(e,6) end
  if EffectSetColor then EffectSetColor(e,116,146,165) end
  if EffectSetLifespan then EffectSetLifespan(e,180) end
  if EffectSetBurstMode then EffectSetBurstMode(e,0) end
  s.configured=true
 end
 local on=fl and fl.started and not fl.won and g_PlayerHealth>0 and distance(e)<1550
 if on and not s.active and EffectStart then EffectStart(e);s.active=true
 elseif not on and s.active and EffectStop then EffectStop(e);s.active=false end
end

local function update_skitter(e,s)
 if g_Time<s.next_tick then return end;s.next_tick=g_Time+90
 local obj=object_of(e);if not obj or not PositionObject or distance(e)>1450 then return end
 local dt=s.last_motion>0 and math.min(.15,(g_Time-s.last_motion)*.001) or 0
 s.last_motion=g_Time
 s.clock=s.clock+dt
 -- Five seconds of movement followed by a short graze/pause reads as an animal instead
 -- of a prop sliding on a mathematical loop forever.
 local move=s.clock%8.0<5.2
 if move then s.motion=s.motion+dt*s.speed end
 local t=s.phase+s.motion
 local dx=(math.sin(t)-math.sin(s.phase))*s.radius
 local dz=(math.cos(t*.83)-math.cos(s.phase*.83))*s.radius
 local x=s.x+dx;local z=s.z+dz
 local y=GetGroundHeight and GetGroundHeight(x,z) or s.y
 y=y+.15+(move and math.abs(math.sin(t*5.1))*.22 or 0)
 PositionObject(obj,x,y,z)
 if RotateObject then
  local vx=x-s.lastx;local vz=z-s.lastz
  if math.abs(vx)+math.abs(vz)>.02 then
   local yaw=math.deg(math.atan2(vx,vz));RotateObject(obj,0,yaw,0)
  end
 end
 s.lastx=x;s.lastz=z
end

local function update_veilwing(e,s)
 if g_Time<s.next_tick then return end;s.next_tick=g_Time+70
 local obj=object_of(e);if not obj or not PositionObject or distance(e)>1850 then return end
 local t=g_Time*.001*s.speed+s.phase
 local x=s.x+math.sin(t*.91)*s.radius+math.sin(t*2.27)*s.radius*.18
 local z=s.z+math.cos(t*.73)*s.radius*.72+math.cos(t*1.91)*s.radius*.14
 local y=s.y+math.sin(t*1.43)*7+math.sin(t*3.11)*1.8
 PositionObject(obj,x,y,z)
 if RotateObject then
  local vx=math.cos(t*.91)*s.radius*.91+math.cos(t*2.27)*s.radius*.18*2.27
  local vz=-math.sin(t*.73)*s.radius*.72*.73-math.sin(t*1.91)*s.radius*.14*1.91
  local yaw=math.deg(math.atan2(vx,vz));local bank=math.sin(t*.91)*11;local pitch=math.sin(t*1.43)*4
  RotateObject(obj,pitch,yaw,bank)
 end
end

function firstlight_biosphere_main(e)
 local s=bio[e];if not s then return end
 if s.kind~='spores' and (not fl or not fl.started or fl.won or g_PlayerHealth<=0) then return end
 if s.kind=='spores' then update_spores(e,s)
 elseif s.kind=='skitter' then update_skitter(e,s)
 elseif s.kind=='veilwing' then update_veilwing(e,s) end
end

function firstlight_biosphere_exit(e)
 local s=bio[e]
 if s and s.kind=='spores' and s.active and EffectStop then EffectStop(e) end
 bio[e]=nil
end

firstlight_biosphere_init_name=firstlight_guard('firstlight_biosphere_init_name',firstlight_biosphere_init_name)
firstlight_biosphere_main=firstlight_guard('firstlight_biosphere_main',firstlight_biosphere_main)
firstlight_biosphere_exit=firstlight_guard('firstlight_biosphere_exit',firstlight_biosphere_exit)
