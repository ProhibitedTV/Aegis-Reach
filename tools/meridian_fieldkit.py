"""Original Meridian field-lab shell and practical mast; no licensed source meshes.

MAX inches, front faces local -Z. No ground slab: native terrain remains the floor.
"""
from pathlib import Path
import math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter

NAME='Meridian Field Lab'
ATLAS='meridian_fieldkit.png'
EMISSION='meridian_fieldkit_emission.png'

NORMAL='meridian_fieldkit_normal.png'
SURFACE='meridian_fieldkit_surface.png'
TILE=512


def textures(folder):
 """Original coordinated albedo/normal/ORM atlases; no licensed image inputs.

 MAX surface packing: R occlusion, G roughness, B metalness, A reflectance.
 R and A remain neutral; cavity shading is not substituted for baked lighting.
 UV islands sample .07.. .93 of each tile: authored details must live inside it.
 """
 rng=random.Random(1207)
 colors=[(172,174,166),(33,42,47),(79,91,95),(47,77,81),(245,202,133),(83,158,172),(166,171,165),(51,66,71)]
 roughness=(189,201,132,170,105,112,184,174)
 metalness=(0,0,210,0,0,0,0,0)
 atlas=Image.new('RGB',(8*TILE,TILE))
 normals=Image.new('RGB',atlas.size,(128,128,255))
 surfaces=Image.new('RGBA',atlas.size,(255,255,0,255))
 emission=Image.new('RGB',atlas.size)
 scale=TILE/256
 def coords(values):return tuple(round(v*scale) for v in values)
 def font(size):return ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',round(size*scale))
 for tile,color in enumerate(colors):
  albedo=Image.new('RGB',(TILE,TILE),color);d=ImageDraw.Draw(albedo)
  height=Image.new('L',albedo.size,128);hd=ImageDraw.Draw(height)
  surface=Image.new('RGBA',albedo.size,(255,roughness[tile],metalness[tile],255));sd=ImageDraw.Draw(surface)
  if tile not in (4,5):
   for _ in range(26000):
    x=rng.randrange(TILE);y=rng.randrange(TILE);n=rng.randrange(-6,7)
    d.point((x,y),fill=tuple(max(0,min(255,c+n)) for c in color))
    sd.point((x,y),fill=(255,roughness[tile]+n,metalness[tile],255))
   # The old seams at 5/250 and rivets at 14/241 were clipped by the UVs.
   seam=coords((23,23,232,232))
   d.rectangle(seam,outline=tuple(int(c*.68) for c in color),width=3)
   hd.rectangle(seam,outline=116,width=3)
   sd.rectangle(seam,outline=(255,220,metalness[tile],255),width=3)
   for _ in range(180):
    x=rng.randrange(27,229);y=rng.choice((rng.randrange(24,29),rng.randrange(227,232)))
    line=coords((x,y,min(230,x+rng.randrange(1,4)),y))
    d.line(line,fill=tuple(int(c*.76) for c in color),width=1)
    sd.line(line,fill=(255,156,max(80,metalness[tile]),255),width=1)
   if tile in (0,3,6):
    for x in (32,223):
     for y in (32,223):
      circle=coords((x-2,y-2,x+2,y+2))
      d.ellipse(circle,fill=(69,78,80));hd.ellipse(circle,fill=146)
      sd.ellipse(circle,fill=(255,140,200,255))
      d.line(coords((x-1,y,x+1,y)),fill=(29,37,40),width=1)
  if tile==6:
   d.polygon(coords((126,40,166,102,151,102,126,63,101,102,86,102)),fill=(31,60,65))
   d.text(coords((39,113)),'MERIDIAN',font=font(29),fill=(26,49,54))
   d.text(coords((30,153)),'SURVEY CAMP 12',font=font(17),fill=(30,52,58))
   d.text(coords((41,186)),'GEOLOGY / FIELD LAB',font=font(13),fill=(44,62,67))
  if tile==7:
   d.text(coords((35,37)),'M-12',font=font(29),fill=(190,199,191))
   d.text(coords((35,90)),'POWER / DATA',font=font(17),fill=(149,172,172))
   for y in range(145,216,14):
    line=coords((35,y,221,y))
    d.line(line,fill=(20,29,34),width=6)
    hd.line(line,fill=116,width=6)
    sd.line(line,fill=(255,213,0,255),width=6)
  # Height comes from physical seams and fasteners. Printed words stay flat.
  normal=Image.new('RGB',albedo.size,(128,128,255))
  if tile not in (4,5):
   hp=height.filter(ImageFilter.GaussianBlur(1.2)).load();np=normal.load()
   for y in range(1,TILE-1):
    for x in range(1,TILE-1):
     nx=-(hp[x+1,y]-hp[x-1,y])*.04
     ny=-(hp[x,y+1]-hp[x,y-1])*.04
     length=math.sqrt(nx*nx+ny*ny+1)
     np[x,y]=(round(127.5+127.5*nx/length),round(127.5+127.5*ny/length),round(127.5+127.5/length))
  atlas.paste(albedo,(tile*TILE,0));normals.paste(normal,(tile*TILE,0));surfaces.paste(surface,(tile*TILE,0))
  if tile in (4,5):
   emission.paste((255,193,104) if tile==4 else (25,96,113),(tile*TILE,0,(tile+1)*TILE,TILE))
 for name,im in ((ATLAS,atlas),(EMISSION,emission),(NORMAL,normals),(SURFACE,surfaces)):
  im.save(folder/name,optimize=True)

