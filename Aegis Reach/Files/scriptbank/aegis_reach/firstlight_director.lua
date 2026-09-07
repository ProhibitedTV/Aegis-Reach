require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Mission 01: FIRST LIGHT. Native MAX mission state and presentation.
fl=fl or {}
local native_qa=os.getenv('AEGIS_FIRSTLIGHT_QA')=='1'
if native_qa then require 'scriptbank\\aegis_reach\\firstlight_qa' end
local points={{-1250,-850},{1300,1050},{0,3200},{0,-2350}}
local objectives={'Restore Northstar power','Recover the evacuation manifest','Cancel the strike at the AEGIS core','Hold Kestrel landing zone'}
local zones={{'MERIDIAN SHELF',-12000,-7700},{'SURVEY CAMP 12',-7700,-6300},{'DRY TIDE CHANNEL',-6300,-3500},{'GATE 07',-3500,-1600},{'NORTHSTAR POWER',-1600,400},{'OPERATIONS',400,1900},{'AEGIS EXCAVATION',1900,6000}}
function fl_log(message)
 if FIRSTLIGHT_TEST then return end
 pcall(function()
  local root=os.getenv('USERPROFILE')
  local path=root..'/Documents/GameGuruApps/GameGuruMAX/Files/first-light-runtime.log'
  local f=io.open(path,'a');if f then f:write(os.date('%Y-%m-%d %H:%M:%S'),' ',message,'\n');f:close() end
 end)
end
function fl_distance(x,z)
 local dx=g_PlayerPosX-x;local dz=g_PlayerPosZ-z;return math.sqrt(dx*dx+dz*dz)
end
function fl_say(a,b,seconds)
 fl.message={a,b or ''};fl.message_until=g_Time+(seconds or 8)*1000
end
function fl_hostiles(x,z,radius)
 local n=0
 for id,state in pairs(fl.enemies or {}) do
  local e=g_Entity[id]
  if state.active and e and e.health>0 and (e.x-x)^2+(e.z-z)^2<radius*radius then n=n+1 end
 end
 return n
end
function firstlight_director_init(e)
 fl={started=false,stage=1,enemies={},intel={},shield=100,armour=100,last_health=200,last_hit=0,next_regen=0,message={},message_until=0,evac_start=0,evac_elapsed=0,evac_last=0,won=false,zone='',zone_until=0,dead=0,clock=0}
 aegis={started=false,music_state='exploration_vesper'}
 Hide(e);CollisionOff(e)
 fl_log('FIRST_LIGHT init director='..e)
