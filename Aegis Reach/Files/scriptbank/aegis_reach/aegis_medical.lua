-- DESCRIPTION: Single-use field repair restores armour without replacing shields.
local used={}
function aegis_medical_init(e) used[e]=false end
function aegis_medical_main(e)
 if used[e] or not aegis or not aegis.started or g_PlayerHealth<=0 then return end
 if GetPlayerDistance(e)>160 then return end
 Prompt("E // Field repair - restore 75 armour")
 if g_KeyPressE==1 then
  used[e]=true;aegis.armour=math.min(100,aegis.armour+75)
  SetPlayerHealth(math.floor(aegis.armour+aegis.shield));aegis.last_health=g_PlayerHealth
  aegis_message("Field repair complete. Ammunition is beside the marked supply crates.",5)
 end
end
