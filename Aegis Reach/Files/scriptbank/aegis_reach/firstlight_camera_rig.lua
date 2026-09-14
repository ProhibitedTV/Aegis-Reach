require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Diegetic opening-camera rig for FIRST LIGHT.
-- These cameras are not omniscient floating viewpoints: they are mounted to plausible
-- Kestrel hardware and inherit the live airframe transform every frame.  The ventral
-- ISR feed is the one deliberately stabilized/gimballed exception.
local rig={ship_obj=nil,cameras={}}

local mounts={
 ARRIVAL_WIDE={name='FL CG ARRIVAL WIDE',label='KSTL-01 NOSE EO',off={0,154,-378},aim={0,-0.08,-1},roll=1.0,vibe=0.18},
 ARRIVAL_PASS={name='FL CG ARRIVAL PASS',label='KSTL-02 STBD SHOULDER',off={360,112,20},aim={-1,-0.10,0.32},roll=1.0,vibe=0.45},
 ARRIVAL_ORBIT={name='FL CG ARRIVAL ORBIT',label='KSTL-03 VENTRAL ISR',off={0,48,-60},target={-240,-8750,120},roll=0.12,vibe=0.10},
 ARRIVAL_DESCENT={name='FL CG ARRIVAL DESCENT',label='KSTL-04 STBD GEAR',off={250,42,110},aim={-0.18,-1,0.20},roll=0.75,vibe=0.55},
 ARRIVAL_HANDOFF={name='FL CG ARRIVAL HANDOFF',label='KSTL-05 RAMP',off={0,138,410},aim={0,-0.18,1},roll=0.35,vibe=0.12},
 ARRIVAL_LIFTOFF={name='FL CG ARRIVAL LIFTOFF',label='KSTL-05 RAMP',off={0,138,410},aim={0,-0.22,1},roll=0.40,vibe=0.48},
 ARRIVAL_CLIMB={name='FL CG ARRIVAL CLIMB',label='KSTL-06 PORT SHOULDER',off={-360,112,30},aim={1,-0.08,0.25},roll=1.0,vibe=0.42},
 ARRIVAL_DEPART={name='FL CG ARRIVAL DEPART',label='KSTL-07 TAIL',off={0,158,420},aim={0,-0.05,1},roll=1.0,vibe=0.28},
}

local rad=math.rad
local deg=math.deg
local sin=math.sin
local cos=math.cos
local sqrt=math.sqrt
local atan=math.atan2

local function rotate_local(x,y,z,rx,ry,rz)
 -- Local roll -> pitch -> yaw.  This is used for both the physical mount offset and
 -- the boresight vector, keeping a fixed hull camera attached through bank/pitch/yaw.
 local cr,sr=cos(rad(rz)),sin(rad(rz))
 local x1,y1,z1=x*cr-y*sr,x*sr+y*cr,z
 local cp,sp=cos(rad(rx)),sin(rad(rx))
 local x2,y2,z2=x1,y1*cp-z1*sp,y1*sp+z1*cp
 local cy,sy=cos(rad(ry)),sin(rad(ry))
 return x2*cy+z2*sy,y2,-x2*sy+z2*cy
end

local function look_angles(cx,cy,cz,tx,ty,tz,roll)
 local dx,dy,dz=tx-cx,ty-cy,tz-cz
 local flat=math.max(0.001,sqrt(dx*dx+dz*dz))
 return -deg(atan(dy,flat)),deg(atan(dx,dz)),roll or 0
end

local function scan()
 if not g_Entity or not GetEntityName then return end
 for id,ent in pairs(g_Entity) do
  if ent and ent.obj then
   local ok,name=pcall(GetEntityName,id)
   if ok and name then
    if name=='FL KESTREL INSERTION FLIGHT' then rig.ship_obj=ent.obj end
    for beat,m in pairs(mounts) do
     if name==m.name then rig.cameras[beat]=ent.obj end
    end
   end
  end
 end
end

local function active_beat()
 if not aegis then return nil end
 return aegis.cinematic_beat or aegis.cinematic_request
end

local function position_mount(beat,m,shipx,shipy,shipz,rx,ry,rz)
 local obj=rig.cameras[beat];if not obj then return end
 local ox,oy,oz=m.off[1],m.off[2],m.off[3]
 if active_beat()==beat and m.vibe and m.vibe>0 then
  local t=(g_Time or 0)*0.001
  ox=ox+sin(t*29.0+#beat)*m.vibe
  oy=oy+sin(t*37.0+#beat*.7)*m.vibe*.55
  oz=oz+sin(t*23.0+#beat*.3)*m.vibe*.35
 end
 local dx,dy,dz=rotate_local(ox,oy,oz,rx,ry,rz)
 local cx,cy,cz=shipx+dx,shipy+dy,shipz+dz
 local tx,ty,tz
 if m.target then
  tx,tz=m.target[1],m.target[2]
  if GetGroundHeight then
   local ok,h=pcall(GetGroundHeight,tx,tz)
   if ok and type(h)=='number' then ty=h+m.target[3] else ty=shipy+m.target[3] end
  else ty=shipy+m.target[3] end
 else
  local ax,ay,az=rotate_local(m.aim[1],m.aim[2],m.aim[3],rx,ry,rz)
  tx,ty,tz=cx+ax*1000,cy+ay*1000,cz+az*1000
 end
 local pitch,yaw,roll=look_angles(cx,cy,cz,tx,ty,tz,rz*(m.roll or 1))
 if PositionObject then PositionObject(obj,cx,cy,cz) end
 if RotateObject then RotateObject(obj,pitch,yaw,roll) end
end

function firstlight_camera_rig_init(e)
 rig.ship_obj=nil;rig.cameras={}
 Hide(e);CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
 scan()
end

function firstlight_camera_rig_main(e)
 if not rig.ship_obj or not next(rig.cameras) then scan() end
 if not rig.ship_obj or not GetObjectPosAng then return end
 local x,y,z,rx,ry,rz=GetObjectPosAng(rig.ship_obj)
 if not x then return end
 for beat,m in pairs(mounts) do position_mount(beat,m,x,y,z,rx or 0,ry or 0,rz or 0) end
end

firstlight_camera_rig_init=firstlight_guard('firstlight_camera_rig_init',firstlight_camera_rig_init)
firstlight_camera_rig_main=firstlight_guard('firstlight_camera_rig_main',firstlight_camera_rig_main)
