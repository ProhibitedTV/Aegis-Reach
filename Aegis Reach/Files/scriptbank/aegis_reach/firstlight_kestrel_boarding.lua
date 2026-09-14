require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Hidden, landed-only player collision for the Kestrel rear ramp and vestibule.
-- The moving visual airframe remains non-physical; this proxy never follows it.
local active={}

local function wanted()
 return fl and fl.started and aegis and aegis.kestrel_landed==true and not aegis.kestrel_depart
end

local function set_collision(e,on)
 if on==active[e] then return end
 if on then
  if CollisionOn then CollisionOn(e) end
 else
  if CollisionOff then CollisionOff(e) end
 end
 active[e]=on
end

function firstlight_kestrel_boarding_init(e)
 active[e]=false
 Hide(e)
 if CollisionOff then CollisionOff(e) end
 if GravityOff then GravityOff(e) end
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_kestrel_boarding_main(e)
 Hide(e)
 set_collision(e,wanted())
end

function firstlight_kestrel_boarding_exit(e)
 if CollisionOff then CollisionOff(e) end
 active[e]=nil
end

firstlight_kestrel_boarding_init=firstlight_guard('firstlight_kestrel_boarding_init',firstlight_kestrel_boarding_init)
firstlight_kestrel_boarding_main=firstlight_guard('firstlight_kestrel_boarding_main',firstlight_kestrel_boarding_main)
firstlight_kestrel_boarding_exit=firstlight_guard('firstlight_kestrel_boarding_exit',firstlight_kestrel_boarding_exit)
