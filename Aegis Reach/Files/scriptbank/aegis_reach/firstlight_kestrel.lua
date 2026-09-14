require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Broadwing Kestrel choreography. Six visual entities share one mission-safe controller:
-- insertion/extraction x flight/flare/landed. Mission state stays authoritative elsewhere.
-- Motion is procedural so the ship carries inertia and VTOL weight even though the
-- current airframe still uses discrete visual mesh swaps for its hardware states.
local ships={}

local function smooth(t)
 if t<0 then return 0 elseif t>1 then return 1 end
 return t*t*(3-2*t)
end
local function clamp01(t)
 if t<0 then return 0 elseif t>1 then return 1 end
 return t
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

-- Deterministic low-amplitude VTOL movement. This is intentionally subtle: the
-- Broadwing should feel like a heavy powered-lift vehicle correcting on its jets,
-- not a light helicopter bobbing on a spring. `amount` fades the correction as the
-- aircraft settles onto its gear or commits to forward flight.
local function hover_motion(ms,amount)
 amount=amount or 1
 local a=(ms or 0)*0.001
 local y=(math.sin(a*4.7)*1.15+math.sin(a*2.1+0.8)*0.55)*amount
 local x=math.sin(a*1.7+1.1)*0.85*amount
 local z=math.sin(a*1.35+2.0)*0.70*amount
 local pitch=math.sin(a*2.5+0.5)*0.32*amount
 local roll=math.sin(a*2.9+1.6)*0.48*amount
 local yaw=math.sin(a*1.1)*0.22*amount
 return x,y,z,pitch,yaw,roll
end

local function pose_hover(e,s,ms,amount,yaw)
 local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,amount)
 pose(e,s.x+dx,s.y+dy,s.z+dz,dp,(yaw or 180)+dyaw,dr)
end

function firstlight_kestrel_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or {}
 local role=string.find(name,'INSERTION',1,true) and 'insertion' or 'extraction'
 ships[e]={role=role,variant=variant_from_name(name),x=ent.x or 0,y=ent.y or 0,z=ent.z or 0,
           visible=false,intro_start=0,handoff_start=0,depart_start=0}
 Hide(e);CollisionOff(e)
 if aegis then if role=='insertion' then aegis.insertion_complete=false else aegis.kestrel_landed=false end end
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

local function insertion(e,s)
 if not fl or not fl.started or (aegis and aegis.insertion_complete) then set_visible(e,s,false);return end
 local beat=aegis and aegis.cinematic_beat or nil
 if beat=='ARRIVAL' then
  if s.intro_start==0 then s.intro_start=aegis.cinematic_started_at or g_Time end
  local elapsed=g_Time-s.intro_start
  -- Recorded VO gives the approach room to breathe: the ship crosses and descends for
  -- ~15.5 s, converts near the pad, then holds through the end of the 18 s shot.
  local raw=elapsed/math.max(1000,(aegis.cinematic_duration_ms or 18000)-2300)
  local t=smooth(raw)
  show_state(e,s,raw<0.78 and 'flight' or 'flare')

  -- The approach carries a shallow coordinated bank and deceleration pitch instead
  -- of sliding a rigid model down a spline. Both return to neutral before touchdown.
  local turn=math.sin(clamp01(t)*math.pi)
  local settle=smooth(clamp01((raw-0.72)/0.28))
  local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,settle*0.55)
  pose(e,lerp(s.x-1250,s.x,t)+dx,
       lerp(s.y+720,s.y,t)+dy,
       lerp(s.z-1450,s.z,t)+dz,
       lerp(-6,0,t)+turn*1.4+dp,
       lerp(148,180,t)+turn*2.2+dyaw,
       lerp(5,0,t)-turn*3.8+dr)
 elseif beat=='ARRIVAL_HANDOFF' then
  if s.handoff_start==0 then s.handoff_start=aegis.cinematic_started_at or g_Time end
  local elapsed=g_Time-s.handoff_start
  local hold=math.max(0,(aegis.cinematic_duration_ms or 25000)-6500)
  if elapsed<hold then
   -- Kestrel stays over the pad while the evidence/order dialogue plays. Powered-lift
   -- corrections keep the hold alive without moving the boarding footprint materially.
   show_state(e,s,'flare')
   pose_hover(e,s,elapsed,0.65,180)
  else
   local raw=(elapsed-hold)/6200
   local t=smooth(raw)
   show_state(e,s,raw<0.28 and 'flare' or 'flight')
   local lift=smooth(clamp01(raw/0.32))
   local cruise=smooth(clamp01((raw-0.24)/0.76))
   local turn=math.sin(clamp01(t)*math.pi)
   local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,math.max(0,1-cruise)*0.55)
   pose(e,lerp(s.x,s.x+2050,t)+dx,
        lerp(s.y,s.y+1080,lift*0.42+t*0.58)+dy,
        lerp(s.z,s.z-2050,t)+dz,
        lerp(0,-5,t)-turn*1.0+dp,
        lerp(180,218,t)+turn*1.8+dyaw,
        lerp(0,-7,t)-turn*2.0+dr)
  end
 elseif s.handoff_start>0 then
  set_visible(e,s,false)
 elseif g_Time-(fl.born or g_Time)>50000 then
  -- Fail-open opening path: never leave any Kestrel state parked forever.
  set_visible(e,s,false)
 else
  set_visible(e,s,false)
 end
