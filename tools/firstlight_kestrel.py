"""Author the Broadwing-pattern Vanguard Kestrel dropship for FIRST LIGHT.

The asset is procedural and original. Three geometry states are authored from one
airframe: clean flight, VTOL/gear flare, and landed/ramp-open.  Lua swaps those
states during insertion/extraction so the ship reads like a vehicle with systems,
not a static prop sliding through space.
"""
import math
from PIL import Image,ImageDraw,ImageFilter
from meridian_fieldkit import quad,strut

NAME='Vanguard Kestrel Dropship'
SCRIPT=r'aegis_reach\firstlight_kestrel.lua'
TEXTURE='kestrel_broadwing_atlas.png'
NORMAL='kestrel_broadwing_normal.png'
SURFACE='kestrel_broadwing_surface.png'
EMISSIVE='kestrel_broadwing_emissive.png'
STATES=('flight','flare','landed')
# Local model-space inches. The ramp tip/foot pad is authored at Y=4 so a landed
# entity placed at ground-4 sits on terrain instead of hovering above it.
LANDED_CONTACT_Y=4
LENGTH_IN=800
SPAN_IN=704


def _atlas(folder):
    """Coordinated APBR maps: cool airframe, TPS belly, restrained service markings."""
    tile=192
    # shell, secondary, structure, glazing, markings, lift/RCS, cruise heat, TPS/interior
    base=[(57,66,68),(83,91,91),(36,43,46),(18,27,31),(151,158,151),(31,71,76),(91,50,34),(20,22,23)]
    rough=(176,154,122,78,160,114,108,214)
    metal=(95,118,168,24,36,110,154,42)
    atlas=Image.new('RGB',(tile*8,tile))
    normal=Image.new('RGB',atlas.size,(128,128,255))
    surface=Image.new('RGBA',atlas.size,(255,160,80,255))
    emissive=Image.new('RGB',atlas.size,(0,0,0))
    for i,color in enumerate(base):
        p=Image.new('RGB',(tile,tile),color);d=ImageDraw.Draw(p)
        n=Image.new('RGB',(tile,tile),(128,128,255));nd=ImageDraw.Draw(n)
        s=Image.new('RGBA',(tile,tile),(255,rough[i],metal[i],255));sd=ImageDraw.Draw(s)
        # broad manufactured panel breaks, not dense sci-fi greeble
        if i not in (3,5,6):
            for y in (42,96,150):
                d.line((18,y,tile-18,y),fill=tuple(max(0,c-12) for c in color),width=2)
                nd.line((18,y,tile-18,y),fill=(128,117,252),width=2)
                sd.line((18,y,tile-18,y),fill=(255,min(245,rough[i]+28),metal[i],255),width=2)
            for x in (54,138):
                d.line((x,22,x,tile-22),fill=tuple(max(0,c-8) for c in color),width=1)
                nd.line((x,22,x,tile-22),fill=(117,128,252),width=1)
        if i==3:
            # armored, smoked cockpit glazing
            d.rectangle((18,18,tile-18,tile-18),outline=(49,73,78),width=6)
        elif i==4:
            # muted rescue/flight-line identifiers
            d.rectangle((22,58,tile-22,78),fill=(190,196,183))
            d.rectangle((22,110,112,128),fill=(103,116,113))
        elif i==5:
            d.ellipse((32,32,tile-32,tile-32),outline=(81,225,235),width=12)
            ImageDraw.Draw(emissive).ellipse((i*tile+26,26,(i+1)*tile-26,tile-26),fill=(38,222,238))
        elif i==6:
            d.ellipse((30,30,tile-30,tile-30),outline=(255,133,70),width=12)
            ImageDraw.Draw(emissive).ellipse((i*tile+22,22,(i+1)*tile-22,tile-22),fill=(255,112,48))
        elif i==7:
            # TPS tiles / cargo-interior anti-slip: deliberately darker and rougher.
            for y in range(22,tile-18,24):
                d.line((18,y,tile-18,y),fill=(35,37,37),width=2)
            for x in range(28,tile-18,32):
                d.line((x,18,x,tile-18),fill=(29,31,31),width=1)
        atlas.paste(p,(i*tile,0));normal.paste(n,(i*tile,0));surface.paste(s,(i*tile,0))
    # soften normal seams enough to avoid glitter at distance while keeping panel depth
    normal=normal.filter(ImageFilter.GaussianBlur(.35))
    atlas.save(folder/TEXTURE,optimize=True)
    normal.save(folder/NORMAL,optimize=True)
    surface.save(folder/SURFACE,optimize=True)
    emissive.save(folder/EMISSIVE,optimize=True)


