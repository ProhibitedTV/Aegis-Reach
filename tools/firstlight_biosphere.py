"""Primitive Vesper biosphere for FIRST LIGHT.

Vesper's atmosphere is not itself evidence of life, but the setting intentionally
supports a sparse indigenous biosphere. Life follows residual brine, wind shelter and
human waste heat, then becomes noticeably rarer toward the AEGIS excavation.

All meshes here are original procedural geometry. Airborne drift-midges reuse an
installed MAX particle preset by reference; no licensed media is copied into the repo.
"""
import math
import random
from PIL import Image,ImageDraw
from meridian_fieldkit import quad,strut
from firstlight_world import ROUTE,RETURN,road_sample

TEXTURE='vesper_biosphere.png'
SCRIPT=r'aegis_reach\firstlight_biosphere.lua'
PARTICLE=r'_markers\Particles.fpe'
MIDGE_PRESET='embers2'

# x, z, editor scale, yaw. Keep the route itself clean; these live on shoulders,
# sheltered benches and facility outskirts rather than becoming traversal clutter.
SCRUB_SITES=(
 (-2920,-7650,92,14),(-2780,-7040,84,116),(-990,-7600,72,202),(-3120,-6750,96,48),
 (-2630,-6250,82,271),(1460,-6080,88,31),(-2140,-5200,105,147),(1540,-5000,78,244),
 (-1180,-4300,90,78),(1220,-3890,76,336),(-1980,-2800,86,193),(1180,-2700,72,25),
 (-2350,-600,82,109),(-150,-1540,74,287),(2620,650,78,51),(1900,2600,64,226),
)

# Brine-reed analogs hug the two residual pools. Their roots can sit slightly below
# the water plane; all stems and leaves remain visual-only.
REED_SITES=(
 (430,-5590,78,12),(560,-5790,92,66),(720,-5740,82,141),
 (840,-5520,88,207),(1040,-5200,76,286),(1190,-5400,86,332),
)

# Tiny noncombat ground fauna. Their movement is an object-space visual loop only.
SKITTER_SITES=(
 (-2860,-7210,84,0),(470,-5650,76,0),(1010,-5380,72,0),
 (-2480,-5850,82,0),(-2250,-1040,78,0),(2360,720,70,0),
)

# Local airborne life. The same native emitter is recolored/slowed in Lua until it
# reads as a sparse midge/spore cloud rather than sparks.
MIDGE_SITES=(
 (560,-5620,105),(980,-5380,95),(-2150,-7550,125),(-1700,-540,145),
)


def _atlas(folder):
    """Create a tiny deterministic eight-tile albedo atlas for native APBR."""
    tile=128
    colors=[
        (48,58,50),(91,106,88),(98,82,103),(92,121,112),
        (147,151,119),(35,52,56),(73,91,82),(116,104,91),
    ]
    image=Image.new('RGB',(tile*8,tile))
    rng=random.Random(1717)
    for i,base in enumerate(colors):
        patch=Image.new('RGB',(tile,tile),base);draw=ImageDraw.Draw(patch)
        for _ in range(900):
            x=rng.randrange(tile);y=rng.randrange(tile);n=rng.randrange(-12,13)
            draw.point((x,y),fill=tuple(max(0,min(255,c+n)) for c in base))
        for y in range(15,tile,28):
            draw.line((8,y,tile-9,y+rng.randrange(-5,6)),fill=tuple(max(0,c-18) for c in base),width=1)
        image.paste(patch,(i*tile,0))
    image.save(folder/TEXTURE,optimize=True)


def _double_quad(m,vs,tile):
    quad(m,vs,tile)
    quad(m,list(reversed(vs)),tile)


def _leaf(m,base,angle,length,width,rise,tile):
    x,y,z=base
    dx,dz=math.sin(angle),math.cos(angle)
    sx,sz=math.cos(angle),-math.sin(angle)
    tip=(x+dx*length,y+rise,z+dz*length)
    root_half=width*.48;tip_half=width*.10
    vs=[
        (x-sx*root_half,y,z-sz*root_half),
        (x+sx*root_half,y,z+sz*root_half),
        (tip[0]+sx*tip_half,tip[1],tip[2]+sz*tip_half),
        (tip[0]-sx*tip_half,tip[1],tip[2]-sz*tip_half),
    ]
    _double_quad(m,vs,tile)


def salt_scrub(Mesh):
    """Low halophile fan: woody dark stems with thick grey-green/violet blades."""
    m=Mesh()
    for i in range(7):
        a=math.radians(i*51+13)
        radius=8+(i%3)*4
        bx,bz=math.sin(a)*radius,math.cos(a)*radius
        height=45+(i%4)*11
        tx,tz=bx+math.sin(a+.25)*18,bz+math.cos(a+.25)*18
        strut(m,(bx,0,bz),(tx,height,tz),3.2,0)
        _leaf(m,(tx,height*.44,tz),a-.72,27+(i%2)*8,10,9,1 if i%3 else 2)
        _leaf(m,(tx,height*.62,tz),a+.68,33+(i%3)*5,11,12,1)
        _leaf(m,(tx,height*.78,tz),a+.05,24+(i%2)*7,9,15,2 if i%2 else 3)
    return m


