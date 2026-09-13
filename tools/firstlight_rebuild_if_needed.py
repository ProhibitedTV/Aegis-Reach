"""Rebuild First Light only when its authored world/build sources changed.

The generated .fpm is expensive and ZipCrypto output is non-deterministic, so normal
play should not rebuild on every launch. A local ignored signature records the exact
source inputs used for the current generated map. Fresh checkouts rebuild once.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

from native_format import ROOT

GAME=ROOT/'Aegis Reach'
MAP=GAME/'Files/mapbank/Aegis Reach - First Light.fpm'
STAMP=ROOT/'.local-review/firstlight-build-signature.json'
SOURCES=(
 ROOT/'tools/firstlight_world.py',
 ROOT/'tools/build_first_light.py',
 ROOT/'tools/firstlight_combat_geometry.py',
 ROOT/'tools/build_first_light_aaa.py',
 ROOT/'tools/environment_pass.py',
)


def digest_sources():
 h=hashlib.sha256()
 for path in SOURCES:
  h.update(str(path.relative_to(ROOT)).encode('utf-8'))
  h.update(b'\0')
  h.update(path.read_bytes())
  h.update(b'\0')
 return h.hexdigest()


def current_stamp():
 try:return json.loads(STAMP.read_text())
 except Exception:return {}


def main():
 signature=digest_sources()
 prior=current_stamp()
 needed=(not MAP.is_file()) or prior.get('source_sha256')!=signature
 if not needed:
  print('FIRST LIGHT // BUILD CURRENT',signature[:16])
  return
 print('FIRST LIGHT // REBUILD REQUIRED')
 print('Source signature:',signature[:16])
 subprocess.run([sys.executable,str(ROOT/'tools/build_first_light_aaa.py')],cwd=ROOT,check=True)
 STAMP.parent.mkdir(parents=True,exist_ok=True)
 STAMP.write_text(json.dumps({'source_sha256':signature,'map':str(MAP),'builder':'build_first_light_aaa.py'},indent=2))
 print('FIRST LIGHT // REBUILD COMPLETE')

if __name__=='__main__':main()
