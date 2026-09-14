"""Execute FIRST LIGHT dialogue, later-story presentation, vehicle and fauna runtime contracts."""
from native_format import ROOT
from python_runtime import ensure_max_lua_runtime
from firstlight_cinematics import TIMELINES,SHOT_PROFILES,OPENING_SEQUENCE
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh,LANDED_CONTACT_Y
from environment_pass import Mesh
import math,wave

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
package.loaded['scriptbank\\aegis_reach\\firstlight_audit']=true
function firstlight_guard(n,f) return f end
g_Time=1000;g_PlayerHealth=200;g_Entity={};calls={};texts={}
fl={started=true,won=false,born=0,stage=1,zone='',evac_start=0,evac_elapsed=0,message_until=0}
aegis={};dist=500
function fl_say(a,b,t) calls.say=a..' '..b;fl.message_until=g_Time+t*1000 end
function fl_log(s) end
function Hide(e) calls['hidden'..e]=true end
function Show(e) calls['hidden'..e]=false end
function CollisionOff(e) end
function SetEntityAlwaysActive(e,v) end
function GetEntityName(e) return g_Entity[e] and g_Entity[e].name or '' end
function PlayNon3DSound(e,s) calls.voice=e end
function StopSound(e,s) calls.stopped=e end
function Panel(...) end
function TextCenterOnXColor(x,y,size,text,...) texts[#texts+1]=text end
function GetPlayerDistance(e) return dist end
function PositionObject(obj,x,y,z) calls[obj]={x=x,y=y,z=z} end
function RotateObject(...) end
function GetGroundHeight(x,z) return 200+.15*x-.07*z end
''')
g=lua.globals();scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
lua.execute((scripts/'firstlight_dialogue.lua').read_text())
by={line['id']:line for line in LINES}
for line in LINES[:4]:
 with wave.open(str(ROOT/'Aegis Reach/Files/audiobank/aegis_reach/dialogue'/line['filename'])) as wav:
  duration=wav.getnframes()/wav.getframerate()
  assert (wav.getnchannels(),wav.getsampwidth(),wav.getframerate())==(1,2,44100)
  assert duration<line['seconds']<duration+.16,'caption timing does not follow PCM duration'

# Later CineGuru beats still own complete dialogue schedules. Opening VO is intentionally
# longer than an individual editorial source because the hard-replacement native opener
# carries voice across cuts.
for beat,events in TIMELINES.items():
 if not events:continue
 for (ms,a),(nxt,b) in zip(events,events[1:]):assert ms+by[a]['seconds']*1000<nxt,(beat,'overlapping dialogue',a,b)
 if beat not in OPENING_SEQUENCE:
  last_ms,last_id=events[-1];assert last_ms+by[last_id]['seconds']*1000<SHOT_PROFILES[beat]['seconds']*1000
assert min(SHOT_PROFILES[b]['seconds'] for b in OPENING_SEQUENCE)<by['FL01_KES_001']['seconds']

g.aegis.cinematic_active=True
for line in LINES:
 g.texts=lua.table();assert g.fl_dialogue(line['id']);g.fl_dialogue_draw_cinematic();rendered=' '.join(g.texts.values())
 assert line['text'] in rendered,('truncated subtitle',line['id']);assert g.fl_dialogue_busy();g.g_Time+=line['seconds']*1000+1;assert not g.fl_dialogue_busy()
g.g_Entity[1]=lua.table_from({'name':'FL VO FL01_KES_001'});g.g_Entity[2]=lua.table_from({'name':'FL VO FL01_KES_002'})
g.fl_dialogue('FL01_KES_001');g.fl_dialogue('FL01_KES_002');assert g.calls.stopped==1 and g.calls.voice==2
g.fl_dialogue_cancel();assert g.calls.stopped==2 and not g.fl_dialogue_busy()

# The shared CineGuru coordinator remains responsible only for post-insertion story beats.
lua.execute('''
active_cam=nil;cg={}
function CG_GetActiveCamera() return active_cam end
function CG_GetCamera(e) return cg[e] end
function CG_IsCamera(e) return cg[e]~=nil end
function CG_ActivateCamera(e) if cg[e] then active_cam=e;cg[e].state='rolling';return true end end
''')
lua.execute((scripts/'firstlight_cinematic.lua').read_text())
g.aegis=lua.table_from({'insertion_complete':True});g.fl.born=g.g_Time-1000;g.firstlight_cinematic_init(41)
# Missing Mira camera must still fail open and deliver the shelter warning.
g.fl.stage=3;g.fl.in_contact=False;g.dist=500
assert g.fl_request_cinematic('MIRA_SIGNAL');g.g_Time+=300;g.firstlight_cinematic_main(41);g.g_Time+=7500;g.firstlight_cinematic_main(41)
assert g.aegis.dialogue_current.id=='FL01_MIR_001'

# Extraction waits for the boarding camera before leaving the landed pose.
lua.execute((scripts/'firstlight_kestrel.lua').read_text())
g.g_Entity[50]=lua.table_from({'obj':50,'x':0,'y':638,'z':-2350});g.firstlight_kestrel_init_name(50,'FL KESTREL EXTRACTION')
g.fl.evac_start=1000;g.fl.evac_elapsed=60000;g.firstlight_kestrel_main(50)
assert g.aegis.kestrel_landed and g.calls[50].y==638
g.aegis.kestrel_depart=True;g.aegis.cinematic_active=False;g.g_Time+=1000;g.firstlight_kestrel_main(50)
assert g.calls[50].y==638,'ship leaves before the boarding camera starts'
g.aegis.cinematic_active=True;g.aegis.cinematic_beat='EXTRACTION';g.aegis.cinematic_started_at=g.g_Time;g.aegis.cinematic_duration_ms=7750
g.firstlight_kestrel_main(50);g.g_Time+=3000;g.firstlight_kestrel_main(50);assert g.calls[50].y>638

# Cross a complete move/pause/move cycle on a slope; there must be no reset jump.
lua.execute((scripts/'firstlight_biosphere.lua').read_text())
g.g_Entity[30]=lua.table_from({'obj':30,'x':100,'y':208,'z':100});g.firstlight_biosphere_init_name(30,'FL BIO SKITTER 01')
positions=[]
for _ in range(150):
 g.g_Time+=90;g.firstlight_biosphere_main(30);p=g.calls[30];positions.append((p.x,p.y,p.z));assert abs(p.y-g.GetGroundHeight(p.x,p.z))<.5,'skitter floats over slope'
steps=[math.dist(a,b) for a,b in zip(positions,positions[1:])]
assert max(steps)<3,'skitter teleports at a pause boundary';assert sum(d<.001 for d in steps)>15,'skitter never pauses'

# Boarding aperture must reveal the cargo bulkhead, not the closed tail/belly.
def rear_sightline(mesh,x=0,y=86):
 hits=[]
 for face in mesh.faces:
  a,b,c=[mesh.verts[i] for i in face]
  det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(det)<1e-8:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/det
  v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/det
  if u>=0 and v>=0 and u+v<=1:hits.append(u*a[2]+v*b[2]+(1-u-v)*c[2])
 return max(hits)
assert 270<rear_sightline(kestrel_mesh(Mesh,'landed'))<290
assert rear_sightline(kestrel_mesh(Mesh,'flight'))>=398
for state in ('flare','landed'):assert abs(min(v[1] for v in kestrel_mesh(Mesh,state).verts)-LANDED_CONTACT_Y)<1e-5
landed=kestrel_mesh(Mesh,'landed')
ramp_faces=[f for f in landed.faces if max(landed.verts[i][2] for i in f)>520 and all(397<=landed.verts[i][2]<=527 and 7<=landed.verts[i][1]<=43 and 7/8<landed.uv[i][0]<1 for i in f)]
assert ramp_faces and all(landed.norm[f[0]][1]>0 for f in ramp_faces),'ramp walking face is culled from above'

m=kestrel_mesh(Mesh);assert min(v[1] for v in m.verts)>=0
for face in m.faces:
 a,b,c=[m.verts[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert sum(x*x for x in n)>1e-8
print('PRESENTATION RUNTIME PASS: hard-replacement onboard insertion is tested separately; later CineGuru fail-open, voice lifecycle, extraction choreography and grounded fauna remain verified.')
