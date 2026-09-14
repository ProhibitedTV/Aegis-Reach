require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Stable mission dialogue catalog. Text always works; ElevenLabs WAVs are optional.
local catalog={
 FL01_KES_001={speaker="KESTREL",text="Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.",seconds=7.987},
 FL01_KES_002={speaker="KESTREL",text="Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.",seconds=9.189},
 FL01_KES_003={speaker="KESTREL",text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=8.64},
 FL01_KES_004={speaker="KESTREL",text="A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.",seconds=11.67},
 FL01_KES_005={speaker="KESTREL",text="You are down. I will stay high and dark until you call for extraction.",seconds=3.6},
 FL01_KES_006={speaker="KESTREL",text="Camp Twelve. No movement. The evacuation board is still powered.",seconds=3.5},
 FL01_KES_007={speaker="KESTREL",text="Gate Zero-Seven. Warden barricades. Somebody wanted the colony sealed in.",seconds=4.0},
 FL01_KES_008={speaker="KESTREL",text="Northstar is intact. Bring it online and let us hear what Meridian tried to send.",seconds=4.0},
 FL01_MIR_001={speaker="MIRA SEN",text="Seven... Shelter Twelve. We are below the array. Do not let them fire.",seconds=4.8},
 FL01_KES_009={speaker="KESTREL",text="Copy. AEGIS is targeting the shelter. Get to the core.",seconds=3.8},
 FL01_MIR_002={speaker="MIRA SEN",text="It is not a foundation. The black ribs continue below the old waterline. It answers the calibration tone.",seconds=5.5},
 FL01_KES_010={speaker="KESTREL",text="Whatever it is, save the people first. Kill the firing order.",seconds=3.9},
 FL01_KES_011={speaker="KESTREL",text="Strike canceled. West service road back to LZ Zero-Seven. I am coming in.",seconds=4.2},
 FL01_KES_012={speaker="KESTREL",text="Sixty seconds. Keep the pad clear. I need one clean approach.",seconds=4.2},
 FL01_SUIT_001={speaker="SUIT",text="Reinforcement movement on both service roads. Multiple contacts converging.",seconds=3.5},
 FL01_KES_013={speaker="KESTREL",text="Visual on the pad. Final approach. Keep your head down.",seconds=3.8},
 FL01_KES_014={speaker="KESTREL",text="Gear down. Six seconds.",seconds=2.8},
 FL01_KES_015={speaker="KESTREL",text="Kestrel is down. Clear the pad and get aboard.",seconds=3.2},
 FL01_KES_016={speaker="KESTREL",text="Seven, you are on. Strap in.",seconds=2.4},
 FL01_KES_017={speaker="KESTREL",text="Lifting. Shelter Twelve is alive. Mira is still transmitting.",seconds=4.0},
 FL01_M17_001={speaker="M-17 PILOT",text="Landing clearance revoked. Gate Zero-Seven will not take our distress call. Putting her down in the tide channel.",seconds=6.0},
}
local voice_entities={};local last_played={};local active_voice=nil;local runtime={zone='',evac_started=false,evac={}}
local function split_line(text,limit)
 if not text or #text<=limit then return text or '','' end
 local cut=limit
 while cut>1 and string.sub(text,cut,cut)~=' ' do cut=cut-1 end
 if cut<=1 then cut=limit end
 local a=string.sub(text,1,cut-1)
 local b=string.sub(text,cut+1)
 return a,b
end
local function entity_name(e)if not GetEntityName then return nil end;local ok,name=pcall(GetEntityName,e);return ok and name or nil end
local function resolve_voice(id)
 if voice_entities[id] and g_Entity and g_Entity[voice_entities[id]] then return voice_entities[id] end
 if not g_Entity then return nil end;local wanted='FL VO '..id
 for e,_ in pairs(g_Entity) do if entity_name(e)==wanted then voice_entities[id]=e;return e end end;return nil
