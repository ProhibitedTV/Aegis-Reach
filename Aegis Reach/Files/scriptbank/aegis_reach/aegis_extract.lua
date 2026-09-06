-- DESCRIPTION: Extraction requires the core override and a clear landing zone.
function aegis_extract_init(e) end
function aegis_extract_main(e)
 if not aegis or not aegis.started or aegis.extracted or g_PlayerHealth<=0 then return end
 if GetPlayerDistance(e)>330 then aegis.hold=0;aegis.hold_last=g_Time;return end
 if aegis.phase<4 then Prompt("KESTREL LZ // Restore all three relays before extraction");return end
 local nearby=0
 for id,_ in pairs(aegis.enemies) do
  local n=g_Entity[id]
  if n and n.health>0 and math.sqrt((n.x-g_Entity[e].x)^2+(n.z-g_Entity[e].z)^2)<1350 then nearby=nearby+1 end
 end
 if nearby>0 then
  Prompt("Clear the landing zone // "..nearby.." hostiles nearby")
  aegis.hold=0;aegis.hold_last=g_Time;return
 end
 local dt=math.min(100,math.max(0,g_Time-(aegis.hold_last or g_Time)))
 aegis.hold_last=g_Time
 if g_KeyPressE==1 then aegis.hold=aegis.hold+dt else aegis.hold=0 end
 Prompt("Hold E to board Kestrel // "..math.floor(aegis.hold/30).."%")
 if aegis.hold>=3000 then
  aegis.extracted=true;aegis.completed_at=g_Time
  aegis.final_time=math.floor((g_Time-aegis.born)/1000)
  aegis.score=3000+aegis.kills*150+math.max(0,900-aegis.final_time)*5
  FreezePlayer();FreezeAI()
 end
end
