"""M-17 cargo lander wreck; authored roadside crash site with dedicated collision.

The visible hull is intentionally canted and torn. Player collision is provided by
separate hidden box-collision cores so MAX never has to infer traversal from the
concave wreck shell or render the proxy geometry as part of the ship.
"""
import math
from meridian_fieldkit import ATLAS, NORMAL, SURFACE, quad, strut

SITE=(-1790,-5560,385)
NAME='Meridian M17 Transport Wreck'
COLLISION_SCRIPT=r'aegis_reach\firstlight_collision_proxy.lua'
CRASH_YAW=14
CRASH_PITCH=-10
CRASH_ROLL=-8


def ring(z,w,bottom,top):
    h=top-bottom
    return [(-w*.64,bottom,z),(w*.64,bottom,z),(w,bottom+h*.23,z),
            (w,top-h*.23,z),(w*.64,top,z),(-w*.64,top,z),
            (-w,top-h*.23,z),(-w,bottom+h*.23,z)]


def skin(m,a,b,tile,skip=()):
    for i in range(8):
        if i in skip:continue
        j=(i+1)%8
        quad(m,[a[j],b[j],b[i],a[i]],tile)


def nozzle(m,x,y,z,radius,length,tile=2):
    rings=[]
    for zz,rr in [(z,radius*.70),(z+length*.72,radius),(z+length,radius*.92)]:
        rings.append([(x+math.cos(i*math.tau/12)*rr,
                       y+math.sin(i*math.tau/12)*rr,zz) for i in range(12)])
    for a,b in zip(rings,rings[1:]):
        for i in range(12):
            j=(i+1)%12
            quad(m,[a[i],a[j],b[j],b[i]],tile)
    outer=rings[-1]
    inner=[(x+(xx-x)*.76,y+(yy-y)*.76,zz-9) for xx,yy,zz in outer]
    for i in range(12):
        j=(i+1)%12
        quad(m,[outer[i],outer[j],inner[j],inner[i]],1)
    m.box(x,y-radius*.54,z+length-24,radius*1.12,radius*1.08,3,1)


def _rotate_point(p,pitch,roll):
    x,y,z=p
    ap=math.radians(pitch);cp,sp=math.cos(ap),math.sin(ap)
    y,z=y*cp-z*sp,y*sp+z*cp
    ar=math.radians(roll);cr,sr=math.cos(ar),math.sin(ar)
    x,y=x*cr-y*sr,x*sr+y*cr
    return (x,y,z)


def crash_attitude(mesh,pitch=CRASH_PITCH,roll=CRASH_ROLL):
    mesh.verts=[_rotate_point(p,pitch,roll) for p in mesh.verts]
    mesh.norm=[_rotate_point(n,pitch,roll) for n in mesh.norm]
    floor=min(p[1] for p in mesh.verts)
    mesh.verts=[(x,y-floor,z) for x,y,z in mesh.verts]
    return mesh


