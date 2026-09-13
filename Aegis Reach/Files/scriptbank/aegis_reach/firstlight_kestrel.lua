require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Visible Kestrel flight choreography. Visual-only; mission state remains authoritative.
local ships={}

local function smooth(t)
 if t<0 then return 0 elseif t>1 then return 1 end
 return t*t*(3-2*t)
end
local function lerp(a,b,t)return a+(b-a)*t end
local function pose(e,x,y,z,rx,ry,rz)
 local ent=g_Entity and g_Entity[e] or nil
 if not ent or not ent.obj or not PositionObject then return end
 PositionObject(ent.obj,x,y,z)
 if RotateObject then RotateObject(ent.obj,rx or 0,ry or 180,rz or 0) end
end
local function show(e,s)
 if not s.visible then Show(e);s.visible=true end
end
local function hide(e,s)
 if s.visible then Hide(e);s.visible=false end
end

function firstlight_kestrel_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or {}
 local role=string.find(name,'INSERTION',1,true) and 'insertion' or 'extraction'
 ships[e]={role=role,x=ent.x or 0,y=ent.y or 0,z=ent.z or 0,visible=false,
           intro_start=0,handoff_start=0,depart_start=0}
 Hide(e);CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

local function insertion(e,s)
 if not fl or not fl.started then hide(e,s);return end
 local beat=aegis and aegis.cinematic_beat or nil
 if beat=='ARRIVAL' then
  if s.intro_start==0 then s.intro_start=g_Time end
  show(e,s)
  local t=smooth((g_Time-s.intro_start)/6200)
  pose(e,lerp(s.x-980,s.x,t),lerp(s.y+620,s.y,t),lerp(s.z-1120,s.z,t),lerp(-7,0,t),lerp(148,180,t),lerp(5,0,t))
 elseif beat=='ARRIVAL_HANDOFF' then
  if s.handoff_start==0 then s.handoff_start=g_Time end
  show(e,s)
  local t=smooth((g_Time-s.handoff_start)/5900)
  pose(e,lerp(s.x,s.x+1750,t),lerp(s.y,s.y+900,t),lerp(s.z,s.z-1700,t),lerp(0,-5,t),lerp(180,218,t),lerp(0,-7,t))
 elseif s.handoff_start>0 and g_Time-s.handoff_start>6200 then
  hide(e,s)
 elseif g_Time-(fl.born or g_Time)>15000 then
  -- Fail-open opening path: never leave the insertion ship parked forever.
  hide(e,s)
 end
end

local function extraction(e,s)
 if not fl or not fl.started or fl.evac_start==0 then hide(e,s);return end
 if aegis and aegis.kestrel_depart then
  if s.depart_start==0 then s.depart_start=g_Time end
  show(e,s)
  local t=smooth((g_Time-s.depart_start)/6000)
  pose(e,lerp(s.x,s.x-1700,t),lerp(s.y,s.y+1050,t),lerp(s.z,s.z-2200,t),lerp(0,-6,t),lerp(180,142,t),lerp(0,8,t))
  if t>=1 then hide(e,s) end
  return
 end
 local elapsed=fl.evac_elapsed or 0
 if elapsed<36000 then hide(e,s);return end
 show(e,s)
 if elapsed<52000 then
  local t=smooth((elapsed-36000)/16000)
  pose(e,lerp(s.x+2850,s.x+520,t),lerp(s.y+1250,s.y+340,t),lerp(s.z-2750,s.z-560,t),lerp(-4,0,t),lerp(228,190,t),lerp(-6,0,t))
 elseif elapsed<60000 then
  local t=smooth((elapsed-52000)/8000)
  pose(e,lerp(s.x+520,s.x,t),lerp(s.y+340,s.y,t),lerp(s.z-560,s.z,t),lerp(0,0,t),lerp(190,180,t),0)
 else
  pose(e,s.x,s.y,s.z,0,180,0)
  if aegis then aegis.kestrel_landed=true end
 end
end

function firstlight_kestrel_main(e)
 local s=ships[e];if not s then return end
 if s.role=='insertion' then insertion(e,s) else extraction(e,s) end
end

function firstlight_kestrel_exit(e) ships[e]=nil end
firstlight_kestrel_init_name=firstlight_guard('firstlight_kestrel_init_name',firstlight_kestrel_init_name)
firstlight_kestrel_main=firstlight_guard('firstlight_kestrel_main',firstlight_kestrel_main)
firstlight_kestrel_exit=firstlight_guard('firstlight_kestrel_exit',firstlight_kestrel_exit)
