"""Landed-only boarding collision for the FIRST LIGHT Broadwing Kestrel.

The moving ship meshes stay non-physical. One tiny polygon proxy covers only the
landed vestibule floor and rear ramp, and its Lua controller enables collision
only while the extraction Kestrel is actually down.
"""
from meridian_fieldkit import quad
from firstlight_kestrel import TEXTURE,LANDED_CONTACT_Y

NAME='Vanguard Kestrel Boarding Collision'
SCRIPT=r'aegis_reach\firstlight_kestrel_boarding.lua'
LZ=(0,-2350)


def boarding_collision_mesh(Mesh):
    m=Mesh()
    # Low-poly vestibule slab. The top face meets the visual cargo floor at Y=42.
    m.box(0,38,338,124,4,116,7)

    # Closed four-inch ramp slab, matching the visual landed-state ramp exactly.
    a=(-62,42,398);b=(-72,8,526);c=(72,8,526);d=(62,42,398)
    aa=(-62,38,398);bb=(-72,4,526);cc=(72,4,526);dd=(62,38,398)
    quad(m,[a,b,c,d],7)       # walking face
    quad(m,[aa,dd,cc,bb],2)   # underside
    quad(m,[a,aa,bb,b],2)     # port edge
    quad(m,[b,bb,cc,c],2)     # terrain tip
    quad(m,[d,c,cc,dd],2)     # starboard edge
    quad(m,[a,d,dd,aa],2)     # hinge edge
    return m


def apply(build):
    proxy=build.own(NAME,boarding_collision_mesh(build.Mesh),TEXTURE,collision=1)
    x,z=LZ
    y=build.ground(x,z)-LANDED_CONTACT_Y
    build.add(
        proxy,'FL KESTREL BOARDING COLLISION',x,z,y=y,ry=180,
        kind='vehicle_collision',script=SCRIPT,
        **{'eleprof.physics':1,'eleprof.phyalways':1,'eleprof.isimmobile':1}
    )
    build.placements[-1].update(
        landing_only=True,
        boarding_surface='rear ramp + vestibule floor',
        collision_mode='polygon',
    )
    return {
        'proxy_entities':1,
        'asset':NAME,
        'landing_only':True,
        'collision_mode':'polygon',
        'surface':'rear ramp + vestibule floor',
        'landed_contact_y':LANDED_CONTACT_Y,
    }