def hull(Mesh):
    m=Mesh()
    sections=[ring(-360,42,10,65),ring(-285,88,18,128),ring(-175,123,24,160),
              ring(-30,136,24,174),ring(120,130,25,166),ring(250,108,30,142)]
    for i,(a,b) in enumerate(zip(sections,sections[1:])):
        # Starboard upper skin is ripped away across the rear half.
        skip=(2,3,4) if i>=3 else ((3,4) if i==2 else ())
        skin(m,a,b,1 if i>=3 else 0,skip=skip)

    # Blunt crushed nose with an offset lower impact plate.
    a=sections[0]
    for i in range(1,7):
        j=i+1
        start=len(m.verts)
        m.verts.extend((a[0],a[j],a[i]))
        m.norm.extend([(0,0,-1)]*3)
        m.uv.extend(((1.1/8,.9),(1.9/8,.1),(1.9/8,.9)))
        m.faces.append((start,start+1,start+2))
    m.box(-18,3,-350,86,11,38,7,7)
    strut(m,(-54,16,-332),(62,34,-288),9,2)

    # Cockpit glazing is broad enough to read as a vehicle rather than architecture.
    quad(m,[(-55,109,-282),(-76,151,-188),(-7,163,-178),(-9,116,-286)],3)
    quad(m,[(6,116,-286),(7,163,-178),(74,151,-188),(54,109,-282)],3)
    strut(m,(0,111,-287),(0,166,-178),6,2)
    strut(m,(-74,151,-188),(74,151,-188),5,2)

    # Cargo spine and two broken ribs; no repeated full-height gantry hoops.
    m.box(0,30,95,166,10,248,1)
    for x in (-68,68):m.box(x,39,95,7,10,236,2)
    for z in (75,205):
        strut(m,(-101,43,z),(-102,135,z+7),7,2)
        strut(m,(-102,135,z+7),(-46,160,z+12),7,2)
    # Torn starboard ribs hang down into the breach.
    strut(m,(100,47,42),(139,115,74),8,2)
    strut(m,(138,112,78),(119,61,147),7,2)
    strut(m,(105,148,178),(150,92,214),6,2)

    # Swept lifting surfaces. Port remains attached; starboard is sheared short.
    port=[(-105,64,-45),(-255,48,38),(-239,57,156),(-106,75,100)]
    quad(m,port,2);quad(m,list(reversed([(x,y-11,z) for x,y,z in port])),1)
    strut(m,(-103,55,-28),(-229,48,146),14,2)
    stb=[(105,64,-32),(191,54,23),(176,61,113),(106,73,88)]
    quad(m,list(reversed(stb)),2);quad(m,[(x,y-10,z) for x,y,z in stb],1)
    strut(m,(104,54,-20),(172,49,101),12,2)

    # Port nacelle is intact and dead. Starboard mount is ripped open; engine is debris.
    x=-210
    rr=[ring(z,38,48,124) for z in (-55,15,95,178)]
    rr=[[(xx+x,yy,zz) for xx,yy,zz in r] for r in rr]
    for a,b in zip(rr,rr[1:]):skin(m,a,b,0)
    nozzle(m,x,84,164,36,54)
    for z in (5,100):m.box(x,124,z,40,3,10,2)

    for z in (18,76,136):
        strut(m,(162,49,z),(218,111,z+8),7,2)
    strut(m,(139,44,6),(224,49,18),13,2)
    strut(m,(143,48,149),(211,87,183),10,2)

    # Crushed belly/skid remains, with one collapsed gear leg and one torn stump.
    m.box(-38,0,-110,132,8,265,1)
    m.box(-106,0,120,56,7,104,2,10)
    strut(m,(-112,7,-172),(-84,34,-146),13,2)
    strut(m,(118,5,118),(102,37,82),11,2)

    # Stabilizer is visibly buckled, not a clean vertical fin.
    quad(m,[(-7,150,104),(-20,211,170),(-36,184,226),(-13,143,222)],1)
    quad(m,[(1,143,222),(25,184,226),(9,211,170),(2,150,104)],1)
    strut(m,(30,167,-34),(68,182,10),3,2)
    return crash_attitude(m)


def detached_engine(Mesh):
    m=Mesh()
    nozzle(m,0,48,-72,39,58,2)
    m.box(0,18,0,82,58,128,1,18)
    m.box(12,64,4,68,18,92,2,-16)
    for z in (-34,8,44):
        strut(m,(-34,26,z),(35,60,z+9),6,2)
    strut(m,(-45,10,-56),(51,15,62),8,2)
    return crash_attitude(m,pitch=4,roll=23)


def torn_panel(Mesh):
    m=Mesh()
    quad(m,[(-74,2,-40),(69,2,-53),(54,6,54),(-52,5,42)],0)
    m.box(-55,1,3,10,7,88,2,-9)
    strut(m,(-68,6,-35),(48,9,45),5,2)
    return m


def recorder(Mesh):
    m=Mesh();m.box(0,0,0,30,13,24,2)
    m.box(0,13,0,24,2,17,3)
    for x in (-16,16):m.box(x,2,0,3,10,29,1)
    m.box(0,5,-14,13,5,3,4)
    return m


def collision_box(Mesh,w,h,d):
    m=Mesh();m.box(0,0,0,w,h,d,7)
    return m


def world_offset(dx,dz):
    a=math.radians(CRASH_YAW);co,si=math.cos(a),math.sin(a)
    return (SITE[0]+dx*co+dz*si,SITE[1]-dx*si+dz*co)


def _finish_fpe(build,name):
    f=build.AS/(name+'.fpe')
    f.write_text(f.read_text()+f'normalMap = {NORMAL}\nnormalStrength = 0.55\nsurfaceMap = {SURFACE}\nreflectance = 0.04\n')


