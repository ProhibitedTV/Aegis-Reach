-- DESCRIPTION: Sparse environmental-story trigger for authored Vesper props.
-- The world should speak first. These lines react to details the player can already see.
local story={}

function aegis_story_init_name(e,name)
 story[e]={name=name or "",fired=false,near=false}
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
 return nil,0
end

function aegis_story_main(e)
 local s=story[e]
 if not s or s.fired or not aegis or not aegis.started or aegis.extracted then return end
 if GetPlayerDistance(e)>240 then return end
 -- Never interrupt a hot fight for optional environmental narration.
 if aegis.combat_active then return end
 local text,seconds=line_for(s.name)
 if text then
  aegis_message(text,seconds)
  s.fired=true
 end
end