end
function firstlight_director_main(e)
 if not fl.started then
  fl.started=true;fl.born=g_Time;fl.last_hit=g_Time;fl.last_health=200
  SetPlayerHealth(200);aegis.started=true
  fl_say('KESTREL: The colony has gone silent. Northstar can tell us why.','Follow the old survey road. I will keep a channel open.',12)
  if PlayNon3DSound then PlayNon3DSound(e,0) end
  fl_log('mission_started x='..g_PlayerPosX..' y='..g_PlayerPosY..' z='..g_PlayerPosZ)
 end
 if native_qa then firstlight_qa_tick() end
 if g_PlayerHealth<=0 then return end
 if fl.won then
  Panel(15,26,85,73)
  TextCenterOnXColor(50,31,4,'FIRST LIGHT // MISSION COMPLETE',103,220,230)
  TextCenterOnX(50,41,2,'The strike is cancelled. Forty-two evacuees have a way home.')
  TextCenterOnX(50,47,2,'Mira Sen is still transmitting from beneath the relay.')
  TextCenterOnX(50,54,2,'FIELD RECORDS '..fl.intel_count..'/3     TIME '..fl.final_time..'s     ELIMINATIONS '..fl.kills)
  TextCenterOnX(50,65,2,'Press E to debrief')
  if g_Time-fl.completed>2500 and g_KeyPressE==1 then WinGame() end
  return
 end
 local damage=math.max(0,fl.last_health-g_PlayerHealth)
 if damage>0 then
  fl.last_hit=g_Time;local absorbed=math.min(fl.shield,damage);fl.shield=fl.shield-absorbed;fl.armour=math.max(0,fl.armour-damage+absorbed)
 end
 local expected=g_PlayerHealth
 local delay=fl.stage==4 and 3600 or 5500
 if fl.stage==3 and fl_distance(0,3200)<1400 then delay=7600 end
 if g_Time-fl.last_hit>delay and g_Time>=fl.next_regen and fl.shield<100 then
  fl.shield=math.min(100,fl.shield+(fl.stage==4 and 3 or 2));fl.next_regen=g_Time+100
  expected=math.floor(fl.armour+fl.shield);SetPlayerHealth(expected)
 end
 fl.last_health=expected
 fl.kills=0
 for id,state in pairs(fl.enemies) do if state.active and g_Entity[id] and g_Entity[id].health<=0 then fl.kills=fl.kills+1 end end
 local contacts=fl_hostiles(g_PlayerPosX,g_PlayerPosZ,1700)
 if fl.discovery_until and g_Time<fl.discovery_until then aegis.music_state=fl.discovery_track

 elseif fl.stage==4 then aegis.music_state='resolution_aegis'
 elseif g_PlayerPosZ<-3500 then aegis.music_state='exploration_vesper'
 elseif g_PlayerPosZ>2100 then aegis.music_state='tension_aegis'
 else aegis.music_state='exploration_fortress' end
 local zone=fl.zone
 for _,v in ipairs(zones) do if g_PlayerPosZ>=v[2] and g_PlayerPosZ<v[3] then zone=v[1] end end
 if zone~=fl.zone then fl.zone=zone;fl.zone_until=g_Time+4500;fl_log('zone '..zone) end
 if fl.stage==4 and fl.evac_start==0 and fl_distance(0,-2350)<700 then
  fl.evac_start=g_Time;fl.evac_last=g_Time
  fl_say('KESTREL: Sixty seconds to landing. Hold this ground.','The Wardens are coming down the service roads.',8)
  fl_log('evacuation_started')
 end
 if fl.evac_start>0 then
  local dt=math.min(150,math.max(0,g_Time-fl.evac_last));fl.evac_last=g_Time
  if fl_distance(0,-2350)<1800 then fl.evac_elapsed=math.min(60000,fl.evac_elapsed+dt) end
 end
 Panel(1,1,44,17);Panel(74,1,99,13)
 TextColor(3,3,2,'FIRST LIGHT  /  '..fl.zone,103,220,230)
 TextColor(3,7,2,string.format('%02d',fl.stage)..'  '..objectives[fl.stage],230,235,231)
 local p=points[fl.stage];local dist=fl_distance(p[1],p[2])
 local dx=p[1]-g_PlayerPosX;local dz=p[2]-g_PlayerPosZ
 local bearing=math.deg(math.atan2(dx,dz));local delta=(bearing-(g_PlayerAngY or 0)+540)%360-180
 local direction=math.abs(delta)<25 and 'AHEAD' or (math.abs(delta)>145 and 'BEHIND' or (delta>0 and 'RIGHT' or 'LEFT'))
 TextColor(3,12,1,math.floor(dist*.0254)..' m  /  '..direction..'    LOCAL CONTACTS '..contacts,239,189,113)
 TextColor(76,3,2,'SHIELD '..math.floor(fl.shield)..' / 100',103,220,230)
 TextColor(76,8,2,'ARMOUR '..math.floor(fl.armour)..' / 100',232,234,224)
 if fl.stage==3 and dist<1400 then TextCenterOnXColor(50,18,2,'AEGIS INTERFERENCE // SHIELD RECHARGE DELAYED',239,153,96) end
 if fl.evac_start>0 then
  local remain=math.max(0,math.ceil((60000-fl.evac_elapsed)/1000))
  TextCenterOnXColor(50,76,2,remain>0 and ('KESTREL ETA '..remain..'s  /  HOLD THE LANDING ZONE') or 'KESTREL ON STATION // CLEAR THE PAD AND HOLD E',103,220,230)
 end
 if g_Time<fl.message_until then
  Panel(9,20,91,32)
  TextCenterOnXColor(50,22,2,fl.message[1] or '',228,225,209)
  TextCenterOnXColor(50,27,1,fl.message[2] or '',196,210,218)
 end
 if g_Time<fl.zone_until then TextCenterOnXColor(50,62,3,fl.zone,217,230,230) end
 if g_Time-fl.born<30000 then TextCenterOnX(50,91,1,'WASD move / Mouse fire / RMB aim / R reload / Shift sprint / Hold E interact') end
 if not fl.audit_next or g_Time>fl.audit_next then
  fl.audit_next=g_Time+12000
  fl_log('tick stage='..fl.stage..' y='..string.format('%.1f',g_PlayerPosY)..' x='..math.floor(g_PlayerPosX)..' z='..math.floor(g_PlayerPosZ)..' contacts='..contacts..' health='..g_PlayerHealth..' kills='..fl.kills)
 end
end

firstlight_director_init=firstlight_guard('firstlight_director_init',firstlight_director_init)

firstlight_director_main=firstlight_guard('firstlight_director_main',firstlight_director_main)
