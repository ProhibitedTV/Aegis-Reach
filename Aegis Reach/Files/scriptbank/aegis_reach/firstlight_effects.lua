-- Native MAX particle markers: localized environmental consequences.
-- Engine owns emitter allocation/cleanup. No legacy particle allocator or global wind.
local states={}
local configs={
 CAMP_FAULT={kind='spark',opacity=80,speed=190,life=18,color={147,207,238},period=3100},
 GATE_SMOKE={kind='smoke',opacity=28,speed=48,life=65,color={99,109,118}},
 GATE_EMBERS={kind='spark',opacity=62,speed=130,life=28,color={239,144,66},period=2700},
 POWER_VENT={kind='smoke',opacity=18,speed=60,life=55,color={171,186,200}},
 ARCHIVE_SMOKE={kind='smoke',opacity=24,speed=38,life=60,color={87,98,110}},
 ARRAY_FAULT={kind='spark',opacity=78,speed=210,life=16,color={112,185,235},period=2200},
 WRECK_FIRE={kind='fire',opacity=96,speed=96,life=84,color={255,196,132},range=5200},
 WRECK_FIRE_AUX={kind='fire',opacity=90,speed=82,life=76,color={255,176,110},range=4500},
 WRECK_SMOKE={kind='smoke',opacity=54,speed=72,life=135,color={70,77,84},range=6500},
 WRECK_SPARKS={kind='spark',opacity=96,speed=240,life=24,color={255,151,62},period=1150,range=3800},
}

local function long_range_wreck(role)
 return role=='WRECK_FIRE' or role=='WRECK_FIRE_AUX' or role=='WRECK_SMOKE' or role=='WRECK_SPARKS'
end

function firstlight_effects_init_name(e,name)
 local role=string.match(name,'FL FX ([%w_]+)')
 states[e]={role=role,active=false,configured=false,next_burst=0,next_check=0}
 CollisionOff(e)
 -- MAX distributes ordinary entity logic by distance. These four wreck markers are
 -- intentional long-range landmarks, so keep only their lightweight 10 Hz controller
 -- alive; the particle emitters themselves are still started/stopped by player range.
 if SetEntityAlwaysActive and long_range_wreck(role) then SetEntityAlwaysActive(e,1) end
 if EffectStop then EffectStop(e) end
end

local function allowed(role,stage)
 if role=='CAMP_FAULT' then return stage==1 end
 if role=='POWER_VENT' then return stage>=2 end
 if role=='ARRAY_FAULT' then return stage==3 end
 return true
end

function firstlight_effects_main(e)
 local s=states[e];if not s or not EffectStart then return end
 local c=configs[s.role];if not c then return end
 if g_Time<s.next_check then return end
 s.next_check=g_Time+100
 if not s.configured then
  EffectSetOpacity(e,c.opacity);EffectSetSpeed(e,c.speed)
  EffectSetColor(e,c.color[1],c.color[2],c.color[3])
  EffectSetLifespan(e,c.life)
  EffectSetBurstMode(e,c.kind=='spark' and 1 or 0)
  if s.role=='CAMP_FAULT' or s.role=='ARRAY_FAULT' then EffectSetLocalRotation(e,0,0,70) end
  if s.role=='WRECK_SPARKS' then EffectSetLocalRotation(e,-18,12,58) end
  s.configured=true
 end
 -- Hysteresis avoids repeatedly starting/stopping at the edge of an effect area.
 local distance=GetPlayerDistance(e)
 local range=(c.range or 2100)+(s.active and 300 or 0)
 local on=fl and fl.started and not fl.won and g_PlayerHealth>0
          and allowed(s.role,fl.stage) and distance<range
 if on and not s.active then
  EffectStart(e);s.active=true;s.next_burst=g_Time+(e%5)*110
 elseif not on and s.active then
  EffectStop(e);s.active=false
 end
 -- One close 3D burn loop belongs to the primary rupture; secondary FX stay visual.
 if s.role=='WRECK_FIRE' and LoopSound and SetSoundVolume and StopSound then
  if on and distance<1200 then
   LoopSound(e,0);SetSoundVolume(math.min(58,math.max(0,(1200-distance)*.065)))
   s.audible=true
  elseif s.audible then StopSound(e,0);s.audible=false end
 end
 if s.active and c.kind=='spark' and g_Time>=s.next_burst then
  EffectFireBurst(e);s.next_burst=g_Time+c.period
 end
end

function firstlight_effects_exit(e)
 if EffectStop then EffectStop(e) end
 if states[e] and states[e].audible and StopSound then StopSound(e,0) end
 states[e]=nil
end
