"""Regression gate for FIRST LIGHT's authored Vesper biosphere visual language."""
import json,math,zipfile

from native_format import ROOT,read_ele
from max_archive import PASSWORD
from environment_pass import Mesh
from firstlight_world import ROUTE,RETURN,road_sample
from firstlight_biosphere import (
    salt_scrub,brine_reed,salt_lace,skitter,veilwing,
    SCRUB_SITES,REED_SITES,MAT_SITES,SKITTER_SITES,VEILWING_SITES,MIDGE_SITES,SCRIPT
)


def validate_mesh(fn,min_vertices):
    m=fn(Mesh)
    assert m.faces and len(m.verts)==len(m.norm)==len(m.uv),fn.__name__
    assert len(m.verts)>=min_vertices,(fn.__name__,len(m.verts),min_vertices)
    for face in m.faces:
        a,b,c=[m.verts[i] for i in face]
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        assert sum(k*k for k in n)>1e-8,'degenerate biosphere triangle'
    assert min(v[1] for v in m.verts)>=-1.05,'biosphere mesh is buried too deeply below authored root plane'
    return m


meshes={
    'glass_fan':validate_mesh(salt_scrub,260),
    'brine_cup':validate_mesh(brine_reed,300),
    'salt_lace':validate_mesh(salt_lace,260),
    'skitter':validate_mesh(skitter,320),
    'veilwing':validate_mesh(veilwing,150),
}
# Regression against the original Roblox-like prototype: every species must have enough
# authored curvature/segmentation to avoid collapsing back to boxes plus disconnected cards.
assert all(len(m.faces)>80 for m in meshes.values())

for x,z,*_ in SCRUB_SITES+REED_SITES+MAT_SITES:
    clearance=min(road_sample(x,z,ROUTE)[0],road_sample(x,z,RETURN)[0])
    assert clearance>=300,(x,z,clearance)

DESIGN=ROOT/'Aegis Reach/Design/First Light'
layout=json.loads((DESIGN/'layout.json').read_text())
report=json.loads((DESIGN/'build-report.json').read_text())
summary=report.get('biosphere',{})
flora=[p for p in layout if p.get('kind')=='biosphere_flora']
creatures=[p for p in layout if p.get('kind')=='biosphere_creature']
particles=[p for p in layout if p.get('kind')=='biosphere_particle']
retired=[p for p in layout if p.get('kind')=='retired_vegetation']
assert len(flora)==len(SCRUB_SITES)+len(REED_SITES)+len(MAT_SITES)==summary.get('flora_count')
assert len(creatures)==len(SKITTER_SITES)+len(VEILWING_SITES)
assert summary.get('skitter_count')==len(SKITTER_SITES) and summary.get('veilwing_count')==len(VEILWING_SITES)
assert len(particles)==len(MIDGE_SITES)==summary.get('midge_cloud_count')
assert summary.get('legacy_stock_shrubs_retired',0)==len(retired)>=8
assert summary.get('navigation_collision') is False and summary.get('damage') is False
assert 'glass-fan membranes' in summary.get('visual_language','') and 'segmented mineral-chitin fauna' in summary.get('visual_language','')
assert max(p['z'] for p in creatures+particles)<1000,'ambient fauna should not crowd the AEGIS reveal zone'

MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
with zipfile.ZipFile(MAP) as archive:
    _,entities=read_ele(archive.read('map.ele',pwd=PASSWORD))
byname={e['101:eleprof.name_s']:e for e in entities}
for p in creatures+particles:
    e=byname[p['name']]
    assert str(e['101:eleprof.aimain_s']).replace('/','\\').lower()==SCRIPT.lower(),p['name']

source=(ROOT/'tools/firstlight_biosphere.py').read_text(errors='replace')
assert source.count("'eleprof.physics':0")>=6,'biosphere entities are no longer authored physics-off'
assert source.count("'eleprof.phyalways':0")>=6,'biosphere entities unexpectedly gained persistent physics'
assert "placement.get('name')!='Vesper / salt scrub'" in source,'legacy Earth shrubs are no longer explicitly retired'

bank=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
for tex in ('vesper_biosphere.png','vesper_biosphere_normal.png','vesper_biosphere_surface.png','vesper_biosphere_emission.png'):
    assert (bank/tex).is_file(),'missing generated biosphere material map: '+tex
for name in ('Vesper Glass Fan','Vesper Brine Cup','Vesper Salt Lace','Vesper Crust Skitter','Vesper Veilwing'):
    text=(bank/(name+'.fpe')).read_text(errors='replace').lower()
    assert 'collisionmode = 11' in text,name
    assert 'normalmap = vesper_biosphere_normal.png' in text,name
    assert 'surfacemap = vesper_biosphere_surface.png' in text,name
    assert 'emissivemap = vesper_biosphere_emission.png' in text,name

lua=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_biosphere.lua').read_text(errors='replace')
for token in ('FL BIO SKITTER','FL BIO VEILWING','FL BIO SPORES','PositionObject','RotateObject','EffectSetSpeed(e,6)','g_Time+90','g_Time+70'):
    assert token in lua,token
assert 'CollisionOff' in lua,'ambient fauna no longer explicitly disables runtime collision'
for forbidden in ('SetEntityHealth','SetPlayerHealth','FireWeapon','CharacterControl'):
    assert forbidden not in lua,'ambient biosphere gained gameplay authority: '+forbidden

print('FIRST LIGHT // BIOSPHERE VISUAL-LANGUAGE PASS')
print('Flora:',len(flora),'// mesh fauna:',len(creatures),'// microscopic colonies:',len(particles))
print('Legacy Earth shrubs retired:',len(retired))
print('Five authored species use coordinated APBR maps, visual-only collision and local animation.')
print('Native MAX silhouette, material response and creature motion still require visual review.')
