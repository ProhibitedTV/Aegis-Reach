"""Rebuild First Light only when authored world/build sources changed."""
from pathlib import Path
import hashlib,json,subprocess,sys
from PIL import ImageFile
from native_format import ROOT

# GitHub/connector transports have occasionally stripped only the terminal JPEG EOI
# marker from the checked-in material source sheet. Pillow can safely decode the
# complete scan data in that case; material regression checks still enforce sheet
# dimensions and visual variance before any generated texture is accepted.
ImageFile.LOAD_TRUNCATED_IMAGES=True

GAME=ROOT/'Aegis Reach';MAP=GAME/'Files/mapbank/Aegis Reach - First Light.fpm';STAMP=ROOT/'.local-review/firstlight-build-signature.json'
MATERIAL_SOURCES=(ROOT/'tools/texture_sources/first_light/first_light_material_sources.jpg',)
SOURCES=(
 ROOT/'tools/firstlight_world.py',ROOT/'tools/build_first_light.py',ROOT/'tools/firstlight_combat_geometry.py',
 ROOT/'tools/firstlight_story_effects.py',ROOT/'tools/firstlight_transport.py',ROOT/'tools/firstlight_kestrel.py',
 ROOT/'tools/firstlight_kestrel_boarding.py',ROOT/'tools/firstlight_dialogue.py',ROOT/'tools/firstlight_cinematics.py',ROOT/'tools/firstlight_biosphere.py',
 ROOT/'tools/firstlight_native_engine_pass.py',ROOT/'tools/build_first_light_aaa.py',ROOT/'tools/environment_pass.py',
 ROOT/'tools/meridian_fieldkit.py',ROOT/'tools/build_vesper_sky.py',ROOT/'tools/firstlight_material_polish.py',ROOT/'tools/firstlight_material_contracts.py',
 ROOT/'Aegis Reach/Design/First Light/Sky/vesper-orbital-panorama.png',
 ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_kestrel.lua',
 ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_kestrel_boarding.lua',
 ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_dialogue.lua',
 ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_cinematic.lua',
 *MATERIAL_SOURCES,
)

def digest_sources():
 h=hashlib.sha256()
 for path in SOURCES:h.update(str(path.relative_to(ROOT)).encode());h.update(b'\0');h.update(path.read_bytes());h.update(b'\0')
 # Voice files are optional but adding one must force a rebuild so it gets bound to a marker.
 voice=GAME/'Files/audiobank/aegis_reach/dialogue'
 if voice.is_dir():
  for path in sorted(voice.glob('*.wav')):h.update(path.name.encode());h.update(b'\0');h.update(path.read_bytes());h.update(b'\0')
 return h.hexdigest()
def current_stamp():
 try:return json.loads(STAMP.read_text())
 except Exception:return {}
def main():
 # Generated catalog/timelines are build inputs too. Normalize them before hashing,
 # so a successful build does not immediately report itself stale on the next launch.
 from firstlight_dialogue import sync_catalog
 from firstlight_cinematics import sync_coordinator
 from firstlight_material_polish import apply_material_polish
 from firstlight_material_contracts import enforce_material_contracts
 sync_catalog(GAME/'Files/scriptbank/aegis_reach/firstlight_dialogue.lua')
 sync_coordinator(GAME/'Files/scriptbank/aegis_reach/firstlight_cinematic.lua')
 signature=digest_sources();prior=current_stamp();needed=(not MAP.is_file()) or prior.get('source_sha256')!=signature
 if not needed:
  # Texture outputs are generated assets; restore them if a local cache was cleared
  # even when geometry/story sources are otherwise current.
  apply_material_polish();enforce_material_contracts()
  print('FIRST LIGHT // BUILD CURRENT',signature[:16]);return
 subprocess.run([sys.executable,'-B',str(ROOT/'tools/build_vesper_sky.py')],cwd=ROOT,check=True)
 print('FIRST LIGHT // REBUILD REQUIRED');print('Source signature:',signature[:16])
 subprocess.run([sys.executable,'-B',str(ROOT/'tools/build_first_light_aaa.py')],cwd=ROOT,check=True)
 # Builders own geometry/UVs; material polish intentionally runs last so procedural
 # fallback atlases cannot overwrite the high-detail art pass. Final material
 # contracts then lock engine semantics (for example brineglass remains dielectric).
 apply_material_polish(force=True);enforce_material_contracts()
 STAMP.parent.mkdir(parents=True,exist_ok=True);STAMP.write_text(json.dumps({'source_sha256':signature,'map':str(MAP),'builder':'build_first_light_aaa.py'},indent=2));print('FIRST LIGHT // REBUILD COMPLETE')
if __name__=='__main__':main()
