"""Vesper biosphere visual-language pass for FIRST LIGHT.

The first prototype proved that ambient life can coexist with MAX combat/navigation,
but its boxy fauna, disconnected leaves and stock desert shrubs did not read as one
science-fiction ecosystem. This pass makes the biosphere the visual owner:

* layered glass-fan membranes replace stick-and-leaf scrub;
* mineral-fed brine cups replace terrestrial reed silhouettes;
* creeping salt-lace mats add a low third growth strategy;
* crust skitters use segmented shells, eight hooked legs and antennae;
* veilwings add actual small airborne fauna so particles are no longer asked to sell life;
* legacy stock desert bushes are retired at build time rather than mixed into the biome.

Everything remains visual-only: collision mode 11, no combat/nav authority, and local
runtime animation only when the player is close enough to notice it.
"""
import math
import random
from PIL import Image,ImageDraw,ImageFilter
from meridian_fieldkit import quad,strut
from firstlight_world import ROUTE,RETURN,road_sample

TEXTURE='vesper_biosphere.png'
NORMAL='vesper_biosphere_normal.png'
SURFACE='vesper_biosphere_surface.png'
EMISSION='vesper_biosphere_emission.png'
SCRIPT=r'aegis_reach\firstlight_biosphere.lua'
PARTICLE=r'_markers\Particles.fpe'
MIDGE_PRESET='embers2'
TILE=256

# Existing route-safe sites are deliberately reused. The species mix changes instead
# of simply adding more clutter. Life remains sparse as the player approaches AEGIS.
SCRUB_SITES=(
 (-2920,-7650,92,14),(-2780,-7040,84,116),(-990,-7600,72,202),(-3120,-6750,96,48),
 (-2630,-6250,82,271),(1460,-6080,88,31),(-2140,-5200,105,147),(1540,-5000,78,244),
 (-1180,-4300,90,78),(1220,-3890,76,336),
)
REED_SITES=(
 (430,-5590,78,12),(560,-5790,92,66),(720,-5740,82,141),
 (840,-5520,88,207),(1040,-5200,76,286),(1190,-5400,86,332),
)
MAT_SITES=(
 (-1980,-2800,86,193),(1180,-2700,72,25),(-2350,-600,82,109),
 (-150,-1540,74,287),(2620,650,78,51),
)
SKITTER_SITES=(
 (-2860,-7210,84,0),(470,-5650,76,0),(1010,-5380,72,0),
 (-2480,-5850,82,0),(-2250,-1040,78,0),(2360,720,70,0),
)
VEILWING_SITES=(
 (-2780,-7380,105,78,18),(-2380,-6500,92,72,211),(540,-5660,118,74,42),
 (1030,-5350,112,70,164),(-2180,-1120,104,72,284),(860,-720,96,68,330),
)
# These are now a secondary microscopic layer. Actual mesh fauna carries the biological
# read; the particles only imply spores/tiny colonial organisms in warm/briny niches.
MIDGE_SITES=(
 (560,-5620,105),(980,-5380,95),(-2150,-7550,125),(-1700,-540,145),
)


def _noise_color(base,n):
    return tuple(max(0,min(255,c+n)) for c in base)


def _normal_from_height(height):
    blurred=height.filter(ImageFilter.GaussianBlur(1.0));hp=blurred.load()
    normal=Image.new('RGB',height.size,(128,128,255));np=normal.load()
    w,h=height.size
    for y in range(1,h-1):
        for x in range(1,w-1):
            nx=-(hp[x+1,y]-hp[x-1,y])*.055
            ny=-(hp[x,y+1]-hp[x,y-1])*.055
            length=math.sqrt(nx*nx+ny*ny+1.0)
            np[x,y]=(round(127.5+127.5*nx/length),round(127.5+127.5*ny/length),round(127.5+127.5/length))
    return normal


