-- Native integration probe; opt in only with AEGIS_FIRSTLIGHT_QA=1.
-- Exercises physics and actual stock character animation/navigation before clearing encounters.
-- This is an instrumented test, not a substitute for a human combat/visual review.
local qa={step=1,since=0,done=false,samples={}}
local stops={
 {'insertion',0,-9500,1080,5000},
 {'survey',-1690,-7040,500,6000},
 {'channel',0,-5100,120,26000},
 {'gate',0,-2850,650,14000},
 {'POWER',-1250,-1020,900,16000},
 {'RECORDS',1300,900,1080,16000},
 {'CORE',0,3030,1540,16000},
 {'return',-2920,800,970,14000},
 {'EXTRACT',0,-2510,650,85000}
}
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
  SetFreezePosition(s[2],s[4]+60,s[3]);SetFreezeAngle(0,0,0);TransportToFreezePositionOnly()
  fl_log('QA_STATION '..s[1]..' terrain='..GetTerrainHeight(s[2],s[3])..' expected_floor='..s[4])
 end
 local age=g_Time-qa.since
 for e,v in pairs(fl.enemies) do
  if v.active and g_Entity[e] and g_Entity[e].health>0 then
   local actor=g_Entity[e]
   local frame=GetObjectFrame(actor.obj)
   local sample=qa.samples[e]
   if not sample then qa.samples[e]={frame=frame,x=actor.x,z=actor.z,when=g_Time}
   elseif g_Time-sample.when>3000 then
    firstlight_audit('QA_ACTOR e='..e..' frames='..sample.frame..','..frame..' movement='..math.sqrt((actor.x-sample.x)^2+(actor.z-sample.z)^2))
    sample.when=g_Time;sample.frame=frame
   end
   if age>(s[1]=='channel' and 22000 or 8000) then SetEntityHealth(e,0) end
  end
 end
 SetPlayerHealth(200)
 if age>9500 then g_KeyPressE=1 else g_KeyPressE=0 end
 if age>s[5] then
  fl_log('QA_SAMPLE '..s[1]..' actual_y='..g_PlayerPosY..' actual_x='..g_PlayerPosX..' actual_z='..g_PlayerPosZ..' stage='..fl.stage)
  if g_PlayerPosY< s[4]-100 then fl_log('QA_NATIVE_FAILURE unexpected floor height');qa.done=true;QuitGame();return end
  qa.step=qa.step+1;qa.since=0
 end
end
