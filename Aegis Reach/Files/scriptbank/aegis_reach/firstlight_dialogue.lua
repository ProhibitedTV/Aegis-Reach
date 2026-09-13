require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Stable mission dialogue catalog. Text always works; ElevenLabs WAVs are optional.
local catalog={
 FL01_KES_001={speaker='KESTREL',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.',seconds=4.2},
 FL01_KES_002={speaker='KESTREL',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.',seconds=4.6},
 FL01_KES_003={speaker='KESTREL',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got.",seconds=4.8},
 FL01_KES_004={speaker='KESTREL',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.',seconds=5.4},
 FL01_KES_005={speaker='KESTREL',text='You are down. I will stay high and dark until you call for extraction.',seconds=3.6},
 FL01_KES_006={speaker='KESTREL',text='Camp Twelve. No movement. The evacuation board is still powered.',seconds=3.5},
 FL01_KES_007={speaker='KESTREL',text='Gate Zero-Seven. Warden barricades. Somebody wanted the colony sealed in.',seconds=4.0},
 FL01_KES_008={speaker='KESTREL',text='Northstar is intact. Bring it online and let us hear what Meridian tried to send.',seconds=4.0},
 FL01_MIR_001={speaker='MIRA SEN',text='Seven... Shelter Twelve. We are below the array. Do not let them fire.',seconds=4.8},
 FL01_KES_009={speaker='KESTREL',text='Copy. AEGIS is targeting the shelter. Get to the core.',seconds=3.8},
 FL01_MIR_002={speaker='MIRA SEN',text='It is not a foundation. The black ribs continue below the old waterline. It answers the calibration tone.',seconds=5.5},
 FL01_KES_010={speaker='KESTREL',text='Whatever it is, save the people first. Kill the firing order.',seconds=3.9},
 FL01_KES_011={speaker='KESTREL',text='Strike canceled. West service road back to LZ Zero-Seven. I am coming in.',seconds=4.2},
 FL01_KES_012={speaker='KESTREL',text='Sixty seconds. Keep the pad clear. I need one clean approach.',seconds=4.2},
 FL01_SUIT_001={speaker='SUIT',text='Reinforcement movement on both service roads. Multiple contacts converging.',seconds=3.5},
 FL01_KES_013={speaker='KESTREL',text='Visual on the pad. Final approach. Keep your head down.',seconds=3.8},
 FL01_KES_014={speaker='KESTREL',text='Gear down. Six seconds.',seconds=2.8},
 FL01_KES_015={speaker='KESTREL',text='Kestrel is down. Clear the pad and get aboard.',seconds=3.2},
 FL01_KES_016={speaker='KESTREL',text='Seven, you are on. Strap in.',seconds=2.4},
 FL01_KES_017={speaker='KESTREL',text='Lifting. Shelter Twelve is alive. Mira is still transmitting.',seconds=4.0},
 FL01_M17_001={speaker='M-17 PILOT',text='Landing clearance revoked. Gate Zero-Seven will not take our distress call. Putting her down in the tide channel.',seconds=5.0},
}
local voice_entities={}
local last_played={}

local function entity_name(e)
 if not GetEntityName then return nil end
 local ok,name=pcall(GetEntityName,e)
 return ok and name or nil
end

local function resolve_voice(id)
 if voice_entities[id] and g_Entity and g_Entity[voice_entities[id]] then return voice_entities[id] end
 if not g_Entity then return nil end
 local wanted='FL VO '..id
 for e,_ in pairs(g_Entity) do
  if entity_name(e)==wanted then voice_entities[id]=e;return e end
 end
 return nil
end

local function play_voice(id)
 if not PlayNon3DSound then return end
 local e=resolve_voice(id)
 if e then pcall(PlayNon3DSound,e,0) end
end

function fl_dialogue(id)
 local line=catalog[id]
 if not line then return false end
 if not aegis then aegis={} end
 aegis.dialogue_current={id=id,speaker=line.speaker,text=line.text,until=g_Time+math.floor(line.seconds*1000)}
 if not aegis.cinematic_active and fl_say then
  fl_say(line.speaker..': '..line.text,'',line.seconds)
 end
 if not last_played[id] or g_Time-last_played[id]>500 then
  last_played[id]=g_Time;play_voice(id)
 end
 if fl_log then fl_log('dialogue '..id) end
 return true
end

function fl_dialogue_draw_cinematic()
 if not aegis or not aegis.dialogue_current then return end
 local line=aegis.dialogue_current
 if g_Time>(line.until or 0) then return end
 if Panel then Panel(8,79,92,92) end
 if TextCenterOnXColor then
  TextCenterOnXColor(50,81,1,line.speaker,103,220,230)
  TextCenterOnXColor(50,86,2,line.text,228,225,209)
 end
end

function firstlight_dialogue_init(e)
 Hide(e);CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_dialogue_main(e)
 -- Intentionally empty. This entity only guarantees the global dialogue catalog loads.
end

firstlight_dialogue_init=firstlight_guard('firstlight_dialogue_init',firstlight_dialogue_init)
firstlight_dialogue_main=firstlight_guard('firstlight_dialogue_main',firstlight_dialogue_main)