def quad(m,vs,tile):
 a,b,c=vs[:3];u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
 n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
 length=math.sqrt(sum(x*x for x in n));assert length>1e-8
 start=len(m.verts)
 for p,uv in zip(vs,((.07,.93),(.07,.07),(.93,.07),(.93,.93))):
  m.verts.append(p);m.norm.append(tuple(x/length for x in n));m.uv.append(((tile+uv[0])/8,uv[1]))
 m.faces.extend(((start,start+1,start+2),(start,start+2,start+3)))

def strut(m,a,b,width,tile=2):
 direction=[b[i]-a[i] for i in range(3)];length=math.sqrt(sum(v*v for v in direction));direction=[v/length for v in direction]
 ref=(0,1,0) if abs(direction[1])<.9 else (1,0,0)
 u=[direction[1]*ref[2]-direction[2]*ref[1],direction[2]*ref[0]-direction[0]*ref[2],direction[0]*ref[1]-direction[1]*ref[0]]
 l=math.sqrt(sum(v*v for v in u));u=[v/l*width/2 for v in u]
 v=[direction[1]*u[2]-direction[2]*u[1],direction[2]*u[0]-direction[0]*u[2],direction[0]*u[1]-direction[1]*u[0]]
 corners=[]
 for p in (a,b):
  for su,sv in ((-1,-1),(-1,1),(1,1),(1,-1)):corners.append(tuple(p[i]+su*u[i]+sv*v[i] for i in range(3)))
 for ids in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
  quad(m,[corners[i] for i in ids],tile)

def comms_dish(m):
 """2.44m parabolic dish on the lab roof; paired skins and a physical feed arm."""
 axis=(0,.6,-.8);centre=(80,205,15)
 def point(r,t,back=0):
  return (centre[0]+r*math.cos(t),centre[1]+r*math.sin(t)*.8+(.6)*(14*(r/48)**2-back),
          centre[2]+r*math.sin(t)*.6+(-.8)*(14*(r/48)**2-back))
 m.box(80,148,15,42,5,44,1)
 strut(m,(80,153,15),(80,204,15),12,2)
 m.box(80,197,15,20,14,20,1)
 for j in range(24):
  a=j*math.tau/24;b=(j+1)*math.tau/24
  for r0,r1 in ((8,22),(22,36),(36,48)):
   quad(m,[point(r0,a),point(r0,b),point(r1,b),point(r1,a)],0)
   quad(m,[point(r0,a,2),point(r1,a,2),point(r1,b,2),point(r0,b,2)],1)
  quad(m,[point(48,a),point(48,b),point(48,b,2),point(48,a,2)],2)
  if j%6==0:strut(m,point(8,a,3),point(48,a,3),2,2)
 feed=(80,230.2,-18.6)
 for t in (math.pi*7/6,math.pi*11/6):strut(m,point(48,t),feed,2,2)
 m.box(feed[0],feed[1]-4,feed[2],10,8,12,3)

