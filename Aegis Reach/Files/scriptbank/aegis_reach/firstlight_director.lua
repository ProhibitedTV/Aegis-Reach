require 'scriptbank\\aegis_reach\\firstlight_audit'
require 'scriptbank\\aegis_reach\\firstlight_hud'
-- Mission 01: FIRST LIGHT. Native MAX mission state and presentation.
-- Production pass: encounter pressure, tactical radio arbitration and readable combat state.
fl=fl or {}
local native_qa=os.getenv('AEGIS_FIRSTLIGHT_QA')=='1'
if native_qa then require 'scriptbank\\aegis_reach\\firstlight_qa' end

local points={{-1250,-850},{1300,1050},{0,3200},{0,-2350}}
local objectives={'Restore Northstar power','Recover the evacuation manifest','Cancel the AEGIS firing order','Hold for Kestrel extraction'}
local zones={
 {'MERIDIAN SHELF',-12000,-7700,'OLD BRINE SHELF',nil,nil},
 {'SURVEY CAMP 12',-7700,-6300,'MERIDIAN FIELD OUTPOST','KESTREL: Camp 12. No movement. Survey systems are still drawing power.','The road continues through the dry channel.'},
 {'DRY TIDE CHANNEL',-6300,-3500,'MERIDIAN SERVICE CORRIDOR',nil,nil},
 {'GATE 07',-3500,-1600,'AEGIS PERIMETER','KESTREL: Gate 07. Warden barricades ahead.','Northstar is beyond the threshold.'},
 {'NORTHSTAR POWER',-1600,400,'GRID / TURBINE SERVICE','KESTREL: Northstar is dark. Bring the grid back before we chase the signal.','Service controls are inside the power yard.'},
 {'OPERATIONS',400,1900,'MERIDIAN PERSONNEL / RECORDS','KESTREL: Operations. The distress packet originated here.','Find the evacuation manifest.'},
 {'AEGIS EXCAVATION',1900,6000,'DEFENSE ARRAY / SUBSURFACE WORKS','KESTREL: AEGIS core ahead. The interference is getting worse.','Whatever they uncovered is beneath this site.'}
}

local function clamp(v,a,b)
 if v<a then return a end
 if v>b then return b end
 return v
end

local function meter(value,width)
 local n=math.floor(clamp(value,0,100)*width/100+0.5)
 return '['..string.rep('|',n)..string.rep('.',width-n)..']'
end

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

local function show_message(a,b,seconds)
 fl.message={a,b or ''};fl.message_until=g_Time+(seconds or 8)*1000
end

-- Story/mission dialogue has priority and intentionally discards stale tactical chatter.
function fl_say(a,b,seconds)
 fl.radio_queue={}
 show_message(a,b,seconds)
end

-- Tactical barks wait behind story dialogue instead of replacing it mid-sentence.
function fl_bark(a,b,seconds)
 if not fl or not fl.started then return end
 if g_Time<(fl.message_until or 0) then
  if #fl.radio_queue<3 then table.insert(fl.radio_queue,{a,b or '',seconds or 5}) end
 else
  show_message(a,b,seconds)
 end
end

local function update_radio_queue()
 if g_Time<(fl.message_until or 0) or #fl.radio_queue==0 then return end
 local next_message=table.remove(fl.radio_queue,1)
 show_message(next_message[1],next_message[2],next_message[3])
end

function fl_hostiles(x,z,radius)
 local n=0
 for id,state in pairs(fl.enemies or {}) do
  local actor=g_Entity[id]
  if state.active and actor and actor.health>0 and (actor.x-x)^2+(actor.z-z)^2<radius*radius then n=n+1 end
 end
 return n
end

local function current_zone()
 for _,v in ipairs(zones) do
  if g_PlayerPosZ>=v[2] and g_PlayerPosZ<v[3] then return v end
 end
 return zones[1]
end

local function update_zone()
 local v=current_zone()
 if v[1]==fl.zone then return end
 fl.zone=v[1]
 fl.zone_subtitle=v[4] or ''
 fl.zone_until=g_Time+2800
 fl_log('zone '..fl.zone)
 if not fl.zone_seen[v[1]] then
  fl.zone_seen[v[1]]=true
  if v[5] and g_Time-fl.born>5000 then fl_say(v[5],v[6],7) end
 end