def brine_reed(Mesh):
    """Short mineral-fed reed analog suited to hypersaline pool margins."""
    m=Mesh()
    for i in range(9):
        a=math.radians(i*137.5)
        radius=4+(i%4)*4
        bx,bz=math.sin(a)*radius,math.cos(a)*radius
        height=54+(i%5)*10
        tx,tz=bx+math.sin(a)*7,bz+math.cos(a)*7
        strut(m,(bx,0,bz),(tx,height,tz),1.8,3)
        _leaf(m,(bx,height*.35,bz),a+1.15,36,5,17,3)
        _leaf(m,(bx,height*.48,bz),a-1.08,30,4,12,4)
    return m


def skitter(Mesh):
    """Small six-legged crust grazer; roughly hand-sized at authored scales."""
    m=Mesh()
    m.box(0,2,0,10,4,15,5)
    m.box(0,4,-8,7,3,6,6)
    for z in (-5,0,5):
        for side in (-1,1):
            hip=(side*4,3,z)
            knee=(side*8,1,z+side*1.5)
            foot=(side*13,0,z+side*3)
            strut(m,hip,knee,1.2,6)
            strut(m,knee,foot,1.0,6)
    return m


def _finish_fpe(build,name):
    f=build.AS/(name+'.fpe')
    text=f.read_text(errors='replace')
    text=text.replace('roughnessStrength = 0.82','roughnessStrength = 1.0')
    text=text.replace('metalnessStrength = 0.22','metalnessStrength = 0.0')
    f.write_text(text+'reflectance = 0.02\n')


def _clear_of_routes(x,z,minimum=300):
    return min(road_sample(x,z,ROUTE)[0],road_sample(x,z,RETURN)[0])>=minimum


def apply(build):
    _atlas(build.AS)
    models={}
    for name,fn in (
        ('Vesper Salt Scrub',salt_scrub),
        ('Vesper Brine Reed',brine_reed),
        ('Vesper Crust Skitter',skitter),
    ):
        path=build.own(name,fn(build.Mesh),TEXTURE,collision=11)
        _finish_fpe(build,name);models[name]=path

    for i,(x,z,scale,yaw) in enumerate(SCRUB_SITES,1):
        if not _clear_of_routes(x,z):raise ValueError('biosphere scrub enters route')
        build.add(models['Vesper Salt Scrub'],f'Vesper salt scrub {i:02d}',x,z,
                  y=build.ground(x,z),ry=yaw,scale=scale,kind='biosphere_flora',
                  **{'eleprof.physics':0,'eleprof.phyalways':0})

    for i,(x,z,scale,yaw) in enumerate(REED_SITES,1):
        if not _clear_of_routes(x,z):raise ValueError('biosphere reed enters route')
        build.add(models['Vesper Brine Reed'],f'Vesper brine reed {i:02d}',x,z,
                  y=build.ground(x,z),ry=yaw,scale=scale,kind='biosphere_flora',
                  **{'eleprof.physics':0,'eleprof.phyalways':0})

    for i,(x,z,scale,yaw) in enumerate(SKITTER_SITES,1):
        build.add(models['Vesper Crust Skitter'],f'FL BIO SKITTER {i:02d}',x,z,
                  y=build.ground(x,z)+1,ry=yaw,scale=scale,kind='biosphere_creature',
                  script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':0})

    preset=build.INSTALL/'particlesbank'/(MIDGE_PRESET+'.arx')
    if not preset.is_file():raise FileNotFoundError('Required installed MAX particle preset: '+MIDGE_PRESET)
    for i,(x,z,height) in enumerate(MIDGE_SITES,1):
        build.add(PARTICLE,f'FL BIO MIDGES {i:02d}',x,z,
                  y=build.ground(x,z)+height,scale=7,kind='biosphere_particle',script=SCRIPT,
                  **{'eleprof.physics':0,'eleprof.phyalways':0,
                     'eleprof.newparticle.emittername':'particlesbank/'+MIDGE_PRESET,
                     'eleprof.newparticle.bParticle_Show_At_Start':0,
                     'eleprof.newparticle.bParticle_Preview':0,
                     'eleprof.newparticle.bParticle_Looping_Animation':1,
                     'eleprof.newparticle.bParticle_Full_Screen':0})

    return {
        'ecology':'primitive halophile biosphere',
        'flora_count':len(SCRUB_SITES)+len(REED_SITES),
        'scrub_count':len(SCRUB_SITES),'reed_count':len(REED_SITES),
        'skitter_count':len(SKITTER_SITES),'midge_cloud_count':len(MIDGE_SITES),
        'life_gradient':'brine + shelter + waste heat; deliberately sparse toward AEGIS',
        'navigation_collision':False,'damage':False,
    }