def _tri(m,a,b,c,tile):
    ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
    vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
    nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
    ll=math.sqrt(nx*nx+ny*ny+nz*nz)
    if ll<=1e-8: raise ValueError('degenerate Kestrel triangle')
    n=(nx/ll,ny/ll,nz/ll);start=len(m.verts)
    m.verts.extend((a,b,c));m.norm.extend((n,n,n))
    m.uv.extend((((tile+.16)/8,.86),((tile+.84)/8,.86),((tile+.50)/8,.14)))
    m.faces.append((start,start+1,start+2))


def _tri2(m,a,b,c,tile):
    _tri(m,a,b,c,tile);_tri(m,c,b,a,tile)


def _ring(z,w,h,y):
    # Octagonal lifting-body section. Bottom two facets are broad enough to read as TPS.
    return [(-w*.64,y-h*.50,z),(w*.64,y-h*.50,z),(w,y-h*.20,z),(w,y+h*.17,z),
            (w*.63,y+h*.50,z),(-w*.63,y+h*.50,z),(-w,y+h*.17,z),(-w,y-h*.20,z)]


def _skin(m,a,b):
    for i in range(len(a)):
        j=(i+1)%len(a)
        tile=7 if i in (0,1,7) else (1 if i in (2,6) else 0)
        quad(m,[a[i],a[j],b[j],b[i]],tile)


def _cap(m,ring,tile=1,reverse=False):
    c=(sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring),ring[0][2])
    for i in range(len(ring)):
        j=(i+1)%len(ring)
        if reverse:_tri(m,c,ring[j],ring[i],tile)
        else:_tri(m,c,ring[i],ring[j],tile)


def _wing_prism(m,side):
    """Thick blended shoulder/lifting surface; broad root, modest tip, no fantasy knife wing."""
    s=1 if side>0 else -1
    root0=(s*118,104,-150);root1=(s*145,108,238)
    tip0=(s*352,86,12);tip1=(s*252,92,286)
    top=[root0,(s*286,93,-28),tip0,tip1,(s*214,101,238),root1]
    bot=[(x,y-15,z) for x,y,z in top]
    if s>0:
        quad(m,[top[0],top[1],top[4],top[5]],1)
        quad(m,[top[1],top[2],top[3],top[4]],1)
        quad(m,[bot[5],bot[4],bot[1],bot[0]],7)
        quad(m,[bot[4],bot[3],bot[2],bot[1]],7)
    else:
        quad(m,[top[5],top[4],top[1],top[0]],1)
        quad(m,[top[4],top[3],top[2],top[1]],1)
        quad(m,[bot[0],bot[1],bot[4],bot[5]],7)
        quad(m,[bot[1],bot[2],bot[3],bot[4]],7)
    # seal exposed leading, trailing and tip edges
    for i,j in ((0,1),(1,2),(2,3),(3,4),(4,5)):
        quad(m,[top[i],bot[i],bot[j],top[j]],2)


def _aft_nozzle(m,x,y,z,outer=42,depth=44,plume=True):
    seg=12;front=[];rim=[];inner=[]
    for i in range(seg):
        a=i*math.tau/seg;co,si=math.cos(a),math.sin(a)
        front.append((x+co*outer*.84,y+si*outer*.84,z-depth))
        rim.append((x+co*outer,y+si*outer,z))
        inner.append((x+co*outer*.57,y+si*outer*.57,z+7))
    for i in range(seg):
        j=(i+1)%seg
        quad(m,[front[i],front[j],rim[j],rim[i]],2)
        quad(m,[rim[i],rim[j],inner[j],inner[i]],7)
        _tri(m,(x,y,z+8),inner[j],inner[i],6)
    if plume:
        hot=[(x+(p[0]-x)*.74,y+(p[1]-y)*.74,z+10) for p in inner]
        tail=[]
        for i in range(seg):
            a=i*math.tau/seg;tail.append((x+math.cos(a)*outer*.10,y+math.sin(a)*outer*.10,z+70))
        for i in range(seg):
            j=(i+1)%seg;quad(m,[hot[i],hot[j],tail[j],tail[i]],6)


