"""Vesper's native height-field and authored First Light landmarks.

World coordinates are MAX inches. Routes are graded before engineering pads.
Buildings supply walls, roofs, railings and machinery, but their walking surfaces
remain native terrain until a MAX-native modular floor solution is proven. The
previous generated floor slabs overlapped terrain and produced severe z-fighting.
"""
import math
from native_terrain_pass import gauss, rect_mask, smoothstep

ROUTE=[(0,-9600,1080),(-700,-8350,810),(-1700,-7350,500),(-1450,-6400,310),(0,-5150,120),(300,-4150,290),(0,-3100,640),(0,-2350,650),(-1250,-1750,900),(-1300,-850,900),(-650,-520,900),(-250,-520,930),(250,-250,1000),(850,-260,1080),(1300,1050,1080),(2100,1250,1080),(2470,1250,1080),(2470,1750,1170),(0,1900,1380),(0,2200,1540),(0,2850,1540),(0,3200,1540)]
RETURN=[(-900,3020,1540),(-1500,3020,1520),(-2250,2100,1280),(-2900,1000,1010),(-2900,-350,900),(-2550,-1600,700),(-1100,-2300,650)]
PADS=[(-1730,-7160,660,550,500),(-1450,-650,980,1040,900),(1250,700,1030,940,1080),(0,3090,1380,900,1540),(0,-2350,1150,500,650)]

def road_sample(x,z,points):
 best=(1e9,0)
 for a,b in zip(points,points[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz)))
  dist=math.hypot(x-a[0]-t*dx,z-a[1]-t*dz)
  if dist<best[0]:best=(dist,a[2]+(b[2]-a[2])*t)
 return best

def ground(x,z):
 h=145+35*math.sin(x/1200)*math.cos(z/1000)
 h+=1080*gauss(x,z,-1400,-10000,4100,1350)
 h+=1980*gauss(x,z,-4650,-4900,1350,2600)
 h+=1450*gauss(x,z,4900,-6800,1850,2050)
 h+=2200*gauss(x,z,4300,-800,1500,2700)
 h+=1050*gauss(x,z,-4900,2100,1600,2700)
 h+=1950*gauss(x,z,0,3900,3450,2850)
 h+=1750*gauss(x,z,0,7400,2100,1000)
 h+=40*math.sin(x/270+z/590)*math.sin(z/390)
 for route,width in ((ROUTE,290),(RETURN,280)):
  distance,y=road_sample(x,z,route);blend=1-smoothstep(width,width+440,distance)
  h=h*(1-blend)+y*blend
 for cx,cz,hx,hz,y in PADS:
  blend=rect_mask(x,z,cx,cz,hx,hz,260);h=h*(1-blend)+y*blend
 pit=1-smoothstep(650,1450,math.hypot(x*.92,(z-5500)*1.10))
 h=h*(1-pit)+180*pit
 return h

TERRAIN_MATERIALS={
 'baseLayerMaterial':256|13,
 'layerStartHeight0':190,'layerEndHeight0':380,'layerMatIndex0':256|3,
 'layerStartHeight1':650,'layerEndHeight1':960,'layerMatIndex1':256|14,
 'layerStartHeight2':1650,'layerEndHeight2':2300,'layerMatIndex2':256|22,
 'layerStartHeight3':12000,'layerEndHeight3':13000,'layerMatIndex3':256|22,
 'layerStartHeight4':15000,'layerEndHeight4':16000,'layerMatIndex4':256|22,
 'slopeStart0':.30,'slopeEnd0':.62,'slopeMatIndex0':256|18,
 'slopeStart1':.80,'slopeEnd1':.98,'slopeMatIndex1':256|17,
 'reflectance':.02,'bumpiness':.55,
}

