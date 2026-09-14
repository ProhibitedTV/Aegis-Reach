"""Execute dialogue, cinematic scheduling and fauna motion in native Lua 5.2."""
from native_format import ROOT
from python_runtime import ensure_max_lua_runtime
from firstlight_cinematics import TIMELINES,SHOT_PROFILES
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh
from environment_pass import Mesh
import math

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
function GetEntityName(e) return g_Entity[e].name end
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
for beat,events in TIMELINES.items():
 for (ms,a),(nxt,b) in zip(events,events[1:]):
  assert ms+by[a]['seconds']*1000<nxt,(beat,'overlapping dialogue',a,b)
 last_ms,last_id=events[-1]
 assert last_ms+by[last_id]['seconds']*1000<SHOT_PROFILES[beat]['seconds']*1000
g.aegis.cinematic_active=True
for line in LINES:
 g.texts=lua.table();assert g.fl_dialogue(line['id'])
 g.fl_dialogue_draw_cinematic()
 rendered=' '.join(g.texts.values())
 assert line['text'] in rendered,('truncated subtitle',line['id'])
 assert g.fl_dialogue_busy()
 g.g_Time+=line['seconds']*1000+1
 assert not g.fl_dialogue_busy()
g.g_Entity[1]=lua.table_from({'name':'FL VO FL01_KES_001'})
g.g_Entity[2]=lua.table_from({'name':'FL VO FL01_KES_002'})
g.fl_dialogue('FL01_KES_001');g.fl_dialogue('FL01_KES_002')
assert g.calls.stopped==1 and g.calls.voice==2
g.fl_dialogue_cancel();assert g.calls.stopped==2 and not g.fl_dialogue_busy()

# Drive the real coordinator, including an early skip and missing-camera recovery.
lua.execute('''
active_cam=nil;cg={}
function CG_GetActiveCamera() return active_cam end
function CG_GetCamera(e) return cg[e] end
function CG_IsCamera(e) return cg[e]~=nil end
function CG_ActivateCamera(e) if cg[e] then active_cam=e;cg[e].state='rolling';return true end end
''')
lua.execute((scripts/'firstlight_cinematic.lua').read_text())
g.g_Entity[40]=lua.table_from({'name':'FL CG ARRIVAL'})
g.cg[40]=lua.table_from({'state':'ready','data':lua.table()})
g.aegis=lua.table();g.fl.born=g.g_Time-1000
g.firstlight_cinematic_init(41)
for _ in range(4):g.g_Time+=300;g.firstlight_cinematic_main(41)
assert g.aegis.cinematic_active and g.aegis.cinematic_beat=='ARRIVAL'
g.active_cam=None;g.g_Time+=900;g.firstlight_cinematic_main(41)
assert not g.aegis.cinematic_active and not g.aegis.cinematic_request
assert g.aegis.insertion_complete,'skipping arrival launches another forced shot'
# Missing Mira camera still delivers the urgent shelter warning.
g.fl.stage=3;assert g.fl_request_cinematic('MIRA_SIGNAL')
g.g_Time+=300;g.firstlight_cinematic_main(41)
g.g_Time+=7500;g.firstlight_cinematic_main(41)
assert g.aegis.dialogue_current.id=='FL01_MIR_001'

# Extraction waits for the boarding camera before leaving the landed pose.
lua.execute((scripts/'firstlight_kestrel.lua').read_text())
g.g_Entity[50]=lua.table_from({'obj':50,'x':0,'y':638,'z':-2350})
g.firstlight_kestrel_init_name(50,'FL KESTREL EXTRACTION')
g.fl.evac_start=1000;g.fl.evac_elapsed=60000
g.firstlight_kestrel_main(50)
assert g.aegis.kestrel_landed and g.calls[50].y==638
g.aegis.kestrel_depart=True;g.aegis.cinematic_active=False
g.g_Time+=1000;g.firstlight_kestrel_main(50)
assert g.calls[50].y==638,'ship leaves before the boarding camera starts'
g.aegis.cinematic_active=True;g.aegis.cinematic_beat='EXTRACTION'
g.aegis.cinematic_started_at=g.g_Time;g.aegis.cinematic_duration_ms=7750
g.firstlight_kestrel_main(50);g.g_Time+=3000;g.firstlight_kestrel_main(50)
assert g.calls[50].y>638

# Cross a complete move/pause/move cycle on a slope; there must be no reset jump.
lua.execute((scripts/'firstlight_biosphere.lua').read_text())
g.g_Entity[30]=lua.table_from({'obj':30,'x':100,'y':208,'z':100})
g.firstlight_biosphere_init_name(30,'FL BIO SKITTER 01')
positions=[]
for _ in range(150):
 g.g_Time+=90;g.firstlight_biosphere_main(30)
 p=g.calls[30];positions.append((p.x,p.y,p.z))
 assert abs(p.y-g.GetGroundHeight(p.x,p.z))<.5,'skitter floats over slope'
steps=[math.dist(a,b) for a,b in zip(positions,positions[1:])]
assert max(steps)<3,'skitter teleports at a pause boundary'
assert sum(d<.001 for d in steps)>15,'skitter never pauses'

# Native vehicle low point meets the pad. No open cap or degenerate face.
m=kestrel_mesh(Mesh)
assert min(v[1] for v in m.verts)>=0
for face in m.faces:
 a,b,c=[m.verts[i] for i in face]
 u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 assert sum(x*x for x in n)>1e-8
print('PRESENTATION RUNTIME PASS: full readable subtitles, non-overlapping schedules, voice lifecycle and grounded continuous fauna.')
