-- DESCRIPTION: Sparse environmental-story trigger for authored Vesper props.
-- The world should speak first. These lines react to details the player can already see.
-- Story props also fire MAX Visual Logic / IfUsed outputs once, allowing CineGuru,
-- audio, particles, lights, or other authored responses without hard-coded entity IDs.
local story={}

function aegis_story_init_name(e,name)
 story[e]={name=name or "",fired=false,near=false}
 SetActivated(e,0)
end

local function line_for(name)
 if string.find(name,"MIRA SURVEY WRECK",1,true) then
  return "KESTREL: Survey skiff. Mira Sen's unit. This was here before AEGIS became a fortress.",7
 end
 if string.find(name,"TIDE GAUGE 17",1,true) then
  return "KESTREL: That gauge is dry by forty metres. Vesper's shelf has changed since my last rotation.",7
 end
 if string.find(name,"TIDE GAUGE 22",1,true) then
  return "KESTREL: Same mineral line. Whatever drained this basin, it wasn't local weather.",7
 end
 if string.find(name,"MERIDIAN SHELTER 12",1,true) then
  return "KESTREL: Meridian shelter twelve. Field heaters, tide charts... this place was a worksite long before it was a fortress.",7
 end
 if string.find(name,"RESONANCE CUT 03",1,true) then
  return "KESTREL: That black rib is below the old waterline. Survey crews didn't put it there.",7
 end
 return nil,0
end

local function subtle_emissive(e,name,distance)
 -- Old survey hardware has just enough surviving instrumentation to catch the eye.
 if string.find(name,"TIDE GAUGE",1,true) then
  local near=math.max(0,1-math.min(1,distance/700))
  local pulse=(math.sin(g_Time*0.0022)+1)*0.5
  SetEntityEmissiveColor(e,72,190,202)
  SetEntityEmissiveStrength(e,15+near*55+pulse*12)
  return
 end
 if string.find(name,"MERIDIAN SHELTER",1,true) then
  local near=math.max(0,1-math.min(1,distance/900))
  SetEntityEmissiveColor(e,219,151,78)
  SetEntityEmissiveStrength(e,6+near*22)
  return
 end
 if string.find(name,"RESONANCE CUT",1,true) then
  -- The Choir should never look like a magic neon collectible. The signal is a faint,
  -- slow mineral response that becomes noticeable only after the player is already near it.
  local near=math.max(0,1-math.min(1,distance/850))
  local pulse=(math.sin(g_Time*0.00115)+1)*0.5
  SetEntityEmissiveColor(e,70,118,122)
  SetEntityEmissiveStrength(e,2+near*(7+pulse*8))
 end
end

function aegis_story_main(e)
 local s=story[e]
 if not s or not aegis or not aegis.started or aegis.extracted then return end
 local distance=GetPlayerDistance(e)
 subtle_emissive(e,s.name,distance)
 if s.fired or distance>240 then return end
 -- Never interrupt a hot fight for optional environmental narration.
 if aegis.combat_active then return end
 local text,seconds=line_for(s.name)
 if text then
  aegis_message(text,seconds)
  s.fired=true
  SetActivated(e,1)
  PerformLogicConnections(e)
  ActivateIfUsed(e)
 end
end
