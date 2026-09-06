------------------------------------------------------------------------------
--   cg_camera_endpoint.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.  --
------------------------------------------------------------------------------
-- Camera endpoint script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
------------------------------------------------------------------------------
local lower = string.lower

local endpointList = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Camera endpoint. 
-- DESCRIPTION: Fade time (seconds) [FADE#=0]
function cg_camera_endpoint_properties( e, fade )
	local ep = endpointList[ e ]
	if ep == nil then return end
	
	ep.fadeTime = fade * 1000
end				   
-----------------------------------------------------
local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function CG_GetEndPos( e )
	for _, v in pairs( endpointList ) do
		if v.camera == e then
			return v
		end
	end
end

function CG_IsEndpoint( e )
	return endpointList[ e ] ~= nil
end

C.Register( 'endpoint', CG_IsEndpoint )

function CG_GetEndpoint( e )
	return endpointList[ e ]
end

local debugFlag = false 

function cg_camera_endpoint_init( e )
	endpointList[ e ] = { state    = 'init',
						  obj      = g_Entity[ e ].obj
						}
	if not debugFlag then Hide( e ) end
	CollisionOff( e )
end

function cg_camera_endpoint_main( e )
	local ep = endpointList[ e ]
	if ep == nil then return end
	
	if ep.state == 'done' then
		if not debugFlag then return end
		PromptLocal( e, "CG_Endpoint: " ..
		                ep.state .. ", " ..
						( ep.camera  or 'nil' ) .. ", " ..
						( ep.nextcam or 'nil' )
				   )
	elseif
	   ep.state == 'too many' then
		PromptLocal( e, "CG_Endpoint: Too many connections" )
	end
end
