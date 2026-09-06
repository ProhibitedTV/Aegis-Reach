--------------------------------------------------------------------------------
--   cg_lightmarker.lua  Copyright C D Stapleton (AKA AmenMoses) 2023.   --
--------------------------------------------------------------------------------
-- cinematic lightmarker script, part of the Cine Guru pack.
--
-- For instructions on use see Cine Guru documentation.
--------------------------------------------------------------------------------
local lightmarkers = {}

local default_ltime   = 10000
local default_fadeTime   = 0
local default_rangeStart = 1000
local default_rangeEnd   = 1000
local default_intensity  = 100

-- DESCRIPTION: Cine Guru lightmarker. 
-- DESCRIPTION: Light time (seconds) [lTime#=10.0]
-- DESCRIPTION: Fade time (seconds) [FADE#=0]
-- DESCRIPTION: Intensity %    [IN#=100(0,100)]

function cg_light_marker_properties( e, ltime, fade, int )
	local light = lightmarkers[ e ]
	if light == nil then return end
	if ltime > 0 then light.filmtime = ltime * 1000 end
	light.fadeTime   = fade * 1000
	light.intensity  = int
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"
local Q = require "scriptbank\\quatlib"
local V = require "scriptbank\\vectlib"

function CG_IsLightMarker( e )
	return lightmarkers[ e ] ~= nil
end	

C.Register( 'lightmarker', CG_IsLightMarker )

function CG_GetLightMarker( e )
	return lightmarkers[ e ]
end

local find  = string.find
local atan  = math.atan2
local deg   = math.deg
local rad   = math.rad
local log   = math.log
local sqrt  = math.sqrt
local abs   = math.abs
local max   = math.max
local min   = math.min

local gEnt = g_Entity

g_timeDiff = g_timeDiff or 1

local waitAbit = math.huge

function CG_ActivateLightMarker( e, followOn, origlight )
	if type( e ) == "string" then
		for k, v in pairs( lightmarkers ) do
			if v.name == e then
				e = k
				break
			end
		end
	end
	local light = lightmarkers[ e ]
	if light ~= nil then
		if light.state ~= 'shining' then
			light.triggered = true
			light.followOn = followOn
		end
		return true
	end
end

local function Abort() 
	for k, v in pairs( lightmarkers ) do
		if v.state == 'shining' then 
			v.state = 'abort'
			return
		end
	end	
end

local debugFlag = false

function cg_light_marker_init_name( e, name )
	lightmarkers[ e ] = { state       = "init",
					      name        = name,
					      rangeStart  = default_rangeStart,
					      rangeEnd    = default_rangeEnd,
					      filmtime    = default_ltime,
					      fadeTime    = default_fadeTime,
						  intensity   = default_intensity
				        }
					  
	if not debugFlag then Hide( e ) end
	CollisionOff( e )

	if g_Entity[ e ].activated == 1 then 
		lightmarkers[ e ].state = 'finished'
	end
end

local function MoveLightMarker( light, timeNow, onlyInit )
	if light.curCM ~= nil then

		local tCM = light.CMList[ light.curCM ]
		local nCM = light.CMList[ light.curCM + 1 ]
		
		-- get lightmarker position and orientation
		local lightx, lighty, lightz, cxa, cya, cza = GetObjectPosAng( light.obj )
		
		-- get endpos position and orientation
		local epx, epy, epz, epxa, epya, epza = GetObjectPosAng( nCM.obj )

		if not light.movVec then

			cxa, cya, cza = rad( cxa ), rad( cya ), rad( cza )
			if light.curCM == 2 then
				light.sQuat = nil
				light.CMstartTime = timeNow	
			else
				light.sQuat = light.eQuat
				light.timer = light.CMstartTime + tCM.ti
			end
			
			if light.endPos ~= nil and 
			   nCM.obj == light.endPos.obj and
			   light.endPos.fadeTime > 0 then
			   	if light.fade == 'in' then
					light.fade = 'both'
				else
					light.fadeTime  = light.endPos.fadeTime
					light.fadeStart = light.timer - light.fadeTime
					light.fade = 'out'
				end
			end
			
			light.duration = tCM.ti
			
			--local numSteps = light.duration / 20

			-- get roll angles for end point
			-- (used for focus point calculations)
			epxa, epya, epza = rad( epxa ), rad( epya ), rad( epza )
			 
			if light.sQuat == nil then
				light.sQuat = Q.FromEuler( cxa, cya, cza )
			end
			
			light.eQuat = Q.FromEuler( epxa, epya, epza )
			
			-- calculate CM points for this leg of the journey
			light.p1 = light.CMList[ light.curCM - 1 ].pos
			light.p2 = tCM.pos
			light.p3 = nCM.pos
			light.p4 = light.CMList[ light.curCM + 2 ].pos
			
			light.movVec = true
		end

		light.t = ( timeNow - light.CMstartTime ) / light.duration

		if light.t > 1 then light.t = 1 end

		local v = V.CR_Point( light.t, light.p1, light.p2, light.p3, light.p4 )
		PositionObject( light.obj, v.x, v.y, v.z )
		SetLightPosition( light.light, v.x, v.y, v.z )
		
	else
		-- single lightmarker only tracking or fov changes needed
		if light.trackObj ~= nil then
			local x, y, z = GetObjectPosAng( light.trackObj )	
			x = x + light.trackOff.x
			y = y + light.trackOff.y
			z = z + light.trackOff.z
			PositionObject( light.obj, x, y, z )
			SetLightPosition( light.light, x, y, z )
		end
		
		if not light.movVec then
			light.CMstartTime = timeNow
			light.movVec = true
		end
		light.single = true
		light.duration = light.filmtime
		light.t = ( timeNow - light.CMstartTime ) / light.duration
		if light.t > 1 then light.t = 1 end
	end
end

local function PointLightMarker( light, timeNow )
	local tgt = light.targets[ 'C' ]
	if light.tgt == nil then 
		light.tgt = tgt
		light.posOffset = light.targets.posOffset
	end
	
	if tgt ~= nil then
		if light.currNode > 1 then
			tgt = light.targets[ light.currNode - 1 ]
			if tgt ~= nil then 
				light.tgt = tgt
			end
		end
	end
	
	local cpx, cpy, cpz, cax, cay, caz = GetObjectPosAng( light.obj ) 
	
	local newQ
	
	if light.tgt ~= nil then
		-- work out the angles from us to them
		local x, y, z, ax, ay, az = GetObjectPosAng( light.tgt.obj )
		
		local y = y + light.tgt.offy
		
		if light.posOffset ~= nil then
			local vect = V.Rot( light.posOffset, rad( ax ), rad( ay ), rad( az ) )
			x, y, z = x + vect.x, y + vect.y, z + vect.z
		end
		
		local DX, DY, DZ = x - cpx, y - cpy, z - cpz

		local xAng = -atan( DY, sqrt( DX*DX + DZ*DZ ) )
	
		newQ = Q.FromEuler( 0, atan( DX, DZ ), 0 )
	
		newQ = Q.Mul( newQ, Q.FromEuler( xAng, 0, 0 ) )	
		
	elseif light.single == nil then
		-- Automatic lightmarker pointing code, with 'funky' smoothing
		newQ = Q.SLerp( light.sQuat, light.eQuat, C.myFunkyMath( light.t ) )
	else
		-- Static lightmarker
		newQ = Q.FromEuler( rad( cax), rad( cay ), rad( caz ) )
	end

	local xr, yr, zr = Q.ToEuler( newQ )
	xr, yr, zr = C.avoidGimbalLock( light, xr, yr, zr )
	
	SetLightEuler( light.light, deg( xr ), deg( yr ), deg( zr ) )

end

local function FindTargets( e, light )
	local tgtList = {}
		
	-- if focal_point target available for this lightmarker use it
	if CG_GetTarget ~= nil then
		local obj = CG_GetTarget( e )
		if obj ~= nil then
			tgtList[ 'C' ] = { obj = obj, offy = 0 }
			return tgtList
		end
	end	
	
	-- check for target points
	if CG_GetTargetEnt ~= nil then
		local obj, offs = CG_GetTargetEnt( e )
		if obj ~= nil then
			tgtList[ 'C' ]    = { obj = obj, offy = 0 }
			tgtList.posOffset = offs
			return tgtList
		end
	end			
		
	-- otherwise return targets for named entity	
	for k, v in pairs( g_Entity ) do
		local entName = GetEntityName( k )
		if entName ~= "" and
		   find( entName, light.name .. '_target' ) ~= nil then
			local args = C.GetArgs( entName )
			local num = 'C'
			local offy = 0
			if args[ 2 ] ~= nil then offy = tonumber( args[ 2 ] ) end
			if args[ 3 ] ~= nil then num  = tonumber( args[ 3 ] ) end
			tgtList[ num ] = { obj = g_Entity[ k ].obj, offy = offy }
		end
	end
	return tgtList
end		

local controlEnt    = nil
local timeLastFrame = nil

local function processNode( e, node, lightEnt, num, from )
	if node.state == 'done' then
		node.state = 'too many'
		Show( e )
		return
	end
	node.lightmarker = lightEnt
	node.node        = num
	local links      = C.GetEntityLinks( e, { 'lightnode' } )
	if #links > 2 then
		node.state = 'too many'
		Show( e )
		return
	end	
	node.state = 'done'	
	for _, l in pairs( links ) do
		if from == nil or
		   from ~= l   then
			if C.isLightNode( l ) then
				processNode( l, CG_GetLightNode( l ), lightEnt, num + 1, e )
				return
			end
		end
	end
end

function CG_ProcessLightMarker( e, from )
	local links = C.GetEntityLinks( e, { 'lightnode' } )
	if #links > 2 then
		lightmarkers[ e ].state = 'too many'
		Show( e )
		return
	end
	for _, l in pairs( links ) do
		if from == nil or 
		   from ~= l   then
			if C.isLightNode( l ) then
				processNode( l, CG_GetLightNode( l ), e, 1, e )
				break
			end
		end
	end
end

local lights = {}

local function getLights()
	for k, v in pairs( gEnt ) do
		local lId = GetEntityLightNumber( k )
		if lId and lId > 0 then
			lights[ lId ] = { used = false,  e = k, pos = V.Create( v.x, v.y, v.z ) }
		end
	end
end

local function findLight( light )
	local posV = V.Create( GetObjectPosAng( light.obj ) )
	local nearest = math.huge
	local found = nil
	for k, v in pairs( lights ) do
		if not v.used then
			local dist = V.SqDist( posV, v.pos )
			if dist < nearest then
				found = k
				nearest = dist
			end
		end
	end
	if found then
		lights[ found ].used = true
		SwitchScript( lights[ found ].e, "no_behaviour_selected.lua" )
	end
	return found
end

function cg_light_marker_main( e )
	local timeNow = C.getTime()

	if controlEnt == nil then 
		controlEnt = e 
		getLights()
		waitAbit = timeNow + 100
	end
	
	local light = lightmarkers[ e ]
	if light == nil or light.state == 'finished' then return end
	
	if light.light == nil and
  	   light.state == 'init' then
	   	light.obj = gEnt[ e ].obj
		light.light = findLight( light )
		if light.light == nil then
			light.state = 'no light'
			Show(e)
			return
		else
			light.maxIntensity = V.Create( GetLightRGB( light.light ) )
			SetLightRGB( light.light, 0, 0, 0 )
		end
	end
	
	if timeNow < waitAbit then return end
	
	if controlEnt == e then
		if timeLastFrame == nil then 
			timeLastFrame = timeNow
			g_timeDiff = 1
			
			if CG_GetTargets    ~= nil then CG_GetTargets()    end
			if CG_GetTargetEnts ~= nil then CG_GetTargetEnts() end
		else
			g_timeDiff = ( timeNow - timeLastFrame ) / 20
			-- this represents a minimum frame rate allowance of 5 FPS, if we get that low
			-- then all bets are off!
			if g_timeDiff > 10 then g_timeDiff = 1 end
			timeLastFrame = timeNow
		end
		if C.checkForAbort( e ) then Abort() end
	end
	
	if debugFlag then
		if not C.checkForAbort( e ) then
			local str = "CG_LightMarker(" .. e .. "): " ..light.state
			if light.nodes then str = str .. ", " .. #light.nodes end
			PromptLocal( e, str )
		end
	end	
	
	if light.state == 'init' then
		
		if light.nodes == nil and
		   CG_FindLightNodes ~= nil then
			light.nodes = CG_FindLightNodes( e )
		else
			light.nodes = {}
		end
		if light.targets == nil then 
			light.targets = FindTargets( e, light )
		end
		
		light.state    = 'ready'
		light.tgt      = nil
		light.currNode = 1 
		C.BuildCMPoints( light )
		
	elseif
	   light.state == 'shining' then

		MoveLightMarker( light, timeNow )
		
		PointLightMarker( light, timeNow )
				
		if timeNow >= light.timer then
			if light.curCM and light.curCM < light.endCM then
				light.curCM = light.curCM + 1
				light.movVec = nil
				light.CMstartTime = timeNow - ( timeNow - light.timer)
				if #light.nodes > 0 and 
					light.currNode <= #light.nodes then
					light.currNode = light.currNode + 1
					light.t = 0
				end
			else
				light.state = 'done'
			end
		else
	
			if light.fadeTime > 0 and 
			   light.fade ~= 'done' then
				local ft = ( timeNow - light.fadeStart ) / light.fadeTime
				if light.fade == 'in'   or 
				   light.fade == 'both' then
					local fadeVal = 1 - ft
					if fadeVal >= 0 then
						--PromptLocal( e, fadeVal )
						local si = V.Mul( light.maxIntensity, ft * light.intensity / 100 )
						SetLightRGB( light.light, si.x, si.y, si.z )
					else
						light.fade = 'done'
					end
				end
			elseif light.fade == nil then
				local si = V.Mul( light.maxIntensity, light.intensity / 100 )
				SetLightRGB( light.light, si.x, si.y, si.z )
				light.fade = 'done'
			end
		end
	end
	
	if light.state == 'done' then 
		SetLightRGB( light.light, 0, 0, 0 )
		light.state = 'finished'
		
	elseif
	   light.state == 'ready' then
		if light.triggered then
			C.clearAbort()
		
			light.timer = timeNow + light.filmtime
		
			if light.fadeTime > 0 then
				light.fadeStart = timeNow
				light.fade = 'in'
			end

			light.state = 'shining'
		
			if CG_triggerTarget ~= nil then
				CG_triggerTarget( e )
			end
			MoveLightMarker( light, timeNow )
			PointLightMarker( light, timeNow )
		else
			if g_Entity[ e ].activated == 1 then
				CG_ActivateLightMarker( e )
			end
		end
		
	elseif
	   light.state == 'abort' then
		SetLightRGB( light.light, 0, 0, 0 )
		light.state = 'finished'
		
	elseif
	   light.state == 'no light' then
		PromptLocal( e, "CineGuru: Cannot find dynamic light" )

	end
end
