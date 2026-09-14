require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Broadwing Kestrel choreography. Eight visual entities share one mission-safe controller:
-- insertion/extraction x flight/convert/flare/landed. Mission state stays authoritative elsewhere.
-- Opening insertion motion is one continuous 50.8 second flight clock. Camera cuts can
-- now happen every few seconds without restarting the aircraft path or making it pop.
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
local function curve(a,b,bow,t)return lerp(a,b,t)+math.sin(clamp01(t)*math.pi)*bow end
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
local function show_state(e,s,wanted)set_visible(e,s,s.variant==wanted) end
local function variant_from_name(name)
 if string.find(name,'LANDED',1,true) then return 'landed' end
 if string.find(name,'FLARE',1,true) then return 'flare' end
 if string.find(name,'CONVERT',1,true) then return 'convert' end
 return 'flight'
end

-- Deterministic low-amplitude VTOL movement. The Broadwing should feel like a heavy
-- powered-lift vehicle correcting on jets, not a light helicopter bobbing on a spring.
local function hover_motion(ms,amount)
 amount=amount or 1;local a=(ms or 0)*0.001
 local y=(math.sin(a*4.7)*1.15+math.sin(a*2.1+0.8)*0.55)*amount
 local x=math.sin(a*1.7+1.1)*0.85*amount;local z=math.sin(a*1.35+2.0)*0.70*amount
 local pitch=math.sin(a*2.5+0.5)*0.32*amount;local roll=math.sin(a*2.9+1.6)*0.48*amount;local yaw=math.sin(a*1.1)*0.22*amount
 return x,y,z,pitch,yaw,roll
end

local function insertion_ground_y(s)
 if GetGroundHeight then local ok,h=pcall(GetGroundHeight,s.x,s.z);if ok and type(h)=='number' then return h-4 end end
 return s.y-194
end

local function opening_ms()
 if not aegis then return nil end
 if type(aegis.opening_elapsed_ms)=='number' then return aegis.opening_elapsed_ms end
 if aegis.opening_started_at then return g_Time-aegis.opening_started_at end
 return nil
end

function firstlight_kestrel_init_name(e,name)
 local ent=g_Entity and g_Entity[e] or {};local role=string.find(name,'INSERTION',1,true) and 'insertion' or 'extraction'
 ships[e]={role=role,variant=variant_from_name(name),x=ent.x or 0,y=ent.y or 0,z=ent.z or 0,visible=false,depart_start=0}
 Hide(e);CollisionOff(e)
 if aegis then if role=='insertion' then aegis.insertion_complete=false else aegis.kestrel_landed=false end end
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

