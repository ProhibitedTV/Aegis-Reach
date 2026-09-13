"""Author the visible Kestrel insertion/extraction dropship for FIRST LIGHT."""
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
            de=ImageDraw.Draw(em);de.rectangle((i*tile+12,12,(i+1)*tile-12,tile-12),fill=(40,210,225) if i==5 else (255,112,48))
        im.paste(p,(i*tile,0))
    im.save(folder/TEXTURE,optimize=True);em.save(folder/EMISSIVE,optimize=True)


def _skin(m,a,b,tile=0):
    for i in range(len(a)):
        j=(i+1)%len(a);quad(m,[a[i],a[j],b[j],b[i]],tile)


def _ring(z,w,h,y):
    return [(-w*.64,y-h*.5,z),(w*.64,y-h*.5,z),(w,y-h*.18,z),(w,y+h*.18,z),(w*.64,y+h*.5,z),(-w*.64,y+h*.5,z),(-w,y+h*.18,z),(-w,y-h*.18,z)]


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
    # twin engine pods and bright throats
    for x in (-220,220):
        m.box(x,73,96,74,62,152,1)
        m.box(x,73,180,58,46,16,6)
        m.box(x,73,35,54,50,18,5)
        strut(m,(x-28,92,42),(x+28,92,150),5,2)
    # dorsal spine / tail
    m.box(0,145,80,34,20,205,2)
    quad(m,[(-7,146,130),(-10,228,212),(-28,194,250),(-12,145,238)],1)
    quad(m,[(7,146,130),(12,145,238),(28,194,250),(10,228,212)],1)
    # landing skids visible on final approach
    for x in (-66,66):
        strut(m,(x,55,-25),(x,18,10),8,2)
        strut(m,(x,18,-48),(x,18,88),7,2)
    # small side position lights
    m.box(-296,78,82,7,7,14,6);m.box(296,78,82,7,7,14,5)
    return m


def apply(build):
    _atlas(build.AS)
    path=build.own(NAME,kestrel_mesh(build.Mesh),TEXTURE,collision=11)
    f=build.AS/(NAME+'.fpe')
    text=f.read_text(errors='replace').replace('roughnessStrength = 0.82','roughnessStrength = 0.72').replace('metalnessStrength = 0.22','metalnessStrength = 0.48')
    f.write_text(text+f'emissiveMap = {EMISSIVE}\nemissiveStrength = 0.65\nreflectance = 0.12\n')

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
    }