def field_work_bay(m):
 """An attached, sheltered work bay; its middle/right remains a clear entrance."""
 # Roof bolts into the facade, with front posts outside the door's sightline.
 m.box(0,128,-190,388,6,124,0)
 m.box(0,121,-248,388,7,8,2)
 for x in (-185,185):
  m.box(x,0,-244,8,121,8,2)
  m.box(x,0,-244,18,3,18,1)
  m.box(x,121,-188,8,7,112,2)
  strut(m,(x,96,-244),(x,121,-214),5,2)
 # A half-height side screen protects the bench without closing the court.
 m.box(-185,4,-190,5,58,100,0)
 m.box(-185,62,-190,7,4,102,2)
 # Compact sample workstation, low enough to keep the technical window visible.
 for x in (-144,-54):m.box(x,0,-185,7,32,28,2)
 m.box(-99,32,-185,112,3,38,2)
 m.box(-99,9,-185,82,20,28,0)
 for x in (-120,-78):
  m.box(x,12,-200,38,13,2,1)
  m.box(x,20,-202,16,2,2,2)
 m.box(-116,35,-183,38,12,22,1) # closed specimen transport case
 for x in (-130,-102):m.box(x,38,-195,3,6,2,2)
 m.box(-68,35,-183,23,4,25,3) # bench instrument, with a restrained status bar
 m.box(-68,39,-184,19,9,5,1)
 m.box(-68,42,-187,14,3,1,5)
 # Housing touches the roof underside; the practical lights the occupied bay.
 m.box(-92,124,-204,110,4,14,1)
 m.box(-92,122,-204,100,2,8,4)


def utility_spine(Mesh):
 """Two low feeds attached to the lab side panels, in camp-relative inches.

 Origin is the lab centre (-2350,-7270), unrotated. All runs stay on the flat
 native pad, outside the doorway and vehicle lane. No replacement floor.
 """
 m=Mesh()
 for points,terminal_z in [([(140,-255),(50,-255),(50,-216)],-214),
                            ([(205,310),(50,310),(50,214)],214)]:
  for (x,z),(xx,zz) in zip(points,points[1:]):
   strut(m,(x,3,z),(xx,3,zz),6,1)
  x,z=points[-1]
  strut(m,(x,3,z),(x,41,z),5,2)
  m.box(x,25,terminal_z,26,28,8,0)
  m.box(x,29,terminal_z+(-5 if terminal_z<0 else 5),18,17,2,3)
 return m


def shell(Mesh,comms=True):
 m=Mesh()
 # 10.67 x 6.60m transportable shell; 3.76m tall with a chamfered crown.
 # Curved-looking faceted roof has thickness and an interior ceiling.
 profile=[(-210,0),(-210,113),(-198,136),(-176,148),(176,148),(198,136),(210,113),(210,0)]
 inner=[(-202,0),(-202,111),(-192,130),(-174,140),(174,140),(192,130),(202,111),(202,0)]
 for j in range(7):
  x1,y1=profile[j];x2,y2=profile[j+1]
  a,b=inner[j],inner[j+1]
  quad(m,[(x1,y1,-130),(x1,y1,130),(x2,y2,130),(x2,y2,-130)],0)
  quad(m,[(a[0],a[1],-123),(b[0],b[1],-123),(b[0],b[1],123),(a[0],a[1],123)],0)
 # End walls are panels. Front opening X 22..122, Y 0..101 is genuinely empty.
 for x,w in [(-99,222),(166,88)]:m.box(x,0,-126,w,113,8,0)
 m.box(72,101,-126,100,12,8,0)
 m.box(0,0,126,404,113,8,0)
 # End panels have distinct outer and inner faces. A single outward-facing
 # triangle fan disappears from inside the lab under ordinary backface culling.
 cap=[(-210,113),(-198,136),(-176,148),(176,148),(198,136),(210,113)]
 # Clip the inner roof profile at the existing end wall's 113-inch top so the
 # panels meet edge-to-edge instead of overlapping on a coplanar strip.
 inner_edge=202-(113-111)*(202-192)/(130-111)
 inside_cap=[(-inner_edge,113),(-192,130),(-174,140),(174,140),(192,130),(inner_edge,113)]
 for side in (-1,1):
  for polygon,z,nz in ((cap,side*130,side),(inside_cap,side*122,-side)):
   for i in range(1,len(polygon)-1):
    vs=[(polygon[j][0],polygon[j][1],z) for j in (0,i,i+1)]
    if nz>0:vs.reverse()
    start=len(m.verts)
    for point in vs:
     m.verts.append(point);m.norm.append((0,0,nz))
     # Nonzero UV area is required for a stable normal-map tangent frame.
     m.uv.append(((.07+.86*(point[0]+210)/420)/8,.93-.86*(point[1]-113)/35))
    m.faces.append((start,start+1,start+2))
 # Structural ribs, spaced seams and low wear rails break up the broad ivory mass.
 for z in (-132,-66,0,66,132):
  for a,b in zip(profile,profile[1:]):strut(m,(a[0],a[1]+1,z),(b[0],b[1]+1,z),5,2)
 for x in (-214,214):
  m.box(x,13,0,6,9,264,1)
  for z in (-100,100):m.box(x,0,z,14,12,23,2)
 # Recessed entrance jambs, header and short weather visor. No raised floor/step.
 for x in (17,127):m.box(x,0,-134,10,107,18,2)
 m.box(72,101,-134,120,9,18,2)
 m.box(72,112,-147,132,6,40,1)
 m.box(72,109,-150,82,2.5,5,4)
 # Transport hinges / latches and two roof service boxes, not loose scatter.
 for x in (-195,195):
  for y in (25,78):m.box(x,y,-133,7,14,6,2)
 m.box(-80,149,25,96,18,72,1)
 m.box(-80,168,25,80,3,58,3)
 for x in range(-115,-39,12):m.box(x,171,25,2,1,52,2)
 # Inset technical pane and a broad identifier panel next to the entrance.
 m.box(-124,61,-133,110,37,5,1)
 m.box(-124,64,-136,99,29,2,3)
 m.box(-124,93,-138,66,1.2,2,5)
 m.box(-99,12,-133,104,45,3,6)
 # Interior equipment backing and ceiling practical strip.
 m.box(-140,26,119,85,55,4,7)
 m.box(10,137,0,148,3,12,1) # housing meets the 140-inch interior ceiling
 m.box(10,135,0,140,2,7,4)
 if comms:
  comms_dish(m)
  field_work_bay(m)
 return m

