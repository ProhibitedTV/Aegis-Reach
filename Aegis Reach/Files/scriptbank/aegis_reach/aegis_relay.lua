-- DESCRIPTION: Sequential relay objective. Hold E for three seconds beside it.
local relay={}
function aegis_relay_init_name(e,name)
 relay[e]={index=tonumber(string.match(name,"RELAY (%d)")) or 1,progress=0,last=0,done=false}
end
function aegis_relay_main(e)
 if not aegis or not aegis.started or g_PlayerHealth<=0 or aegis.extracted then return end
 local r=relay[e]; if not r then return end
 local now=g_Time;local dt=0
 if r.last>0 then dt=math.min(100,math.max(0,now-r.last)) end
 r.last=now
 if r.done then
  if GetPlayerDistance(e)<180 then Prompt("RELAY ONLINE") end
  return
 end
 if GetPlayerDistance(e)>175 then r.progress=0; return end
 if aegis.phase~=r.index then Prompt("Restore the previous relay first");return end
 if g_KeyPressE==1 then r.progress=r.progress+dt else r.progress=0 end
 Prompt("Hold E to override relay // "..math.floor(r.progress/30).."%")
 if r.progress>=3000 then
  r.done=true
  aegis.relays[r.index]=true
  aegis.relay_times=aegis.relay_times or {}
  aegis.relay_times[r.index]=math.floor((g_Time-(aegis.born or g_Time))/1000)
  aegis.phase=r.index+1
  PlaySound(e,0)
  if r.index==1 then
   aegis_message("NORTHSTAR online. Flank through the blast gates to LANTERN.",8)
  elseif r.index==2 then
   aegis_message("LANTERN online. The AEGIS core is ahead. Expect countermeasures and reserves.",8)
  else
   aegis_message("Orbital strike CANCELLED. AEGIS uplink captured -- suit boost live. Kestrel inbound!",10)
  end
 end
end
