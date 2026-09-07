require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Mission 01 physical interactions; objectives have distinct consequences.
local items={}
local records={
 INTEL1={'EVACUATION ROSTER: 42 aboard. M. Sen unaccounted for.','Someone has crossed out the departure time and written: WAIT FOR MIRA.'},
 INTEL2={'SURVEY NOTE: The black ribs continue below the old waterline.','MIRA SEN: It answers the calibration tone. This is not a mineral deposit.'},
 INTEL3={'WARDEN ORDER: Seal Shelter 12. Retask AEGIS. Erase the survey.','KESTREL: They were never defending the relay. They were burying the evidence.'}
}
function firstlight_interact_init_name(e,name)
 items[e]={role=string.match(name,'FL (%w+)'),hold=0,last=0,used=false}
end
function firstlight_interact_main(e)
 if not fl or not fl.started or fl.won or g_PlayerHealth<=0 then return end
 local item=items[e];if not item then return end
 local dt=item.last>0 and math.min(150,math.max(0,g_Time-item.last)) or 0;item.last=g_Time
 if item.used then return end
 local role=item.role;local radius=role=='EXTRACT' and 360 or 210
 if GetPlayerDistance(e)>radius then item.hold=0;return end
 if records[role] then
  Prompt('E // Read field record')
  if g_KeyPressE==1 then
   item.used=true;fl.intel[role]=true;local r=records[role];fl_say(r[1],r[2],13)
   fl.discovery_until=g_Time+12000;fl.discovery_track=role=='INTEL2' and 'discovery_choir' or 'discovery_human'
   fl_log('intel '..role)
  end
  return
 end
 if role=='MED' then
  Prompt('E // Field repair: restore armour')
  if g_KeyPressE==1 and fl.armour<100 then
   item.used=true;fl.armour=100;fl.last_health=math.floor(fl.armour+fl.shield);SetPlayerHealth(fl.last_health)
   fl_say('SUIT: Field repair complete. Armour restored.','Shield regenerates when you break contact.',5);Hide(e);CollisionOff(e)
  end
  return
 end
 local required=({POWER=1,RECORDS=2,CORE=3,EXTRACT=4})[role]
 if fl.stage~=required then Prompt(fl.stage>required and 'SYSTEM RESTORED' or 'Complete the current objective first');return end
 if role=='EXTRACT' then
  if fl.evac_start==0 or fl.evac_elapsed<60000 then Prompt('Defend the landing zone until Kestrel arrives');return end
  if fl_hostiles(0,-2350,1500)>0 then Prompt('Clear nearby Wardens before boarding');return end
 elseif fl_hostiles(g_Entity[e].x,g_Entity[e].z,680)>0 then
  Prompt('Clear the immediate area before operating this terminal');item.hold=0;return
 end
 if g_KeyPressE==1 then item.hold=item.hold+dt else item.hold=0 end
 Prompt('Hold E // '..({POWER='Restore power',RECORDS='Recover manifest',CORE='Cancel firing order',EXTRACT='Board Kestrel'})[role]..' '..math.min(100,math.floor(item.hold/30))..'%')
 if item.hold<3000 then return end
 item.used=true
 PlaySound(e,0)
 if role=='EXTRACT' then
  fl.won=true;fl.completed=g_Time;fl.final_time=math.floor((g_Time-fl.born)/1000);fl.intel_count=0
  for _ in pairs(fl.intel) do fl.intel_count=fl.intel_count+1 end
  FreezeAI();FreezePlayer();fl_log('MISSION_COMPLETE records='..fl.intel_count..' kills='..fl.kills..' seconds='..fl.final_time)
  return
 end
 fl.stage=fl.stage+1
 if SetEntityEmissiveColor then SetEntityEmissiveColor(e,50,210,230) end
 if SetEntityEmissiveStrength then SetEntityEmissiveStrength(e,25) end
 if role=='POWER' then
  fl_say('NORTHSTAR ONLINE. Civilian channel restored.','KESTREL: That distress call is coming from Operations. Go east.',10)
 elseif role=='RECORDS' then
  fl_say('MIRA SEN: We are under Shelter 12. Do not let them fire.','KESTREL: AEGIS is aimed at the shelter. Get to the core. Now.',12)
  fl.discovery_until=g_Time+12000;fl.discovery_track='discovery_choir'
 else
  fl_say('FIRING ORDER CANCELLED. Civilian shelter removed from target list.','KESTREL: Take the west service yard back to Gate 7. I am coming in.',12)
  fl.last_hit=g_Time-8000
 end
 if PlayNon3DSound then PlayNon3DSound(e,1) end
 fl_log('objective '..role..' stage='..fl.stage)
end

firstlight_interact_init_name=firstlight_guard('firstlight_interact_init_name',firstlight_interact_init_name)

firstlight_interact_main=firstlight_guard('firstlight_interact_main',firstlight_interact_main)
