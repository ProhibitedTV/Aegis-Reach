"""Sparse CineGuru MAX story cameras for FIRST LIGHT.

The mission remains playable if CineGuru is unavailable: these are presentation
entities only. Runtime progression lives in the normal FIRST LIGHT director/interact
scripts and firstlight_cinematic.lua simply requests named cameras when appropriate.
"""
import math

CAMERA_SCRIPT=r'Cine Guru MAX\cg_cinematic_camera.lua'
CONTROLLER_SCRIPT=r'aegis_reach\firstlight_cinematic.lua'
MARKER=r'Aegis Reach\Supply Crate.fpe'

SHOTS=(
    # beat, entity name, camera x/z, height above terrain, target x/z, target height
    ('ARRIVAL','FL CG ARRIVAL',-360,-8820,340,-2050,-7250,95),
    ('MIRA_SIGNAL','FL CG MIRA SIGNAL',820,650,205,1420,1050,85),
    ('AEGIS_REVEAL','FL CG AEGIS REVEAL',-1060,2070,335,0,3200,175),
    ('EXTRACTION','FL CG EXTRACTION',-820,-3020,300,0,-2350,80),
)


def _pose(build,x,z,height,tx,tz,target_height):
    y=build.ground(x,z)+height
    ty=build.ground(tx,tz)+target_height
    dx,dz=tx-x,tz-z
    horizontal=max(0.001,math.hypot(dx,dz))
    yaw=math.degrees(math.atan2(dx,dz))%360
    pitch=-math.degrees(math.atan2(ty-y,horizontal))
    return y,pitch,yaw


def apply(build):
    cameras=[]
    for beat,name,x,z,height,tx,tz,target_height in SHOTS:
        y,pitch,yaw=_pose(build,x,z,height,tx,tz,target_height)
        build.add(
            MARKER,name,x,z,y=y,ry=yaw,kind='cinematic_camera',script=CAMERA_SCRIPT,
            **{'rx':pitch,'rz':0,'eleprof.physics':0,'eleprof.phyalways':0}
        )
        cameras.append({
            'beat':beat,'name':name,'x':x,'y':round(y,2),'z':z,
            'pitch':round(pitch,2),'yaw':round(yaw,2),'seconds':5,
        })

    # A separate invisible mission-side coordinator requests CineGuru by camera name.
    # Using the same harmless authored marker asset avoids introducing another model.
    build.add(
        MARKER,'FIRST LIGHT // CINEMATIC',180,-9500,y=100,kind='controller',
        script=CONTROLLER_SCRIPT,
        **{'eleprof.physics':0,'eleprof.phyalways':0}
    )
    return {
        'system':'CineGuru MAX',
        'camera_count':len(cameras),
        'beats':[c['beat'] for c in cameras],
        'cameras':cameras,
        'fail_open':True,
        'music_owner':'firstlight_score.lua',
    }