def mast(Mesh):
 m=Mesh();legs=[(-15,-12),(15,-12),(0,16)]
 for x,z in legs:strut(m,(x,0,z),(x,272,z),3,2)
 for y in range(0,264,44):
  for i,(x,z) in enumerate(legs):
   xx,zz=legs[(i+1)%3]
   strut(m,(x,y,z),(xx,y+44,zz),2,2)
   strut(m,(x,y,z),(xx,y,zz),2,1)
 m.box(0,0,0,46,6,46,1)
 m.box(0,210,0,83,5,15,2)
 for x in (-32,32):
  m.box(x,205,-3,21,14,10,1);m.box(x,207,-9,17,9,2,4)
 strut(m,(0,272,0),(0,345,0),2,2)
 # Compact radio panels attach to the existing truss, above the work lights.
 for x in (-22,22):
  strut(m,(0,248,0),(x,248,0),3,2)
  m.box(x,229,-4,10,39,8,0)
  m.box(x,233,-8.5,5,4,1,5)
 return m

def power_station(Mesh):
 """Grounded machinery enclosure with two exhaust towers, not an empty arch."""
 m=Mesh()
 m.box(0,0,0,560,16,300,1)
 m.box(0,16,0,544,176,284,0)
 m.box(0,192,0,568,14,304,1)
 for x in (-268,-134,0,134,268):m.box(x,16,-145,7,176,7,2)
 for x in (-193,193):
  m.box(x,44,-148,90,84,5,7)
  m.box(x,156,-152,64,8,8,1);m.box(x,158,-157,54,4,2,4)
 for x in (-140,140):
  # Faceted cylinders have continuous sides; recessed dark caps read as vents.
  for j in range(20):
   a=j*math.tau/20;b=(j+1)*math.tau/20
   for radius,y,h,tile in ((47,206,136,2),(53,329,12,1)):
    quad(m,[(x+radius*math.cos(a),y,radius*math.sin(a)),
            (x+radius*math.cos(a),y+h,radius*math.sin(a)),
            (x+radius*math.cos(b),y+h,radius*math.sin(b)),
            (x+radius*math.cos(b),y,radius*math.sin(b))],tile)
  m.box(x,314,0,61,4,61,1)
 # Two low feeder conduits join the west generator cluster to the plant.
 for x in (-210,-145):
  strut(m,(x,10,-550),(x,10,-154),6,2)
  strut(m,(x,10,-154),(x,65,-154),6,2)
 return m

