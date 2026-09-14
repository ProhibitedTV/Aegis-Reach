require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Broadwing Kestrel choreography. Six visual entities share one mission-safe controller:
-- insertion/extraction x flight/flare/landed. Mission state stays authoritative elsewhere.
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
local function set_visible(e,s,on)
 if on and not s.visible then Show(e);s.visible=true
 elseif not on and s.visible then Hide(e);s.visible=false end
end
local function show_state(e,s,wanted)
 set_visible(e,s,s.variant==wanted)
end
local function variant_from_name(name)
 if string.find(name,'LANDED',1,true) then return 'landed' end
 if string.find(name,'FLARE',1,true) then return 'flare' end
 return 'flight'
end

function firstlight_kestrel_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or {}
 local role=string.find(name,'INSERTION',1,true) and 'insertion' or 'extraction'
 ships[e]={role=role,variant=variant_from_name(name),x=ent.x or 0,y=ent.y or 0,z=ent.z or 0,
           visible=false,intro_start=0,handoff_start=0,depart_start=0}
 Hide(e);CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

local function insertion(e,s)
 if not fl or not fl.started then set_visible(e,s,false);return end
 local beat=aegis and aegis.cinematic_beat or nil
 if beat=='ARRIVAL' then
  if s.intro_start==0 then s.intro_start=g_Time end
  local elapsed=g_Time-s.intro_start
  -- Recorded VO gives the approach room to breathe: the ship crosses and descends for
  -- ~15.5 s, converts near the pad, then holds through the end of the 18 s shot.
  local raw=elapsed/15500
  local t=smooth(raw)
  show_state(e,s,raw<0.78 and 'flight' or 'flare')
  pose(e,lerp(s.x-1250,s.x,t),lerp(s.y+720,s.y,t),lerp(s.z-1450,s.z,t),
       lerp(-6,0,t),lerp(148,180,t),lerp(5,0,t))
 elseif beat=='ARRIVAL_HANDOFF' then
  if s.handoff_start==0 then s.handoff_start=g_Time end
  local elapsed=g_Time-s.handoff_start
  if elapsed<18500 then
   -- Kestrel stays settled while the evidence/order dialogue plays. This prevents
   -- the aircraft from flying away long before the pilot finishes the briefing.
   show_state(e,s,'flare')
   pose(e,s.x,s.y,s.z,0,180,0)
  else
   local raw=(elapsed-18500)/6200
   local t=smooth(raw)
   show_state(e,s,raw<0.28 and 'flare' or 'flight')
   pose(e,lerp(s.x,s.x+2050,t),lerp(s.y,s.y+1080,t),lerp(s.z,s.z-2050,t),
        lerp(0,-5,t),lerp(180,218,t),lerp(0,-7,t))
  end
 elseif s.handoff_start>0 and g_Time-s.handoff_start>25500 then
  set_visible(e,s,false)
 elseif g_Time-(fl.born or g_Time)>50000 then
  -- Fail-open opening path: never leave any Kestrel state parked forever.
  set_visible(e,s,false)
 else
  set_visible(e,s,false)
 end
end

local function departure(e,s)
 if s.depart_start==0 then s.depart_start=g_Time end
 local ms=g_Time-s.depart_start
 if aegis then aegis.kestrel_landed=false end
 if ms<1100 then
  -- Ramp closes / ship takes the weight before thrust comes up.
  show_state(e,s,'landed')
  pose(e,s.x,s.y,s.z,0,180,0)
 elseif ms<3300 then
  -- Vertical clearance on the lift system with gear still out.
  local t=smooth((ms-1100)/2200)
  show_state(e,s,'flare')
  pose(e,s.x,lerp(s.y,s.y+360,t),lerp(s.z,s.z-80,t),lerp(0,-2,t),lerp(180,174,t),0)
 else
  -- Once clear of the pad, stow the VTOL/gear hardware and accelerate away.
  local t=smooth((ms-3300)/4700)
  show_state(e,s,'flight')
  pose(e,lerp(s.x,s.x-2050,t),lerp(s.y+360,s.y+1320,t),lerp(s.z-80,s.z-2550,t),
       lerp(-2,-7,t),lerp(174,142,t),lerp(0,8,t))
  if ms>=8000 then set_visible(e,s,false) end
 end
end

local function extraction(e,s)
 if not fl or not fl.started or fl.evac_start==0 then set_visible(e,s,false);return end
 if aegis and aegis.kestrel_depart then departure(e,s);return end
 local elapsed=fl.evac_elapsed or 0
 if elapsed<36000 then set_visible(e,s,false);return end

 if elapsed<50000 then
  -- Long oblique approach: clean airframe, cruise thrust, no dangling landing gear.
  local t=smooth((elapsed-36000)/14000)
  show_state(e,s,'flight')
  pose(e,lerp(s.x+3400,s.x+780,t),lerp(s.y+1480,s.y+470,t),lerp(s.z-3350,s.z-730,t),
       lerp(-4,0,t),lerp(228,192,t),lerp(-6,0,t))
 elseif elapsed<60000 then
  -- Convert to lift around the CG, slow forward motion first, then settle mostly vertically.
  local t=smooth((elapsed-50000)/10000)
  show_state(e,s,'flare')
  local horizontal=smooth(math.min(1,(elapsed-50000)/5200))
  pose(e,lerp(s.x+780,s.x,horizontal),lerp(s.y+470,s.y,t),lerp(s.z-730,s.z,horizontal),
       lerp(0,0,t),lerp(192,180,horizontal),0)
 else
  show_state(e,s,'landed')
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
