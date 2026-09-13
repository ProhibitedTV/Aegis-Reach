"""Author the visible Kestrel insertion/extraction dropship for FIRST LIGHT."""
import math
from PIL import Image,ImageDraw
from meridian_fieldkit import quad,strut

NAME='Vanguard Kestrel Dropship'
SCRIPT=r'aegis_reach\firstlight_kestrel.lua'
TEXTURE='kestrel_atlas.png'
EMISSIVE='kestrel_emissive.png'


def _atlas(folder):
    tile=128
    base=[(34,42,47),(53,63,68),(80,88,90),(18,24,28),(112,125,128),(29,64,70),(84,48,34),(18,18,18)]
    im=Image.new('RGB',(tile*8,tile))
    em=Image.new('RGB',(tile*8,tile),(0,0,0))
    for i,color in enumerate(base):
        p=Image.new('RGB',(tile,tile),color);d=ImageDraw.Draw(p)
        for y in range(12,tile,22):d.line((8,y,tile-8,y),fill=tuple(max(0,c-10) for c in color),width=1)
        for x in range(18,tile,32):d.line((x,8,x,tile-8),fill=tuple(max(0,c+8) for c in color),width=1)
        if i in (5,6):
            d.rectangle((20,20,108,108),outline=(112,220,230) if i==5 else (255,126,72),width=5)
            de=ImageDraw.Draw(em);de.rectangle((i*tile+8,8,(i+1)*tile-8,tile-8),fill=(52,235,255) if i==5 else (255,132,58))
        im.paste(p,(i*tile,0))
    im.save(folder/TEXTURE,optimize=True);em.save(folder/EMISSIVE,optimize=True)


def _skin(m,a,b,tile=0):
    for i in range(len(a)):
        j=(i+1)%len(a);quad(m,[a[i],a[j],b[j],b[i]],tile)


def _ring(z,w,h,y):
    return [(-w*.64,y-h*.5,z),(w*.64,y-h*.5,z),(w,y-h*.18,z),(w,y+h*.18,z),(w*.64,y+h*.5,z),(-w*.64,y+h*.5,z),(-w,y+h*.18,z),(-w,y-h*.18,z)]


def _tri(m,a,b,c,tile):
    ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
    vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
    nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
    ll=max(1e-6,math.sqrt(nx*nx+ny*ny+nz*nz));n=(nx/ll,ny/ll,nz/ll)
    start=len(m.verts);m.verts.extend((a,b,c));m.norm.extend((n,n,n))
    m.uv.extend((((tile+.18)/8,.82),((tile+.82)/8,.82),((tile+.50)/8,.18)))
    m.faces.append((start,start+1,start+2))


def _aft_nozzle(m,x,y,z,outer=37,depth=34):
    """Faceted recessed main engine bell plus a short emissive plasma plume."""
    seg=12
    front=[];rim=[];inner=[]
    for i in range(seg):
        a=i*math.tau/seg;co,si=math.cos(a),math.sin(a)
        front.append((x+co*outer*.82,y+si*outer*.82,z-depth))
        rim.append((x+co*outer,y+si*outer,z))
        inner.append((x+co*outer*.58,y+si*outer*.58,z+5))
    for i in range(seg):
        j=(i+1)%seg
        quad(m,[front[i],front[j],rim[j],rim[i]],1)
        quad(m,[rim[i],rim[j],inner[j],inner[i]],7)
        _tri(m,(x,y,z+6),inner[j],inner[i],6)
    # A deliberately short opaque/emissive plasma spear gives MAX a readable thrust
    # silhouette without depending on an extra particle emitter or licensed media.
    hot=[(x+(p[0]-x)*.76,y+(p[1]-y)*.76,z+8) for p in inner]
    tail=[]
    for i in range(seg):
        a=i*math.tau/seg;tail.append((x+math.cos(a)*outer*.12,y+math.sin(a)*outer*.12,z+54))
    for i in range(seg):
        j=(i+1)%seg;quad(m,[hot[i],hot[j],tail[j],tail[i]],6)


