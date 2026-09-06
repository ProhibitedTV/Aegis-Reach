-- DESCRIPTION: Sequential relay objective. Hold E for three seconds beside it.
-- Uses MAX-native emissive + Visual Logic hooks so authored set pieces can hang off relay completion.
local relay={}

local function relay_color(e,r,g,b,strength)
 SetEntityEmissiveColor(e,r,g,b)
 SetEntityEmissiveStrength(e,strength)
end

function aegis_relay_init_name(e,name)
 relay[e]={index=tonumber(string.match(name,"RELAY (%d)")) or 1,progress=0,last=0,done=false}
 -- Hostile/offline state: warm low-energy glow. This becomes cyan once captured.
 relay_color(e,255,136,66,35)
 SetActivated(e,0)
end

function aegis_relay_main(e)
 if not aegis or not aegis.started or g_PlayerHealth<=0 or aegis.extracted then return end
 local r=relay[e]; if not r then return end
 local now=g_Time;local dt=0
 if r.last>0 then dt=math.min(100,math.max(0,now-r.last)) end
 r.last=now

 if r.done then
  relay_color(e,72,226,238,480)
  if GetPlayerDistance(e)<180 then Prompt("RELAY ONLINE") end
  return
 end

 if aegis.phase~=r.index then
  relay_color(e,194,101,53,25)
  if GetPlayerDistance(e)<175 then Prompt("Restore the previous relay first") end
  return
 end

 -- Active objective breathes gently even before interaction so the world itself points the way.
 local idle=75+math.floor((math.sin(g_Time*0.003)+1)*22)
 relay_color(e,242,164,56,idle)
 if GetPlayerDistance(e)>175 then r.progress=0; return end

 if g_KeyPressE==1 then r.progress=r.progress+dt else r.progress=0 end
 local pct=math.min(100,math.floor(r.progress/30))
 Prompt("Hold E to override relay // "..pct.."%")
 -- Charge from amber toward hot white-cyan during the hold.
 local charge=math.min(1,r.progress/3000)
 relay_color(e,math.floor(242-145*charge),math.floor(164+66*charge),math.floor(56+176*charge),120+math.floor(520*charge))

 if r.progress>=3000 then
  r.done=true
  aegis.relays[r.index]=true
  aegis.relay_times=aegis.relay_times or {}
  aegis.relay_times[r.index]=math.floor((g_Time-(aegis.born or g_Time))/1000)
  aegis.phase=r.index+1
  relay_color(e,72,226,238,650)
  PlaySound(e,0)

  -- Native MAX integration: anything connected in Visual Logic can now react
  -- without the mission script knowing its entity ID (lights, doors, CineGuru,
  -- particles, audio, holograms, etc.). IfUsed remains available for classic links.
  SetActivated(e,1)
  PerformLogicConnections(e)
  ActivateIfUsed(e)

  if r.index==1 then
   aegis_message("NORTHSTAR online. Flank through the blast gates to LANTERN.",8)
  elseif r.index==2 then
   aegis_message("LANTERN online. The AEGIS core is ahead. Expect countermeasures and reserves.",8)
  else
   aegis_message("Orbital strike CANCELLED. AEGIS uplink captured -- suit boost live. Kestrel inbound!",10)
  end
 end
end
