require 'scriptbank\\aegis_reach\\firstlight_audit'
-- FIRST LIGHT opening camera mount.
--
-- Opening camera entities are physical/editor-space mounts only. They deliberately do
-- not run CineGuru's camera state machine; firstlight_opening_director.lua is the sole
-- writer of the real game camera during insertion. firstlight_camera_rig.lua may move
-- Kestrel-mounted entities with the live airframe and the director samples them.
function firstlight_camera_mount_init(e)
 Hide(e)
 CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end

function firstlight_camera_mount_main(e)
 -- Intentionally inert. Keeping this entity alive gives the director a transform to
 -- sample without allowing a second cinematic system to call SetCameraPosition/Angle.
end

firstlight_camera_mount_init=firstlight_guard('firstlight_camera_mount_init',firstlight_camera_mount_init)
firstlight_camera_mount_main=firstlight_guard('firstlight_camera_mount_main',firstlight_camera_mount_main)
