"""Original M-17 cargo lander wreck; one authored roadside story composition.

All dimensions are MAX inches. The flat contact feet sit on native terrain;
the faceted hull has a crushed nose, open aft ribs and asymmetric engine damage.
"""
import math
from meridian_fieldkit import ATLAS, NORMAL, SURFACE, quad, strut

SITE=(-1790,-5560,385)
NAME='Meridian M17 Transport Wreck'


def ring(z,w,bottom,top):
    h=top-bottom
    return [(-w*.64,bottom,z),(w*.64,bottom,z),(w,bottom+h*.23,z),
            (w,top-h*.23,z),(w*.64,top,z),(-w*.64,top,z),
            (-w,top-h*.23,z),(-w,bottom+h*.23,z)]


def skin(m,a,b,tile,skip=()):
    for i in range(8):
        if i in skip: continue
        j=(i+1)%8
        quad(m,[a[j],b[j],b[i],a[i]],tile)


def nozzle(m,x,y,z,radius,length):
    # Twelve-sided flared exhaust, dark inset throat, visible metallic rim.
    rings=[]
    for zz,rr in [(z,radius*.72),(z+length*.75,radius),(z+length,radius*.94)]:
        rings.append([(x+math.cos(i*math.tau/12)*rr,y+math.sin(i*math.tau/12)*rr,zz) for i in range(12)])
    for a,b in zip(rings,rings[1:]):
        for i in range(12):
            j=(i+1)%12;quad(m,[a[i],a[j],b[j],b[i]],2)
    outer=rings[-1]
    inner=[(x+(xx-x)*.78,y+(yy-y)*.78,zz-8) for xx,yy,zz in outer]
    for i in range(12):
        j=(i+1)%12;quad(m,[outer[i],outer[j],inner[j],inner[i]],1)
    # Close the throat deep inside, so the engine does not appear transparent.
    m.box(x,y-radius*.58,z+length-22,radius*1.2,radius*1.16,2,1)


def hull(Mesh):
    m=Mesh()
    sections=[ring(-335,34,8,58),ring(-245,76,22,130),
              ring(-145,108,26,174),ring(30,115,26,174),
              ring(185,108,26,165),ring(270,96,28,143)]
    for i,(a,b) in enumerate(zip(sections,sections[1:])):
        skin(m,a,b,1 if i==4 else 0,skip=(3,4,5) if i==4 else ())
    # The crushed nose is capped; the ruptured aft stays open behind cargo rails.
    a=sections[0]
    for i in range(1,7):
        j=i+1
        start=len(m.verts)
        m.verts.extend((a[0],a[j],a[i]));m.norm.extend([(0,0,-1)]*3)
        m.uv.extend(((1.1/8,.9),(1.9/8,.1),(1.9/8,.9)))
        m.faces.append((start,start+1,start+2))
    # Raised separate cockpit glazing follows the sloped dorsal nose, with ribs.
    quad(m,[(-46,133,-246),(-67,177,-146),(-5,177,-146),(-5,133,-246)],3)
    quad(m,[(5,133,-246),(5,177,-146),(67,177,-146),(46,133,-246)],3)
    strut(m,(0,132,-247),(0,178,-145),5,2)
    for z in (-142,28,183):
        a=ring(z,118,23,178)
        for p,q in zip(a,a[1:]+a[:1]):strut(m,p,q,5,2)
    # Aft structural hoops are naked after the outer panels tore away.
    for z in (222,268):
        a=ring(z,99,28,148)
        for p,q in zip(a,a[1:]+a[:1]):strut(m,p,q,6,2)
    m.box(0,29,142,178,9,225,1)
    for x in (-71,71):m.box(x,38,148,6,7,218,2)
    for x in (-43,43):
        m.box(x,41,126,62,45,91,1)
        for zz in (98,151):m.box(x,40,zz,66,5,7,2)
    # Swept stub wings connect the lifting engines to the load-bearing fuselage.
    for side in (-1,1):
        poly=[(side*100,67,-35),(side*222,57,35),(side*213,65,154),(side*100,77,104)]
        quad(m,list(reversed(poly)) if side==1 else poly,2)
        quad(m,[(x,y-10,z) for x,y,z in poly] if side==1 else list(reversed([(x,y-10,z) for x,y,z in poly])),1)
        strut(m,(side*95,54,-25),(side*210,50,143),13,2)
    # Port nacelle retains its segmented cowling. Starboard is torn open.
    for side in (-1,1):
        x=side*207
        rr=[ring(z,39,48,126) for z in (-40,25,110,181)]
        rr=[[(xx+x,yy,zz) for xx,yy,zz in r] for r in rr]
        for i,(a,b) in enumerate(zip(rr,rr[1:])):
            skin(m,a,b,0 if side<0 else 1,skip=(3,4) if side>0 and i>0 else ())
        nozzle(m,x,85,168,37,56)
        if side>0:
            for z in (40,90,140):strut(m,(x-24,53,z),(x+18,110,z),5,2)
        else:
            for z in (20,105):m.box(x,127,z,42,3,9,2)
    # Compressed landing gear makes contact explicit on the native crash shelf.
    for x in (-122,122):
        for z in (-197,172):
            m.box(x,0,z,45,7,68,2)
            strut(m,(x,7,z),(x*.7,37,z-14),12,2)
    # Bent top stabilizer and broken aerial distinguish this from a field module.
    quad(m,[(-7,170,100),(-7,238,185),(-7,206,247),(-7,151,240)],1)
    quad(m,[(7,151,240),(7,206,247),(7,238,185),(7,170,100)],1)
    strut(m,(38,175,-40),(72,196,18),3,2)
    # Low damaged panel still attached beside the starboard engine.
    quad(m,[(240,50,15),(258,15,38),(250,10,141),(239,52,152)],0)
    return m


