require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Broadwing Kestrel choreography. Eight visual entities share one mission-safe controller:
-- insertion/extraction x flight/convert/flare/landed. Mission state stays authoritative elsewhere.
-- Motion is procedural so the ship carries inertia and VTOL weight while the authored
-- conversion mesh bridges cruise hardware and full powered-lift configuration.
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
 if string.find(name,'CONVERT',1,true) then return 'convert' end
 return 'flight'
end
local function staged(raw,a,b,first,middle,last)
 if raw<a then return first end
 if raw<b then return middle end
 return last
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
  -- ~15.5 s, starts conversion before the pad, then establishes full lift for the hold.
  local raw=elapsed/math.max(1000,(aegis.cinematic_duration_ms or 18000)-2300)
  local t=smooth(raw)
  show_state(e,s,staged(raw,0.58,0.78,'flight','convert','flare'))

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
   show_state(e,s,staged(raw,0.18,0.50,'flare','convert','flight'))
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
 elseif ms<2700 then
  -- Vertical clearance begins on full lift with the gear still fully deployed.
  local t=smooth((ms-1100)/1600)
  local correction=math.max(0,1-t)*0.60
  local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,correction)
  show_state(e,s,'flare')
  pose(e,s.x+dx,
       lerp(s.y,s.y+270,t)+dy,
       lerp(s.z,s.z-55,t)+dz,
       lerp(0,-1.5,t)+dp,
       lerp(180,176,t)+dyaw,
       lerp(0,-1.0,t)+dr)
 elseif ms<4000 then
  -- Above the LZ, unload vertical thrust while the gear and lift doors visibly retract.
  local t=smooth((ms-2700)/1300)
  local correction=math.max(0,1-t)*0.35
  local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,correction)
  show_state(e,s,'convert')
  pose(e,lerp(s.x,s.x-90,t)+dx,
       lerp(s.y+270,s.y+430,t)+dy,
       lerp(s.z-55,s.z-140,t)+dz,
       lerp(-1.5,-2.8,t)+dp,
       lerp(176,169,t)+dyaw,
       lerp(-1.0,1.5,t)+dr)
 else
  -- Once conversion is complete, accelerate away on cruise thrust with a coordinated
  -- bank and nose-down attitude arriving progressively with forward speed.
  local t=smooth((ms-4000)/4000)
  local turn=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flight')
  pose(e,lerp(s.x-90,s.x-2050,t),
       lerp(s.y+430,s.y+1320,t),
       lerp(s.z-140,s.z-2550,t),
       lerp(-2.8,-7,t)-turn*1.4,
       lerp(169,142,t)-turn*1.2,
       lerp(1.5,8,t)+turn*3.0)
  if ms>=8000 then set_visible(e,s,false) end
 end
end

local function extraction(e,s)
 if not fl or not fl.started or fl.evac_start==0 then set_visible(e,s,false);return end
 if aegis and aegis.kestrel_depart then departure(e,s);return end
 local elapsed=fl.evac_elapsed or 0
 if elapsed<36000 then set_visible(e,s,false);return end

 if elapsed<47000 then
  -- Long oblique approach: clean airframe and cruise thrust. Bank follows the turn
  -- and unloads before the conversion gate instead of disappearing on a mesh pop.
  local raw=(elapsed-36000)/11000
  local t=smooth(raw)
  local turn=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flight')
  pose(e,lerp(s.x+3400,s.x+1050,t),
       lerp(s.y+1480,s.y+590,t),
       lerp(s.z-3350,s.z-980,t),
       lerp(-4,-0.4,t)+turn*1.2,
       lerp(228,198,t)-turn*1.5,
       lerp(-6,-0.8,t)-turn*3.2)
 elseif elapsed<53000 then
  -- Mechanical conversion has its own authored silhouette: lift doors crack open and
  -- the landing gear is only part-way down while cruise thrust still carries the ship.
  local raw=(elapsed-47000)/6000
  local t=smooth(raw)
  local correction=math.sin(clamp01(t)*math.pi)*0.24
  local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,correction)
  show_state(e,s,'convert')
  pose(e,lerp(s.x+1050,s.x+440,t)+dx,
       lerp(s.y+590,s.y+300,t)+dy,
       lerp(s.z-980,s.z-410,t)+dz,
       lerp(-0.4,-1.2,t)+dp,
       lerp(198,187,t)+dyaw,
       lerp(-0.8,-1.1,t)+dr)
 elseif elapsed<60000 then
  -- Full powered-lift flare: forward motion bleeds away, then the craft settles mostly vertically.
  local raw=(elapsed-53000)/7000
  local t=smooth(raw)
  local damping=math.max(0,1-t)*0.75
  local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,damping)
  local flare=math.sin(clamp01(t)*math.pi)
  show_state(e,s,'flare')
  pose(e,lerp(s.x+440,s.x,t)+dx,
       lerp(s.y+300,s.y,t)+dy,
       lerp(s.z-410,s.z,t)+dz,
       lerp(-1.2,0,t)-flare*1.6+dp,
       lerp(187,180,t)+dyaw,
       lerp(-1.1,0,t)-flare*1.3+dr)
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