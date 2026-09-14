"""Regression checks for FIRST LIGHT story delivery and Broadwing Kestrel choreography."""
from pathlib import Path
from native_format import ROOT
from environment_pass import Mesh
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh,STATES,LENGTH_IN,SPAN_IN,LANDED_CONTACT_Y
from firstlight_cinematics import SHOT_PROFILES,OPENING_SEQUENCE
from python_runtime import ensure_max_lua_runtime

ids=[x['id'] for x in LINES];files=[x['filename'] for x in LINES]
assert len(ids)==len(set(ids)) and len(files)==len(set(files))
for required in ('FL01_KES_001','FL01_KES_004','FL01_MIR_001','FL01_MIR_002','FL01_KES_012','FL01_KES_015','FL01_KES_016','FL01_KES_017','FL01_M17_001'):
 assert required in ids,required
assert len(LINES)>=20

meshes={}
for state in STATES:
 m=kestrel_mesh(Mesh,state);meshes[state]=m
 assert m.faces and len(m.verts)==len(m.norm)==len(m.uv),state
 for face in m.faces:
  a,b,c=[m.verts[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
  n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
  assert sum(q*q for q in n)>1e-8,(state,face)

flight=meshes['flight'];convert=meshes['convert'];flare=meshes['flare'];landed=meshes['landed']
fx=[p[0] for p in flight.verts];fz=[p[2] for p in flight.verts]
assert max(fx)-min(fx)>=SPAN_IN,('Kestrel span regressed',max(fx)-min(fx))
assert max(fz)-min(fz)>=LENGTH_IN-2,('Kestrel length regressed',max(fz)-min(fz))
assert len(convert.verts)>len(flight.verts),'conversion state lost partial lift/gear hardware'
assert min(p[1] for p in convert.verts)>LANDED_CONTACT_Y,'partial conversion gear reaches the ground too early'
assert len(flare.verts)>len(flight.verts),'VTOL/gear state lost deployed hardware'
assert max(p[2] for p in landed.verts)>=520,'rear cargo ramp no longer reaches ground behind ship'
assert min(p[1] for p in flare.verts)<=LANDED_CONTACT_Y,'landing gear no longer reaches authored contact plane'

source=(ROOT/'tools/firstlight_kestrel.py').read_text(errors='replace')
for token in (
 "STATES=('flight','convert','flare','landed')","rear_cargo_aperture':True","balanced_vtol_nozzles':4",
 "'state_entities':8",'normalMap = {NORMAL}','surfaceMap = {SURFACE}',
 'wide four-point outriggers outside lift wash; partial conversion deployment','ventral TPS + hot cruise throats'
):
 assert token in source,token
assert 'long rail skids' not in source.lower()
assert len(OPENING_SEQUENCE)==8 and OPENING_SEQUENCE[0]=='ARRIVAL_WIDE' and OPENING_SEQUENCE[-1]=='ARRIVAL_DEPART'
assert sum(SHOT_PROFILES[x]['seconds'] for x in OPENING_SEQUENCE)>50

scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
k=(scripts/'firstlight_kestrel.lua').read_text(errors='replace')
c=(scripts/'firstlight_cinematic.lua').read_text(errors='replace')
d=(scripts/'firstlight_dialogue.lua').read_text(errors='replace')
i=(scripts/'firstlight_interact.lua').read_text(errors='replace')
for token in ("variant_from_name","string.find(name,'CONVERT',1,true)","show_state(e,s,'convert')",
              "show_state(e,s,'flare')","show_state(e,s,'landed')","ms<1100","ms<2700","ms<4000",
              "elapsed<47000","elapsed<53000","elapsed<60000"):
 assert token in k,token
for beat in OPENING_SEQUENCE:assert f"beat=='{beat}'" in k,beat
assert 'curve(' in k and "show_state(e,s,'flight')" in k and "beat=='ARRIVAL_ORBIT'" in k and "beat=='ARRIVAL_DESCENT'" in k
assert 'fl.evac_elapsed' in k and 'aegis.kestrel_landed=true' in k and 'aegis.kestrel_depart' in k
assert 'next_opening_beat' in c and "ARRIVAL_WIDE" in c and "ARRIVAL_DEPART" in c and "FL01_KES_001" in c and "FL01_KES_017" in c
assert 'function fl_dialogue(id)' in d and 'FL VO ' in d and 'PlayNon3DSound' in d
assert 'aegis.kestrel_landed' in i and "aegis.kestrel_depart=true" in i
assert "local radius=role=='EXTRACT' and 640 or 210" in i,'Broadwing ramp fell outside extraction boarding radius'

# Execute the real Kestrel Lua in the vendored MAX-compatible runtime. This catches
# native syntax/runtime regressions and verifies opening cuts own the mechanical
# states while the ship's position remains continuous across adjacent edits.
LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('FIRSTLIGHT_TEST=true')
lua.execute((scripts/'firstlight_audit.lua').read_text(errors='replace'))
lua.execute(r'''
shown={};poses={};g_Entity={}
for e=1,8 do g_Entity[e]={obj=e,x=0,y=496,z=-2350} end
function Hide(e) shown[e]=false end
function Show(e) shown[e]=true end
function CollisionOff(e) end
function SetEntityAlwaysActive(e,v) end
function PositionObject(obj,x,y,z) poses[obj]={x=x,y=y,z=z} end
function RotateObject(obj,rx,ry,rz) end
fl={started=true,born=0,evac_start=1,evac_elapsed=0}
aegis={}
g_Time=0
''')
lua.execute('\n'.join(line for line in k.splitlines() if not line.startswith("require ")))
lua.execute(r'''
firstlight_kestrel_init_name(1,'FL KESTREL INSERTION FLIGHT')
firstlight_kestrel_init_name(2,'FL KESTREL INSERTION CONVERT')
firstlight_kestrel_init_name(3,'FL KESTREL INSERTION FLARE')
firstlight_kestrel_init_name(4,'FL KESTREL INSERTION LANDED')
firstlight_kestrel_init_name(5,'FL KESTREL EXTRACTION FLIGHT')
firstlight_kestrel_init_name(6,'FL KESTREL EXTRACTION CONVERT')
firstlight_kestrel_init_name(7,'FL KESTREL EXTRACTION FLARE')
firstlight_kestrel_init_name(8,'FL KESTREL EXTRACTION LANDED')

-- Opening states are editorially isolated: no visible in-shot mesh swap.
aegis.cinematic_beat='ARRIVAL_WIDE';aegis.cinematic_started_at=1000;aegis.cinematic_duration_ms=9000;g_Time=5500
for e=1,4 do firstlight_kestrel_main(e) end
assert(shown[1]==true and shown[2]==false and shown[3]==false and shown[4]==false)

aegis.cinematic_beat='ARRIVAL_ORBIT';aegis.cinematic_started_at=10000;aegis.cinematic_duration_ms=9600;g_Time=14800
for e=1,4 do firstlight_kestrel_main(e) end
assert(shown[1]==false and shown[2]==true and shown[3]==false and shown[4]==false)

aegis.cinematic_beat='ARRIVAL_DESCENT';aegis.cinematic_started_at=20000;aegis.cinematic_duration_ms=12670;g_Time=26000
for e=1,4 do firstlight_kestrel_main(e) end
assert(shown[1]==false and shown[2]==false and shown[3]==true and shown[4]==false)

aegis.cinematic_beat='ARRIVAL_HANDOFF';aegis.cinematic_started_at=33000;aegis.cinematic_duration_ms=4600;g_Time=33200
for e=1,4 do firstlight_kestrel_main(e) end
assert(shown[1]==false and shown[2]==false and shown[3]==false and shown[4]==true)

-- PASS end and ORBIT start share the exact same world position; the camera cut hides
-- only the geometry-state change, not a teleport.
aegis.cinematic_beat='ARRIVAL_PASS';aegis.cinematic_started_at=40000;aegis.cinematic_duration_ms=10000;g_Time=50000
for e=1,4 do firstlight_kestrel_main(e) end
px=poses[1].x;py=poses[1].y;pz=poses[1].z
aegis.cinematic_beat='ARRIVAL_ORBIT';aegis.cinematic_started_at=50000;aegis.cinematic_duration_ms=10000;g_Time=50000
for e=1,4 do firstlight_kestrel_main(e) end
assert(math.abs(poses[2].x-px)<0.01 and math.abs(poses[2].y-py)<0.01 and math.abs(poses[2].z-pz)<0.01)

fl.evac_elapsed=40000;g_Time=40000;aegis.cinematic_beat=nil
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==true and shown[6]==false and shown[7]==false and shown[8]==false)

fl.evac_elapsed=48000;g_Time=48000
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==true and shown[7]==false and shown[8]==false)

fl.evac_elapsed=56000;g_Time=56000
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==false and shown[7]==true and shown[8]==false)

fl.evac_elapsed=60000;g_Time=60000
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==false and shown[7]==false and shown[8]==true)
assert(aegis.kestrel_landed==true)

aegis.kestrel_depart=true;aegis.cinematic_active=true;aegis.cinematic_beat='EXTRACTION';aegis.cinematic_started_at=100000;aegis.cinematic_duration_ms=8300;g_Time=100000
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[8]==true and aegis.kestrel_landed==false)

g_Time=101500
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==false and shown[7]==true and shown[8]==false)

g_Time=103200
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==true and shown[7]==false and shown[8]==false)

g_Time=104200
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==true and shown[6]==false and shown[7]==false and shown[8]==false)
''')

assert (ROOT/'Aegis Reach/Design/First Light/DIALOGUE_ELEVENLABS.md').is_file()
assert (ROOT/'Aegis Reach/Design/First Light/KESTREL_DESIGN.md').is_file()
print('FIRST LIGHT // STORY DELIVERY PASS')
print('Dialogue lines:',len(LINES),'// Broadwing Kestrel states:',
      ', '.join(f'{s}:{len(meshes[s].verts)}v' for s in STATES),
      '// continuous eight-shot insertion + cut-hidden VTOL state changes + grounded rear-ramp verified.')
