"""Regression checks for FIRST LIGHT story delivery and Broadwing Kestrel choreography."""
from native_format import ROOT
from environment_pass import Mesh
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh,STATES,LENGTH_IN,SPAN_IN,LANDED_CONTACT_Y
from firstlight_cinematics import SHOT_PROFILES,OPENING_SEQUENCE,OPENING_TOTAL_MS
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
):assert token in source,token
assert 'long rail skids' not in source.lower()
assert len(OPENING_SEQUENCE)==17 and OPENING_SEQUENCE[0]=='ARRIVAL_PERIM' and OPENING_SEQUENCE[-1]=='ARRIVAL_DEPART'
assert OPENING_TOTAL_MS==50800
assert max(SHOT_PROFILES[x]['seconds'] for x in OPENING_SEQUENCE)<=4.2

scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
k=(scripts/'firstlight_kestrel.lua').read_text(errors='replace')
c=(scripts/'firstlight_cinematic.lua').read_text(errors='replace')
d=(scripts/'firstlight_dialogue.lua').read_text(errors='replace')
i=(scripts/'firstlight_interact.lua').read_text(errors='replace')
for token in ("variant_from_name","string.find(name,'CONVERT',1,true)","show_state(e,s,'convert')",
              "show_state(e,s,'flare')","show_state(e,s,'landed')","ms<8400","ms<17500","ms<23500","ms<32500",
              "ms<42700","ms<45300","ms<47800","ms<50800","elapsed<47000","elapsed<53000","elapsed<60000"):
 assert token in k,token
assert 'opening_elapsed_ms' in k and 'opening_ms()' in k and 'beat_elapsed' not in k
assert 'fl.evac_elapsed' in k and 'aegis.kestrel_landed=true' in k and 'aegis.kestrel_depart' in k
assert 'next_opening_beat' in c and "ARRIVAL_PERIM" in c and "ARRIVAL_DEPART" in c and 'opening_started_at' in c
assert "FL01_KES_001" in c and "FL01_KES_017" in c
assert 'function fl_dialogue(id)' in d and 'FL VO ' in d and 'PlayNon3DSound' in d
assert 'aegis.kestrel_landed' in i and "aegis.kestrel_depart=true" in i
assert "local radius=role=='EXTRACT' and 640 or 210" in i,'Broadwing ramp fell outside extraction boarding radius'

# Execute real Kestrel Lua under the MAX-compatible runtime. Camera beats are not fed
# into the insertion controller: only the single opening_elapsed_ms clock drives it.
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

local function insertion_at(ms)
 aegis.opening_elapsed_ms=ms
 for e=1,4 do firstlight_kestrel_main(e) end
end
insertion_at(4000);assert(shown[1]==true and shown[2]==false and shown[3]==false and shown[4]==false)
insertion_at(18000);assert(shown[1]==false and shown[2]==true and shown[3]==false and shown[4]==false)
insertion_at(26000);assert(shown[1]==false and shown[2]==false and shown[3]==true and shown[4]==false)
insertion_at(36000);assert(shown[1]==false and shown[2]==false and shown[3]==false and shown[4]==true)
insertion_at(44000);assert(shown[1]==false and shown[2]==false and shown[3]==true and shown[4]==false)
insertion_at(46000);assert(shown[1]==false and shown[2]==true and shown[3]==false and shown[4]==false)
insertion_at(49000);assert(shown[1]==true and shown[2]==false and shown[3]==false and shown[4]==false)

-- A camera-source cut inside the flight state does not reset or teleport the path.
insertion_at(8399);local ax,ay,az=poses[1].x,poses[1].y,poses[1].z
insertion_at(8400);assert(math.abs(poses[1].x-ax)<1.0 and math.abs(poses[1].y-ay)<1.0 and math.abs(poses[1].z-az)<1.0)
-- Mechanical state boundary is position-continuous even though the mesh changes.
insertion_at(17499);local bx,by,bz=poses[1].x,poses[1].y,poses[1].z
insertion_at(17500);assert(math.abs(poses[2].x-bx)<1.0 and math.abs(poses[2].y-by)<1.0 and math.abs(poses[2].z-bz)<1.0)

fl.evac_elapsed=40000;g_Time=40000;aegis.opening_elapsed_ms=nil
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==true and shown[6]==false and shown[7]==false and shown[8]==false)
fl.evac_elapsed=48000;g_Time=48000;for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==true and shown[7]==false and shown[8]==false)
fl.evac_elapsed=56000;g_Time=56000;for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==false and shown[7]==true and shown[8]==false)
fl.evac_elapsed=60000;g_Time=60000;for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[5]==false and shown[6]==false and shown[7]==false and shown[8]==true and aegis.kestrel_landed==true)

aegis.kestrel_depart=true;aegis.cinematic_active=true;aegis.cinematic_beat='EXTRACTION';aegis.cinematic_started_at=100000;aegis.cinematic_duration_ms=8300;g_Time=100000
for e=5,8 do firstlight_kestrel_main(e) end
assert(shown[8]==true and aegis.kestrel_landed==false)
g_Time=101500;for e=5,8 do firstlight_kestrel_main(e) end;assert(shown[7]==true)
g_Time=103200;for e=5,8 do firstlight_kestrel_main(e) end;assert(shown[6]==true)
g_Time=104200;for e=5,8 do firstlight_kestrel_main(e) end;assert(shown[5]==true)
''')

assert (ROOT/'Aegis Reach/Design/First Light/DIALOGUE_ELEVENLABS.md').is_file()
assert (ROOT/'Aegis Reach/Design/First Light/KESTREL_DESIGN.md').is_file()
print('FIRST LIGHT // STORY DELIVERY PASS')
print('Dialogue lines:',len(LINES),'// Broadwing Kestrel states:',
      ', '.join(f'{s}:{len(meshes[s].verts)}v' for s in STATES),
      '// continuous 50.8s insertion independent of 17 rapid camera cuts + cut-hidden VTOL states verified.')
