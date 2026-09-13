"""Build FIRST LIGHT, then apply the production combat-space layer.

`build_first_light.py` remains the known-good world generator. Importing it performs the
baseline build. This wrapper then adds combat cover, moves dormant Warden starts onto
those authored pockets, adds restrained contact backlights, and rewrites the exact same
native MAX archive with navmesh data intentionally absent so MAX regenerates navigation.
"""
import json
import zipfile

import build_first_light as build
from firstlight_combat_geometry import apply,write_manifest

summary=apply(build)

# The baseline module leaves its native payload in memory. Replace only the entity bank
# after the combat layer mutates `entities`/`bank`; terrain, visuals, cfg and bespoke
# environment data remain byte-for-byte the baseline composition in this process.
build.payload['map.ele']=build.write_ele(build.version,build.entities)
build.payload['map.ent']=build.write_bank(build.bank)
for key in list(build.payload):
 if key=='map.obs' or 'navmesh' in key.lower():del build.payload[key]

with zipfile.ZipFile(build.MAP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for name,data in build.payload.items():out.writestr(name,data)
build.convert(build.MAP)

# Refresh authored manifests after the layer is applied. These are the source-of-truth
# review artifacts for encounter placement; licensed DLC still remains installation-only.
(build.DESIGN/'layout.json').write_text(json.dumps(build.placements,indent=2))
report_path=build.DESIGN/'build-report.json'
try:report=json.loads(report_path.read_text())
except Exception:report={}
report.update({
 'map':build.MAP.name,
 'entities':len(build.entities),
 'asset_types':len(build.bank),
 'assets':build.bank,
 'staged_dependencies':sorted(build.staged),
 'lights':len(build.light_locations)+len(build.crystal_sites)+summary['combat_light_count'],
 'production_combat_geometry':summary,
 'environment_pass':'single-owner-production-recomposition + tactical-cover-layer',
})
report_path.write_text(json.dumps(report,indent=2))
write_manifest(build.DESIGN/'combat-geometry.json',summary)

print('FIRST LIGHT // PRODUCTION COMBAT LAYER')
print('Cover pieces:',summary['cover_count'])
print('Combat backlights:',summary['combat_light_count'])
print('Repositioned Warden starts:',len(summary['enemy_starts']))
print('Landing-zone center preserved:',summary['clear_lz_center'])
