"""Copy this mission's stock dependencies from the user's licensed MAX install."""
from native_format import *
import json,shutil,re
FILES=ROOT/'Aegis Reach/Files';manifest=json.loads((ROOT/'Aegis Reach/Design/asset-manifest.json').read_text())
copied=[];missing=[]
def copyfile(src):
 if not src.is_file():return False
 rel=src.relative_to(INSTALL);dst=FILES/rel
 if not dst.exists():
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);copied.append(str(rel))
 return True
def copydir(rel):
 for p in (INSTALL/rel).rglob('*'):
  if p.is_file():copyfile(p)
for rel in ('scriptbank','audiobank/characters/human/male','gamecore/ammo/enhanced','gamecore/guns/enhanced/Mk18','gamecore/guns/enhanced/AR','gamecore/guns/enhanced/R870','gamecore/guns/enhanced/M67','gamecore/guns/enhanced/Gloves_Unarmed','gamecore/guns/enhanced/AK','gamecore/guns/enhanced/Mk19T'):
 copydir(rel)
for path in manifest['stock_entities']:
 if path.startswith('Aegis Reach'):continue
 src=INSTALL/'entitybank'/path
 if not copyfile(src):missing.append(path);continue
 for p in src.parent.glob(src.stem+'*'):copyfile(p)
 for line in src.read_text(errors='replace').splitlines():
  if '=' not in line or line.lstrip().startswith(';'):continue
  key,val=map(str.strip,line.split('=',1));val=val.replace('\\','/')
  if not re.search(r'\.(x|dbo|png|dds|wav|ogg|lua|fx|fbx)$',val,re.I):continue
  if copyfile(INSTALL/val):continue
  if copyfile(src.parent/val):continue
  if key.lower() in ('aimain','aiinit','aidestroy') and (FILES/'scriptbank'/val).is_file():continue
  if key.lower().startswith('thumbnail'):continue
  if val.lower().endswith('.x') and (FILES/Path(val).with_suffix('.dbo')).is_file():continue
  if val.lower().startswith('effectbank/reloaded/') and val.endswith('.fx'):continue # MAX's built-in shader identifiers
  # Character Creator runtime resolves a baked body atlas from the character stem.
  if val.startswith('tempfinalalbedo'):continue
  missing.append(path+' -> '+val)
# Maps retain optional material overrides; copy their referenced texture files too.
templates=json.loads((ROOT/'tools/reference/entity-templates.json').read_text())
for path in manifest['stock_entities']:
 for k,v in templates.get(path,{}).items():
  if isinstance(v,str) and re.search(r'\.(png|dds|wav|ogg|dbo|x)$',v,re.I):
   copyfile(INSTALL/v)
(ROOT/'Aegis Reach/Design/staged-assets.json').write_text(json.dumps({'copied':copied,'unresolved':missing},indent=2))
print('Staged',len(copied),'dependencies; unresolved:',missing)
