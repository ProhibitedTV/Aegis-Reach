-----------------------------------------------------------------------
--   cg_trigger.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
-----------------------------------------------------------------------
-- Timer-delayed trigger script, part of the Cine Guru GameGuru pack.
--
-- For instructions on use see Cine Guru documentation.
-----------------------------------------------------------------------

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local lower = string.lower

local triggered = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru trigger. 
-- DESCRIPTION: Trigger time (seconds) [TI#=0]
function cg_trigger_properties( e, ti )
	local trigger = triggered[ e ]
	if trigger == nil then return end
	trigger.tTime = ti * 1000 
end	

function CG_IsTrigger( e )
	return triggered[ e ] ~= nil
end

C.Register( 'trigger', CG_IsTrigger )

function cg_trigger_init( e )
	triggered[ e ] = { state = 'init', tryAgain = true }
    Hide( e )
	CollisionOff( e )
end

local function marklight( e )
	local light = CG_GetLightMarker( e )
	light.IsTriggered = true
	light.IsFirst = true
	CG_ProcessLightMarker( e )
end

function cg_trigger_main( e )
	local trigger = triggered[ e ]
	if trigger == nil or trigger.state == 'done' then return end
	
	if trigger.state == 'init' then
		local Ent = g_Entity[ e ]
		if Ent.activated == 1 then
			trigger.state = 'done'
			return
		end
		local links = C.GetEntityLinks( e, { 'camera', 'lightmarker', 'node', 'trigger' } )
		-- can be only connected to one camera or one node at present 
		for _, v in pairs( links ) do
			if C.isCamera( v ) then
				if trigger.camera == nil then
					trigger.camera = v
					trigger.node   = 0
					trigger.state  = 'idle'
				else
					trigger.state = 'too many'
				end
				
			elseif 
			   C.isNode( v ) then
				local node = CG_GetNode( v )
				if trigger.camera == nil then
					trigger.camera = node.camera
					trigger.node   = node.node
					trigger.state  = 'idle'
				else
					trigger.state = 'too many'
				end
			elseif
			   C.isLightMarker( v ) then
				marklight( v )
			end
		end	
		-- Could be connected to another trigger
		for _, v in pairs( links ) do
			if C.isTrigger( v ) then
				local trig = triggered[ v ]
				if trig.camera ~= nil then
					trigger.camera = trig.camera
					trigger.node   = trig.node
					trigger.state  = 'idle'
					break
				end
			end
		end
		if trigger.camera == nil then
			if trigger.tryAgain then
				trigger.tryAgain = false
				return
			end
			Show( e )
			trigger.state = 'no camera'
			return
		end
		
    elseif 
	   trigger.state == 'idle' then
		local camera, cnode = CG_GetActiveCamera()
		if camera == trigger.camera  and
		   ( trigger.node == 0       or
		     trigger.node == cnode ) then
			trigger.timer = C.getTime() + trigger.tTime
			trigger.state = 'wait'
		end
	end
	
    if trigger.state == 'wait' and 
	   not C.checkForAbort( e ) and
	   C.getTime() >= trigger.timer then
		ActivateIfUsed( e )
		PerformLogicConnections( e )
		SetEntityActivated( e, 1 )
		trigger.state = 'done'
	elseif
	   trigger.state == 'too many' then
		PromptLocal( e, "CineGuru: Trigger - too many cameras/nodes attached" )
		
	elseif 
	   trigger.state == 'no camera' then
		PromptLocal( e, "CineGuru: Trigger - no camera/node attached" )
    end
end
 

	
	


