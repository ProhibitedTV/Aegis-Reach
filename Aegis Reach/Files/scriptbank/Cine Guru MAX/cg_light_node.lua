--------------------------------------------------------------------------
--   cg_spotlight_node.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.  --
--------------------------------------------------------------------------
-- light Node script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
local nodeList = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru light Node. 
-- DESCRIPTION: Duration (seconds) [LTIME#=5.0]
function cg_light_node_properties( e, ltime )
	local node = nodeList[ e ]
	if node == nil then return end
	
	if ltime > 0 then 
		node.filmtime = ltime * 1000
	end
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local debugFlag = false

function cg_light_node_init( e )
	nodeList[ e ] = { node        = 0,
					  filmtime    = 5000,
					  state       = 'init'
					}
	if not debugFlag then Hide( e ) end
	CollisionOff( e )
end

function CG_IsLightNode( e )
	return nodeList[ e ] ~= nil
end

C.Register( 'lightnode', CG_IsLightNode )

function CG_GetLightNode( e )
	return nodeList[ e ]
end

function CG_FindLightNodes( ent )
	local list = {}
	for k, v in pairs( nodeList ) do
		if v.lightmarker == ent and
		   v.state  == 'done' then
			list[ v.node ] = 
			  { obj      = g_Entity[ k ].obj,
			    filmtime = v.filmtime
			  }
		end
	end
	return list
end	
	
function cg_light_node_main( e )
	
	local node = nodeList[ e ]
	if node == nil then return end

	if node.state == 'done' then
		if not debugFlag then return end
		PromptLocal( e, "CG_LightNode: " .. 
		                node.state .. ", " ..
						( node.lightmarker or 'nil' ) .. ", " ..
						( node.node  or 'nil' )
				   )
	elseif
	   node.state == 'too many' then
		Show( e )
		PromptLocal( e, "CG_Node: Too many connections" )
	end	
end
