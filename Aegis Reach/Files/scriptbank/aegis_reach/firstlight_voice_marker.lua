require 'scriptbank\\aegis_reach\\firstlight_audit'
-- Hidden always-active carrier for one optional non-3D dialogue WAV.
function firstlight_voice_marker_init(e)
 Hide(e);CollisionOff(e)
 if SetEntityAlwaysActive then SetEntityAlwaysActive(e,1) end
end
function firstlight_voice_marker_main(e) end
firstlight_voice_marker_init=firstlight_guard('firstlight_voice_marker_init',firstlight_voice_marker_init)
firstlight_voice_marker_main=firstlight_guard('firstlight_voice_marker_main',firstlight_voice_marker_main)
