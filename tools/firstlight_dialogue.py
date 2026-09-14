"""Stable FIRST LIGHT dialogue IDs plus optional ElevenLabs audio binding."""
from pathlib import Path
import json
DIALOGUE_SCRIPT=r'aegis_reach\firstlight_dialogue.lua';VOICE_SCRIPT=r'aegis_reach\firstlight_voice_marker.lua';MARKER=r'Aegis Reach\Supply Crate.fpe';AUDIO_REL=Path('aegis_reach/dialogue')
LINES=(
 dict(id='FL01_KES_001',speaker='KESTREL',filename='fl01_kestrel_001.wav',seconds=7.9,direction='controlled insertion briefing; professional, low urgency',text='Vanguard Seven, we are crossing Meridian Shelf. Meridian Control missed two scheduled check-ins.'),
 dict(id='FL01_KES_002',speaker='KESTREL',filename='fl01_kestrel_002.wav',seconds=9.1,direction='human stakes; restrained concern',text='Forty-two colonists were due off-world six hours ago. No beacon, no traffic, no automated distress call.'),
 dict(id='FL01_KES_003',speaker='KESTREL',filename='fl01_kestrel_003.wav',seconds=8.5,direction='recount corrupted evidence; measured',text="Mira Sen forced one burst through Northstar before the relay died: 'array waking.' That is all we got."),
 dict(id='FL01_KES_004',speaker='KESTREL',filename='fl01_kestrel_004.wav',seconds=11.6,direction='mission order; decisive',text='A Warden transponder crossed Gate Zero-Seven nine minutes later. I am putting you down short. Restore Northstar and find our people.'),
 dict(id='FL01_KES_005',speaker='KESTREL',filename='fl01_kestrel_005.wav',seconds=3.6,direction='touchdown handoff; calm confidence',text='You are down. I will stay high and dark until you call for extraction.'),
 dict(id='FL01_KES_006',speaker='KESTREL',filename='fl01_kestrel_006.wav',seconds=3.5,direction='quiet observation at abandoned camp',text='Camp Twelve. No movement. The evacuation board is still powered.'),
 dict(id='FL01_KES_007',speaker='KESTREL',filename='fl01_kestrel_007.wav',seconds=4.0,direction='suspicion sharpening',text='Gate Zero-Seven. Warden barricades. Somebody wanted the colony sealed in.'),
 dict(id='FL01_KES_008',speaker='KESTREL',filename='fl01_kestrel_008.wav',seconds=4.0,direction='objective confirmation; technical',text='Northstar is intact. Bring it online and let us hear what Meridian tried to send.'),
 dict(id='FL01_MIR_001',speaker='MIRA SEN',filename='fl01_mira_001.wav',seconds=4.8,direction='damaged emergency transmission; exhausted but urgent',text='Seven... Shelter Twelve. We are below the array. Do not let them fire.'),
 dict(id='FL01_KES_009',speaker='KESTREL',filename='fl01_kestrel_009.wav',seconds=3.8,direction='immediate tactical realization',text='Copy. AEGIS is targeting the shelter. Get to the core.'),
 dict(id='FL01_MIR_002',speaker='MIRA SEN',filename='fl01_mira_002.wav',seconds=5.5,direction='scientist confronting the impossible; fearful restraint',text='It is not a foundation. The black ribs continue below the old waterline. It answers the calibration tone.'),
 dict(id='FL01_KES_010',speaker='KESTREL',filename='fl01_kestrel_010.wav',seconds=3.9,direction='cuts through the mystery; rescue first',text='Whatever it is, save the people first. Kill the firing order.'),
 dict(id='FL01_KES_011',speaker='KESTREL',filename='fl01_kestrel_011.wav',seconds=4.2,direction='relief turning immediately tactical',text='Strike canceled. West service road back to LZ Zero-Seven. I am coming in.'),
 dict(id='FL01_KES_012',speaker='KESTREL',filename='fl01_kestrel_012.wav',seconds=4.2,direction='holdout start; brisk pilot workload',text='Sixty seconds. Keep the pad clear. I need one clean approach.'),
 dict(id='FL01_SUIT_001',speaker='SUIT',filename='fl01_suit_001.wav',seconds=3.5,direction='neutral synthetic combat warning',text='Reinforcement movement on both service roads. Multiple contacts converging.'),
 dict(id='FL01_KES_013',speaker='KESTREL',filename='fl01_kestrel_013.wav',seconds=3.8,direction='audible engine workload; final approach',text='Visual on the pad. Final approach. Keep your head down.'),
 dict(id='FL01_KES_014',speaker='KESTREL',filename='fl01_kestrel_014.wav',seconds=2.8,direction='compressed landing call',text='Gear down. Six seconds.'),
 dict(id='FL01_KES_015',speaker='KESTREL',filename='fl01_kestrel_015.wav',seconds=3.2,direction='landed under fire; command voice',text='Kestrel is down. Clear the pad and get aboard.'),
 dict(id='FL01_KES_016',speaker='KESTREL',filename='fl01_kestrel_016.wav',seconds=2.4,direction='boarding acknowledgement',text='Seven, you are on. Strap in.'),
 dict(id='FL01_KES_017',speaker='KESTREL',filename='fl01_kestrel_017.wav',seconds=4.0,direction='liftoff; controlled relief with unresolved tension',text='Lifting. Shelter Twelve is alive. Mira is still transmitting.'),
 dict(id='FL01_M17_001',speaker='M-17 PILOT',filename='fl01_m17_pilot_001.wav',seconds=5.0,direction='recorded cockpit distress; clipped, under stress',text='Landing clearance revoked. Gate Zero-Seven will not take our distress call. Putting her down in the tide channel.'),
)
def apply(build):
 audio_root=build.FILES/'audiobank'/AUDIO_REL;audio_root.mkdir(parents=True,exist_ok=True)
 build.add(MARKER,'FIRST LIGHT // DIALOGUE',260,-9500,y=-3000,scale=1,kind='controller',script=DIALOGUE_SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1})
 bound=[]
 for line in LINES:
  wav=audio_root/line['filename']
  if not wav.is_file():continue
  build.add(MARKER,'FL VO '+line['id'],0,-9900,y=-3000,scale=1,kind='dialogue_audio',script=VOICE_SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1,'eleprof.soundset_s':str(AUDIO_REL/line['filename']).replace('/','\\')});bound.append(line['id'])
 (build.DESIGN/'dialogue-manifest.json').write_text(json.dumps({'lines':LINES,'audio_bound':bound},indent=2))
 return {'line_count':len(LINES),'audio_bound_count':len(bound),'audio_bound':bound,'audio_directory':str(AUDIO_REL).replace('/','\\'),'missing_audio':[line['id'] for line in LINES if line['id'] not in bound]}
