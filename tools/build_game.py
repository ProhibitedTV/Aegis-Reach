"""Rebuild the original Aegis Reach mission and its native MAX assets."""
from native_format import *
from PIL import Image, ImageDraw, ImageFont
import math, copy, json, random, shutil, struct

GAME=ROOT/'Aegis Reach'; FILES=GAME/'Files'; ASSETS=FILES/'entitybank/Aegis Reach'; MAP='Aegis Reach - Relayfall.fpm'
for path in (ASSETS,FILES/'mapbank',FILES/'scriptbank/aegis_reach',FILES/'audiobank/aegis_reach',GAME/'Design'):
 path.mkdir(parents=True,exist_ok=True)
TEMPLATES=json.loads((ROOT/'tools/reference/entity-templates.json').read_text())

PALETTE=[(33,45,58),(61,78,89),(97,121,127),(39,213,231),(245,164,56),(200,216,210),(17,24,37),(159,51,43)]
random.seed(18)
atlas=Image.new('RGB',(1024,128));px=atlas.load()
for x in range(1024):
 for y in range(128):
  c=PALETTE[x//128];noise=random.randint(-3,3);edge=0.65 if x%128<5 or x%128>122 or y<5 or y>122 else 1
  px[x,y]=tuple(max(0,min(255,int(v*edge)+noise)) for v in c)
d=ImageDraw.Draw(atlas)
for i in range(8):
 d.line((i*128+12,18,i*128+114,18),fill=tuple(min(255,c+25) for c in PALETTE[i]),width=2)
 for x,y in ((10,10),(118,10),(10,118),(118,118)):d.ellipse((i*128+x-2,y-2,i*128+x+2,y+2),fill=(16,23,28))
atlas.save(ASSETS/'aegis_atlas.png')

class Mesh:
 def __init__(self):self.verts=[];self.norm=[];self.uv=[];self.faces=[]
 def box(self,x,y,z,w,h,l,color=0,angle=0):
  # Coordinates are inches, with y measured upward from the object's base.
  a=math.radians(angle);co,si=math.cos(a),math.sin(a)
  corners=[(-w/2,0,-l/2),(w/2,0,-l/2),(w/2,h,-l/2),(-w/2,h,-l/2),(-w/2,0,l/2),(w/2,0,l/2),(w/2,h,l/2),(-w/2,h,l/2)]
  for inds,n in [((0,3,2,1),(0,0,-1)),((4,5,6,7),(0,0,1)),((1,2,6,5),(1,0,0)),((0,4,7,3),(-1,0,0)),((3,7,6,2),(0,1,0)),((0,1,5,4),(0,-1,0))]:
   start=len(self.verts)
   for j,idx in enumerate(inds):
    xx,yy,zz=corners[idx];self.verts.append((x+xx*co+zz*si,y+yy,z-xx*si+zz*co))
    self.norm.append((n[0]*co+n[2]*si,n[1],-n[0]*si+n[2]*co))
    u,v=((.07,.93),(.07,.07),(.93,.07),(.93,.93))[j];self.uv.append(((color+u)/8,v))
   self.faces.extend(((start,start+1,start+2),(start,start+2,start+3)))
 def write(self,name,script='no_behavior_selected.lua',collision=1):
  def seq(vals):return ',\n'.join(';'.join(f'{v:.6f}' for v in row)+';' for row in vals)+';'
  faces=',\n'.join('3;'+','.join(map(str,f))+';' for f in self.faces)+';'
  text='xof 0303txt 0032\nMesh AegisMesh {\n'+str(len(self.verts))+';\n'+seq(self.verts)+'\n'+str(len(self.faces))+';\n'+faces
  text+='\nMeshNormals {\n'+str(len(self.norm))+';\n'+seq(self.norm)+'\n'+str(len(self.faces))+';\n'+faces+'\n}\n'
  text+='MeshTextureCoords {\n'+str(len(self.uv))+';\n'+seq(self.uv)+'\n}\n'
  text+='MeshMaterialList {\n1;\n'+str(len(self.faces))+';\n'+','.join('0' for _ in self.faces)+';;\nMaterial {1.0;1.0;1.0;1.0;;32.0;0.2;0.2;0.2;;0.0;0.0;0.0;;TextureFilename {"aegis_atlas.png";} }\n}\n}\n'
  (ASSETS/(name+'.x')).write_text(text)
  (ASSETS/(name+'.fpe')).write_text(f'; Original Aegis Reach modular asset\ndesc = {name}\nmodel = {name}.x\nscale = 100\ntextured = aegis_atlas.png\nbaseColorMap = aegis_atlas.png\neffect = effectbank\\reloaded\\apbr_basic.fx\ncollisionmode = {collision}\nmaterialindex = 2\ndefaultstatic = 1\nstrength = 0\ncastshadow = 1\nroughnessStrength = 0.75\nmetalnessStrength = 0.4\nreflectance = 0.2\nbasecolor = 4294967295\naimain = {script}\n')
  return name

mesh=Mesh()
for x in range(-2000,2001,400):
 for z in range(-2800,3601,400):mesh.box(x,-35,z,400,35,400,0)
mesh.write('Station Deck')
mesh=Mesh();mesh.box(0,0,0,600,390,80,1);mesh.box(0,360,0,630,45,110,6)
for x in (-270,270):mesh.box(x,0,0,65,430,130,2);mesh.box(x,180,-68,18,170,8,3)
mesh.write('Bastion Wall')
mesh=Mesh();mesh.box(0,0,0,240,90,100,1);mesh.box(0,84,0,254,15,116,2);mesh.box(0,34,-52,190,12,4,4);mesh.write('Infantry Cover')
mesh=Mesh();mesh.box(0,0,0,140,110,120,2)
for x in (-55,55):mesh.box(x,0,0,12,115,128,6)
mesh.box(0,40,-61,70,20,4,4);mesh.write('Supply Crate')
mesh=Mesh();mesh.box(0,0,0,120,25,120,6);mesh.box(0,25,0,70,135,65,2);mesh.box(0,148,-5,126,65,90,1);mesh.box(0,168,-52,100,32,5,3);mesh.box(-46,214,0,12,120,12,3);mesh.box(46,214,0,12,120,12,3);mesh.write('Relay Terminal',r'aegis_reach\aegis_relay.lua')
mesh=Mesh();mesh.box(0,0,0,300,65,300,6);mesh.box(0,65,0,210,470,210,1);mesh.box(0,130,-110,150,330,10,3)
for x in (-145,145):mesh.box(x,0,0,55,750,65,2);mesh.box(x,580,0,25,210,28,3)
mesh.box(0,600,0,400,75,90,2);mesh.write('Signal Spire')
mesh=Mesh();mesh.box(0,0,0,680,15,540,2)
for x in (-320,320):mesh.box(x,15,0,18,12,530,3)
for z in (-250,250):mesh.box(0,15,z,640,12,18,3)
mesh.box(0,16,0,36,4,180,5);mesh.box(0,16,0,180,4,36,5);mesh.write('Extraction Pad',r'aegis_reach\aegis_extract.lua')
mesh=Mesh();mesh.box(0,0,0,700,240,700,6);mesh.box(0,230,0,740,28,740,2);mesh.box(0,258,0,600,170,560,1);mesh.box(0,300,-286,450,50,14,3);mesh.write('Relay Bunker')
# Vast broken antenna arc: original architecture; not a recreation of Halo's ringworld.
mesh=Mesh()
for i in range(21):
 a=math.radians(-75+i*7.5);x=math.sin(a)*800;y=math.cos(a)*800
 mesh.box(x,y,0,125,90,110,2,angle=-i*7.5)
mesh.write('Orbital Antenna Arc')

entities=[];bank=[];layout=[]
static_template=next(e for p,e in TEMPLATES.items() if 'Warehouse - Red Grey' in p)
def add(path,name,x,z,y=600,ry=0,kind='scenery',**params):
 base=copy.deepcopy(TEMPLATES.get(path,static_template))
 for k in list(base):
  if k.startswith(('319:','334:')) or 'ObjectRelationships' in k:base[k]='' if isinstance(base[k],str) else 0
 for k in ('310:eleprof.parententityindex','310:eleprof.parentlimbindex','312:iHasParentIndex','335:creationOfGroupID','329:quatmode','330:eleprof.bAutoFlatten'):base[k]=0
 base['329:quatw']=1.0
 if path.startswith('Aegis Reach'):
  for k in list(base):
   if k.startswith('material'):base[k]='' if isinstance(base[k],str) else 0
  base.update({'314:custom':0,'314:active':0,'101:eleprof.texd_s':'aegis_atlas.png','101:eleprof.effect_s':r'effectbank\reloaded\apbr_basic.fx','101:eleprof.aimain_s':'no_behavior_selected.lua','101:eleprof.strength':0,'101:eleprof.transparency':0,'101:staticflag':1,'101:eleprof.scale':100.0,'305:scalex':0.0,'305:scaley':0.0,'305:scalez':0.0,'103:eleprof.physics':1,'101:eleprof.isimmobile':1,'310:eleprof.soundset4_s':''})
 if path not in bank:bank.append(path)
 base.update({'101:maintype':1,'101:bankindex':bank.index(path)+1,'101:x':float(x),'101:y':float(y),'101:z':float(z),'101:rx':0.0,'101:ry':float(ry),'101:rz':0.0,'101:eleprof.name_s':name})
 for k,v in params.items():
  keys=[key for key in base if key.split(':',1)[-1]==k]
  if not keys:raise KeyError(k)
  for key in keys:base[key]=v
 entities.append(base);layout.append({'id':len(entities),'name':name,'kind':kind,'x':x,'y':y,'z':z,'rotation':ry,'asset':path})
 return base
def custom(asset,name,x,z,**kw):return add('Aegis Reach\\'+asset+'.fpe',name,x,z,**kw)
custom('Station Deck','REACH // Fortress foundation',0,0)
# Perimeter: overlapping segments close every boundary, while internal gates stay wide.
for z in range(-2900,3701,550):
 for x in (-2150,2150):custom('Bastion Wall','Perimeter bastion',x,z,ry=90)
for x in range(-1900,2001,550):
 for z in (-2960,3760):custom('Bastion Wall','Perimeter bastion',x,z)
for z,centers in [(-1650,[-1850,-1250,0,1250,1850]),(200,[-1850,-1250,0,1250,1850]),(1950,[-1850,-1250,0,1250,1850])]:
 for x in centers:custom('Bastion Wall','Blast wall / flank gates',x,z)
for x,z in [(-950,-2550),(800,-2450),(-1300,-2100),(250,-2080),(-1500,-900),(650,-950),(-200,-450),(1400,-220),(-1200,720),(200,820),(1300,1350),(-550,1460),(-1400,2580),(450,2380),(1250,3020)]:
 custom('Infantry Cover','Infantry hard cover',x,z,kind='cover')
for x,z in [(-700,-2700),(-650,-2600),(1100,-1100),(1250,-1000),(-1350,1000),(-1200,900),(700,2820),(850,2840)]:custom('Supply Crate','Supply cache',x,z,kind='cover')
for x,z in [(-1550,-520),(1550,1150),(-1450,2900)]:custom('Relay Bunker','Command enclosure',x,z)
for x,z in [(-1500,-2650),(1550,-1500),(-1600,400),(1600,2300),(-750,3330),(750,3330)]:custom('Signal Spire','AEGIS array mast',x,z)
custom('Orbital Antenna Arc','Broken orbital antenna',0,3600,y=1150)

player=add(r'_markers\Player Start.fpe','Vanguard 7 // insertion',0,-2700,y=645,kind='player',**{'eleprof.strength':200,'eleprof.hasweapon_s':r'enhanced\MK18','eleprof.quantity':180,'eleprof.lives':1,'eleprof.speed':115,'eleprof.hurtfall':100,'eleprof.aimain_s':'no_behavior_selected.lua'})
controller=custom('Supply Crate','AEGIS MISSION CONTROLLER',-1900,-2950,kind='controller',**{'staticflag':0,'eleprof.aimain_s':r'aegis_reach\aegis_director.lua','eleprof.phyalways':1,'eleprof.soundset_s':r'audiobank\aegis_reach\briefing.wav','eleprof.soundset1_s':r'audiobank\aegis_reach\reach-underscore.wav'})
for i,(x,z,label) in enumerate([(-700,-1100,'NORTHSTAR'),(800,850,'LANTERN'),(0,2870,'AEGIS CORE')],1):
 custom('Relay Terminal',f'RELAY {i} // {label}',x,z,kind='relay',**{'staticflag':0,'eleprof.aimain_s':r'aegis_reach\aegis_relay.lua','eleprof.phyalways':1,'eleprof.soundset_s':r'audiobank\aegis_reach\relay.wav'})
custom('Extraction Pad','EXTRACT // Kestrel landing zone',0,-2510,kind='extraction',**{'staticflag':0,'eleprof.aimain_s':r'aegis_reach\aegis_extract.lua','eleprof.phyalways':1})
custom('Supply Crate','FIELD REPAIR // 75 armour',700,700,kind='medical',**{'staticflag':0,'eleprof.aimain_s':r'aegis_reach\aegis_medical.lua','eleprof.phyalways':1})

enemy_positions=[(-800,-2130),(880,-2010),(-900,-680),(600,-690),(1450,-470),(-720,630),(450,1120),(1480,1570),(-1450,2230),(650,2530),(-400,3290),(950,3410)]
for i,(x,z) in enumerate(enemy_positions,1):
 add(r'Characters\Tony - Armed Response.fpe',f'IRON WARDEN {i:02}',x,z,y=605,ry=180,kind='enemy',**{'eleprof.strength':100 if i<9 else 150,'eleprof.hasweapon_s':r'enhanced\MK18' if i%3 else r'enhanced\AR','eleprof.quantity':30,'eleprof.damage':8,'eleprof.accuracy':140,'eleprof.conerange':1100.0,'eleprof.weapondamagemultiplier':0.3,'eleprof.aimain_s':r'aegis_reach\aegis_enemy.lua','eleprof.soundset4_s':'','eleprof.phyalways':1})
for i,(x,z) in enumerate([(-950,2520),(950,2520),(-700,-1850),(700,-1850)],1):
 add(r'Characters\Tony - Armed Response.fpe',f'RESERVE {i:02}',x,z,y=605,ry=180,kind='reserve',**{'eleprof.strength':130,'eleprof.hasweapon_s':r'enhanced\AR','eleprof.damage':8,'eleprof.accuracy':120,'eleprof.weapondamagemultiplier':0.3,'eleprof.aimain_s':r'aegis_reach\aegis_enemy.lua','eleprof.soundset4_s':'','eleprof.phyalways':1})

for i,(x,z) in enumerate([(-420,-2590),(950,-1000),(-1030,850),(480,2800)],1):
 add(r'Max Collection\Weapons\Compact Assault Rifle Ammo.fpe',f'MK18 ammunition {i}',x,z,y=630,kind='ammo',**{'eleprof.quantity':90,'eleprof.hasweapon_s':r'enhanced\MK18'})
add(r'Max Collection\Weapons\Tactical Pump Shotgun.fpe','Breach shotgun',900,-1130,y=630,kind='weapon',**{'eleprof.quantity':24})
add(r'Max Collection\Weapons\Patrol Rifle.fpe','Marksman rifle',-1130,1050,y=630,kind='weapon',**{'eleprof.quantity':60})
for x,z in [(-380,-2570),(-340,-2570),(940,-1130),(-1090,1050)]:add(r'Max Collection\Weapons\Frag Grenade.fpe','Fragmentation grenade',x,z,y=630,kind='weapon',**{'eleprof.quantity':2})
for i,(x,z) in enumerate([(0,-2350),(-700,-1050),(800,900),(0,2880),(-1500,3000),(1500,1600)],1):
 add(r'_markers\White Light.fpe',f'Relay illumination {i}',x,z,y=880,kind='light',**{'eleprof.light.color':0x59CEE8 if i%2 else 0xFFAE56,'eleprof.light.range':1050,'eleprof.light.index':i,'eleprof.light.fLightHasProbe':1,'eleprof.soundset4_s':''})

z,version,_,_=read_map('switch escape.fpm')
ele=write_ele(version,entities);assert write_ele(version,read_ele(ele)[1])==ele
cfg=z.read('cfg.cfg').replace(b'mapbank\\switch escape.fpm',('mapbank\\'+MAP).encode())
# Native editor camera fields, retaining format revision V2.
cfg=bytearray(cfg);struct.pack_into('<fff',cfg,0,10,-4800,20)
if b'V2\r\n' in cfg:
 off=cfg.index(b'V2\r\n')+8;struct.pack_into('<fffffff',cfg,off,10,3500,-4800,10,-4800,37,0)
visuals=z.read('visuals.ini').decode('latin1')
settings={'SunIntensity':1.1,'SunRed':.75,'SunGreen':.88,'SunBlue':1.0,'ZenithRed':17,'ZenithGreen':30,'ZenithBlue':54,'Exposure':1.0,'CameraFOV#':65,'WeaponFOV#':55,'Waterheight':-10000,'VegQuantity#':0,'MotionIntensity#':0,'FogNearest#':9000,'FogDistance#':40000,'FogR#':25,'FogG#':45,'FogB#':68,'BloomStrength':.35,'LevelVSyncEnabled':1}
for k,v in settings.items():visuals=re.sub(r'(visuals\.'+re.escape(k)+r'=)[^\r\n]*',lambda m:m[1]+str(v),visuals)
pc=bytearray(z.read('playerconfig.dat'));struct.pack_into('<fff',pc,45,0,100,6000) # script owns shield regeneration
with zipfile.ZipFile(FILES/'mapbank'/MAP,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
 for info in z.infolist():
  name=info.filename
  if name in ('map.ele','map.ent','cfg.cfg','map.way','visuals.ini','locked.cfg','playerconfig.dat'):continue
  out.writestr(name,z.read(name))
 out.writestr('map.ele',ele);out.writestr('map.ent',struct.pack('<i',len(bank))+('\r\n'.join(bank)+'\r\n').encode())
 out.writestr('cfg.cfg',cfg);out.writestr('map.way',struct.pack('<ii',0,0));out.writestr('locked.cfg',struct.pack('<i',0))
 out.writestr('visuals.ini',visuals);out.writestr('playerconfig.dat',pc)

from max_archive import convert
convert(FILES/'mapbank'/MAP)
(GAME/'Design/mission-layout.json').write_text(json.dumps(layout,indent=2))
(GAME/'Design/asset-manifest.json').write_text(json.dumps({'original_assets':[p.name for p in ASSETS.glob('*.fpe')],'stock_entities':bank,'map_version':version,'entities':len(entities)},indent=2))
print('Built',FILES/'mapbank'/MAP,'with',len(entities),'entities,',len(bank),'asset types')