end
local function play_voice(id)
 if active_voice and StopSound then StopSound(active_voice,0) end
 active_voice=nil
 if not PlayNon3DSound then return end
 local e=resolve_voice(id);if e then pcall(PlayNon3DSound,e,0);active_voice=e end
end
function fl_dialogue_busy()
 return aegis and aegis.dialogue_current and g_Time<(aegis.dialogue_current.expires_at or 0)
end
function fl_dialogue_cancel()
 if active_voice and StopSound then StopSound(active_voice,0) end;active_voice=nil
 if aegis then aegis.dialogue_current=nil end
end
function fl_dialogue(id)
 local line=catalog[id];if not line then return false end;if not aegis then aegis={} end
 aegis.dialogue_current={id=id,speaker=line.speaker,text=line.text,expires_at=g_Time+math.floor(line.seconds*1000)}
 if not aegis.cinematic_active and fl_say then local a,b=split_line(line.text,68);fl_say(line.speaker..': '..a,b,line.seconds) end
 if not last_played[id] or g_Time-last_played[id]>500 then last_played[id]=g_Time;play_voice(id) end
 if fl_log then fl_log('dialogue '..id) end;return true
end
function fl_dialogue_draw_cinematic()
 if not aegis or not aegis.dialogue_current then return end;local line=aegis.dialogue_current;if g_Time>(line.expires_at or 0) then return end
 local rows={};local rest=line.text
 while rest~='' do local row,next_part=split_line(rest,78);rows[#rows+1]=row;rest=next_part end
 local top=89-#rows*4
 if Panel then Panel(8,top-7,92,95) end
 if TextCenterOnXColor then
  TextCenterOnXColor(50,top-5,1,line.speaker,103,220,230)
  for i,row in ipairs(rows) do TextCenterOnXColor(50,top+(i-1)*4,2,row,228,225,209) end
  TextCenterOnXColor(50,96,1,'SPACE // SKIP',144,165,178)
 end
end
local function mission_radio_tick()
 if not fl or not fl.started or fl.won or (aegis and (aegis.cinematic_active or aegis.cinematic_request)) then return end
 -- Zone calls wait for a full sentence, including a field record or mission update.
 if fl_dialogue_busy() or g_Time<(fl.message_until or 0) then return end
 if fl.zone~=runtime.zone then
  runtime.zone=fl.zone
  if fl.zone=='SURVEY CAMP 12' then fl_dialogue('FL01_KES_006');return
  elseif fl.zone=='GATE 07' then fl_dialogue('FL01_KES_007');return
  elseif fl.zone=='NORTHSTAR POWER' then fl_dialogue('FL01_KES_008');return end
 end
 if fl.evac_start and fl.evac_start>0 then
  if not runtime.evac_started then runtime.evac_started=true;fl_dialogue('FL01_KES_012');return end
  local t=fl.evac_elapsed or 0
  if t>=20000 and not runtime.evac[1] then runtime.evac[1]=true;fl_dialogue('FL01_SUIT_001');return end
  if t>=38000 and not runtime.evac[2] then runtime.evac[2]=true;fl_dialogue('FL01_KES_013');return end
  if t>=54000 and not runtime.evac[3] then runtime.evac[3]=true;if t<60000 then fl_dialogue('FL01_KES_014');return end end
  if t>=60000 and not runtime.evac[4] and aegis and aegis.kestrel_landed then runtime.evac[4]=true;fl_dialogue('FL01_KES_015') end
 end
end
function firstlight_dialogue_init(e)runtime={zone='',evac_started=false,evac={}};Hide(e);CollisionOff(e);if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end end
function firstlight_dialogue_main(e)mission_radio_tick() end
firstlight_dialogue_init=firstlight_guard('firstlight_dialogue_init',firstlight_dialogue_init)
firstlight_dialogue_main=firstlight_guard('firstlight_dialogue_main',firstlight_dialogue_main)