local function insertion(e,s)
 if not fl or not fl.started or (aegis and aegis.insertion_complete) then set_visible(e,s,false);return end
 local ms=opening_ms();if not ms then set_visible(e,s,false);return end
 local base_y=insertion_ground_y(s)

 -- 0-8.4s: distant approach. The first perimeter/security views see the ship already
 -- in motion at long range instead of waiting for it to materialize near the base.
 if ms<8400 then
  local t=smooth(ms/8400)
  if aegis then aegis.kestrel_opening_state='flight' end;show_state(e,s,'flight')
  pose(e,s.x+curve(-2700,-1450,180,t),base_y+curve(1250,880,70,t),s.z+curve(-2500,-1550,-120,t),
       lerp(-5,-3,t),lerp(138,154,t),lerp(7,4,t))

 -- 8.4-17.5s: fast crossing and bank around the site. Multiple camera cuts happen
 -- during this single uninterrupted flight segment.
 elseif ms<17500 then
  local t=smooth((ms-8400)/9100);local arc=math.sin(t*math.pi)
  if aegis then aegis.kestrel_opening_state='flight' end;show_state(e,s,'flight')
  pose(e,s.x+curve(-1450,850,320,t),base_y+curve(880,650,35,t),s.z+curve(-1550,-650,-220,t),
       lerp(-3,-1,t)-arc*.7,lerp(154,194,t)+arc*4.5,lerp(4,-7,t)-arc*2.5)

 -- 17.5-23.5s: mechanical conversion. The flight->convert state swap lands on the
 -- MAST->VENTRAL-AFT edit, while the world-space trajectory itself remains continuous.
 elseif ms<23500 then
  local t=smooth((ms-17500)/6000);local arc=math.sin(t*math.pi)
  if aegis then aegis.kestrel_opening_state='convert' end;show_state(e,s,'convert')
  pose(e,s.x+curve(850,520,-1150,t),base_y+curve(650,500,80,t),s.z+curve(-650,360,260,t),
       lerp(-1,-.6,t)-arc*.8,lerp(194,180,t)+arc*34,lerp(-7,-2,t)+arc*9)

 -- 23.5-32.5s: full powered-lift approach. Three short sources cover the same
 -- continuous flare instead of one long camera staring at the base.
 elseif ms<32500 then
  local t=smooth((ms-23500)/9000);local flare=math.sin(t*math.pi)
  local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,(1-t)*.45)
  if aegis then aegis.kestrel_opening_state='flare' end;show_state(e,s,'flare')
  pose(e,s.x+curve(520,0,-120,t)+dx,base_y+curve(500,0,45,t)+dy,s.z+curve(360,0,60,t)+dz,
       lerp(-.6,0,t)-flare*1.7+dp,180+dyaw,lerp(-2,0,t)-flare*1.4+dr)

 -- 32.5-42.7s: actual grounded deployment. Pad cameras see the whole ship settle,
 -- then the ramp feed takes over while the recorded briefing finishes.
 elseif ms<42700 then
  if aegis then aegis.kestrel_opening_state='landed' end;show_state(e,s,'landed');pose(e,s.x,base_y,s.z,0,180,0)

 -- 42.7-45.3s: vertical clearance on lift thrust.
 elseif ms<45300 then
  local t=smooth((ms-42700)/2600);local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,(1-t)*.55)
  if aegis then aegis.kestrel_opening_state='flare' end;show_state(e,s,'flare')
  pose(e,s.x+dx,base_y+lerp(0,300,t)+dy,s.z+lerp(0,-70,t)+dz,lerp(0,-1.5,t)+dp,lerp(180,176,t)+dyaw,lerp(0,-1,t)+dr)

 -- 45.3-47.8s: unload powered lift and retract toward cruise configuration.
 elseif ms<47800 then
  local t=smooth((ms-45300)/2500);local arc=math.sin(t*math.pi)
  if aegis then aegis.kestrel_opening_state='convert' end;show_state(e,s,'convert')
  pose(e,s.x+curve(0,180,70,t),base_y+lerp(300,620,t),s.z+curve(-70,-420,-45,t),
       lerp(-1.5,-3,t),lerp(176,166,t),lerp(-1,3,t)+arc*2)

 -- 47.8-50.8s: tail camera watches a clean cruise departure.
 elseif ms<50800 then
  local t=smooth((ms-47800)/3000);local arc=math.sin(t*math.pi)
  if aegis then aegis.kestrel_opening_state='flight' end;show_state(e,s,'flight')
  pose(e,s.x+curve(180,2300,260,t),base_y+curve(620,1300,80,t),s.z+curve(-420,-2600,-180,t),
       lerp(-3,-7,t)-arc*1.2,lerp(166,142,t)-arc*3,lerp(3,9,t)+arc*4)
 else
  set_visible(e,s,false)
 end
end