end

local function departure(e,s)
 if not aegis.cinematic_active or aegis.cinematic_beat~='EXTRACTION' then return end
 if s.depart_start==0 then s.depart_start=aegis.cinematic_started_at or g_Time end
 -- Keep the researched staged choreography inside the actual boarding shot.
 local ms=(g_Time-s.depart_start)*8000/math.max(1000,(aegis.cinematic_duration_ms or 8300)-300)
 if aegis then aegis.kestrel_landed=false end
 if ms<1100 then
  -- Boarding pause. Keep the landed airframe hard-stable so the collision proxy and
  -- visible ramp never disagree under the player's feet.
  show_state(e,s,'landed')
  pose(e,s.x,s.y,s.z,0,180,0)
 elseif ms<3300 then
  -- Vertical clearance on the lift system with gear still out. Lateral/yaw correction
  -- fades as the ship gains a safe cushion above the LZ.
  local t=smooth((ms-1100)/2200)
  local correction=math.max(0,1-t)*0.60
  local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,correction)
  show_state(e,s,'flare')
  pose(e,s.x+dx,
       lerp(s.y,s.y+360,t)+dy,
       lerp(s.z,s.z-80,t)+dz,
       lerp(0,-2,t)+dp,
       lerp(180,174,t)+dyaw,
       lerp(0,-1.6,t)+dr)
 else
  -- Once clear of the pad, stow the VTOL/gear hardware and accelerate away. A
  -- coordinated bank and nose-down attitude arrive progressively with forward speed.
  local t=smooth((ms-3300)/4700)
  local turn=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flight')
  pose(e,lerp(s.x,s.x-2050,t),
       lerp(s.y+360,s.y+1320,t),
       lerp(s.z-80,s.z-2550,t),
       lerp(-2,-7,t)-turn*1.4,
       lerp(174,142,t)-turn*1.2,
       lerp(-1.6,8,t)+turn*3.0)
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
  -- Bank follows the turn and unloads as the ship reaches the conversion gate.
  local raw=(elapsed-36000)/14000
  local t=smooth(raw)
  local turn=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flight')
  pose(e,lerp(s.x+3400,s.x+780,t),
       lerp(s.y+1480,s.y+470,t),
       lerp(s.z-3350,s.z-730,t),
       lerp(-4,0,t)+turn*1.2,
       lerp(228,192,t)-turn*1.5,
       lerp(-6,0,t)-turn*3.2)
 elseif elapsed<60000 then
  -- Convert to lift around the CG, slow forward motion first, then settle mostly vertically.
  local raw=(elapsed-50000)/10000
  local t=smooth(raw)
  local horizontal=smooth(math.min(1,(elapsed-50000)/5200))
  local damping=math.max(0,1-t)*0.75
  local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,damping)
  local flare=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flare')
  pose(e,lerp(s.x+780,s.x,horizontal)+dx,
       lerp(s.y+470,s.y,t)+dy,
       lerp(s.z-730,s.z,horizontal)+dz,
       -flare*1.6+dp,
       lerp(192,180,horizontal)+dyaw,
       -flare*1.3+dr)
 else
  -- Once the ramp/collision state is live, do not add hover noise: visible geometry,
  -- the boarding collision proxy and interaction radius must remain perfectly aligned.
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