def recorder(Mesh):
    m=Mesh();m.box(0,0,0,30,13,24,2)
    m.box(0,13,0,24,2,17,3)
    for x in (-16,16):m.box(x,2,0,3,10,29,1)
    m.box(0,5,-14,13,5,3,4)
    return m


def apply(build):
    models={}
    for name,fn in [(NAME,hull),('Meridian Flight Recorder',recorder)]:
        p=build.own(name,fn(build.Mesh),ATLAS)
        f=build.AS/(name+'.fpe')
        f.write_text(f.read_text()+f'normalMap = {NORMAL}\nnormalStrength = 0.55\nsurfaceMap = {SURFACE}\nreflectance = 0.04\n')
        models[name]=p
    x,z,y=SITE
    build.add(models[NAME],'M-17 / interrupted colony resupply',x,z,y=y,kind='wreck')
    # One detached case and recorder; cargo never scatters across the main road.
    build.add(r'Aegis Reach\First Light\Meridian Scorched Case.fpe','M-17 / ruptured cargo',x+10,z+310,kind='wreck_detail')
    build.add(models['Meridian Flight Recorder'],'FL FLIGHTLOG',x+176,z+307,kind='record',
              script=r'aegis_reach\firstlight_interact.lua')
    ammo=r'Max Collection\Weapons\Compact Assault Rifle Ammo.fpe'
    build.add(ammo,'M-17 / recoverable security ammunition',x+150,z+425,
              y=build.ground(x+150,z+425)+28,kind='ammo',template=build.T[ammo],script='ammo.lua',
              **{'eleprof.quantity':60,'eleprof.hasweapon_s':r'enhanced\MK18'})
    light=r'_markers\White Light.fpe'
    build.add(light,'M-17 / engine fire practical',x+212,z+125,y=y+110,kind='wreck_light',
              template=build.T[light],script=r'markers\ConstantLight.lua',
              **{'eleprof.light.color':0xE99A52,'eleprof.light.range':310,
                 'eleprof.light.index':len(build.light_locations)+len(build.crystal_sites)+9,
                 'eleprof.light.fLightHasProbe':0})
    return {'name':'Meridian M-17','site':SITE,'lights':1,'ammo':60,'record':'FLIGHTLOG'}