local function departure(e,s)
 if not aegis.cinematic_active or aegis.cinematic_beat~='EXTRACTION' then return end
 if s.depart_start==0 then s.depart_start=aegis.cinematic_started_at or g_Time end
 local ms=(g_Time-s.depart_start)*8000/math.max(1000,(aegis.cinematic_duration_ms or 8300)-300)
 if aegis then aegis.kestrel_landed=false end
 if ms<1100 then
  show_state(e,s,'landed');pose(e,s.x,s.y,s.z,0,180,0)
 elseif ms<2700 then
  local t=smooth((ms-1100)/1600);local correction=math.max(0,1-t)*0.60;local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,correction)
  show_state(e,s,'flare')
  pose(e,s.x+dx,lerp(s.y,s.y+270,t)+dy,lerp(s.z,s.z-55,t)+dz,lerp(0,-1.5,t)+dp,lerp(180,176,t)+dyaw,lerp(0,-1.0,t)+dr)
 elseif ms<4000 then
  local t=smooth((ms-2700)/1300);local correction=math.max(0,1-t)*0.35;local dx,dy,dz,dp,dyaw,dr=hover_motion(ms,correction)
  show_state(e,s,'convert')
  pose(e,lerp(s.x,s.x-90,t)+dx,lerp(s.y+270,s.y+430,t)+dy,lerp(s.z-55,s.z-140,t)+dz,lerp(-1.5,-2.8,t)+dp,lerp(176,169,t)+dyaw,lerp(-1.0,1.5,t)+dr)
 else
  local t=smooth((ms-4000)/4000);local turn=math.sin(clamp01(t)*math.pi);show_state(e,s,'flight')
  pose(e,lerp(s.x-90,s.x-2050,t),lerp(s.y+430,s.y+1320,t),lerp(s.z-140,s.z-2550,t),
       lerp(-2.8,-7,t)-turn*1.4,lerp(169,142,t)-turn*1.2,lerp(1.5,8,t)+turn*3.0)
  if ms>=8000 then set_visible(e,s,false) end
 end
end

local function extraction(e,s)
 if not fl or not fl.started or fl.evac_start==0 then set_visible(e,s,false);return end
 if aegis and aegis.kestrel_depart then departure(e,s);return end
 local elapsed=fl.evac_elapsed or 0
 if elapsed<36000 then set_visible(e,s,false);return end
 if elapsed<47000 then
  local t=smooth((elapsed-36000)/11000);local turn=math.sin(clamp01(t)*math.pi);show_state(e,s,'flight')
  pose(e,lerp(s.x+3400,s.x+1050,t),lerp(s.y+1480,s.y+590,t),lerp(s.z-3350,s.z-980,t),
       lerp(-4,-0.4,t)+turn*1.2,lerp(228,198,t)-turn*1.5,lerp(-6,-0.8,t)-turn*3.2)
 elseif elapsed<53000 then
  local t=smooth((elapsed-47000)/6000);local correction=math.sin(clamp01(t)*math.pi)*0.24;local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,correction);show_state(e,s,'convert')
  pose(e,lerp(s.x+1050,s.x+440,t)+dx,lerp(s.y+590,s.y+300,t)+dy,lerp(s.z-980,s.z-410,t)+dz,
       lerp(-0.4,-1.2,t)+dp,lerp(198,187,t)+dyaw,lerp(-0.8,-1.1,t)+dr)
 elseif elapsed<60000 then
  local t=smooth((elapsed-53000)/7000);local damping=math.max(0,1-t)*0.75;local dx,dy,dz,dp,dyaw,dr=hover_motion(elapsed,damping);local flare=math.sin(clamp01(t)*math.pi);show_state(e,s,'flare')
  pose(e,lerp(s.x+440,s.x,t)+dx,lerp(s.y+300,s.y,t)+dy,lerp(s.z-410,s.z,t)+dz,
       lerp(-1.2,0,t)-flare*1.6+dp,lerp(187,180,t)+dyaw,lerp(-1.1,0,t)-flare*1.3+dr)
 else
  show_state(e,s,'landed');pose(e,s.x,s.y,s.z,0,180,0);if aegis then aegis.kestrel_landed=true end
 end
end

function firstlight_kestrel_main(e)local s=ships[e];if not s then return end;if s.role=='insertion' then insertion(e,s) else extraction(e,s) end end
function firstlight_kestrel_exit(e)ships[e]=nil end
firstlight_kestrel_init_name=firstlight_guard('firstlight_kestrel_init_name',firstlight_kestrel_init_name)
firstlight_kestrel_main=firstlight_guard('firstlight_kestrel_main',firstlight_kestrel_main)
firstlight_kestrel_exit=firstlight_guard('firstlight_kestrel_exit',firstlight_kestrel_exit)