def _atlas(folder):
    """Generate coordinated albedo/normal/surface/emission maps for one biosphere."""
    rng=random.Random(1717)
    albedo=Image.new('RGB',(TILE*8,TILE))
    normal=Image.new('RGB',albedo.size,(128,128,255))
    surface=Image.new('RGBA',albedo.size,(255,220,0,48))
    emission=Image.new('RGB',albedo.size,(0,0,0))
    bases=[
        (32,47,48),   # 0 mineral root / vein
        (70,91,103),  # 1 glass-fan membrane
        (86,66,116),  # 2 fan rim / live vein
        (54,92,96),   # 3 brine-cup exterior
        (154,164,146),# 4 pale cup interior / salt tissue
        (38,31,53),   # 5 fauna chitin
        (45,72,83),   # 6 sensory membrane / luminous spots
        (104,98,116), # 7 creeping salt lace
    ]
    rough=(212,172,150,184,208,138,158,220)
    reflect=(32,52,58,45,34,62,58,28)
    for tile,base in enumerate(bases):
        patch=Image.new('RGB',(TILE,TILE),base);d=ImageDraw.Draw(patch)
        height=Image.new('L',(TILE,TILE),128);hd=ImageDraw.Draw(height)
        glow=Image.new('RGB',(TILE,TILE),(0,0,0));gd=ImageDraw.Draw(glow)
        surf=Image.new('RGBA',(TILE,TILE),(255,rough[tile],0,reflect[tile]));sd=ImageDraw.Draw(surf)

        # Fine mottling avoids plastic-flat generated surfaces without baking lighting.
        for _ in range(7500):
            x=rng.randrange(TILE);y=rng.randrange(TILE);n=rng.randrange(-10,11)
            d.point((x,y),fill=_noise_color(base,n))
            sd.point((x,y),fill=(255,max(80,min(245,rough[tile]+n)),0,reflect[tile]))

        if tile==0:
            # Rope-like mineral fibres and root scars.
            for x in range(18,TILE,29):
                pts=[]
                for y in range(-8,TILE+8,12):pts.append((x+int(math.sin(y*.045+x)*5),y))
                d.line(pts,fill=(20,34,35),width=4);hd.line(pts,fill=108,width=4)
        elif tile in (1,2):
            # Broad pressure membranes with branching conductive veins.
            for branch in range(7):
                root=(TILE//2+rng.randrange(-28,29),TILE+8)
                tip=(24+branch*34+rng.randrange(-9,10),-8)
                mid=((root[0]+tip[0])//2+rng.randrange(-18,19),TILE//2)
                pts=[root,mid,tip]
                d.line(pts,fill=(116,113,148) if tile==1 else (143,102,177),width=2+(branch%2))
                hd.line(pts,fill=147,width=2)
                if tile==2:
                    gd.line(pts,fill=(28,94,116),width=3)
            for y in range(18,TILE,34):
                d.arc((18,y-20,TILE-18,y+26),5,175,fill=(53,71,91),width=1)
        elif tile in (3,4):
            # Cellular/radial brine-fed tissue rather than grass texture.
            cx,cy=TILE//2,TILE//2
            for r in range(20,125,18):
                d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(77,123,122) if tile==3 else (126,145,127),width=2)
                hd.ellipse((cx-r,cy-r,cx+r,cy+r),outline=142,width=2)
            for a in range(0,360,30):
                x=cx+math.cos(math.radians(a))*130;y=cy+math.sin(math.radians(a))*130
                d.line((cx,cy,x,y),fill=(62,109,110) if tile==3 else (136,151,132),width=1)
            if tile==4:
                gd.ellipse((104,104,152,152),fill=(18,55,62))
        elif tile==5:
            # Overlapping mineral-chitin plates.
            for y in range(18,TILE,28):
                offset=14 if (y//28)%2 else 0
                for x in range(-10+offset,TILE,36):
                    d.arc((x,y-12,x+38,y+18),185,355,fill=(69,55,86),width=3)
                    hd.arc((x,y-12,x+38,y+18),185,355,fill=151,width=3)
        elif tile==6:
            # Sensory membranes with restrained cold bioluminescent ocelli.
            for _ in range(36):
                x=rng.randrange(20,TILE-20);y=rng.randrange(20,TILE-20);r=rng.randrange(2,6)
                d.ellipse((x-r,y-r,x+r,y+r),fill=(81,137,147));hd.ellipse((x-r,y-r,x+r,y+r),fill=151)
                gd.ellipse((x-r,y-r,x+r,y+r),fill=(24,91,110))
        else:
            # Creeping salt-lace: branching pale channels in a leathery mat.
            for branch in range(11):
                y=18+branch*21
                pts=[]
                for x in range(-5,TILE+10,18):pts.append((x,y+int(math.sin(x*.065+branch)*9)))
                d.line(pts,fill=(139,127,151),width=4);hd.line(pts,fill=148,width=4)
            for _ in range(90):
                x=rng.randrange(TILE);y=rng.randrange(TILE);r=rng.randrange(1,4)
                d.ellipse((x-r,y-r,x+r,y+r),fill=(82,75,100))

        albedo.paste(patch,(tile*TILE,0))
        normal.paste(_normal_from_height(height),(tile*TILE,0))
        surface.paste(surf,(tile*TILE,0))
        emission.paste(glow.filter(ImageFilter.GaussianBlur(1.3)),(tile*TILE,0))

    for name,image in ((TEXTURE,albedo),(NORMAL,normal),(SURFACE,surface),(EMISSION,emission)):
        image.save(folder/name,optimize=True)


def _double_quad(m,vs,tile):
    quad(m,vs,tile);quad(m,list(reversed(vs)),tile)


def _tri(m,a,b,c,tile):
    ux,uy,uz=b[0]-a[0],b[1]-a[1],b[2]-a[2]
    vx,vy,vz=c[0]-a[0],c[1]-a[1],c[2]-a[2]
    nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx
    length=math.sqrt(nx*nx+ny*ny+nz*nz);assert length>1e-8
    n=(nx/length,ny/length,nz/length);start=len(m.verts)
    for p,uv in zip((a,b,c),((.16,.86),(.84,.86),(.50,.14))):
        m.verts.append(p);m.norm.append(n);m.uv.append(((tile+uv[0])/8,uv[1]))
    m.faces.append((start,start+1,start+2))


def _ellipsoid(m,center,rx,ry,rz,tile,segments=10,rings=4):
    cx,cy,cz=center
    rows=[]
    for j in range(1,rings+1):
        phi=-math.pi/2+math.pi*j/(rings+1)
        rr=math.cos(phi);y=cy+math.sin(phi)*ry
        rows.append([(cx+math.cos(i*math.tau/segments)*rx*rr,y,
                      cz+math.sin(i*math.tau/segments)*rz*rr) for i in range(segments)])
    bottom=(cx,cy-ry,cz);top=(cx,cy+ry,cz)
    for i in range(segments):
        j=(i+1)%segments;_tri(m,bottom,rows[0][j],rows[0][i],tile)
    for a,b in zip(rows,rows[1:]):
        for i in range(segments):
            j=(i+1)%segments;quad(m,[a[i],a[j],b[j],b[i]],tile)
    for i in range(segments):
        j=(i+1)%segments;_tri(m,rows[-1][i],rows[-1][j],top,tile)


def _ribbon_blade(m,origin,angle,height,width,lean,curl,phase=0):
    ox,oy,oz=origin;points=[]
    for i in range(6):
        t=i/5
        bend=lean*(t**1.45);side=curl*math.sin(t*math.pi)*(.35+.65*t)
        dx=math.sin(angle)*bend+math.cos(angle)*side
        dz=math.cos(angle)*bend-math.sin(angle)*side
        points.append((ox+dx,oy+height*t,oz+dz))
    for i,(a,b) in enumerate(zip(points,points[1:])):
        ta=i/5;tb=(i+1)/5
        wa=width*(.20+.82*math.sin(math.pi*min(.96,max(.04,ta+.07)))**.66)
        wb=width*(.14+.82*math.sin(math.pi*min(.96,max(.04,tb+.07)))**.66)
        sa=(math.cos(angle)*wa*.5,0,-math.sin(angle)*wa*.5)
        sb=(math.cos(angle)*wb*.5,0,-math.sin(angle)*wb*.5)
        tile=2 if i>=3 and phase%2==0 else 1
        _double_quad(m,[(a[0]-sa[0],a[1],a[2]-sa[2]),(a[0]+sa[0],a[1],a[2]+sa[2]),
                        (b[0]+sb[0],b[1],b[2]+sb[2]),(b[0]-sb[0],b[1],b[2]-sb[2])],tile)
    # One structural vein unifies the membrane visually without turning it into a stick plant.
    strut(m,points[0],points[-2],.85,2)


def salt_scrub(Mesh):
    """Layered mineral-rooted glass fan; broad membranes form one coherent silhouette."""
    m=Mesh();_ellipsoid(m,(0,5,0),18,6,14,0,segments=12,rings=4)
    for i in range(7):
        angle=math.radians(i*51+11);radius=5+(i%3)*4
        origin=(math.sin(angle)*radius,1,math.cos(angle)*radius)
        _ribbon_blade(m,origin,angle,58+(i%4)*11,24+(i%3)*5,22+(i%2)*10,
                      (-1 if i%2 else 1)*(8+(i%3)*3),i)
    return m


def _cup(m,cx,cz,height,rim,phase):
    segments=12;rings=[]
    for level,radius in ((1.0,rim*.17),(height*.42,rim*.47),(height*.76,rim*.78),(height,rim)):
        ring=[]
        for i in range(segments):
            a=i*math.tau/segments
            wobble=1+.08*math.sin(a*3+phase)+.04*math.sin(a*5-phase)
            yy=level+(2.4*math.sin(a*4+phase) if level==height else 0)
            ring.append((cx+math.cos(a)*radius*wobble,yy,cz+math.sin(a)*radius*wobble))
        rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        for i in range(segments):
            j=(i+1)%segments;quad(m,[a[i],a[j],b[j],b[i]],3)
    inner=[]
    for i,p in enumerate(rings[-1]):
        a=i*math.tau/segments
        inner.append((cx+math.cos(a)*rim*.43,height*.47,cz+math.sin(a)*rim*.43))
    for i in range(segments):
        j=(i+1)%segments;quad(m,[rings[-1][j],rings[-1][i],inner[i],inner[j]],4)
    _ellipsoid(m,(cx,4,cz),rim*.29,5,rim*.29,0,segments=10,rings=3)
    for i in (1,5,9):
        a=i*math.tau/segments+phase*.08
        strut(m,(cx,height*.43,cz),(cx+math.cos(a)*rim*.38,height*1.05,cz+math.sin(a)*rim*.38),.7,2)


def brine_reed(Mesh):
    """Cluster of open mineral-fed brine cups; intentionally unlike terrestrial reeds."""
    m=Mesh()
    for cx,cz,height,rim,phase in ((-14,-8,57,18,.3),(12,5,74,22,1.4),(4,-18,46,15,2.6)):
        _cup(m,cx,cz,height,rim,phase)
    return m


def _ground_ribbon(m,angle,length,width,phase):
    pts=[]
    for i in range(6):
        t=i/5;radius=length*t;a=angle+.10*math.sin(t*math.pi*2+phase)
        pts.append((math.sin(a)*radius,.7+1.4*math.sin(t*math.pi),math.cos(a)*radius))
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        wa=width*(1-.46*(i/5));wb=width*(1-.46*((i+1)/5))
        sx,sz=math.cos(angle),-math.sin(angle)
        _double_quad(m,[(a[0]-sx*wa/2,a[1],a[2]-sz*wa/2),(a[0]+sx*wa/2,a[1],a[2]+sz*wa/2),
                        (b[0]+sx*wb/2,b[1],b[2]+sz*wb/2),(b[0]-sx*wb/2,b[1],b[2]-sz*wb/2)],7)
    tip=pts[-1];_ellipsoid(m,(tip[0],3,tip[2]),4.8,4,4.8,6,segments=8,rings=3)


def salt_lace(Mesh):
    """Low creeping colony: branching salt membranes with sensory/reproductive nodules."""
    m=Mesh();_ellipsoid(m,(0,3,0),13,4,11,7,segments=12,rings=3)
    for i in range(8):_ground_ribbon(m,math.radians(i*45+9),34+(i%3)*9,8+(i%2)*3,i*.8)
    return m


def skitter(Mesh):
    """Eight-legged mineral-chitin grazer with segmented body, hooked legs and antennae."""
    m=Mesh()
    _ellipsoid(m,(0,8,3),9,5.2,13,5,segments=12,rings=5)
    _ellipsoid(m,(0,8,-9),7.2,4.6,8,5,segments=10,rings=4)
    _ellipsoid(m,(0,8,15),7.5,4.7,9,5,segments=10,rings=4)
    # Dorsal sensory ridge and paired ocelli.
    strut(m,(0,12,-7),(0,13,18),1.4,6)
    for side in (-1,1):_ellipsoid(m,(side*3.0,10,-15),1.8,1.5,1.8,6,segments=8,rings=3)
    # Four leg pairs create an unmistakably non-terrestrial silhouette.
    for index,z in enumerate((-8,-2,5,11)):
        reach=15+(index%2)*2
        for side in (-1,1):
            hip=(side*6.5,7,z);knee=(side*reach,5,z+(index-1.5)*1.7);foot=(side*(reach+7),1.2,z+(index-1.5)*3.6)
            strut(m,hip,knee,1.25,5);strut(m,knee,foot,.9,0)
    for side in (-1,1):
        strut(m,(side*2.5,9,-15),(side*7,11,-22),.75,5)
        strut(m,(side*7,11,-22),(side*12,7,-28),.55,6)
    return m


def veilwing(Mesh):
    """Small atmospheric grazer with a spindle body and four pressure-sail membranes."""
    m=Mesh();_ellipsoid(m,(0,7,0),4.5,4,13,5,segments=10,rings=4)
    _ellipsoid(m,(0,7,-12),3.2,3.1,4.5,6,segments=8,rings=3)
    # Paired fore/aft sails. The geometry is broad and faceted rather than insect wings.
    sails=[
        [(-3,8,-5),(-30,10,-13),(-24,15,5),(-2,10,5)],
        [(3,8,-5),(2,10,5),(24,15,5),(30,10,-13)],
        [(-3,8,5),(-21,8,10),(-14,12,22),(-1,9,12)],
        [(3,8,5),(1,9,12),(14,12,22),(21,8,10)],
    ]
    for i,vs in enumerate(sails):_double_quad(m,vs,2 if i<2 else 1)
    for side in (-1,1):
        strut(m,(side*1.5,8,9),(side*7,6,25),.7,5)
        _ellipsoid(m,(side*2.2,8,-16),1.4,1.2,1.4,6,segments=7,rings=3)
    return m


def _finish_fpe(build,name,emissive=.08):
    f=build.AS/(name+'.fpe');text=f.read_text(errors='replace')
    text=text.replace('roughnessStrength = 0.82','roughnessStrength = 1.0').replace('metalnessStrength = 0.22','metalnessStrength = 1.0')
    f.write_text(text+f'normalMap = {NORMAL}\nnormalStrength = 0.70\nsurfaceMap = {SURFACE}\nreflectance = 0.04\n'
                 f'emissiveMap = {EMISSION}\nemissiveStrength = {emissive:.2f}\n')


def _clear_of_routes(x,z,minimum=300):
    return min(road_sample(x,z,ROUTE)[0],road_sample(x,z,RETURN)[0])>=minimum


def _retire_legacy_shrubs(build):
    """Zero-scale the old Earth-desert stock shrubs without disturbing base composition."""
    retired=0
    for entity,placement in zip(build.entities,build.placements):
        if placement.get('name')!='Vesper / salt scrub':continue
        for suffix in ('scalex','scaley','scalez'):build.set_suffix(entity,suffix,-100)
        build.set_suffix(entity,'eleprof.physics',0)
        placement['kind']='retired_vegetation';placement['retired_by']='firstlight_biosphere';retired+=1
    return retired


def apply(build):
    _atlas(build.AS);retired=_retire_legacy_shrubs(build)
    models={}
    specs=(
        ('Vesper Glass Fan',salt_scrub,.10),('Vesper Brine Cup',brine_reed,.08),
        ('Vesper Salt Lace',salt_lace,.07),('Vesper Crust Skitter',skitter,.11),
        ('Vesper Veilwing',veilwing,.15),
    )
    for name,fn,emissive in specs:
        path=build.own(name,fn(build.Mesh),TEXTURE,collision=11);_finish_fpe(build,name,emissive);models[name]=path

    for i,(x,z,scale,yaw) in enumerate(SCRUB_SITES,1):
        if not _clear_of_routes(x,z):raise ValueError('biosphere glass fan enters route')
        build.add(models['Vesper Glass Fan'],f'Vesper glass fan {i:02d}',x,z,y=build.ground(x,z),ry=yaw,scale=scale,
                  kind='biosphere_flora',**{'eleprof.physics':0,'eleprof.phyalways':0})
    for i,(x,z,scale,yaw) in enumerate(REED_SITES,1):
        if not _clear_of_routes(x,z):raise ValueError('biosphere brine cup enters route')
        build.add(models['Vesper Brine Cup'],f'Vesper brine cup {i:02d}',x,z,y=build.ground(x,z),ry=yaw,scale=scale,
                  kind='biosphere_flora',**{'eleprof.physics':0,'eleprof.phyalways':0})
    for i,(x,z,scale,yaw) in enumerate(MAT_SITES,1):
        if not _clear_of_routes(x,z):raise ValueError('biosphere salt lace enters route')
        build.add(models['Vesper Salt Lace'],f'Vesper salt lace {i:02d}',x,z,y=build.ground(x,z),ry=yaw,scale=scale,
                  kind='biosphere_flora',**{'eleprof.physics':0,'eleprof.phyalways':0})

    for i,(x,z,scale,yaw) in enumerate(SKITTER_SITES,1):
        build.add(models['Vesper Crust Skitter'],f'FL BIO SKITTER {i:02d}',x,z,y=build.ground(x,z)+1,ry=yaw,scale=scale,
                  kind='biosphere_creature',script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':0})
    for i,(x,z,height,scale,yaw) in enumerate(VEILWING_SITES,1):
        build.add(models['Vesper Veilwing'],f'FL BIO VEILWING {i:02d}',x,z,y=build.ground(x,z)+height,ry=yaw,scale=scale,
                  kind='biosphere_creature',script=SCRIPT,**{'eleprof.physics':0,'eleprof.phyalways':0})

    preset=build.INSTALL/'particlesbank'/(MIDGE_PRESET+'.arx')
    if not preset.is_file():raise FileNotFoundError('Required installed MAX particle preset: '+MIDGE_PRESET)
    for i,(x,z,height) in enumerate(MIDGE_SITES,1):
        build.add(PARTICLE,f'FL BIO SPORES {i:02d}',x,z,y=build.ground(x,z)+height,scale=5,
                  kind='biosphere_particle',script=SCRIPT,
                  **{'eleprof.physics':0,'eleprof.phyalways':0,
                     'eleprof.newparticle.emittername':'particlesbank/'+MIDGE_PRESET,
                     'eleprof.newparticle.bParticle_Show_At_Start':0,
                     'eleprof.newparticle.bParticle_Preview':0,
                     'eleprof.newparticle.bParticle_Looping_Animation':1,
                     'eleprof.newparticle.bParticle_Full_Screen':0})

    return {
        'ecology':'primitive halophile / mineral-membrane biosphere',
        'visual_language':'glass-fan membranes + brine cups + salt lace + segmented mineral-chitin fauna',
        'flora_count':len(SCRUB_SITES)+len(REED_SITES)+len(MAT_SITES),
        'glass_fan_count':len(SCRUB_SITES),'brine_cup_count':len(REED_SITES),'salt_lace_count':len(MAT_SITES),
        'skitter_count':len(SKITTER_SITES),'veilwing_count':len(VEILWING_SITES),'midge_cloud_count':len(MIDGE_SITES),
        'legacy_stock_shrubs_retired':retired,
        'life_gradient':'brine + shelter + waste heat; deliberately barren toward AEGIS',
        'navigation_collision':False,'damage':False,
    }
