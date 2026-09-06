-- DESCRIPTION: Iron Warden infantry using MAX's standard soldier combat behavior.
require "scriptbank\\people\\character_attack"
local enemy={}
function aegis_enemy_init_name(e,name)
 local reserve=tonumber(string.match(name,"RESERVE (%d)"))
 enemy[e]={reserve=reserve,registered=false,active=not reserve}
 character_attack_init_file(e,"people\\character_attack")
 character_attack_properties(e,0,1,350,0,1,3,0,1,15000,1,1000,0,0)
 if reserve then Hide(e);CollisionOff(e) end
end
function aegis_enemy_main(e)
 local w=enemy[e];if not w or not aegis or not aegis.started then return end
 if not w.registered then
  w.registered=true
  if w.active then aegis.enemies[e]=true else aegis.reserves[e]=true end
 end
 if not w.active then
  local threshold=w.reserve<=2 and 3 or 4
  if aegis.phase<threshold then return end
  w.active=true;Show(e);CollisionOn(e);aegis.enemies[e]=true
 end
 if not aegis.extracted then character_attack_main(e) end
end
