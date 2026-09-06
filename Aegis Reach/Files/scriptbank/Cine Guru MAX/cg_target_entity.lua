---------------------------------------------------------------------------
--   cg_target_entity.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------------
-- cinematic target entity script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------------
local V = require "scriptbank\\vectlib"

local lower  = string.lower

local tepoints = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: MAX CineGuru Target Entity. 
-- DESCRIPTION: [YOffset=50]
-- DESCRIPTION: [XOffset=0]
-- DESCRIPTION: [ZOffset=0]
function cg_target_entity_properties( e, yoff, xoff, zoff )
	xoff = xoff or 0
	zoff = zoff or 0
	local tep = tepoints[ e ]
	if tep == nil then return end
	tep.posOffset = V.Create( xoff, yoff, zoff )
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function cg_target_entity_init( e )			
	tepoints[ e ] = { state     = 'init',
	                  posOffset = V.Create( 0, 50, 0 )
					}
	Hide( e )
	CollisionOff( e )
end

function CG_IsTargetEnt( e )
	return tepoints[ e ] ~= nil
end

C.Register( 'tgtEnt', CG_IsTargetEnt )

function CG_GetTargetEnt( cam )
	for _, v in pairs( tepoints ) do
		if v.camera == cam then
			return v.obj, v.posOffset
		end
	end
end

local targetsReady = false

local function checkForCamera( tep, e )
	if C.isCamera( e ) then
		-- check if the camera already connected
		for _, v in pairs( tepoints ) do
			if v.camera == e then
				tep.state = 'has camera'
				return
			end
		end
		tep.node = 1
		tep.camera = e
		tep.state = 'single'
	end
end
		
function CG_GetTargetEnts()
	-- get all links from point to other entities
	for k, v in pairs( tepoints ) do
		v.links = C.GetEntityLinks( k )
		if #v.links == 0 then
			Show( k )
			v.state = 'orphan'
		end
	end
	
	-- next find nodes connected to cameras
	for k, v in pairs( tepoints ) do
		if v.state == 'init' then
			for _, l in ipairs( v.links ) do
				checkForCamera( v, l )
			end
		end	
	end
	
	-- now complete processing of all nodes for each camera
	for k, v in pairs( tepoints ) do
		for _, l in ipairs( v.links ) do
			if not C.isCamera( l ) then
				v.obj   = g_Entity[ l ].obj
				v.state = 'done'
				break
			end
		end
		if v.state ~= 'done' then
			Show( k )
		end
	end

	targetsReady = true
end

function cg_target_entity_main( e )

	local Ent = g_Entity[e]
	
	if Ent == nil then return end

	local tepoint = tepoints[ e ]

	if tepoint == nil or not targetsReady then return end

	if tepoint.state == 'done' then
		return
		
	elseif
	   tepoint.state == 'orphan' then
		PromptLocal( e, "CineGuru: No connections" )

	elseif
	   tepoint.state == 'has camera' then
		PromptLocal( e, "Cine|Guru Too many cameras" )
		
	elseif
	   tepoint.state == 'single' then
		PromptLocal( e, "Cine|Guru No Entity connected" )
	end	
	
end




