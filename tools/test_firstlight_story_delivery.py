"""Regression checks for FIRST LIGHT story delivery and Broadwing Kestrel choreography."""
from pathlib import Path
from native_format import ROOT
from environment_pass import Mesh
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh,STATES,LENGTH_IN,SPAN_IN,LANDED_CONTACT_Y
from firstlight_cinematics import SHOT_PROFILES
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

flight=meshes['flight'];flare=meshes['flare'];landed=meshes['landed']
fx=[p[0] for p in flight.verts];fz=[p[2] for p in flight.verts]
assert max(fx)-min(fx)>=SPAN_IN,('Kestrel span regressed',max(fx)-min(fx))
assert max(fz)-min(fz)>=LENGTH_IN-2,('Kestrel length regressed',max(fz)-min(fz))
assert len(flare.verts)>len(flight.verts),'VTOL/gear state lost deployed hardware'
assert max(p[2] for p in landed.verts)>=520,'rear cargo ramp no longer reaches ground behind ship'
assert min(p[1] for p in flare.verts)<=LANDED_CONTACT_Y,'landing gear no longer reaches authored contact plane'

source=(ROOT/'tools/firstlight_kestrel.py').read_text(errors='replace')
for token in (
 "STATES=('flight','flare','landed')","rear_cargo_aperture':True","balanced_vtol_nozzles':4",
 "'state_entities':6",'normalMap = {NORMAL}','surfaceMap = {SURFACE}',
 'wide four-point outriggers outside lift wash','ventral TPS + hot cruise throats'
):
 assert token in source,token
assert 'long rail skids' not in source.lower()
assert SHOT_PROFILES['ARRIVAL']['seconds']>=6 and SHOT_PROFILES['ARRIVAL_HANDOFF']['seconds']>=6

scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
k=(scripts/'firstlight_kestrel.lua').read_text(errors='replace')
c=(scripts/'firstlight_cinematic.lua').read_text(errors='replace')
d=(scripts/'firstlight_dialogue.lua').read_text(errors='replace')
i=(scripts/'firstlight_interact.lua').read_text(errors='replace')
for token in ("variant_from_name","show_state(e,s,'flight')","show_state(e,s,'flare')","show_state(e,s,'landed')",
              "ms<1100","ms<3300","elapsed<50000","elapsed<60000"):
 assert token in k,token
assert 'PositionObject' in k and "beat=='ARRIVAL'" in k and "beat=='ARRIVAL_HANDOFF'" in k
assert 'fl.evac_elapsed' in k and 'aegis.kestrel_landed=true' in k and 'aegis.kestrel_depart' in k
assert "aegis.cinematic_request='ARRIVAL_HANDOFF'" in c and "FL01_KES_001" in c and "FL01_KES_017" in c
assert 'function fl_dialogue(id)' in d and 'FL VO ' in d and 'PlayNon3DSound' in d
assert 'aegis.kestrel_landed' in i and "aegis.kestrel_depart=true" in i
assert "local radius=role=='EXTRACT' and 640 or 210" in i,'Broadwing ramp fell outside extraction boarding radius'

# Execute the real Kestrel Lua in the vendored MAX-compatible runtime. This catches
# native syntax/runtime regressions and verifies that the six authored entities swap
# flight -> flare -> landed -> flare -> flight at the expected extraction phases.
LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('FIRSTLIGHT_TEST=true')
lua.execute((scripts/'firstlight_audit.lua').read_text(errors='replace'))
lua.execute(r'''
shown={};poses={};g_Entity={}
for e=1,6 do g_Entity[e]={obj=e,x=0,y=496,z=-2350} end
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
firstlight_kestrel_init_name(2,'FL KESTREL INSERTION FLARE')
firstlight_kestrel_init_name(3,'FL KESTREL INSERTION LANDED')
firstlight_kestrel_init_name(4,'FL KESTREL EXTRACTION FLIGHT')
firstlight_kestrel_init_name(5,'FL KESTREL EXTRACTION FLARE')
firstlight_kestrel_init_name(6,'FL KESTREL EXTRACTION LANDED')

fl.evac_elapsed=40000;g_Time=40000
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[4]==true and shown[5]==false and shown[6]==false)

fl.evac_elapsed=55000;g_Time=55000
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[4]==false and shown[5]==true and shown[6]==false)

fl.evac_elapsed=60000;g_Time=60000
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[4]==false and shown[5]==false and shown[6]==true)
assert(aegis.kestrel_landed==true)

aegis.kestrel_depart=true;aegis.cinematic_active=true;aegis.cinematic_beat='EXTRACTION';aegis.cinematic_started_at=100000;aegis.cinematic_duration_ms=8300;g_Time=100000
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[6]==true and aegis.kestrel_landed==false)

g_Time=101500
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[4]==false and shown[5]==true and shown[6]==false)

g_Time=104000
for e=4,6 do firstlight_kestrel_main(e) end
assert(shown[4]==true and shown[5]==false and shown[6]==false)
''')

assert (ROOT/'Aegis Reach/Design/First Light/DIALOGUE_ELEVENLABS.md').is_file()
assert (ROOT/'Aegis Reach/Design/First Light/KESTREL_DESIGN.md').is_file()
print('FIRST LIGHT // STORY DELIVERY PASS')
print('Dialogue lines:',len(LINES),'// Broadwing Kestrel states:',
      ', '.join(f'{s}:{len(meshes[s].verts)}v' for s in STATES),
      '// lifting-body + VTOL conversion + grounded rear-ramp + MAX-Lua state-swap contract verified.')