def _down_nozzle(m,x,y,z,outer=17):
    """Compact VTOL bell and cyan down-thrust core under the engine pods."""
    seg=8
    rim=[];inner=[];tail=[]
    for i in range(seg):
        a=i*math.tau/seg;co,si=math.cos(a),math.sin(a)
        rim.append((x+co*outer,y,z+si*outer))
        inner.append((x+co*outer*.62,y-5,z+si*outer*.62))
        tail.append((x+co*outer*.18,y-28,z+si*outer*.18))
    for i in range(seg):
        j=(i+1)%seg
        quad(m,[rim[i],rim[j],inner[j],inner[i]],7)
        quad(m,[inner[i],inner[j],tail[j],tail[i]],5)


def kestrel_mesh(Mesh):
    m=Mesh()
    sections=[_ring(-250,44,70,92),_ring(-165,88,108,96),_ring(-35,112,122,98),_ring(125,108,116,98),_ring(230,72,88,101)]
    for a,b in zip(sections,sections[1:]):_skin(m,a,b,0)
    # cockpit canopy
    quad(m,[(-42,120,-170),(-70,143,-104),(-8,153,-86),(-4,126,-178)],3)
    quad(m,[(4,126,-178),(8,153,-86),(70,143,-104),(42,120,-170)],3)
    strut(m,(0,124,-180),(0,154,-86),5,2)
    # broad swept wings
    port=[(-91,88,-25),(-295,72,80),(-260,80,186),(-93,96,110)]
    star=[(91,88,-25),(295,72,80),(260,80,186),(93,96,110)]
    quad(m,port,1);quad(m,list(reversed(star)),1)
    quad(m,[(x,y-12,z) for x,y,z in reversed(port)],2);quad(m,[(x,y-12,z) for x,y,z in star],2)
    # Twin propulsion pods now terminate in real recessed engine bells rather than
    # glowing rectangular blocks. The orange aft cores are readable from the arrival
    # and extraction cameras, while four cyan lift cores explain low-speed VTOL flight.
    for x in (-220,220):
        m.box(x,73,88,78,64,146,1)
        m.box(x,73,26,58,50,24,5)
        strut(m,(x-29,94,36),(x+29,94,145),5,2)
        _aft_nozzle(m,x,75,166,39,34)
        for zz in (58,116):
            m.box(x,42,zz,43,18,44,2)
            _down_nozzle(m,x,32,zz,16)
    # dorsal spine / tail
    m.box(0,145,80,34,20,205,2)
    quad(m,[(-7,146,130),(-10,228,212),(-28,194,250),(-12,145,238)],1)
    quad(m,[(7,146,130),(12,145,238),(28,194,250),(10,228,212)],1)
    # Compact four-point gear replaces the long rail skids that read like stairs from
    # the rear. These are short fixed landing feet tucked directly under the fuselage.
    for x,z in ((-70,-82),(70,-82),(-78,112),(78,112)):
        m.box(x,50,z,26,14,34,2)
        strut(m,(x,50,z),(x,22,z),7,2)
        m.box(x,17,z,32,5,28,7)
    # small side position lights
    m.box(-296,78,82,7,7,14,6);m.box(296,78,82,7,7,14,5)
    return m


def apply(build):
    _atlas(build.AS)
    path=build.own(NAME,kestrel_mesh(build.Mesh),TEXTURE,collision=11)
    f=build.AS/(NAME+'.fpe')
    text=f.read_text(errors='replace').replace('roughnessStrength = 0.82','roughnessStrength = 0.72').replace('metalnessStrength = 0.22','metalnessStrength = 0.48')
    f.write_text(text+f'emissiveMap = {EMISSIVE}\nemissiveStrength = 1.35\nreflectance = 0.12\n')

    ix,iz=-120,-9140
    build.add(path,'FL KESTREL INSERTION',ix,iz,y=build.ground(ix,iz)+180,ry=180,
              kind='vehicle',script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1})
    lx,lz=0,-2350
    build.add(path,'FL KESTREL EXTRACTION',lx,lz,y=build.ground(lx,lz)+105,ry=180,
              kind='vehicle',script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1})
    return {
        'ship':NAME,'vehicle_entities':2,'insertion_visible':True,'extraction_visible':True,
        'extraction_approach_ms':36000,'touchdown_ms':60000,
        'boarding_requires_landed_state':True,'collision':'visual-only',
        'propulsion':{'aft_nozzles':2,'vtol_nozzles':4,'emissive_plumes':True},
        'landing_gear':'compact four-point feet',
    }
