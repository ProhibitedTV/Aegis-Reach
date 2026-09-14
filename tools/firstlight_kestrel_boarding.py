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
    top=[(-62,42,398),(-72,8,526),(72,8,526),(62,42,398)]
    bottom=[(-62,38,398),(62,38,398),(72,4,526),(-72,4,526)]
    quad(m,top,7)
    quad(m,bottom,2)
    quad(m,[top[0],bottom[3],bottom[0],top[3]],2)
    quad(m,[top[1],top[2],bottom[2],bottom[3]],2)
    quad(m,[top[3],bottom[0],bottom[1],top[2]],2)
    quad(m,[top[0],top[1],bottom[2],bottom[1]],2)
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
