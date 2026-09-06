----------------------------------------------------------------------------
--   cg_trigger_zone.lua  Copyright C D Stapleton (AKA AmenMoses) 2024.   --
----------------------------------------------------------------------------
-- cinematic trigger zone script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
----------------------------------------------------------------------------
local lower = string.lower

local zones = {}

local default_delayTime = 0.1

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Trigger Zone. 
-- DESCRIPTION: Delay time (seconds) [DTIME#=0.1]
-- DESCRIPTION: [EnableSkip!=1]
-- DESCRIPTION: [DisableIfCombat!=0]
-- DESCRIPTION: [Triggerable!=0]

function cg_trigger_zone_properties( e, dtime, enableSkip, 
                                     disableIfCombat, triggerable )
	local zone = zones[ e ]
	if zone == nil then return end
	if dtime ~= nil and 
	   dtime ~= default_delayTime then 
		zone.trigTime = dtime 
	end
	if enableSkip ~= nil then
		zone.enableSkip = enableSkip == 1
	end
	if disableIfCombat ~= nil then
		zone.disableIfCombat = disableIfCombat == 1
	end
	if triggerable ~= nil then
		zone.triggerable = triggerable == 1
	end
end				   
-----------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function cg_trigger_zone_init( e )
	zones[ e ] = { trigTime        = 100,
	               state           = 'init',
				   disableIfCombat = false,
				   triggerable     = false,
				   enableSkip      = true
				 }
end

function CG_IsZone( e )
	return zones[ e ] ~= nil
end

C.Register( 'zone', CG_IsZone )

local function markCamera( e )
	local cam = CG_GetCamera( e )
	cam.IsTriggered = true
	cam.IsFirst = true
	CG_ProcessCamera( e )
end

local function marklight( e )
	local light = CG_GetLightMarker( e )
	light.IsTriggered = true
	light.IsFirst = true
	CG_ProcessLightMarker( e )
end

function cg_trigger_zone_main( e )
	local z = zones[ e ]
	if z.state == 'done' then return end
	
	local Ent = g_Entity[ e ]

	if Ent.activated == 2 then 
		z.state = 'done'
		return
	end

	-- PromptLocal( e, z.script or 'nil' )
	
	if z.state == 'init' then
		local links = C.GetEntityLinks( e )
		z.trigTyp = 'none'
		for _, v in ipairs( links ) do
			if C.isCredits( v ) then
				if z.creditsEnt ~= nil then
					z.state = 'Too many Credits!'
					return
				end
				z.creditsEnt = v
				
			elseif
			   C.isCamera( v ) then
				if z.cameraEnt ~= nil then
					z.state = 'Too many Cameras!'
					return
				end
				z.cameraEnt = v
				markCamera( v )
				
			elseif
			   C.isActor( v ) then
				if z.actorEnt ~= nil then
					z.state = 'Too many Actors!' 
					return
				end
				z.actorEnt = v
				z.script   = CG_GetActor( v ).script
				
			elseif
			   C.isLightMarker( v ) then
				if z.lightEnts == nil then
					z.lightEnts = {}
				end
				z.lightEnts[ #z.lightEnts + 1 ] = v
				marklight( v )
			end
		end
		z.state = 'idle'

	elseif
	   z.state == 'idle' then
		if not ( z.disableIfCombat and 
	             C.inCombat( e ) )   and
		   ( not z.triggerable     or
		     Ent.activated == 1 )    and
		   Ent.plrinzone == 1        and 
	       g_PlayerPosY + 50 > Ent.y and 
	       g_PlayerPosY - 50 < Ent.y then
	   
			z.waitAbit = C.getTime() + z.trigTime 
			z.state = 'triggered'
			C.clearAbort()
		end
		return
		
	elseif
	   z.state == 'triggered' and
		C.getTime() > z.waitAbit then
		local success = true
		z.trigtyp = ""
		if z.lightEnts ~= nil and CG_ActivateLightMarker ~= nil then
			for _, lEnt in pairs( z.lightEnts ) do
				if not CG_ActivateLightMarker( lEnt ) then
					success = false
				end
			end
		end
		if not success then  
			z.trigtyp = "Light" 
		else
			if z.script ~= nil and CG_Action ~= nil then
				success = CG_Action( z.script )
			end
			if not success then 
				z.trigtyp = "Actor"
			else
				if z.cameraEnt ~= nil and CG_ActivateCamera ~= nil then 
					success = CG_ActivateCamera( z.cameraEnt )
				end
				if not success then 
					z.trigTyp = "Camera"
				else
					if z.creditsEnt ~= nil and CG_RollCredits ~= nil then
						success = CG_RollCredits( z.creditsEnt )
					end
					if not success then z.trigTyp = "Credits" end
				end
			end
		end
		if success then
			z.state = 'done'
			if z.enableSkip then 
				C.enableAbort()
			else
				C.disableAbort()
			end
			SetEntityActivated( e, 2 )
		else
			z.state = 'error'
		end
		
	elseif
	   z.state == 'error' then
		Show( e )
		PromptLocal( e, "CineGuru: Could not trigger : " .. z.trigTyp )
	
	elseif
	   z.state ~= 'triggered' then
		Show( e )
		PromptLocal( e, "CineGuru: " .. z.state )
	end
	
end
