import json,struct,re
from native_format import *
out={}
for name in ('switch escape.fpm','Disruption.fpm'):
 z,v,es,bank=read_map(name)
 for e in es:
  path=bank[e['101:bankindex']]
  if path and path not in out and e['101:maintype']:
   out[path]=e
(ROOT/'tools/reference/entity-templates.json').write_text(json.dumps(out,indent=2))
for p,e in out.items():
 if any(k in p for k in ('Player Start','Tony -','Compact Assault Rifle.fpe','White Light','Behavior')):
  print(p,json.dumps({k:v for k,v in e.items() if not k.startswith(('material','334:','319:')) and v not in (0,'')},indent=1))
z,_,_,_=read_map('switch escape.fpm')
for name in ('cfg.cfg','header.dat','playerconfig.dat','ggterrain.dat','map.way'):
 d=z.read(name);print(name,len(d),repr(d[:400]))
print(z.read('visuals.ini').decode('latin1')[:3500])
for project in ('Switch Escape','River Raiders'):
 p=INSTALL/'projectbank'/project/'project.dat';d=p.read_bytes()
 print(project,len(d),'version',struct.unpack_from('<i',d,268))
 print([(m.start(),m[0].decode('latin1')) for m in re.finditer(rb'[ -~]{6,}',d)][:60])
