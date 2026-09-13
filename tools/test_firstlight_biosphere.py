"""Regression gate for FIRST LIGHT's sparse primitive Vesper biosphere."""
import json,math,zipfile

from native_format import ROOT,read_ele
from max_archive import PASSWORD
from environment_pass import Mesh
from firstlight_world import ROUTE,RETURN,road_sample
from firstlight_biosphere import (
    salt_scrub,brine_reed,skitter,SCRUB_SITES,REED_SITES,SKITTER_SITES,MIDGE_SITES,SCRIPT
)


def validate_mesh(fn):
    m=fn(Mesh)
    assert m.faces and len(m.verts)==len(m.norm)==len(m.uv),fn.__name__
    for face in m.faces:
        a,b,c=[m.verts[i] for i in face]
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        assert sum(k*k for k in n)>1e-8,'degenerate biosphere triangle'
    assert min(v[1] for v in m.verts)>=-0.01,'biosphere mesh extends below authored root plane'


for fn in (salt_scrub,brine_reed,skitter):validate_mesh(fn)

# Flora should dress shoulders/pool margins without becoming combat-road clutter.
for x,z,*_ in SCRUB_SITES+REED_SITES:
    clearance=min(road_sample(x,z,ROUTE)[0],road_sample(x,z,RETURN)[0])
    assert clearance>=300,(x,z,clearance)

DESIGN=ROOT/'Aegis Reach/Design/First Light'
layout=json.loads((DESIGN/'layout.json').read_text())
report=json.loads((DESIGN/'build-report.json').read_text())
summary=report.get('biosphere',{})
flora=[p for p in layout if p.get('kind')=='biosphere_flora']
creatures=[p for p in layout if p.get('kind')=='biosphere_creature']
particles=[p for p in layout if p.get('kind')=='biosphere_particle']
assert len(flora)==len(SCRUB_SITES)+len(REED_SITES)==summary.get('flora_count')
assert len(creatures)==len(SKITTER_SITES)==summary.get('skitter_count')
assert len(particles)==len(MIDGE_SITES)==summary.get('midge_cloud_count')
assert summary.get('navigation_collision') is False and summary.get('damage') is False
assert max(p['z'] for p in creatures+particles)<1000,'ambient fauna should not crowd the AEGIS reveal zone'

MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
with zipfile.ZipFile(MAP) as archive:
    _,entities=read_ele(archive.read('map.ele',pwd=PASSWORD))
byname={e['101:eleprof.name_s']:e for e in entities}
for p in creatures+particles:
    e=byname[p['name']]
    assert e['101:eleprof.physics']==0,p['name']
    assert str(e['101:eleprof.aimain_s']).replace('/','\\').lower()==SCRIPT.lower(),p['name']

bank=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
assert (bank/'vesper_biosphere.png').is_file(),'missing generated biosphere atlas'
for name in ('Vesper Salt Scrub','Vesper Brine Reed','Vesper Crust Skitter'):
    text=(bank/(name+'.fpe')).read_text(errors='replace').lower()
    assert 'collisionmode = 11' in text,name

lua=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_biosphere.lua').read_text(errors='replace')
assert 'PositionObject' in lua and 'EffectStart' in lua and 'EffectSetSpeed(e,13)' in lua
for forbidden in ('SetEntityHealth','SetPlayerHealth','FireWeapon','CharacterControl'):
    assert forbidden not in lua,'ambient biosphere gained gameplay authority: '+forbidden

print('FIRST LIGHT // BIOSPHERE PASS')
print('Flora:',len(flora),'// skitters:',len(creatures),'// airborne colonies:',len(particles))
print('Primitive life remains visual-only, route-safe and intentionally sparse near AEGIS.')
print('Native MAX scale, particle readability and creature motion still require visual review.')