def apply(build):
    models={}
    for name,fn,collision in [
        (NAME,hull,11),
        ('Meridian M17 Detached Engine',detached_engine,11),
        ('Meridian M17 Torn Panel',torn_panel,11),
        ('Meridian Flight Recorder',recorder,1),
    ]:
        p=build.own(name,fn(build.Mesh),ATLAS,collision=collision);_finish_fpe(build,name);models[name]=p

    # Hidden proxy volumes sit fully inside the visible wreck. They are intentionally
    # tighter than the previous boxes so the player does not hit invisible walls beyond
    # torn plating, while still closing the large phase-through holes in the render shell.
    blockers=[
        ('Meridian M17 Collision Forward',144,106,208,0,-174,0),
        ('Meridian M17 Collision Cargo',164,116,220,-4,72,0),
        ('Meridian M17 Collision Port Engine',70,78,160,-208,72,0),
        ('Meridian M17 Collision Starboard Root',86,66,102,132,55,0),
    ]
    for name,w,h,d,dx,dz,dy in blockers:
        p=build.own(name,collision_box(build.Mesh,w,h,d),ATLAS,collision=0)
        _finish_fpe(build,name);models[name]=p

    x,z,y=SITE
    build.add(models[NAME],'M-17 / interrupted colony resupply',x,z,y=y,ry=CRASH_YAW,kind='wreck',
              **{'eleprof.physics':0,'eleprof.phyalways':0})

    for name,w,h,d,dx,dz,dy in blockers:
        bx,bz=world_offset(dx,dz)
        build.add(models[name],'M-17 / collision '+name.rsplit(' ',1)[-1].lower(),
                  bx,bz,y=build.ground(bx,bz)+dy,ry=CRASH_YAW,kind='wreck_collision',
                  script=COLLISION_SCRIPT,
                  **{'eleprof.physics':1,'eleprof.phyalways':1})

    # Detached engine and torn panels make the right-side failure readable from the road.
    ex,ez=world_offset(275,80)
    build.add(models['Meridian M17 Detached Engine'],'M-17 / detached starboard engine',
              ex,ez,y=build.ground(ex,ez)+2,ry=CRASH_YAW+28,kind='wreck_detail',
              **{'rx':7,'rz':18,'eleprof.physics':0,'eleprof.phyalways':0})
    for i,(dx,dz,ang) in enumerate(((218,-38,31),(156,221,-24)),1):
        px,pz=world_offset(dx,dz)
        build.add(models['Meridian M17 Torn Panel'],f'M-17 / torn hull panel {i}',
                  px,pz,y=build.ground(px,pz)+1,ry=CRASH_YAW+ang,kind='wreck_detail',
                  **{'rx':6 if i==1 else -4,'rz':14 if i==1 else -11,
                     'eleprof.physics':0,'eleprof.phyalways':0})

    # Cargo/recorder stay off the combat road and read as a trail away from the rupture.
    cx,cz=world_offset(45,325)
    build.add(r'Aegis Reach\First Light\Meridian Scorched Case.fpe',
              'M-17 / ruptured cargo',cx,cz,y=build.ground(cx,cz),ry=CRASH_YAW+12,kind='wreck_detail')
    ex2,ez2=world_offset(-72,372)
    build.add(r'Aegis Reach\First Light\Meridian Scorched Case.fpe',
              'M-17 / ejected cargo',ex2,ez2,y=build.ground(ex2,ez2),
              ry=CRASH_YAW-28,scale=88,kind='wreck_detail',
              **{'rx':4,'rz':-9})
    rx,rz=world_offset(188,316)
    build.add(models['Meridian Flight Recorder'],'FL FLIGHTLOG',rx,rz,
              y=build.ground(rx,rz),ry=CRASH_YAW-8,kind='record',
              script=r'aegis_reach\firstlight_interact.lua')
    ax,az=world_offset(175,430)
    ammo=r'Max Collection\Weapons\Compact Assault Rifle Ammo.fpe'
    build.add(ammo,'M-17 / recoverable security ammunition',ax,az,
              y=build.ground(ax,az)+28,ry=CRASH_YAW,kind='ammo',
              template=build.T[ammo],script='ammo.lua',
              **{'eleprof.quantity':60,'eleprof.hasweapon_s':r'enhanced\MK18'})

    # Two local practicals make the rupture throw warm light across the hull/ground.
    light=r'_markers\White Light.fpe'
    lights=((205,82,126,0xFF8B42,520),(78,45,32,0xD84A32,260))
    for i,(dx,dy,dz,color,rng) in enumerate(lights,1):
        lx,lz=world_offset(dx,dz)
        build.add(light,f'M-17 / fire practical {i}',lx,lz,
                  y=build.ground(lx,lz)+dy,kind='wreck_light',
                  template=build.T[light],script=r'markers\ConstantLight.lua',
                  **{'eleprof.light.color':color,'eleprof.light.range':rng,
                     'eleprof.light.index':len(build.light_locations)+len(build.crystal_sites)+8+i,
                     'eleprof.light.fLightHasProbe':0})

    return {'name':'Meridian M-17','site':SITE,'lights':2,'ammo':60,'record':'FLIGHTLOG',
            'collision_boxes':len(blockers),'hidden_collision':True,
            'detached_engine':True,'crash_yaw':CRASH_YAW}
