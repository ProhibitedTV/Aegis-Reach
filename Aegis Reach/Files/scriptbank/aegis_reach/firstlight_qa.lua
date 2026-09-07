-- Native integration observer; opt in only with AEGIS_FIRSTLIGHT_QA=1.
-- This mode MUST NOT alter the player's position, health, input, objectives, or enemy health.
-- It records real human-play traversal, animation and movement evidence for post-run collection.
local qa={done=false,samples={},stations={}}
local stops={
 {'insertion',0,-9500,1080,900},
 {'survey',-1690,-7040,500,900},
 {'channel',0,-5100,120,900},
 {'gate',0,-2850,650,900},
 {'POWER',-1250,-1020,900,900},
 {'RECORDS',1300,900,1080,900},
 {'CORE',0,3030,1540,900},
 {'return',-2920,800,970,900},
 {'EXTRACT',0,-2510,650,900}
}

local function qdist(ax,az,bx,bz)
 return math.sqrt((ax-bx)^2+(az-bz)^2)
end

function firstlight_qa_tick()
 if qa.done then return end

 -- Observe each authored review station when the human player actually reaches it.
 for _,s in ipairs(stops) do
  if not qa.stations[s[1]] and qdist(g_PlayerPosX,g_PlayerPosZ,s[2],s[3])<s[5] then
   qa.stations[s[1]]=true
   fl_log('QA_STATION '..s[1]..' actual_y='..g_PlayerPosY..' terrain='..GetTerrainHeight(g_PlayerPosX,g_PlayerPosZ)..' expected_floor='..s[4]..' stage='..fl.stage)
   if g_PlayerPosY < s[4]-120 then fl_log('QA_GEOMETRY_WARNING '..s[1]..' player below expected floor') end
  end
 end

 -- Sample only active living actors. Never damage, move, activate or otherwise influence them.
 for e,v in pairs(fl.enemies) do
  if v.active and g_Entity[e] and g_Entity[e].health>0 then
   local actor=g_Entity[e]
   local frame=GetObjectFrame(actor.obj)
   local sample=qa.samples[e]
   if not sample then
    qa.samples[e]={frame=frame,x=actor.x,z=actor.z,when=g_Time}
   elseif g_Time-sample.when>3000 then
    local movement=math.sqrt((actor.x-sample.x)^2+(actor.z-sample.z)^2)
    firstlight_audit('QA_ACTOR e='..e..' frames='..sample.frame..','..frame..' movement='..movement..' health='..actor.health)
    sample.when=g_Time;sample.frame=frame;sample.x=actor.x;sample.z=actor.z
   end
  end
 end

 if fl.won then
  qa.done=true
  local visited=0
  for _name,_seen in pairs(qa.stations) do visited=visited+1 end
  fl_log('QA_NATIVE_COMPLETE stage='..fl.stage..' kills='..fl.kills..' elapsed='..fl.final_time..' stations='..visited..'/'..#stops)
 end
end
