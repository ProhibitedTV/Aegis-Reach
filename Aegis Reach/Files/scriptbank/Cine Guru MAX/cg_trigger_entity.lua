------------------------------------------------------------------------------
--   cg_trigger_entity.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
------------------------------------------------------------------------------
-- cinematic trigger script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
------------------------------------------------------------------------------
-- DESCRIPTION: Cine Guru Entity Trigger
-- DESCRIPTION: [EnableSkip!=1]
-- DESCRIPTION: [DisableIfCombat!=0]

local triggers = {}
function cg_trigger_entity_properties( e, enableSkip, disableIfCombat )
	local trig = triggers[ e ]
	if trig == nil then return end
	if enableSkip ~= nil then
		trig.enableSkip = enableSkip == 1
	end
	if disableIfCombat ~= nil then
		trig.disableIfCombat = disableIfCombat == 1
	end
end

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function cg_trigger_entity_init( e )
	triggers[ e ] = { state = 'init', enableSkip = true }
	Hide( e )
	CollisionOff( e )
end

function CG_IsTriggerEnt( e )
	return triggers[ e ] ~= nil
end

C.Register( 'trigEnt', CG_IsTriggerEnt )

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

function cg_trigger_entity_main( e )
	local trig = triggers[ e ]
	if trig.state == 'done' then return end
	
	local Ent = g_Entity[ e ]
	
	if Ent.activated == 1    and
	   trig.state == 'idle'  and
	   not ( trig.disableIfCombat and 
	         C.inCombat() )  then
		trig.state = 'triggered'
	elseif
	   Ent.activated == 2 then
		trig.state = 'done'
		return
	end
	
	if trig.state == 'init' then
		local links = C.GetEntityLinks( e )
		trig.trigTyp = 'none'
		for _, v in ipairs( links ) do
			if C.isCredits( v ) then
				trig.trigTyp = 'credits'
				trig.creditsEnt = v
				
			elseif
			   C.isCamera( v ) then
				if trig.cameraEnt ~= nil then
					trig.state = 'Too many Cameras!'
					return
				end
				trig.cameraEnt = v
				markCamera( v )
				
			elseif
			   C.isActor( v ) then
				if trig.actorEnt ~= nil then
					trig.state = 'Too many Actors!' 
					return
				end
				trig.actorEnt = v
				trig.script   = CG_GetActor( v ).script
				
			elseif
			   C.isLightMarker( v ) then
				if trig.lightEnts == nil then
					trig.lightEnts = {}
				end
				trig.lightEnts[ #trig.lightEnts + 1 ] = v
				marklight( v )
			end
		end
		trig.state = 'idle'
		return

	elseif 
	   trig.state == 'triggered' then
		local success = true
		trig.trigtyp = ""
		if trig.lightEnts ~= nil and CG_ActivateLightMarker ~= nil then
			for _, lEnt in pairs( trig.lightEnts ) do
				if not CG_ActivateLightMarker( lEnt ) then
					success = false
				end
			end
		end
		if not success then  
			trig.trigtyp = "Light" 
		else
			if trig.script ~= nil and CG_Action ~= nil then
				success = CG_Action( trig.script )
			end
			if not success then 
				trig.trigtyp = "Actor"
			else
				if trig.cameraEnt ~= nil and CG_ActivateCamera ~= nil then 
					success = CG_ActivateCamera( trig.cameraEnt )
				end
				if not success then 
					trig.trigTyp = "Camera"
				else
					if trig.creditsEnt ~= nil and CG_RollCredits ~= nil then
						success = CG_RollCredits( trig.creditsEnt )
					end
					if not success then trig.trigTyp = "Credits" end
				end
			end
		end
		if success then
			trig.state = 'done'
			if trig.enableSkip then 
				C.enableAbort()
			else
				C.disableAbort()
			end
			SetEntityActivated( e, 2 )
			
		else
			trig.state = 'error'
		end
		
	elseif
	   trig.state == 'error' then
		--Show( e )
		--PromptLocal( e, "CineGuru: Could not trigger : " .. trig.trigTyp )
	
	elseif
	   trig.state ~= 'triggered' then
		--Show( e )
		--PromptLocal( e, "CineGuru: " .. trig.state )
	end
end
