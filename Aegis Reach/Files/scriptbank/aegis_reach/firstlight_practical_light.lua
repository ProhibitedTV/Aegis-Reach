require 'scriptbank\\aegis_reach\\firstlight_audit'

-- Responsive local practicals for the M-17 wreck.
-- Uses MAX's native light API rather than spawning extra lights or particle emitters.
local states={}

local function config(name)
 if string.find(name or '','2',1,true) then
  return {base=260,r=216,g=74,b=50,phase=1.9}
 end
 return {base=520,r=255,g=139,b=66,phase=.4}
end

function firstlight_practical_light_init_name(e,name)
 local c=config(name)
 states[e]={base=c.base,r=c.r,g=c.g,b=c.b,phase=c.phase+(e%11)*.17,next_tick=0}
end

function firstlight_practical_light_main(e)
 local s=states[e]
 if not s or not GetEntityLightNumber or not SetLightRange then return end
 if g_Time < s.next_tick then return end
 s.next_tick=g_Time+70

 local light=GetEntityLightNumber(e)
 if light==nil or light<0 then return end

 -- Two incommensurate waves give fire-like motion without per-frame random churn.
 local t=g_Time*.0105+s.phase
 local pulse=.55+.28*math.sin(t)+.17*math.sin(t*2.37+1.7)
 if pulse<0 then pulse=0 elseif pulse>1 then pulse=1 end
 local range=s.base*(.72+.28*pulse)
 SetLightRange(light,range)

 if SetLightRGB then
  local hot=math.floor(18*pulse)
  SetLightRGB(light,
   math.min(255,s.r+hot),
   math.min(255,s.g+math.floor(hot*.35)),
   s.b)
 end
end

function firstlight_practical_light_exit(e)
 local s=states[e]
 if s and GetEntityLightNumber and SetLightRange then
  local light=GetEntityLightNumber(e)
  if light~=nil and light>=0 then
   SetLightRange(light,s.base)
   if SetLightRGB then SetLightRGB(light,s.r,s.g,s.b) end
  end
 end
 states[e]=nil
end

firstlight_practical_light_init_name=firstlight_guard('firstlight_practical_light_init_name',firstlight_practical_light_init_name)
firstlight_practical_light_main=firstlight_guard('firstlight_practical_light_main',firstlight_practical_light_main)
firstlight_practical_light_exit=firstlight_guard('firstlight_practical_light_exit',firstlight_practical_light_exit)