end

local function update_pressure(contacts,damage,dt)
 local since_hit=math.max(0,g_Time-fl.last_hit)
 local recent_damage=since_hit<4200 and (1-since_hit/4200) or 0
 local shield_stress=(100-fl.shield)*0.12
 local armour_stress=(100-fl.armour)*0.18
 local contact_stress=math.min(52,contacts*14)
 local extraction_stress=0
 if fl.evac_start>0 then extraction_stress=8+18*clamp(fl.evac_elapsed/60000,0,1) end
 local target=clamp(contact_stress+shield_stress+armour_stress+recent_damage*24+extraction_stress,0,100)
 local response=target>fl.pressure and 850 or 1900
 local blend=clamp(dt/response,0,1)
 fl.pressure=fl.pressure+(target-fl.pressure)*blend
 if fl.pressure>fl.pressure_peak then fl.pressure_peak=fl.pressure end
 if fl.pressure>=72 then fl.pressure_band='CRITICAL'
 elseif fl.pressure>=42 then fl.pressure_band='HIGH'
 elseif fl.pressure>=16 then fl.pressure_band='ELEVATED'
 else fl.pressure_band='LOW' end
 aegis.combat_intensity=fl.pressure
end

local function update_combat_budget()
 local budget=fl.stage==4 and 5 or 4
 if fl.shield<=0 or fl.armour<40 then budget=budget-1 end
 if fl.stage==3 and fl_distance(0,3200)<1500 then budget=math.min(budget,4) end
 fl.combat_budget=math.max(3,budget)
end

local function update_music_state(contacts)
 local interference=fl.stage==3 and fl_distance(0,3200)<1500
 if fl.discovery_until and g_Time<fl.discovery_until then
  aegis.music_state=fl.discovery_track
 elseif contacts>0 then
  if interference then aegis.music_state='combat_interference'
  elseif fl.pressure>=72 or (fl.stage==4 and fl.evac_start>0) then aegis.music_state='combat_overcharge'
  else aegis.music_state='combat' end
 elseif fl.stage==4 then
  aegis.music_state='resolution_aegis'
 elseif g_PlayerPosZ<-3500 then
  aegis.music_state='exploration_vesper'
 elseif g_PlayerPosZ>2100 then
  aegis.music_state='tension_aegis'
 else
  aegis.music_state='exploration_fortress'
 end
end

local function update_extraction_barks()
 if fl.evac_start==0 then return end
 local elapsed=fl.evac_elapsed
 if elapsed>=3000 and not fl.evac_barks[1] then
  fl.evac_barks[1]=true
  fl_bark('KESTREL: Warden reserve signatures just lit up.','Hold the center. I need the pad intact.',6)
 elseif elapsed>=20000 and not fl.evac_barks[2] then
  fl.evac_barks[2]=true
  fl_bark('SUIT: Reinforcement movement on both service roads.','Multiple contacts converging on the landing zone.',5)
 elseif elapsed>=38000 and not fl.evac_barks[3] then
  fl.evac_barks[3]=true
  fl_bark('KESTREL: Final approach.','They are throwing everything they have at the pad.',6)
 elseif elapsed>=52000 and not fl.evac_barks[4] then
  fl.evac_barks[4]=true
  fl_bark('KESTREL: Eight seconds. Stay alive.','Landing gear is down.',5)
 end
end

function firstlight_director_init(e)
 fl_hud_reset()
 fl={
  started=false,stage=1,last_stage=1,enemies={},intel={},shield=100,armour=100,
  last_health=200,last_hit=0,next_regen=0,message={},message_until=0,radio_queue={},
  evac_start=0,evac_elapsed=0,evac_last=0,evac_barks={},won=false,zone='',zone_subtitle='',
  zone_until=0,zone_seen={},objective_pulse_until=0,in_contact=false,dead=0,clock=0,
  pressure=0,pressure_peak=0,pressure_band='LOW',combat_budget=4,combat_since=0,
  last_clear_bark=-20000,shield_break_announced=false,armour_warned=false,last_director_tick=0
 }
 aegis={started=false,music_state='exploration_vesper',combat_intensity=0}
 Hide(e);CollisionOff(e)
 fl_log('FIRST_LIGHT init director='..e)
