"""CineGuru story cameras for FIRST LIGHT.

The opening is a two-shot insertion sequence built around the visible Kestrel.
The opening shot lengths now follow the recorded Kestrel performances rather than
forcing the VO into the original placeholder timing.
"""
import math,json,re
from firstlight_dialogue import LINES

CAMERA_SCRIPT=r'Cine Guru MAX\cg_cinematic_camera.lua'
CONTROLLER_SCRIPT=r'aegis_reach\firstlight_cinematic.lua'
MARKER=r'Aegis Reach\Supply Crate.fpe'

SHOT_PROFILES={
    'ARRIVAL':dict(seconds=18.0,focal_start=58,focal_end=76),
    'ARRIVAL_HANDOFF':dict(seconds=25.0,focal_start=64,focal_end=84),
    'MIRA_SIGNAL':dict(seconds=5.2,focal_start=70,focal_end=84),
    'AEGIS_REVEAL':dict(seconds=6.3,focal_start=58,focal_end=90),
    'EXTRACTION':dict(seconds=6.0,focal_start=62,focal_end=82),
}
SHOT_LINES={
 'ARRIVAL':('FL01_KES_001','FL01_KES_002'),
 'ARRIVAL_HANDOFF':('FL01_KES_003','FL01_KES_004','FL01_KES_005'),
 'MIRA_SIGNAL':('FL01_MIR_001','FL01_KES_009'),
 'AEGIS_REVEAL':('FL01_MIR_002','FL01_KES_010'),
 'EXTRACTION':('FL01_KES_016','FL01_KES_017'),
}
LINE_BY_ID={line['id']:line for line in LINES}
TIMELINES={}
for beat,ids in SHOT_LINES.items():
 elapsed=.35;TIMELINES[beat]=[]
 for line_id in ids:
  TIMELINES[beat].append((round(elapsed*1000),line_id))
  elapsed+=LINE_BY_ID[line_id]['seconds']+.35
 SHOT_PROFILES[beat]['seconds']=round(elapsed+.3,2)

def sync_coordinator(script):
 source=script.read_text()
 profiles=[]
 for beat,p in SHOT_PROFILES.items():
  profiles.append(beat+'={seconds='+str(p['seconds'])+',fade=.35,fls='+str(p['focal_start'])+',fle='+str(p['focal_end'])+'}')
 source,n=re.subn(r'local profiles=\{[^\n]+',lambda _:'local profiles={'+','.join(profiles)+'}',source,count=1)
 assert n==1
 rows=['local function update_story_timeline(beat,elapsed)']
 for index,(beat,events) in enumerate(TIMELINES.items()):
  rows.append((' if' if index==0 else ' elseif')+' beat=='+json.dumps(beat)+' then')
  for ms,line_id in events:
   line=LINE_BY_ID[line_id]
   rows.append('  if elapsed>='+str(ms)+' then mark_line('+json.dumps(line_id)+','+json.dumps(line_id)+','+json.dumps(line['speaker']+': '+line['text'])+',"",'+str(line['seconds'])+') end')
 rows+=[' end',' if fl_dialogue_draw_cinematic then fl_dialogue_draw_cinematic() end','end','local function finish_opening_handoff']
 source,n=re.subn(r'local function update_story_timeline\(beat,elapsed\).*?local function finish_opening_handoff',lambda _:'\n'.join(rows),source,count=1,flags=re.S)
 assert n==1
 script.write_text(source)

SHOTS=(
    # beat, name, camera x/z, height, target x/z, target height
    # Side-on insertion view: Kestrel crosses the frame and settles into the drop point.
    ('ARRIVAL','FL CG ARRIVAL',690,-9640,330,-120,-9140,180),
    # Handoff faces up the dead service corridor while Kestrel climbs out behind/above Seven.
    ('ARRIVAL_HANDOFF','FL CG ARRIVAL HANDOFF',-560,-9270,250,-1980,-7240,105),
    ('MIRA_SIGNAL','FL CG MIRA SIGNAL',820,650,205,1420,1050,85),
    ('AEGIS_REVEAL','FL CG AEGIS REVEAL',-1060,2070,335,0,3200,175),
    # Boarding shot owns the Kestrel lift-off, not the combat approach.
    ('EXTRACTION','FL CG EXTRACTION',-1050,-3070,340,0,-2350,125),
)


def _pose(build,x,z,height,tx,tz,target_height):
    y=build.ground(x,z)+height
    ty=build.ground(tx,tz)+target_height
    dx,dz=tx-x,tz-z
    horizontal=max(0.001,math.hypot(dx,dz))
    yaw=math.degrees(math.atan2(dx,dz))%360
    pitch=-math.degrees(math.atan2(ty-y,horizontal))
    return y,pitch,yaw


def apply(build):
    if hasattr(build,'FILES'):sync_coordinator(build.FILES/'scriptbank/aegis_reach/firstlight_cinematic.lua')
    cameras=[]
    for beat,name,x,z,height,tx,tz,target_height in SHOTS:
        y,pitch,yaw=_pose(build,x,z,height,tx,tz,target_height)
        profile=SHOT_PROFILES[beat]
        build.add(
            MARKER,name,x,z,y=y,ry=yaw,kind='cinematic_camera',script=CAMERA_SCRIPT,
            **{'rx':pitch,'rz':0,'eleprof.physics':0,'eleprof.phyalways':1}
        )
        cameras.append({
            'beat':beat,'name':name,'x':x,'y':round(y,2),'z':z,
            'pitch':round(pitch,2),'yaw':round(yaw,2),
            'seconds':profile['seconds'],'focal_start':profile['focal_start'],
            'focal_end':profile['focal_end'],'always_active':True,
        })
    build.add(
        MARKER,'FIRST LIGHT // CINEMATIC',180,-9500,y=100,kind='controller',
        script=CONTROLLER_SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1}
    )
    return {
        'system':'CineGuru MAX','camera_count':len(cameras),'beats':[c['beat'] for c in cameras],
        'cameras':cameras,
        'opening':{
            'shots':['ARRIVAL','ARRIVAL_HANDOFF'],
            'purpose':'show Kestrel insertion, establish 42 missing colonists, Mira signal, Warden intrusion, then hand control toward Northstar',
            'first_action':'Restore Northstar and recover the evacuation packet',
            'seconds':SHOT_PROFILES['ARRIVAL']['seconds']+SHOT_PROFILES['ARRIVAL_HANDOFF']['seconds'],
        },
        'extraction':'Kestrel approaches visibly during gameplay; EXTRACTION camera is reserved for boarding/liftoff',
        'always_active':True,'registration_retry':True,'fail_open':True,
        'music_owner':'firstlight_score.lua',
    }
