--------------------------------------------------------------------------
--   cg_camera_node.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.  --
--------------------------------------------------------------------------
-- Camera Node script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
local nodeList = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Camera Node. 
-- DESCRIPTION: Film time (seconds) [FILMTIME#=5.0]
-- DESCRIPTION: Focal length at start [FLS#=80(20,120)]
-- DESCRIPTION: Focal length at end   [FLE#=80(20,120)]
function cg_camera_node_properties( e, filmtime, fls, fle )
	local node = nodeList[ e ]
	if node == nil then return end
	
	node.data.fls = fls
	node.data.fle = fle
	if filmtime > 0 then 
		node.filmtime = filmtime * 1000
	end
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local debugFlag = false

function cg_camera_node_init( e )
	nodeList[ e ] = { node        = 0,
					  filmtime    = 5000,
					  data = { fls = 80, fle = 90 },
					  state       = 'init'
					}
	if not debugFlag then Hide( e ) end
	CollisionOff( e )
end

function CG_IsNode( e )
	return nodeList[ e ] ~= nil
end

C.Register( 'node', CG_IsNode )

function CG_GetNode( e )
	return nodeList[ e ]
end

function CG_FindNodes( camEnt )
	local list = {}
	for k, v in pairs( nodeList ) do
		if v.camera == camEnt and
		   v.state  == 'done' then
			list[ v.node ] = 
			  { obj         = g_Entity[ k ].obj,
			    filmtime    = v.filmtime,
			    data = { fls = v.data.fls,
						 fle = v.data.fle }
			  }
		end
	end
	return list
end	
	
function cg_camera_node_main( e )
	
	local node = nodeList[ e ]
	if node == nil then return end

	if node.state == 'done' then
		if not debugFlag then return end
		PromptLocal( e, "CG_Node: " .. 
		                node.state .. ", " ..
						( node.camera  or 'nil' ) .. ", " ..
						( node.node    or 'nil' )
				   )
	elseif
	   node.state == 'too many' then
		PromptLocal( e, "CG_Node: Too many connections" )
	end	
end
