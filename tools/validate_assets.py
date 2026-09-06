from pathlib import Path
import ctypes as C,json,zipfile,sys,struct
from native_format import ROOT,INSTALL,read_ele,write_ele
FILES=ROOT/'Aegis Reach/Files'
dll=C.CDLL(str(INSTALL.parent/'assimp.dll'))
dll.aiImportFile.argtypes=[C.c_char_p,C.c_uint];dll.aiImportFile.restype=C.c_void_p
dll.aiReleaseImport.argtypes=[C.c_void_p];dll.aiGetErrorString.restype=C.c_char_p
checks=[]
for file in (FILES/'entitybank/Aegis Reach').glob('*.x'):
 ptr=dll.aiImportFile(str(file).encode(),0x8)
 assert ptr,(file,dll.aiGetErrorString())
 dll.aiReleaseImport(ptr);checks.append(file.name+' imports through installed Assimp')
for p in (FILES/'mapbank').glob('*.fpm'):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  v,es=read_ele(z.read('map.ele'));assert write_ele(v,es)==z.read('map.ele')
  bank=z.read('map.ent')[4:].decode().splitlines()
  for b in bank:assert (FILES/'entitybank'/b).is_file(),b
  for e in es:
   script=e['101:eleprof.aimain_s']
   if script and script!='no_behavior_selected.lua':assert (FILES/'scriptbank'/script).is_file(),script
   for key in ('101:eleprof.soundset_s','101:eleprof.soundset1_s','310:eleprof.soundset2_s','310:eleprof.soundset3_s'):
    val=e[key]
    if val and val.lower().endswith(('.wav','.ogg')):assert (FILES/val).is_file(),val
  checks.append(f'{p.name}: {len(es)} entities, all map asset/script/audio references present, archive CRC and entity roundtrip valid')
report={'checks':checks,'engine_import_library':'installed GameGuru MAX assimp.dll','in_engine_playtest':False}
(ROOT/'Aegis Reach/Design/asset-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
