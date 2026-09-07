-- Opt-in native integration probe. Enabled only by AEGIS_FIRSTLIGHT_QA=1.
-- Exercises real entity initialization, terrain/physics, interactions and extraction.
-- It teleports between test stations and removes active enemies; it is not a combat playtest.
local qa={step=1,since=0,done=false}
local stops={{'landing',0,-9500,850,5000},{'survey',-1690,-7040,550,4500},{'channel',0,-5100,500,4500},{'POWER',-1250,-1020,655,6500},{'RECORDS',1300,900,655,6500},{'CORE',0,3030,655,6500},{'EXTRACT',0,-2510,665,76000}}
function firstlight_qa_tick()
 if qa.done then return end
 if fl.won then
  qa.done=true;fl_log('QA_NATIVE_COMPLETE stage='..fl.stage..' kills='..fl.kills..' elapsed='..fl.final_time)
  QuitGame();return
 end
 local s=stops[qa.step]
 if not s then fl_log('QA_NATIVE_FAILURE incomplete objective sequence stage='..fl.stage);qa.done=true;QuitGame();return end
 if qa.since==0 then
  qa.since=g_Time
  SetFreezePosition(s[2],s[4],s[3]);TransportToFreezePositionOnly();SetFreezeAngle(0,0,0)
  fl_log('QA_STATION '..s[1])
 end
 for e,v in pairs(fl.enemies) do if v.active and g_Entity[e] and g_Entity[e].health>0 then SetEntityHealth(e,0) end end
 SetPlayerHealth(200)
 if g_Time-qa.since>1000 then g_KeyPressE=1 else g_KeyPressE=0 end
 if g_Time-qa.since>s[5] then
  fl_log('QA_SAMPLE '..s[1]..' actual_y='..g_PlayerPosY..' actual_x='..g_PlayerPosX..' actual_z='..g_PlayerPosZ..' stage='..fl.stage)
  if g_PlayerPosY< -200 then fl_log('QA_NATIVE_FAILURE fell through terrain');qa.done=true;QuitGame();return end
  qa.step=qa.step+1;qa.since=0
 end
end
