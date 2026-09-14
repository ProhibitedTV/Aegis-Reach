"""Runtime regression for the diegetic Kestrel-mounted opening cameras."""
from native_format import ROOT
from python_runtime import ensure_max_lua_runtime
from firstlight_cinematics import OPENING_MOUNTS,OPENING_SEQUENCE

assert tuple(OPENING_MOUNTS)==OPENING_SEQUENCE
assert len(OPENING_MOUNTS)==8
assert OPENING_MOUNTS['ARRIVAL_ORBIT']['mode']=='gimbal stabilized'
assert all('mount' in OPENING_MOUNTS[beat] and 'label' in OPENING_MOUNTS[beat] for beat in OPENING_SEQUENCE)

LuaRuntime=ensure_max_lua_runtime(__file__)
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
function firstlight_guard(n,f) return f end
g_Time=1000
aegis={cinematic_beat='ARRIVAL_WIDE'}
g_Entity={};names={};objpose={};campos={};camrot={}
function GetEntityName(e) return names[e] end
function Hide(e) end
function CollisionOff(e) end
function SetEntityAlwaysActive(e,v) end
function GetGroundHeight(x,z) return 500 end
function GetObjectPosAng(obj)
 local p=objpose[obj]
 if not p then return nil end
 return p.x,p.y,p.z,p.rx,p.ry,p.rz
end
function PositionObject(obj,x,y,z) campos[obj]={x=x,y=y,z=z} end
function RotateObject(obj,rx,ry,rz) camrot[obj]={rx=rx,ry=ry,rz=rz} end

names[1]='FL KESTREL INSERTION FLIGHT'
g_Entity[1]={obj=101}
objpose[101]={x=100,y=600,z=-9000,rx=2,ry=180,rz=6}

local camera_names={
 'FL CG ARRIVAL WIDE','FL CG ARRIVAL PASS','FL CG ARRIVAL ORBIT','FL CG ARRIVAL DESCENT',
 'FL CG ARRIVAL HANDOFF','FL CG ARRIVAL LIFTOFF','FL CG ARRIVAL CLIMB','FL CG ARRIVAL DEPART'
}
for i,name in ipairs(camera_names) do
 local e=9+i;local obj=209+i
 names[e]=name;g_Entity[e]={obj=obj};objpose[obj]={x=0,y=0,z=0,rx=0,ry=0,rz=0}
end
g_Entity[99]={obj=999};names[99]='FIRST LIGHT // CAMERA RIG'
''')
source=(ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_camera_rig.lua').read_text(errors='replace')
lua.execute('\n'.join(line for line in source.splitlines() if not line.startswith('require ')))
lua.execute(r'''
firstlight_camera_rig_init(99)
assert(aegis.kestrel_camera_rig_ready==true,'rig did not publish ready state')
firstlight_camera_rig_main(99)
for obj=210,217 do assert(campos[obj]~=nil and camrot[obj]~=nil,'camera mount not positioned '..obj) end

local ship=objpose[101]
local nose=campos[210]
local d=math.sqrt((nose.x-ship.x)^2+(nose.y-ship.y)^2+(nose.z-ship.z)^2)
local expected=math.sqrt(154^2+378^2)
assert(math.abs(d-expected)<0.01,'nose mount lost rigid offset')

-- HANDOFF and LIFTOFF deliberately reuse the same physical ramp camera.
assert(math.abs(campos[214].x-campos[215].x)<0.001)
assert(math.abs(campos[214].y-campos[215].y)<0.001)
assert(math.abs(campos[214].z-campos[215].z)<0.001)

-- The ventral ISR is position-attached but roll-stabilized relative to the hull.
assert(math.abs(camrot[212].rz-ship.rz*.12)<0.01,'ISR roll stabilization regressed')

local oldx,oldz=nose.x,nose.z
ship.x=1100;ship.y=700;ship.z=-8500;ship.rx=-4;ship.ry=128;ship.rz=-9
g_Time=1500;aegis.cinematic_beat='ARRIVAL_PASS'
firstlight_camera_rig_main(99)
assert(aegis.kestrel_camera_rig_ready==true)
local newnose=campos[210]
assert(math.abs(newnose.x-oldx)>100 or math.abs(newnose.z-oldz)>100,'camera did not follow translated ship')
local nd=math.sqrt((newnose.x-ship.x)^2+(newnose.y-ship.y)^2+(newnose.z-ship.z)^2)
assert(math.abs(nd-expected)<0.01,'camera offset changed under ship rotation')

-- Shoulder and tail feeds must remain physically distinct mounts.
local shoulder=campos[211];local tail=campos[217]
assert(math.sqrt((shoulder.x-tail.x)^2+(shoulder.y-tail.y)^2+(shoulder.z-tail.z)^2)>100)
''')
print('FIRST LIGHT // DIEGETIC CAMERA RIG PASS')
print('Eight Kestrel-mounted feeds follow live airframe translation/rotation; ventral ISR remains gimbal-stabilized.')
