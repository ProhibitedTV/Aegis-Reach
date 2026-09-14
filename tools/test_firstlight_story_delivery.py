"""Regression checks for FIRST LIGHT story delivery and Broadwing Kestrel choreography."""
from pathlib import Path
from native_format import ROOT
from environment_pass import Mesh
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh,STATES,LENGTH_IN,SPAN_IN,LANDED_CONTACT_Y
from firstlight_cinematics import SHOT_PROFILES

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
assert (ROOT/'Aegis Reach/Design/First Light/DIALOGUE_ELEVENLABS.md').is_file()
assert (ROOT/'Aegis Reach/Design/First Light/KESTREL_DESIGN.md').is_file()
print('FIRST LIGHT // STORY DELIVERY PASS')
print('Dialogue lines:',len(LINES),'// Broadwing Kestrel states:',
      ', '.join(f'{s}:{len(meshes[s].verts)}v' for s in STATES),
      '// lifting-body + VTOL conversion + grounded rear-ramp contract verified.')