def architecture(Mesh,own,add,prop,P,I):
 """Assembled shells without terrain-overlapping floor planes."""
 def beam(m,x,y,z,w,h,d,c=1):m.box(x,y,z,w,h,d,c)
 def endwall(m,z,left,right,opening,h=390,color=1):
  lo,hi=opening
  if lo>left:beam(m,(lo+left)/2,0,z,lo-left,h,45,color)
  if right>hi:beam(m,(right+hi)/2,0,z,right-hi,h,45,color)
  beam(m,(lo+hi)/2,280,z,hi-lo,h-280,45,color)
 def sidewall(m,x,near,far,opening,h=390,color=1):
  lo,hi=opening
  if lo>near:beam(m,x,0,(near+lo)/2,45,h,lo-near,color)
  if far>hi:beam(m,x,0,(hi+far)/2,45,h,far-hi,color)
  beam(m,x,280,(lo+hi)/2,45,h-280,hi-lo,color)

 # Gate 07: walls and roof only. Native terrain forms the threshold floor.
 m=Mesh()
 beam(m,-390,0,0,180,460,680);beam(m,390,0,0,180,460,680)
 beam(m,0,340,0,650,130,680,2)
 for z in (-320,320):beam(m,0,337,z,590,10,18,5)
 gate=own('Gate 07 Cut Portal',m);add(gate,'Gate 07 / sea wall threshold',0,-3100,y=640)

 # Northstar: tall turbine nave + lower west maintenance aisle. No generated floor slab.
 m=Mesh()
 endwall(m,-1000,-950,950,(-30,470),560);beam(m,0,0,1000,1900,560,45)
 sidewall(m,950,-1000,1000,(-240,260),560);beam(m,-950,0,0,45,390,2000)
 beam(m,230,560,0,1440,30,2000,2);beam(m,-720,390,0,450,30,2000,2)
 for z in (-760,140,760):beam(m,-500,0,z,60,560,60,2)
 for z in (-800,0,800):beam(m,230,520,z,1440,40,65,2)
 shell=own('Northstar Turbine Hall',m);add(shell,'Northstar / turbine nave and maintenance aisle',-1450,-650,y=900)
 for z in (-1000,-50):prop(P+'Generator 04a.fpe',-1590,z,y=902,ry=90)
 for z in (-1110,-120):prop(I+'Storage Tank - Small.fpe',-2210,z,y=902)
 for x in (-1350,-1070):prop(I+'Control Box - Large.fpe',x,170,y=902,ry=180)

 # Operations: civilian shell and partitions; terrain is the stable walking surface.
 m=Mesh()
 endwall(m,-840,-1000,1000,(-620,-180),330)
 sidewall(m,-1000,-840,660,(-100,340),330)
 sidewall(m,1000,-840,920,(450,890),330)
 beam(m,-520,0,660,960,330,35);beam(m,440,0,920,1120,330,35)
 beam(m,-40,0,790,35,330,260)
 beam(m,0,330,-90,2000,25,1500,1);beam(m,460,330,790,1080,25,260,1)
 beam(m,130,0,60,35,250,600,1);beam(m,130,245,60,35,12,620,4)
 shell=own('Meridian Operations House',m);add(shell,'Operations / requisitioned civilian workplace',1250,600,y=1080)
 for x,z in [(620,40),(950,720),(1670,1000)]:
  prop(P+'Desk 01a.fpe',x,z,y=1082,ry=90);prop(P+'Computer 01a.fpe',x,z,y=1157,ry=90)
 for z in (0,260,520):prop(P+'Locker 01a.fpe',2100,z,y=1082,ry=-90)
 for x in (1550,1820):prop(P+'Portable Cot 01a.fpe',x,1370,y=1082,ry=90)
 prop(P+'Desk Chair 01a.fpe',1720,900,y=1082,ry=135)

 # AEGIS: walls/roof/railings only. The previously atlas-textured floor was the worst flicker case.
 m=Mesh()
 endwall(m,-875,-1250,1250,(-300,300),680,2)
 sidewall(m,-1250,-875,875,(-280,280),680,2)
 sidewall(m,1250,-875,875,(-380,220),680,2)
 beam(m,0,680,-525,2500,45,700,2)
 for x in (-1130,-800,-470,-140,190,520,850,1180):beam(m,x,0,875,12,100,12,2)
 beam(m,0,95,875,2500,12,12,2);beam(m,0,45,875,2500,8,10,2)
 for x in (-1210,1210):
  beam(m,x,0,80,55,680,80,2);beam(m,x,450,-20,22,110,160,5)
 shell=own('AEGIS Cliff Gallery',m);add(shell,'AEGIS / armoured hall above the Choir cut',0,3090,y=1540)
 for x in (-880,880):prop(I+'Control Box - Tall.fpe',x,3250,y=1542,ry=180)

 # Choir arch remains purpose-built non-height-field geometry.
 m=Mesh()
 for x,y,z,w,h,d,angle in [(-420,0,0,210,2850,310,-11),(490,0,180,260,3300,340,9),(20,2520,100,980,300,400,-8)]:
  m.box(x,y,z,w,h,d,6,angle)
 for y in (390,430,500):m.box(-420,y,-160,205,9,9,7,-11)
 arch=own('Choir Breach Arch',m);add(arch,'Choir / buried arch exposed by the receded sea',0,5100,y=180,ry=16)

 # Elevated service bridge still needs a real deck because terrain drops away beneath it.
 m=Mesh();beam(m,0,-16,0,500,22,980,2)
 for x in (-245,245):
  beam(m,x,95,0,12,12,980,2)
  for z in (-460,0,460):beam(m,x,0,z,12,100,12,2)
 bridge=own('Excavation Service Bridge',m);add(bridge,'AEGIS / inspection bridge at the fracture',-940,4050,y=1540)
