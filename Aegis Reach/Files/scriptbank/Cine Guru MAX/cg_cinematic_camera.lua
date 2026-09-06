--------------------------------------------------------------------------------
--   cg_cinematic_camera.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
--------------------------------------------------------------------------------
-- cinematic camera script, part of the Cine Guru pack.
--
-- For instructions on use see Cine Guru documentation.
--------------------------------------------------------------------------------
local cameras = {}

local default_filmtime    = 5000
local default_fadetime    = 0
local default_foclenstart = 100
local default_foclenend   = 100

-- DESCRIPTION: Cine Guru Camera. 
-- DESCRIPTION: Film time (seconds) [FILMTIME#=5.0]
-- DESCRIPTION: Fade time (seconds) [FADE#=0]
-- DESCRIPTION: Focal length at start [FLS#=80(20,120)]
-- DESCRIPTION: Focal length at end   [FLE#=80(20,120)]

function cg_cinematic_camera_properties( e, filmtime, fade, fls, fle )
	local cam = cameras[ e ]
	if cam == nil then return end
	if filmtime > 0 then cam.filmtime = filmtime * 1000 end
	cam.fadeTime = fade * 1000
	cam.data.fls = fls
	cam.data.fle = fle
end				   
-----------------------------------------------------

local N = require "scriptbank\\Cine Guru MAX\\cg_pnoise"
local C = require "scriptbank\\Cine Guru MAX\\cg_lib"
local Q = require "scriptbank\\quatlib"
local U = require "scriptbank\\utillib"
local V = require "scriptbank\\vectlib"

function CG_IsCamera( e )
	return cameras[ e ] ~= nil
end	

C.Register( 'camera', CG_IsCamera )

function CG_GetCamera( e )
	return cameras[ e ]
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

local random = math.random

math.randomseed(os.time())
random(); random(); random()

local INF = math.huge

local gEnt = g_Entity
local CG_camRolling = false

function UpdateEntityRT( e, object, x, y, z, rx, ry, rz, ave, act, 
                         col, key, zon, ezon, plrvis, hea, frm, pdst, avd, lmb, lmi )
	if g_Entity[e] ~= nil then
		local ent = gEnt[ e ]
		ent.x = x
		ent.y = y
		ent.z = z
		ent.anglex = rx
		ent.angley = ry
		ent.anglez = rz
		ent.obj = object
		ent.active = ave
		ent.activated = act
		ent.collected = col
		ent.haskey = key
		ent.entityinzone = ezon
		ent.health = hea
		ent.frame = frm
		ent.avoid = avd
		ent.limbhit = lmb
		ent.limbhitindex = lmi
		if not CG_camRolling then
			ent.plrinzone = zon
			ent.plrvisible = plrvis
			ent.plrdist = pdst
		else
		    ent.plrvisible = 0
		end
	end
end

local CG_camRollingCount = 10

function LookAtPlayer( e )
	if CG_camRolling then
		if CG_camRollingCount > 0 then
			SendMessageF_lookforward( e, 100 )
			CG_camRollingCount = CG_camRollingCount - 1
		end
	else
		SendMessageF_lookatplayer( e, 100 )
		CG_camRollingCount = 10
	end
end

function LookAtPlayer( e, v )
	if CG_camRolling then
		if CG_camRollingCount > 0 then
			SendMessageF_lookforward( e, 100 )
			CG_camRollingCount = CG_camRollingCount - 1
		end
	else
		SendMessageF_lookattargete( e, 0 )
		SendMessageF_lookatplayer( e, v )
		CG_camRollingCount = 10
	end
end

local fadeSpr = CreateSprite( LoadImage("scriptbank\\Cine Guru MAX\\black.png") )
SetSpriteSize    ( fadeSpr, 100, 100 )
SetSpritePosition( fadeSpr, 200, 200 )
SetSpriteColor   ( fadeSpr, 255, 255, 255, 255 )
SetSpriteDepth   ( fadeSpr, 5 )

g_timeDiff = g_timeDiff or 1

local waitAbit = math.huge

function CG_ActivateCamera( e, followOn, origCam )
	if type( e ) == "string" then
		for k, v in pairs( cameras ) do
			if v.name == e then
				e = k
				break
			end
		end
	end
	local cam = cameras[ e ]
	if cam ~= nil then
		if cam.state ~= 'rolling' then
			cam.triggered = true
			cam.followOn = followOn
			if origCam ~= nil then
				cam.origfov = origCam.origfov
				cam.PMI = origCam.PMI
				cam.FLenable = origCam.FLenable
				cam.CurrentlyHeldWeaponID = 
				      origCam.CurrentlyHeldWeaponID
				cam.playerPosAng = origCam.playerPosAng
			end
		end
		return true
	end
end

function CG_GetActiveCamera()
	for k, v in pairs( cameras ) do
		if v.state == 'rolling' then 
			return k, v.currNode, v.t * v.duration, v.duration
		end
	end
end

local function Abort() 
	for k, v in pairs( cameras ) do
		if v.state == 'rolling' then 
			v.state = 'abort'
			return
		end
	end	
end

local debugFlag = false

function cg_cinematic_camera_init_name( e, name )
	cameras[ e ] = { state       = "init",
					 name        = name,
					 data = { fls = default_foclenstart,
					          fle = default_foclenend },
					 filmtime    = default_filmtime,
					 fadeTime    = default_fadetime
				   }					 
	if not debugFlag then Hide( e ) end
	CollisionOff( e )
end

local function MoveCamera( cam, timeNow, onlyInit )
	if cam.curCM ~= nil then

		local tCM = cam.CMList[ cam.curCM ]
		local nCM = cam.CMList[ cam.curCM + 1 ]
		
		-- get camera position and orientation
		local camx, camy, camz, cxa, cya, cza = GetObjectPosAng( cam.obj )
		
		-- get endpos position and orientation
		local epx, epy, epz, epxa, epya, epza = GetObjectPosAng( nCM.obj )

		if not cam.movVec then

			cxa, cya, cza = rad( cxa ), rad( cya ), rad( cza )
			if cam.curCM == 2 then
				-- get roll angles for start point
				local rza = C.getRollAngle( cxa, cya, cza ) 
				cam.rollStart = deg( -rza )
				cam.sQuat = nil
				cam.CMstartTime = timeNow	
			else
				-- use ending roll angle from last leg
				cam.rollStart = cam.rollFinish
				cam.sQuat     = cam.eQuat
				cam.timer     = cam.CMstartTime + tCM.ti
			end
			
			if cam.endPos ~= nil and 
			   nCM.obj == cam.endPos.obj and
			   cam.endPos.fadeTime > 0 then
			   	if cam.fade == 'in' then
					cam.fade = 'both'
				else
					cam.fadeTime  = cam.endPos.fadeTime
					cam.fadeStart = cam.timer - cam.fadeTime
					cam.fade = 'out'
				end
			end
			
			cam.duration = tCM.ti
			
			local numSteps = cam.duration / 20

			-- get roll angles for end point
			-- (used for focus point calculations)
			epxa, epya, epza = rad( epxa ), rad( epya ), rad( epza )
			rza = C.getRollAngle( epxa, epya, epza ) 
			cam.rollFinish = deg( -rza )
							
			cam.currRoll = cam.rollStart
			if cam.rollStart ~= cam.rollFinish then
				cam.rollInc  = abs( cam.rollFinish - cam.rollStart ) / numSteps
				if cam.rollStart > cam.rollFinish then cam.rollInc = -cam.rollInc end
			else
				cam.rollInc = nil
			end
						
			-- calculate fov change
			cam.currfov = tCM.data.fls
			SetCameraPanelFOV( cam.currfov / 2 )
			if tCM.data.fls ~= tCM.data.fle then
				cam.foclenInc = abs( tCM.data.fle - tCM.data.fls ) / numSteps
				if tCM.data.fls > tCM.data.fle then cam.foclenInc = -cam.foclenInc end
			end
			 
			if cam.sQuat == nil then
				cam.sQuat = Q.FromEuler( cxa, cya, cza )
			end
			
			cam.eQuat = Q.FromEuler( epxa, epya, epza )
			
			-- calculate CM points for this leg of the journey
			cam.p1 = cam.CMList[ cam.curCM - 1 ].pos
			cam.p2 = tCM.pos
			cam.p3 = nCM.pos
			cam.p4 = cam.CMList[ cam.curCM + 2 ].pos
			
			cam.movVec = true
		end

		cam.t = ( timeNow - cam.CMstartTime ) / cam.duration

		if cam.t > 1 then cam.t = 1 end

		local v = V.CR_Point( cam.t, cam.p1, cam.p2, cam.p3, cam.p4 )
		PositionObject( cam.obj, v.x, v.y, v.z )
		
	else
		-- single camera only tracking or fov changes needed
		if cam.trackObj ~= nil then
			local x, y, z = GetObjectPosAng( cam.trackObj )	
			x = x + cam.trackOff.x
			y = y + cam.trackOff.y
			z = z + cam.trackOff.z
			PositionObject( cam.obj, x, y, z )
		end
		
		if not cam.movVec then
			-- calculate fov change
			cam.currfov = cam.data.fls
			SetCameraPanelFOV( cam.currfov / 2 )
			if cam.data.fle ~= cam.data.fls then
				local numSteps = cam.filmtime / 20
				cam.foclenInc = abs( cam.data.fle - cam.data.fls ) / numSteps
				if cam.data.fls > cam.data.fle then 
					cam.foclenInc = -cam.foclenInc 
				end
			end
			cam.CMstartTime = timeNow
			cam.movVec = true
		end
		cam.single = true
		cam.duration = cam.filmtime
		cam.t = ( timeNow - cam.CMstartTime ) / cam.duration
		if cam.t > 1 then cam.t = 1 end
	end
end

local shake, addTrauma, setTrauma = 0, 0, 0

function CG_AddTrauma( num )   -- 0 - 100%
	num = num or 25
	
	if num >= 100 then 
		addTrauma = 1
	else
		addTrauma = min( 1, addTrauma + num / 100 )
	end
end

function CG_SetTrauma( num )   -- 0 - 100%
	num = num or 0
	if num >= 100 then 
		setTrauma = 1
	else
		setTrauma = num / 100
	end
end

local addPeriod  = 50
local setPeriod  = 50

function CG_SetPeriod( num )
	num = max( 1, num or 50 )
	setPeriod = num
end

function CG_AddPeriod( num )
	num = max( 1, num or 50 )
	addPeriod = num
end

local lastFade = nil
local traumaFade = 0.02

function CG_AddFade( num, temp )  -- 0 - 10
	num = num or 2
	if num > 10 then num = 10 end
	if temp then
		lastFade = lastFade or traumaFade
	else
		lastFade = nil
	end
	traumaFade = num / 100
end

local lastShakeTime = 0
local addSeed1, addSeed2, addSeed3 = random() * 1000, random() * 1000, random() * 1000
local setSeed1, setSeed2, setSeed3 = random() * 1000, random() * 1000, random() * 1000
local maxPitch = 10  -- Maximum allowed camera angle shake in degrees
local maxYaw   = 10  -- Maximum allowed camera angle shake in degrees
local maxRoll  =  5  -- Maximum allowed camera angle shake in degrees

local function AddShake( newQ, timeNow )
	-- trauma fade over time
	if addTrauma > 0 or
       setTrauma > 0 then

		if timeNow - lastShakeTime > 5000 then
			addSeed1 = random() * 1000
			addSeed2 = random() * 1000
			addSeed3 = random() * 1000
			setSeed1 = random() * 1000
			setSeed2 = random() * 1000
			setSeed3 = random() * 1000
		end
		
		if setTrauma > 0 then
			-- Set trauma doesn't fade
			shake = setTrauma^2
			local t = timeNow / setPeriod
			local rotQ = Q.FromEuler( rad( maxPitch * shake * N.PNoise( t, setSeed1 ) ), 
									  rad( maxYaw   * shake * N.PNoise( t, setSeed2 ) ),
									  rad( maxRoll  * shake * N.PNoise( t, setSeed3 ) ) )
			newQ = Q.Mul( newQ, rotQ )
		end
		
		if addTrauma > 0 then
		
			shake = addTrauma^2
			addTrauma = max( addTrauma - traumaFade * g_timeDiff, 0 )
			local t = timeNow / addPeriod
			local rotQ = Q.FromEuler( rad( maxPitch * shake * N.PNoise( t, addSeed1 ) ), 
									  rad( maxYaw   * shake * N.PNoise( t, addSeed2 ) ),
									  rad( maxRoll  * shake * N.PNoise( t, addSeed3 ) ) )
			newQ = Q.Mul( newQ, rotQ )
		else 
			if lastFade ~= nil then traumaFade = lastFade end
		end 
		
		lastShakeTime = timeNow
	end

	return newQ
end

local function PointCamera( cam, timeNow )
	local tgt = cam.targets[ 'C' ]
	if cam.tgt == nil then 
		cam.tgt = tgt
		cam.posOffset = cam.targets.posOffset
	end
	
	if tgt ~= nil then
		if cam.currNode > 1 then
			tgt = cam.targets[ cam.currNode - 1 ]
			if tgt ~= nil then 
				cam.tgt = tgt
			end
		end
	end
	
	local cpx, cpy, cpz, cax, cay, caz = GetObjectPosAng( cam.obj ) 

	SetCameraPosition( 0, cpx, cpy, cpz )
	
	local newQ
	
	if cam.tgt ~= nil then
		-- work out the angles from us to them
		local x, y, z, ax, ay, az = GetObjectPosAng( cam.tgt.obj )
		
		local y = y + cam.tgt.offy
		
		if cam.posOffset ~= nil then
			local vect = V.Rot( cam.posOffset, rad( ax ), rad( ay ), rad( az ) )
			x, y, z = x + vect.x, y + vect.y, z + vect.z
		end
		
		local DX, DY, DZ = x - cpx, y - cpy, z - cpz

		local xAng = -atan( DY, sqrt( DX*DX + DZ*DZ ) )
	
		newQ = Q.FromEuler( 0, atan( DX, DZ ), 0 )
	
		newQ = Q.Mul( newQ, Q.FromEuler( xAng, 0, 0 ) )	
		
		if cam.currRoll ~= nil then
			local rollQ =  Q.FromEuler( 0, 0, rad( cam.currRoll ) )
			newQ = Q.Mul( newQ, rollQ )
			if cam.rollInc then
				cam.currRoll = cam.currRoll + cam.rollInc * g_timeDiff
			end
		end		
		
	elseif cam.single == nil then
		-- Automatic camera pointing code, with 'funky' smoothing
		newQ = Q.SLerp( cam.sQuat, cam.eQuat, C.myFunkyMath( cam.t ) )
	else
		-- Static camera
		newQ = Q.FromEuler( rad( cax), rad( cay ), rad( caz ) )
	end

	-- add camera shake
	newQ = AddShake( newQ, timeNow )

	local xr, yr, zr = Q.ToEuler( newQ )
	xr, yr, zr = C.avoidGimbalLock( cam, xr, yr, zr )
	
	SetCameraAngle( 0, deg( xr ), deg( yr ), deg( zr ) )
end

local function FindTargets( e, cam )
	local tgtList = {}
		
	-- if focal_point target available for this camera use it
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
		   find( entName, cam.name .. '_target' ) ~= nil then
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
local spacePressed  = false
local spaceTimer    = nil

local function processEndpoint( e, cameraEnt )
	local ep = CG_GetEndpoint( e )
	if ep.state == 'done' then
		ep.state = 'too many'
		Show( e )
		return
	end	
	ep.camera  = cameraEnt
	ep.state = 'done'
	local links = C.GetEntityLinks( e, { 'camera' } )
	if #links > 2 then
		ep.state = 'too many'
		Show( e )
		return
	end
	for _, l in pairs( links ) do
		-- if link is not for camera we came from then
		-- must be for next camera
		if l ~= cameraEnt then
			ep.nextcam = l
			cameras[ l ].IsTriggered = true
			CG_ProcessCamera( l, e )
		end
	end
end

local function processNode( e, node, cameraEnt, num, from )
	if node.state == 'done' then
		node.state = 'too many'
		Show( e )
		return
	end
	node.camera = cameraEnt
	node.node   = num
	local links = C.GetEntityLinks( e, { 'node', 'endpoint' } )
	if #links > 2 then
		node.state = 'too many'
		Show( e )
		return
	end	
	node.state  = 'done'	
	for _, l in pairs( links ) do
		if from == nil or
		   from ~= l   then
			if C.isNode( l ) then
				processNode( l, CG_GetNode( l ), cameraEnt, num + 1, e )
				return
			elseif
			   C.isEndpoint( l ) then
				processEndpoint( l, cameraEnt )
				return
			end
		end
	end
end

function CG_ProcessCamera( e, from )
	local links = C.GetEntityLinks( e, { 'camera', 'node', 'endpoint' } )
	if #links > 2 then 
		cameras[ e ].state = 'too many'
		Show( e )
		return
	end
	for _, l in pairs( links ) do
		if from == nil or 
		   from ~= l   then
			if C.isCamera( l ) then
				if cameras[ l ].IsTriggered then
					cameras[ e ].state = 'too many'
					Show( e )
					return
				end
				cameras[ e ].nextcam = l
				cameras[ l ].IsTriggered = true
				CG_ProcessCamera( l, e )
				break
			elseif
			   C.isNode( l ) then
				processNode( l, CG_GetNode( l ), e, 1, e )
				break
			elseif
			   C.isEndpoint( l ) then
				processEndpoint( l, e )
				break
			end
		end
	end
end

function cg_cinematic_camera_main( e )
	local timeNow = C.getTime()

	if controlEnt == nil then 
		controlEnt = e 
		waitAbit = timeNow + 100
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
	
	local cam = cameras[ e ]
	
	if cam == nil then return end
	
	if debugFlag then
		if not C.checkForAbort( e ) then
		  PromptLocal( e, "CG_Camera(" .. e .. "): " .. 
		                  cam.state .. ", " ..
			  			  ( cam.nextcam or 'nil' ) )
		end
	end	
	
	if cam.state == 'finished' then 
		return
		
	elseif 
	   cam.state == 'init' then
		if cam.nodes    == nil and
		   CG_FindNodes ~= nil then
			cam.nodes = CG_FindNodes( e )
		else
			cam.nodes = {}
		end		
		if cam.targets == nil then 
			cam.targets = FindTargets( e, cam )
		end
		if cam.endPos   == nil and 
		   CG_GetEndPos ~= nil then
			cam.endPos = CG_GetEndPos( e )
		end
		
		cam.state    = 'ready'
		cam.tgt      = nil
		cam.obj      = g_Entity[ e ].obj
		cam.currNode = 1 
		cam.FLenable = GetGamePlayerStateFlashlightKeyEnabled()
		C.BuildCMPoints( cam )
		
		if cam.endPos ~= nil then 
			cam.nextcam = cam.endPos.nextcam
		elseif
		   #cam.nodes == 0 then
			-- 'static' camera, check if attached to a 'follow' entity
			local links = C.GetEntityLinks( e, { 'other' } )
			if #links == 1 then
				cam.trackObj = g_Entity[ links[ 1 ] ].obj
				local cx, cy, cz = GetObjectPosAng( cam.obj )	
				local ox, oy, oz = GetObjectPosAng( cam.trackObj )	
				cam.trackOff = V.Create( cx - ox, cy - oy, cz - oz )
			end
		end 
			
	elseif
	   cam.state == 'rolling' then

		CG_camRolling = true

		MoveCamera( cam, timeNow )
		
		PointCamera( cam, timeNow )
		
		if cam.foclenInc ~= nil then
			cam.currfov = cam.currfov + cam.foclenInc * g_timeDiff
			SetCameraPanelFOV( cam.currfov / 2 )
		end
		
		if timeNow >= cam.timer then
			if cam.curCM and cam.curCM < cam.endCM then
				cam.curCM = cam.curCM + 1
				cam.movVec = nil
				cam.CMstartTime = timeNow - ( timeNow - cam.timer)
				if #cam.nodes > 0 and 
					cam.currNode <= #cam.nodes then
					cam.currNode = cam.currNode + 1
					cam.t = 0
				end
			else
				cam.state = 'done'
				CG_SetTrauma()
				CG_SetPeriod()

				if cam.nextcam ~= nil then 
					CG_ActivateCamera( cam.nextcam, true, cam ) 
				else
					CG_camRolling = false
					SetCameraOverride( 0 )
					SetCameraPanelFOV( cam.origfov )
					SetPostMotionIntensity( cam.PMI )
					SetPlayerWeapons(1)
					SetFlashLightKeyEnabled( cam.FLenable )
					ChangePlayerWeaponID( cam.CurrentlyHeldWeaponID )
					ShowHuds()
					if radar_showallsprites ~= nil then radar_showallsprites() end
				end
			end
		else
			if cam.fadeTime > 0 and 
			   cam.fade ~= 'done' then
				local ft = ( timeNow - cam.fadeStart ) / cam.fadeTime
				if cam.fade == 'in'   or 
				   cam.fade == 'both' then
					local alphaVal = 255 * ( 1 - ft )
					if alphaVal >= 0 then
						SetSpriteColor( fadeSpr, 255, 255, 255, alphaVal )
						C.AddSprite( 'fade', fadeSpr )
					else
						SetSpritePosition( fadeSpr, 200, 200 )
						if cam.fade == 'both' then
							cam.fade = 'out'
							cam.fadeTime  = cam.endPos.fadeTime
							cam.fadeStart = cam.timer - cam.fadeTime
						else
							cam.fade = 'done'
						end
					end
				
				elseif 
				   cam.fade == 'out' then
					if ft > 0 then
						local alphaVal = 255 * ft
						if alphaVal <= 255 then
							SetSpriteColor( fadeSpr, 255, 255, 255, alphaVal )
						end
						C.AddSprite( 'fade', fadeSpr )
					end
				end
			end
		end

		C.DisplaySprites()
				
		local ppa = cam.playerPosAng
		SetFreezePosition( ppa.x, ppa.y, ppa.z  )
		SetFreezeAngle( ppa.ax, ppa.ay, ppa.az )
		TransportToFreezePosition()
		
	elseif
	   cam.state == 'fade in' then
		local ft = ( timeNow - cam.fadeStart ) / cam.fadeTime
		local alphaVal = 255 * ( 1 - ft )
		if alphaVal > 1 then
			C.AddSprite( 'fade', fadeSpr )
			SetSpriteColor( fadeSpr, 255, 255, 255, alphaVal )
		else
			SetSpritePosition( fadeSpr, 200, 200 )
			cam.state = 'finished'
		end	
		C.DisplaySprites()
	end
	
	if cam.state == 'done' then 
		if cam.fade == 'out' then
			cam.fadeStart = timeNow
			C.AddSprite( 'fade', fadeSpr )
			cam.state = 'fade in'
		else
			cam.state = 'finished'
		end
		C.DisplaySprites()
		
	elseif
	   cam.state == 'ready' and
	   cam.triggered then
		C.clearAbort()
		if not cam.followOn then
			cam.playerPosAng = {  x = g_PlayerPosX,
								  y = g_PlayerPosY,
								  z = g_PlayerPosZ,
							     ax = g_PlayerAngX,
							     ay = g_PlayerAngY,
							     az = g_PlayerPosZ }
			cam.origfov = GetGamePlayerStateCameraFov()
			cam.PMI = GetPostMotionIntensity()
			SetPostMotionIntensity( 0 )
			SetCameraOverride ( 3 )
			SetFlashLightKeyEnabled( 0 )
			cam.CurrentlyHeldWeaponID = GetPlayerWeaponID()
			SetPlayerWeapons( 0 )
			HideHuds()
			if radar_hideallsprites ~= nil then radar_hideallsprites() end
		end
		
		cam.timer = timeNow + cam.filmtime
		
		if cam.fadeTime > 0 then
			C.AddSprite( 'fade', fadeSpr )
			cam.fadeStart = timeNow
			cam.fade = 'in'
		end

		cam.state = 'rolling'
		if CG_triggerTarget ~= nil then
			CG_triggerTarget( e )
		end
		MoveCamera( cam, timeNow )
		PointCamera( cam, timeNow )
		C.DisplaySprites()
		
	elseif
	   cam.state == 'abort' and
	   cam.origfov ~= nil then
	    CG_camRolling = false
		SetCameraOverride( 0 )
		SetCameraPanelFOV( cam.origfov )
		SetPostMotionIntensity( cam.PMI )
		SetPlayerWeapons(1)
		ChangePlayerWeaponID( cam.CurrentlyHeldWeaponID )
		SetFlashLightKeyEnabled( cam.FLenable )
		ShowHuds()
		if radar_showallsprites ~= nil then radar_showallsprites() end
		cam.state = 'finished'
		
		local ppa = cam.playerPosAng
		SetFreezePosition( ppa.x, ppa.y, ppa.z  )
		SetFreezeAngle( ppa.ax, ppa.ay, ppa.az )
		TransportToFreezePosition()

	end
end
