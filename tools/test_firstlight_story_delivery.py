"""Regression checks for FIRST LIGHT story delivery, Kestrel choreography and VO handoff."""
from pathlib import Path
from native_format import ROOT
from environment_pass import Mesh
from firstlight_dialogue import LINES
from firstlight_kestrel import kestrel_mesh
from firstlight_cinematics import SHOT_PROFILES

ids=[x['id'] for x in LINES];files=[x['filename'] for x in LINES]
assert len(ids)==len(set(ids)) and len(files)==len(set(files))
for required in ('FL01_KES_001','FL01_KES_004','FL01_MIR_001','FL01_MIR_002','FL01_KES_012','FL01_KES_015','FL01_KES_016','FL01_KES_017','FL01_M17_001'):
 assert required in ids,required
assert len(LINES)>=20
m=kestrel_mesh(Mesh);assert m.faces and len(m.verts)==len(m.norm)==len(m.uv)
for face in m.faces:
 a,b,c=[m.verts[i] for i in face];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert sum(q*q for q in n)>1e-8
assert SHOT_PROFILES['ARRIVAL']['seconds']>=6 and SHOT_PROFILES['ARRIVAL_HANDOFF']['seconds']>=6
scripts=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach'
k=(scripts/'firstlight_kestrel.lua').read_text(errors='replace')
c=(scripts/'firstlight_cinematic.lua').read_text(errors='replace')
d=(scripts/'firstlight_dialogue.lua').read_text(errors='replace')
i=(scripts/'firstlight_interact.lua').read_text(errors='replace')
assert 'PositionObject' in k and "beat=='ARRIVAL'" in k and "beat=='ARRIVAL_HANDOFF'" in k
assert 'fl.evac_elapsed' in k and 'aegis.kestrel_landed=true' in k and 'aegis.kestrel_depart' in k
assert "aegis.cinematic_request='ARRIVAL_HANDOFF'" in c and "FL01_KES_001" in c and "FL01_KES_017" in c
assert 'function fl_dialogue(id)' in d and 'FL VO ' in d and 'PlayNon3DSound' in d
assert 'aegis.kestrel_landed' in i and "aegis.kestrel_depart=true" in i
assert (ROOT/'Aegis Reach/Design/First Light/DIALOGUE_ELEVENLABS.md').is_file()
print('FIRST LIGHT // STORY DELIVERY PASS')
print('Dialogue lines:',len(LINES),'// Kestrel mesh verts:',len(m.verts),'// two-shot insertion + visible extraction vehicle contract verified.')
