-- DESCRIPTION: Mission-reactive perimeter / horizon beacon.
-- Uses MAX's native emissive API; intended for immobile Always Active environment props.
local beacon={}

function aegis_beacon_init_name(e,name)
 local hash=0
 for i=1,string.len(name or "") do hash=(hash+string.byte(name,i)*i)%628 end
 beacon[e]={phase=-1,offset=hash/100}
 SetEntityEmissiveColor(e,74,204,218)
 SetEntityEmissiveStrength(e,35)
 SetActivated(e,0)
end

function aegis_beacon_main(e)
 local b=beacon[e]
 if not b then return end
 local mode=(aegis and aegis.signal_mode) or "standard"
 local t=g_Time*0.002+b.offset
 local strength=45
 local r,g,bl=74,204,218

 if mode=="interference" then
  -- Disturbed network: asymmetric amber flicker.
  local flicker=math.abs(math.sin(t*3.1)*math.sin(t*1.37))
  r,g,bl=244,142,66
  strength=35+flicker*180
 elseif mode=="overcharge" then
  -- Captured network: clean, confident cyan pulse.
  r,g,bl=72,232,225
  strength=110+(math.sin(t*1.8)+1)*75
 else
  strength=45+(math.sin(t)+1)*28
 end

 SetEntityEmissiveColor(e,r,g,bl)
 SetEntityEmissiveStrength(e,strength)

 local phase=(aegis and aegis.phase) or 0
 if phase~=b.phase then
  b.phase=phase
  -- Make each phase transition available to authored MAX logic as well.
  SetActivated(e,1)
  PerformLogicConnections(e)
  ActivateIfUsed(e)
  SetActivated(e,0)
 end
end
