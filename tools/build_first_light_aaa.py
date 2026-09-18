"""Build FIRST LIGHT, then apply production gameplay/story/environment layers."""
import json
import zipfile

import build_first_light as build
from firstlight_combat_geometry import apply,write_manifest

summary=apply(build)
from firstlight_story_effects import apply as add_story_effects
story_effects=add_story_effects(build)
from firstlight_transport import apply as add_transport
transport=add_transport(build)
from firstlight_kestrel import apply as add_kestrel
kestrel=add_kestrel(build)
from firstlight_kestrel_boarding import apply as add_kestrel_boarding
kestrel_boarding=add_kestrel_boarding(build)
from firstlight_dialogue import apply as add_dialogue
dialogue=add_dialogue(build)
from firstlight_cinematics import apply as add_cinematics
cinematics=add_cinematics(build)
from firstlight_opening_director import apply as add_opening_director
opening_director=add_opening_director(build)
from firstlight_cineguru_native_chain import apply as add_cineguru_native_chain
cineguru_chain=add_cineguru_native_chain(build)
from firstlight_biosphere import apply as add_biosphere
biosphere=add_biosphere(build)
from firstlight_title_screen_convergence import apply as add_title_screen_convergence
title_screen=add_title_screen_convergence(build)
from firstlight_native_engine_pass import apply as add_native_engine_pass
native_engine=add_native_engine_pass(build)

build.payload['map.ele']=build.write_ele(build.version,build.entities)
build.payload['map.ent']=build.write_bank(build.bank)
for key in list(build.payload):
 if key=='map.obs' or 'navmesh' in key.lower():del build.payload[key]
with zipfile.ZipFile(build.MAP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,data in build.payload.items():out.writestr(name,data)
build.convert(build.MAP)

(build.DESIGN/'layout.json').write_text(json.dumps(build.placements,indent=2))
report_path=build.DESIGN/'build-report.json'
try:report=json.loads(report_path.read_text())
except Exception:report={}
report.update({
 'map':build.MAP.name,'entities':len(build.entities),'asset_types':len(build.bank),'assets':build.bank,
 'staged_dependencies':sorted(build.staged),
 'lights':len(build.light_locations)+len(build.crystal_sites)+summary['combat_light_count']+transport['lights'],
 'production_combat_geometry':summary,'story_effects':story_effects,'transport_wreck':transport,
 'kestrel':kestrel,'kestrel_boarding':kestrel_boarding,'dialogue':dialogue,'cinematics':cinematics,
 'opening_director':opening_director,'cineguru_native_chain':cineguru_chain,'biosphere':biosphere,
 'title_screen_convergence':title_screen,'native_engine_pass':native_engine,
 'environment_pass':'single-owner-production-recomposition + tactical-cover-layer + title-screen skyline convergence',
})
report_path.write_text(json.dumps(report,indent=2));write_manifest(build.DESIGN/'combat-geometry.json',summary)

print('FIRST LIGHT // PRODUCTION COMBAT + STORY + VEHICLE + BIOSPHERE + NATIVE ENGINE LAYER')
print('Cover pieces:',summary['cover_count']);print('Combat backlights:',summary['combat_light_count']);print('Repositioned Warden starts:',len(summary['enemy_starts']))
print('CineGuru story beats:',', '.join(cinematics['beats']))
print('Opening director:',opening_director['cut_count'],'hard cuts //',opening_director['opening_ms']/1000,'s // camera owner',opening_director['camera_owner'])
print('CineGuru compatibility marker:',cineguru_chain['compatibility_only'],'//',cineguru_chain['camera_count'],'linked ARRIVAL cameras')
print('Title-screen skyline:',title_screen['entity_count'],'visual-only landmarks //',title_screen['spire_count'],'relay spires')
print('Kestrel:',kestrel['vehicle_entities'],'visible vehicle entities // landing at',kestrel['touchdown_ms']//1000,'s')
print('Kestrel boarding:',kestrel_boarding['proxy_entities'],'landed-only polygon collision proxy')
print('Dialogue:',dialogue['line_count'],'scripted lines /',dialogue['audio_bound_count'],'audio files currently bound')
print('Vesper life:',biosphere['flora_count'],'flora /',biosphere['skitter_count'],'skitters /',biosphere['veilwing_count'],'veilwings /',biosphere['midge_cloud_count'],'microscopic colonies')
print('Legacy Earth shrubs retired:',biosphere['legacy_stock_shrubs_retired'])
print('Responsive practical lights:',native_engine['responsive_practical_lights']);print('Landing-zone center preserved:',summary['clear_lz_center'])