def control_console(Mesh):
 """Standing-height sealed workstation, maximum height 65 inches."""
 m=Mesh()
 m.box(0,0,0,44,5,38,2)
 m.box(0,5,0,22,30,24,0)
 m.box(0,35,0,50,6,38,1)
 quad(m,[(-25,41,-20),(-25,65,9),(25,65,9),(25,41,-20)],1)
 quad(m,[(-21,44,-17),(-21,62,5),(21,62,5),(21,44,-17)],3)
 m.box(0,41,-22,40,2,5,2)
 for x in (-12,0,12):m.box(x,43,-22,7,1,3,5)
 # Rear enclosure physically supports the sloped display.
 m.box(0,41,11,50,24,6,0)
 for x in (-24,24):
  side=[(x,41,-20),(x,41,11),(x,65,11),(x,65,9)]
  if x>0:side.reverse()
  quad(m,side,2)
 return m


def service_link(Mesh):
 """Covered connection between two field modules, without a floor slab."""
 m=Mesh();m.box(0,128,0,345,7,120,0)
 for z in (-56,56):m.box(0,121,z,345,7,8,2)
 for x in (-162.5,162.5):
  for z in (-50,50):
   m.box(x,0,z,8,121,8,2);m.box(x,0,z,18,3,18,1)
 m.box(0,124,0,100,4,12,1);m.box(0,122,0,90,2,8,4)
 return m


def array_equipment(Mesh):
 """Paired grounded relay cabinets with antenna spines; no giant empty frame."""
 m=Mesh()
 for x in (-450,450):
  m.box(x,0,0,156,12,176,2)
  m.box(x,12,0,140,168,160,0)
  m.box(x,180,0,152,10,172,1)
  m.box(x,28,-82,94,100,5,7)
  for xx in (-56,56):m.box(x+xx,12,-83,6,168,7,2)
  m.box(x,146,-85,88,6,7,1);m.box(x,147,-90,74,3,2,5)
  m.box(x,190,0,28,150,34,2)
  m.box(x,215,-19,8,90,3,5)
  for y in (240,285,330):m.box(x,y,0,100,7,18,1)
 return m


def build(Mesh,own,folder):
 textures(folder)
 lab=own(NAME,shell(Mesh),ATLAS)
 tower=own('Camp 12 Survey Mast',mast(Mesh),ATLAS)
 service_atlas='meridian_services.png'
 atlas=Image.open(folder/ATLAS).convert('RGB')
 atlas.paste(atlas.crop((0,0,TILE,TILE)),(6*TILE,0))
 d=ImageDraw.Draw(atlas)
 for text,size,yy in [('MERIDIAN',51,100),('FIELD SERVICES',29,208),('AUTHORIZED ACCESS',23,295)]:
  font=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',size)
  d.text((6*TILE+70,yy),text,font=font,fill=(29,55,60))
 atlas.save(folder/service_atlas,optimize=True)
 service=own('Meridian Service Module',shell(Mesh,comms=False),service_atlas)
 power=own('Northstar Stack Pair',power_station(Mesh),ATLAS)
 utility=own('Camp 12 Utility Spine',utility_spine(Mesh),ATLAS)
 console=own('Meridian Control Console',control_console(Mesh),ATLAS)
 link=own('Meridian Service Link',service_link(Mesh),ATLAS)
 array=own('AEGIS Arrival Frame',array_equipment(Mesh),ATLAS)
 for name in (NAME,'Camp 12 Survey Mast','Meridian Service Module','Northstar Stack Pair','Camp 12 Utility Spine',
              'Meridian Control Console','Meridian Service Link','AEGIS Arrival Frame'):
  f=folder/(name+'.fpe');text=f.read_text()
  text=text.replace('roughnessStrength = 0.82','roughnessStrength = 1.0').replace('metalnessStrength = 0.22','metalnessStrength = 1.0')
  text+='normalMap = '+NORMAL+'\nnormalStrength = 0.65\nsurfaceMap = '+SURFACE+'\n'
  f.write_text(text+'basecolor = 4294967295\nreflectance = 0.04\nemissivecolor = 4294967295\nemissiveMap = '+EMISSION+'\nemissiveStrength = 0.6\n')
 return lab,tower,service,power,utility,console,link,array