def _down_nozzle(m,x,y,z,outer=21,plume=True):
    seg=10;rim=[];inner=[];tail=[]
    for i in range(seg):
        a=i*math.tau/seg;co,si=math.cos(a),math.sin(a)
        rim.append((x+co*outer,y,z+si*outer))
        inner.append((x+co*outer*.58,y-6,z+si*outer*.58))
        tail.append((x+co*outer*.12,y-44,z+si*outer*.12))
    for i in range(seg):
        j=(i+1)%seg
        quad(m,[rim[i],rim[j],inner[j],inner[i]],7)
        _tri(m,(x,y-7,z),inner[i],inner[j],5)
        if plume:quad(m,[inner[i],inner[j],tail[j],tail[i]],5)


def _gear(m):
    """Wide four-point outriggers kept outside the central lift-wash footprint."""
    for x,z in ((-286,-92),(286,-92),(-278,132),(278,132)):
        sx=-1 if x<0 else 1
        # triangulated two-link oleo reads as aircraft gear rather than stair rails
        strut(m,(sx*184,62,z),(x,22,z),10,2)
        strut(m,(sx*212,54,z+8),(x,22,z),7,2)
        m.box(x,4,z,46,8,34,7)
        m.box(x,12,z,22,11,22,2)


def _gear_doors(m):
    for x,z in ((-214,-92),(214,-92),(-210,132),(210,132)):
        m.box(x,46,z,62,4,50,7,angle=8 if x<0 else -8)


def _lift_bays(m,state):
    # Four lift sources straddle the CG fore/aft and sit in the shoulder roots.
    for x in (-218,218):
        for z in (-86,96):
            if state=='flight':
                m.box(x,49,z,58,5,60,1)
            else:
                # open split doors expose a recessed throat
                sx=-1 if x<0 else 1
                m.box(x-sx*35,50,z,24,4,58,1,angle=-18*sx)
                m.box(x+sx*35,50,z,24,4,58,1,angle=18*sx)
                _down_nozzle(m,x,48,z,22,plume=(state=='flare'))


def _cargo(m,state):
    """Rear roll-on aperture sized as a compact squad/cargo vestibule."""
    if state!='landed':
        m.box(0,42,397,126,88,8,1)
        m.box(0,79,392,94,50,5,4)
        return
    # aperture frame, dark vestibule and ramp. Threshold and ramp tip avoid terrain clipping.
    for x in (-70,70):m.box(x,38,394,12,94,18,2)
    m.box(0,126,394,152,13,18,2)
    # short anti-slip cargo floor inside the tail
    quad(m,[(-62,39,286),(62,39,286),(62,39,405),(-62,39,405)],7)
    quad(m,[(-61,122,294),(-61,122,397),(61,122,397),(61,122,294)],7)
    # ramp from 39-inch threshold to Y=4 contact point
    quad(m,[(-62,39,404),(62,39,404),(72,4,526),(-72,4,526)],7)
    quad(m,[(-72,1,526),(72,1,526),(62,35,404),(-62,35,404)],2)
    for x in (-68,68):strut(m,(x,37,404),(x,5,524),5,2)


def _tails(m):
    # Twin canted fins preserve a clear cargo centerline and keep control surfaces in propulsive flow.
    for side in (-1,1):
        s=1 if side>0 else -1
        a=(s*72,142,270);b=(s*98,224,346);c=(s*126,148,375)
        _tri2(m,a,b,c,1)
        strut(m,(s*74,142,272),(s*102,199,329),6,2)


def _cockpit(m):
    # Armored forward glazing: small facets, not a bubble canopy.
    quad(m,[(-50,121,-316),(-72,132,-260),(-12,148,-237),(-8,136,-321)],3)
    quad(m,[(8,136,-321),(12,148,-237),(72,132,-260),(50,121,-316)],3)
    quad(m,[(-7,137,-322),(-11,149,-239),(11,149,-239),(7,137,-322)],3)
    strut(m,(0,136,-324),(0,150,-238),6,2)


