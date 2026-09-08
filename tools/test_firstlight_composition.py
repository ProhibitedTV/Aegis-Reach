"""Regression checks for First Light's production environment composition.

Run after build_first_light.py. The test cannot judge art quality, but it prevents
known structural regressions: duplicate Camp 12 dressing, giant legacy bespoke
shells, repeated custom floodlights/revetments, and unbounded prop growth.
"""
import json

from native_format import ROOT
from firstlight_world import ground

DESIGN=ROOT/'Aegis Reach/Design/First Light'
LAYOUT=DESIGN/'layout.json'
REPORT=DESIGN/'build-report.json'

if not LAYOUT.is_file() or not REPORT.is_file():
 raise SystemExit('FIRST LIGHT // COMPOSITION TEST FAILED: build reports missing; rebuild First Light first')

placements=json.loads(LAYOUT.read_text())
report=json.loads(REPORT.read_text())

assert report.get('environment_pass')=='single-owner-production-recomposition', report.get('environment_pass')

joined='\n'.join(str(p.get('name',''))+' '+str(p.get('asset','')) for p in placements)
for banned in (
 'Camp 12 Equipment Canopy',
 'Gate 07 Cut Portal',
 'Northstar Turbine Hall',
 'Meridian Operations House',
 'AEGIS Cliff Gallery',
 'Floodlight Mast',
 'Revetment',
):
 assert banned not in joined, 'legacy environment primitive returned: '+banned

def in_camp(p):
 try:return -2520<=float(p['x'])<=-780 and -7800<=float(p['z'])<=-6350
 except Exception:return False

camp=[p for p in placements if in_camp(p) and p.get('kind','environment')=='environment']
assert 10<=len(camp)<=22, 'Camp 12 prop budget escaped: '+str(len(camp))
for p in camp:
 asset=str(p.get('asset',''))
 for banned in ('Tent 01','Portable Cot','Camping Pack'):
  assert banned not in asset, 'Camp 12 secondary dressing returned: '+asset

# The deliberate indoor desk/chair are owned by the lab composition, not a second dressing pass.
workstation=[p for p in camp if any(k in p.get('asset','') for k in ('Desk 01','Desk Chair'))]
assert len(workstation)<=2, 'indoor work station grew into secondary dressing'
assert all(-2330<p['x']<-2160 and -7390<p['z']<-7090 for p in workstation), 'lab furniture escaped into court'

assets='\n'.join(str(p.get('asset','')) for p in camp)
for required in (
 'CS_Wall_01_Window.fpe',
 'CS_Roof_Tile_2x2.fpe',
 'SurveyorStand1.fpe',
 'Light Generator.fpe',
 'Freight Container.fpe',
):
 assert required in assets, 'Camp 12 missing composition anchor: '+required

# The installed Entry_01 has solid geometry across the doorway; it must not
# seal the service bay again. A visible door texture does not imply an opening.
assert 'CS_Wall_01_Entry_01.fpe' not in assets, 'closed facade blocks Camp 12 service bay'
camp_barriers=[p for p in camp if p['asset'].endswith('Roadblock2.fpe')]
assert len(camp_barriers)==1, 'camp perimeter is no longer one restrained marker'
for p in camp_barriers:
 # Installed local footprint is 54.2 x 61.0 inches, scaled to 86% and rotated.
 # This conservative 76-inch square encloses all feet without importing DLC.
 for dx in (-38,0,38):
  for dz in (-38,0,38):
   assert abs(ground(p['x']+dx,p['z']+dz)-p['y'])<0.5, 'camp barrier straddles uneven ground'

route_markers=[p for p in placements if str(p.get('name','')).startswith('Meridian route marker ')]
assert 3<=len(route_markers)<=6, 'route beacon count is no longer sparse: '+str(len(route_markers))

# Brineglass is geology, not another prop family. Keep it sparse and make the anomaly
# strengthen materially as well as spatially toward the fracture.
crystals=[p for p in placements if p.get('kind')=='geology' and 'Brineglass bloom' in str(p.get('name',''))]
assert 8<=len(crystals)<=12, 'brineglass count escaped sparse range: '+str(len(crystals))
assert not [p for p in crystals if in_camp(p)], 'brineglass intruded into Camp 12 core composition'
zs=[float(p['z']) for p in crystals]
assert min(zs)<-8000 and max(zs)>4800, 'brineglass no longer spans discovery-to-fracture progression'
assert report.get('crystal_clusters')==len(crystals), 'build report crystal count mismatch'
resonant=[p for p in crystals if str(p.get('name','')).startswith('Resonant Brineglass')]
assert 2<=len(resonant)<=4, 'resonant brineglass progression escaped target range: '+str(len(resonant))
materials=report.get('brineglass_materials',[])
assert materials==['vesper_brineglass_energy.png','vesper_brineglass_resonant.png'], 'brineglass energy material suite changed: '+repr(materials)
atmosphere=report.get('atmosphere',{})
assert float(atmosphere.get('Exposure',9))<1.0, 'Vesper atmosphere regressed to washed-out exposure'
assert 0.02<=float(atmosphere.get('BloomStrength',0))<=0.12, 'bloom escaped the restrained mineral-light grade'
assert atmosphere.get('DeSaturate')==1, 'world color was removed'
assert all(128<=atmosphere.get(k,0)<=255 for k in ('SunRed','SunGreen','SunBlue')), 'sun color is not in native 0..255 units'

custom_environment=[]
for p in placements:
 if p.get('kind','environment')!='environment':continue
 asset=str(p.get('asset','')).replace('/','\\')
 if asset.startswith('Aegis Reach\\First Light\\'):
  custom_environment.append(asset.split('\\')[-1])
allowed={
 'Camp 12 Survey Mast.fpe',
 'Northstar Stack Pair.fpe',
 'AEGIS Arrival Frame.fpe',
 'Meridian Route Beacon.fpe',
 'Choir Breach Arch.fpe',
 'Excavation Service Bridge.fpe',
 'Evacuation Board Supports.fpe',
 'Extraction Sign Supports.fpe',
}
unexpected=sorted(set(custom_environment)-allowed)
assert not unexpected, 'unexpected bespoke environment meshes: '+', '.join(unexpected)

print('FIRST LIGHT // COMPOSITION TEST PASS')
print('Camp 12 environment entities:',len(camp))
print('Route markers:',len(route_markers))
print('Brineglass blooms:',len(crystals),'resonant:',len(resonant))
print('Brineglass materials:',', '.join(materials))
print('Bespoke environment vocabulary:',', '.join(sorted(set(custom_environment))))
print('Environment mode:',report['environment_pass'])
