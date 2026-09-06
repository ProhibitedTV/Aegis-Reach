---------------------------------------------------------------------------
--   cg_focal_point.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------------
-- cinematic focal point script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------------
local lower  = string.lower

local points = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Focal point. 
-- DESCRIPTION: [FilmTime#=5.0] (seconds) 
function cg_focal_point_properties( e, ftime )
	local focp = points[ e ]
	if focp == nil then return end
	if ftime > 0 then focp.filmtime = ftime * 1000 end
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"
local U = require "scriptbank\\utillib"
local V = require "scriptbank\\vectlib"

function cg_focal_point_init( e )			
	points[ e ] = { state    = 'init',
	                filmtime = 5000,
		            obj      = g_Entity[ e ].obj }
	Hide( e )
	CollisionOff( e )
end

function CG_IsFocalPoint( e )
	return points[ e ] ~= nil
end

C.Register( 'focal', CG_IsFocalPoint )

function CG_GetTarget( camOrlight )
	for _, v in pairs( points ) do
		if v.node == 1 and
		   ( v.camera == camOrlight or
		     v.light   == camOrlight ) then
			return v.obj
		end
	end
end

function CG_triggerTarget( camOrlight )
	for _, v in pairs( points ) do
		if v.state == 'idle' and
		   v.node  == 1 and
		   ( v.camera == camOrlight or
		     v.light   == camOrlight ) then
			v.state = 'triggered'
			break
		end
	end
end

local targetsReady = false

local function checkForCameraOrLight( node, e )
	if C.isCamera( e ) then
		-- check if the camera/light already connected
		for _, v in pairs( points ) do
			if v.camera == e then
				node.state = 'has camera'
				return
			elseif
			   v.light == e then
				node.state = 'has light'
				return
			end
		end
		node.node = 1
		node.camera = e
		node.state = 'ready'
	elseif
	   C.isLightMarker( e ) then
		-- check if the camera/light already connected
		for _, v in pairs( points ) do
			if v.camera == e then
				node.state = 'has camera'
				return
			elseif
			   v.light == e then
				node.state = 'has light'
				return
			end
		end
		node.node = 1
		node.light = e
		node.state = 'ready'
	end
end

local function processNode( e, node, from, typ )
	local done = false
	for _, l in ipairs( node.links ) do
		if l ~= from and 
		   points[ l ] ~= nil then
			if not done then
				done = true
				local nextNode  = points[ l ]
				nextNode.node   = node.node + 1
				if typ == 'light' then
					nextNode.light = node.light
				else
					nextNode.camera = node.camera
				end
				nextNode.state  = 'ready'
				processNode( l, nextNode, e, typ )
			else
				node.state = 'too many'
				return
			end
		end
	end
end
		
function CG_GetTargets()
	-- get all links from nodes to other entities
	for k, v in pairs( points ) do
		v.links = C.GetEntityLinks( k )
		if #v.links == 0 then
			Show( k )
			v.state = 'orphan'
		end
	end
	
	-- next find nodes connected to cameras or lightlights
	for k, v in pairs( points ) do
		if v.state == 'init' then
			for _, l in ipairs( v.links ) do
				checkForCameraOrLight( v, l )
			end
		end	
	end
	
	-- now complete processing of all nodes for each camera / lightlight
	for k, v in pairs( points ) do
		if v.node == 1 then
			if v.camera ~= nil then
				processNode( k, v, v.camera )
			elseif
			   v.light ~= nil then
				processNode( k, v, v.light, 'light' )
			end
		end
	end

	targetsReady = true
end

local function sameSource( s1, s2 )
	return ( s1.camera ~= nil and 
	         s1.camera == s2.camera ) or
		   ( s1.light ~= nil and 
	         s1.light == s2.light )
end

local function getRoute( e, p )

	local nodes = {}
		
	for k, v in pairs( points ) do
		if sameSource( p, v ) and
		   v.node > 1 then
			if nodes[ v.node - 1 ] == nil then
				nodes[ v.node - 1 ] = { obj = v.obj, filmtime = v.filmtime }
			else
				-- this probably can't happen anymore
				Show( e )
				points[e].state = 'duplicate'
				return
			end
		end
	end	
	
	if #nodes == 0 then return end
	
	for i = 1, #nodes - 1 do
		if nodes[ i ].filmtime == nil then
			points[e].state = 'no time'
			Show( e )
			return
		end
	end
	
	p.endPos = { obj = nodes[ #nodes ].obj }
	nodes[ #nodes ] = nil
	p.nodes = nodes
	C.BuildCMPoints( p )
end

local function updatePosition( e, p )
	CollisionOff( e )
	PositionObject( p.obj, p.posV.x, p.posV.y, p.posV.z )
	CollisionOn( e )
end

local function movefpoint( p, timeNow )
	-- get route points 
	local tCM = p.CMList[ p.curCM ]
	local nCM = p.CMList[ p.curCM + 1 ]
	
	if not p.movVec then

		if p.curCM == 2 then	
			p.CMstartTime = timeNow	
		end
		
		-- calculate CM points for this leg of the journey
		p.p1 = p.CMList[ p.curCM - 1 ].pos
		p.p2 = tCM.pos
		p.p3 = nCM.pos
		p.p4 = p.CMList[ p.curCM + 2 ].pos
			
		p.movVec = true
	end
	
	p.t = ( timeNow - p.CMstartTime ) / tCM.ti

	if p.t > 1 then
		p.posV = V.CR_Point( 1, p.p1, p.p2, p.p3, p.p4 )
		if nCM.obj == p.endPos.obj then
			return true
		else
			p.movVec = false
			p.curCM = p.curCM + 1
			p.CMstartTime = timeNow
		end
	else
		p.posV = V.CR_Point( p.t, p.p1, p.p2, p.p3, p.p4 )
	end
end

function cg_focal_point_main( e )

	local Ent = g_Entity[e]
	
	if Ent == nil then return end

	local fpoint = points[ e ]

	if fpoint == nil or not targetsReady then return end

	--PromptLocal( e, fpoint.state .. ", " .. 
	--                fpoint.node  .. ", " .. 
	--				( fpoint.camera or 0 ) )	
	
	if fpoint.state == 'done' then
		return
		
	elseif 
	   fpoint.state == 'ready'  then
		
		local x, y, z = GetObjectPosAng( fpoint.obj )		
		fpoint.posV = V.Create( x, y, z )
		
		getRoute( e, fpoint )

		if fpoint.CMList == nil then
			fpoint.state = 'done'
			return
		end
		
		fpoint.state = 'idle'
		
	elseif
	   fpoint.state == 'triggered' then
		
		local finished = movefpoint( fpoint, C.getTime() )
		updatePosition( e, fpoint )
		
		if finished then
			fpoint.state = 'done'
		end
		
	elseif
	   fpoint.state == 'orphan' then
		PromptLocal( e, "CineGuru: Orphaned focus node" )

	elseif
	   fpoint.state == 'has camera' then
		PromptLocal( e, "Cine|Guru Focal node already uses for camera" )
		
	elseif
	   fpoint.state == 'has light' then
		PromptLocal( e, "Cine|Guru Focal node already used for lightlight" )
		
	elseif
	   fpoint.state == 'duplicate' then
		PromptLocal( e, "Cine|Guru Duplicate focal node" )

	elseif
	   fpoint.state == 'too many' then
		PromptLocal( e, "CineGuru: Focal node too many connections" )

	elseif
	   fpoint.state == 'no time' then
		PromptLocal( e, "Cine|Guru No time on focal node" )
	end	
	
end