def _service_details(m):
    # Sparse RCS/service points placed where attitude-control plumbing is plausible.
    for x,z in ((-94,-264),(94,-264),(-154,202),(154,202)):
        m.box(x,108,z,18,14,12,2)
        m.box(x,115,z+(5 if z<0 else -5),9,7,4,5)
    # two dorsal service spines and subdued position lights
    m.box(0,151,44,38,16,260,2)
    m.box(0,168,112,20,9,116,1)
    m.box(-348,91,20,8,8,16,5);m.box(348,91,20,8,8,16,4)


def kestrel_mesh(Mesh,state='flight'):
    if state not in STATES:raise ValueError(state)
    m=Mesh()
    sections=[
        _ring(-400,12,20,94),_ring(-350,48,62,95),_ring(-292,78,91,97),
        _ring(-205,112,110,99),_ring(-85,145,120,100),_ring(65,154,124,100),
        _ring(210,142,116,101),_ring(330,105,101,101),_ring(398,77,88,101)]
    for a,b in zip(sections,sections[1:]):_skin(m,a,b)
    _cap(m,sections[0],1,reverse=True)
    # Rear center is intentionally handled by the cargo-state builder.
    _wing_prism(m,-1);_wing_prism(m,1)
    _cockpit(m);_tails(m);_service_details(m)

    # Compact shoulder pods keep thrust near the mass center and leave the cargo centerline clear.
    cruise_plume=state=='flight'
    for x in (-236,236):
        m.box(x,82,140,86,70,250,1)
        m.box(x,96,32,62,32,70,2)
        strut(m,(x-31,117,8),(x+31,117,228),6,2)
        _aft_nozzle(m,x,88,279,43,44,plume=cruise_plume)

    _lift_bays(m,state)
    if state=='flight':_gear_doors(m)
    else:_gear(m)
    _cargo(m,state)
    return m


def _write_fpe_maps(folder,name):
    f=folder/(name+'.fpe')
    text=f.read_text(errors='replace')
    text=text.replace('roughnessStrength = 0.82','roughnessStrength = 1.0')
    text=text.replace('metalnessStrength = 0.22','metalnessStrength = 1.0')
    text+=(
        f'normalMap = {NORMAL}\n'
        f'surfaceMap = {SURFACE}\n'
        f'emissiveMap = {EMISSIVE}\n'
        'emissiveStrength = 0.92\nreflectance = 0.18\n'
    )
    f.write_text(text)


def apply(build):
    _atlas(build.AS)
    paths={}
    labels={'flight':'Flight','flare':'VTOL Flare','landed':'Landed Ramp'}
    for state in STATES:
        asset=NAME+' - '+labels[state]
        paths[state]=build.own(asset,kestrel_mesh(build.Mesh,state),TEXTURE,collision=11)
        _write_fpe_maps(build.AS,asset)

    ix,iz=-120,-9140
    insertion_y=build.ground(ix,iz)+190
    lx,lz=0,-2350
    landed_y=build.ground(lx,lz)-LANDED_CONTACT_Y
    for state in STATES:
        layout_kind='vehicle' if state=='flight' else 'vehicle_state'
        build.add(paths[state],f'FL KESTREL INSERTION {state.upper()}',ix,iz,y=insertion_y,ry=180,
                  kind=layout_kind,script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1})
        build.add(paths[state],f'FL KESTREL EXTRACTION {state.upper()}',lx,lz,y=landed_y,ry=180,
                  kind=layout_kind,script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':1})

    return {
        'ship':NAME,'vehicle_entities':2,'state_entities':6,'state_variants':list(STATES),
        'insertion_visible':True,'extraction_visible':True,
        'extraction_approach_ms':36000,'touchdown_ms':60000,
        'boarding_requires_landed_state':True,'collision':'visual-only',
        'airframe':{'length_in':LENGTH_IN,'span_in':SPAN_IN,'lifting_body':True,'rear_cargo_aperture':True},
        'propulsion':{'cruise_nozzles':2,'balanced_vtol_nozzles':4,'flight_plumes':True,'flare_plumes':True},
        'landing_gear':'wide four-point outriggers outside lift wash',
        'thermal_zones':'ventral TPS + hot cruise throats',
        'landed_contact_y':LANDED_CONTACT_Y,
    }
