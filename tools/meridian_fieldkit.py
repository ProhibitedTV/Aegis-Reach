"""Original Meridian field-lab shell and practical mast; no licensed source meshes.

MAX inches, front faces local -Z. No ground slab: native terrain remains the floor.
"""
from pathlib import Path
import math,random
from PIL import Image,ImageDraw,ImageFont

NAME='Meridian Field Lab'
ATLAS='meridian_fieldkit.png'
EMISSION='meridian_fieldkit_emission.png'

def textures(folder):
 rng=random.Random(1207)
 # Ivory panels, graphite chassis, grey alloy, teal service panels, lamps, trim,
 # Meridian identification, equipment labels. Every UV island stays within a tile.
 colors=[(172,174,166),(33,42,47),(79,91,95),(47,77,81),(245,202,133),(83,158,172),(166,171,165),(51,66,71)]
 im=Image.new('RGB',(2048,256));d=ImageDraw.Draw(im)
 for tile,color in enumerate(colors):
  ox=tile*256;d.rectangle((ox,0,ox+255,255),fill=color)
  if tile in (4,5):continue
  for _ in range(6500):
   x=rng.randrange(256);y=rng.randrange(256);n=rng.randrange(-9,10)
   d.point((ox+x,y),fill=tuple(max(0,min(255,c+n)) for c in color))
  # Paint wear collects near seams, not giant random grunge across every panel.
  for _ in range(200):
   x=rng.randrange(256);y=rng.choice((rng.randrange(5,20),rng.randrange(235,251)))
   d.line((ox+x,y,ox+min(255,x+rng.randrange(1,7)),y),fill=tuple(int(c*.63) for c in color))
  d.rectangle((ox+5,5,ox+250,250),outline=tuple(int(c*.65) for c in color),width=2)
  if tile in (0,3):
   for x in (14,241):
    for y in (14,241):d.ellipse((ox+x-2,y-2,ox+x+2,y+2),fill=(49,57,59))
 font=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',29)
 small=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',17)
 ox=6*256
 d.polygon([(ox+126,24),(ox+176,101),(ox+157,101),(ox+126,51),(ox+95,101),(ox+76,101)],fill=(31,60,65))
 d.text((ox+39,113),'MERIDIAN',font=font,fill=(26,49,54))
 d.text((ox+30,153),'SURVEY CAMP 12',font=small,fill=(30,52,58))
 d.text((ox+41,186),'GEOLOGY / FIELD LAB',font=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',13),fill=(44,62,67))
 ox=7*256
 d.text((ox+24,30),'M-12',font=font,fill=(190,199,191))
 d.text((ox+24,90),'POWER / DATA',font=small,fill=(149,172,172))
 for y in range(145,225,14):d.line((ox+25,y,ox+225,y),fill=(20,29,34),width=5)
 im.save(folder/ATLAS)
 em=Image.new('RGB',im.size,(0,0,0));ed=ImageDraw.Draw(em)
 ed.rectangle((4*256,0,5*256-1,255),fill=(255,193,104))
 ed.rectangle((5*256,0,6*256-1,255),fill=(25,96,113))
 em.save(folder/EMISSION)

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

def shell(Mesh):
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
     m.verts.append(point);m.norm.append((0,0,nz));m.uv.append((.04,.5))
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
 return m

def build(Mesh,own,folder):
 textures(folder)
 lab=own(NAME,shell(Mesh),ATLAS)
 tower=own('Camp 12 Survey Mast',mast(Mesh),ATLAS)
 for name in (NAME,'Camp 12 Survey Mast'):
  f=folder/(name+'.fpe');text=f.read_text()
  text=text.replace('roughnessStrength = 0.82','roughnessStrength = 0.67').replace('metalnessStrength = 0.22','metalnessStrength = 0.12')
  f.write_text(text+'basecolor = 4294967295\nreflectance = 0.04\nemissivecolor = 4294967295\nemissiveMap = '+EMISSION+'\nemissiveStrength = 0.6\n')
 return lab,tower