end

function firstlight_director_main(e)
 if not fl.started then
  fl.started=true;fl.born=g_Time;fl.last_hit=g_Time;fl.last_health=200;fl.last_director_tick=g_Time
  SetPlayerHealth(200);aegis.started=true
  fl_say('KESTREL: The colony has gone silent. Northstar can tell us why.','Follow the old survey road. I will keep a channel open.',11)
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
  TextCenterOnXColor(50,59,1,'PEAK THREAT '..fl.final_pressure_band,239,189,113)
  TextCenterOnX(50,66,2,'Press E to debrief')
  if g_Time-fl.completed>2500 and g_KeyPressE==1 then WinGame() end
  return
 end

 local dt=math.min(200,math.max(1,g_Time-(fl.last_director_tick or g_Time)));fl.last_director_tick=g_Time
 local old_shield=fl.shield;local old_armour=fl.armour
 local damage=math.max(0,fl.last_health-g_PlayerHealth)
 if damage>0 then
  fl.last_hit=g_Time
  local absorbed=math.min(fl.shield,damage)
  fl.shield=fl.shield-absorbed
  fl.armour=math.max(0,fl.armour-damage+absorbed)
  if old_shield>0 and fl.shield<=0 and not fl.shield_break_announced then
   fl.shield_break_announced=true
   fl_bark('SUIT: SHIELD COLLAPSE.','Break line of fire. Armour is exposed.',5)
  end
  if old_armour>=40 and fl.armour<40 and not fl.armour_warned then
   fl.armour_warned=true
   fl_bark('SUIT: ARMOUR INTEGRITY CRITICAL.','Field repair recommended.',5)
  end
 end
 local expected=g_PlayerHealth
 local delay=fl.stage==4 and 3600 or 5500
 if fl.stage==3 and fl_distance(0,3200)<1400 then delay=7600 end
 if g_Time-fl.last_hit>delay and g_Time>=fl.next_regen and fl.shield<100 then
  fl.shield=math.min(100,fl.shield+(fl.stage==4 and 3 or 2))
  fl.next_regen=g_Time+100
  expected=math.floor(fl.armour+fl.shield)
  SetPlayerHealth(expected)
 end
 if fl.shield>=80 then fl.shield_break_announced=false end
 if fl.armour>=55 then fl.armour_warned=false end
 fl.last_health=expected

 fl.kills=0
 for id,state in pairs(fl.enemies) do
  if state.active and g_Entity[id] and g_Entity[id].health<=0 then fl.kills=fl.kills+1 end
 end
 local contacts=fl_hostiles(g_PlayerPosX,g_PlayerPosZ,1700)
 update_pressure(contacts,damage,dt)
 update_combat_budget()
 local in_contact=contacts>0
 if in_contact~=fl.in_contact then
  fl.in_contact=in_contact
  if in_contact then
   fl.combat_since=g_Time
   fl_bark('SUIT: HOSTILE CONTACT.','Warden signatures inside weapons range.',4)
   fl_log('combat_enter contacts='..contacts..' budget='..fl.combat_budget)
  else
   local duration=g_Time-(fl.combat_since or g_Time)
   if duration>3500 and g_Time-fl.last_clear_bark>12000 then
    fl.last_clear_bark=g_Time
    fl_bark('SUIT: LOCAL THREAT SUPPRESSED.','Shield recharge window open.',4)
   end
   fl_log('combat_clear pressure='..math.floor(fl.pressure))
  end
 end
 update_music_state(contacts)
 update_zone()

 if fl.stage~=fl.last_stage then
  fl.last_stage=fl.stage
  fl.objective_pulse_until=g_Time+3500
  fl_log('objective_presented stage='..fl.stage..' text='..objectives[fl.stage])
 end

 if fl.stage==4 and fl.evac_start==0 and fl_distance(0,-2350)<700 then
  fl.evac_start=g_Time;fl.evac_last=g_Time
  fl_say('KESTREL: Sixty seconds to landing. Hold this ground.','The Wardens are coming down the service roads.',8)
  fl_log('evacuation_started')
 end
 if fl.evac_start>0 then
  local evac_dt=math.min(150,math.max(0,g_Time-fl.evac_last));fl.evac_last=g_Time
  if fl_distance(0,-2350)<1800 then fl.evac_elapsed=math.min(60000,fl.evac_elapsed+evac_dt) end
  update_extraction_barks()
 end
 update_radio_queue()

 -- Compact mission HUD. Space and landmarks should carry navigation; HUD confirms it.
 local p=points[fl.stage];local dist=fl_distance(p[1],p[2])
 local dx=p[1]-g_PlayerPosX;local dz=p[2]-g_PlayerPosZ
 local bearing=math.deg(math.atan2(dx,dz))
 fl_hud_draw(objectives[fl.stage],dist*.0254,bearing,g_PlayerAngY or 0,fl.shield,fl.armour)

 if contacts>0 then
  local threat_color=fl.pressure_band=='CRITICAL' and 239 or 239
  TextCenterOnXColor(50,17,2,'THREAT '..fl.pressure_band..'  //  '..contacts..' CONTACT'..(contacts==1 and '' or 'S'),threat_color,153,96)
 end
 if fl.stage==3 and dist<1400 then
  TextCenterOnXColor(50,20,2,'AEGIS INTERFERENCE // SHIELD RECHARGE DELAYED',239,153,96)
 end
 if fl.shield<=0 and fl.armour>=40 then
  TextCenterOnXColor(50,84,2,'SHIELD DOWN // BREAK CONTACT',239,189,113)
 elseif fl.armour<40 then
  TextCenterOnXColor(50,84,2,'ARMOUR CRITICAL // FIND COVER',239,97,88)
 end
 if fl.evac_start>0 then
  local remain=math.max(0,math.ceil((60000-fl.evac_elapsed)/1000))
  local progress=math.floor(fl.evac_elapsed/600)
  TextCenterOnXColor(50,76,2,remain>0 and ('KESTREL ETA '..remain..'s  //  HOLD THE LZ  '..meter(progress,12)) or 'KESTREL ON STATION // CLEAR THE PAD AND HOLD E',103,220,230)
 end
 if g_Time<fl.message_until then
  Panel(9,20,91,32)
  TextCenterOnXColor(50,22,2,fl.message[1] or '',228,225,209)
  TextCenterOnXColor(50,27,1,fl.message[2] or '',196,210,218)
 end
 if g_Time<fl.zone_until then
  TextCenterOnXColor(50,59,3,fl.zone,217,230,230)
  if fl.zone_subtitle~='' then TextCenterOnXColor(50,64,1,fl.zone_subtitle,176,195,202) end
 end
 if g_Time<fl.objective_pulse_until then
  TextCenterOnXColor(50,70,2,'NEW OBJECTIVE // '..objectives[fl.stage],239,189,113)
 end
 if g_Time-fl.born<18000 then
  TextCenterOnX(50,91,1,'WASD move / Mouse fire / RMB aim / R reload / Shift sprint / Hold E interact')
 end

 if not fl.audit_next or g_Time>fl.audit_next then
  fl.audit_next=g_Time+12000
  fl_log('tick stage='..fl.stage..' zone='..fl.zone..' music='..tostring(aegis.music_state)..' pressure='..math.floor(fl.pressure)..' budget='..fl.combat_budget..' y='..string.format('%.1f',g_PlayerPosY)..' x='..math.floor(g_PlayerPosX)..' z='..math.floor(g_PlayerPosZ)..' contacts='..contacts..' health='..g_PlayerHealth..' kills='..fl.kills)
 end
end

firstlight_director_init=firstlight_guard('firstlight_director_init',firstlight_director_init)
firstlight_director_main=firstlight_guard('firstlight_director_main',firstlight_director_main)
