---------------------------------------------------------------------
--   cg_actor.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------
-- actor script, part of the Cine Guru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
-- Commented out 'require' lines for use with actor switch statement
--:
require "scriptbank\\people\\character_attack"
require "scriptbank\\people\\hostage_runs_away"
-- require "scriptbank\\people\\zombie_attack"
-- require "scriptbank\\people\\patrol"
--:
local lower = string.lower

local actors = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Actor script (NEW). 
-- DESCRIPTION: [TextFile$=""]
-- DESCRIPTION: <Default Animations>
-- DESCRIPTION: Speech file (.wav) for lip-sync [SPEECH0$=""]
-- DESCRIPTION: Speech file (.wav) for lip-sync [SPEECH1$=""]
-- DESCRIPTION: Speech file (.wav) for lip-sync [SPEECH2$=""]
-- DESCRIPTION: Speech file (.wav) for lip-sync [SPEECH3$=""]

function cg_actor_properties( e, script )
	local actor = actors[ e ]
	if actor == nil then return end
	actor.script = script
end				   
-----------------------------------------------------					   
-- music functions (copied from music.lua )
local function music_load( id, str, interval, length )
	if str ~= "" then
		SendMessageS_musicload( id, str )
		SendMessageI_musicsetinterval( id, interval )
		SendMessageI_musicsetlength( id, length )
	end
end

local function music_play( m, fadeTime )
	SendMessageI_musicsetfadetime( fadeTime )
	SendMessageI_musicplayfade( m )	
end

local function music_stop( fadeTime )
	SendMessageI_musicsetfadetime( fadeTime )
	SendMessage_musicstop()
end

local function music_set_volume( v, fadeTime )
	SendMessageI_musicsetfadetime( fadeTime )
	SendMessageI_musicsetvolume( v )
end

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

function CG_IsActor( e )
	return actors[ e ] ~= nil
end

C.Register( 'actor', CG_IsActor )

function CG_GetActor( e )
	return actors[ e ]
end

local U = require "scriptbank\\utillib"
local V = require "scriptbank\\vectlib"

local sub  = string.sub
local rad  = math.rad
local deg  = math.deg
local abs  = math.abs
local find = string.find
local sub  = string.sub

local scenes  = {}
local debugOn = false

local backSpr = { CreateSprite( LoadImage("scriptbank\\Cine Guru MAX\\black.png") ),
                  CreateSprite( LoadImage("scriptbank\\Cine Guru MAX\\black.png") ) }
SetSpritePosition( backSpr[1], 200, 200 )
SetSpriteDepth   ( backSpr[1], 2 )
SetSpritePosition( backSpr[2], 200, 200 )
SetSpriteDepth   ( backSpr[2], 2 )

function CG_Action( script )
	local scene = scenes[ script ]
	if scene == nil then return end
	if scene.action ~= nil then
		if scene.action == 0 then
			scene.action = scene.action + 1
			C.clearAbort()
		end
		return true
	end
end

function cg_actor_init_name( e, name )
	local Ent = g_Entity[ e ] 
	actors[ e ] = { name   = lower( name ), 
	                state  = 'idle', 
					obj    = Ent.obj,
					health = Ent.health,
					lookAt = 0
				  }
					   
	SetAnimationName( e, 'Idle' )
    LoopAnimation( e )
	SetEntityHealthSilent( e, 999999 )
end

local subNumLines  = 0
local subScrStart  = 0
local subSpacing   = 0
local subTextSize  = 0

local function readActions( actor, scene )
	scene.actions = {}
	scene.aborts  = {}
	
	local f = io.open( actor.script, 'r' )
	if not f then 
		actor.state = 'no file'
		return
	end
	for line in io.lines( actor.script ) do
		local acts = C.GetArgs( line )
		local firstAct  = true
		local secondAct = true
		
		for k, v in ipairs( acts ) do
			local actor = lower( acts[ 1 ] )
			
			if sub( actor, 1, 2 ) == '--' then
				-- comment line, just ignore
			elseif
			   actor == 'debug' then
				debugOn = true
				
			elseif 
			   actor == 'music' then
				music_load( 32, acts[ 2 ], 0, tonumber( acts[ 3 ] ) )
   
			elseif
			   actor == 'subtitles' then
				scene.subtitles = {}
			    for line in io.lines( acts[ 2 ] ) do
					scene.subtitles[ #scene.subtitles + 1 ] = line
				end
				subScrStart = ( tonumber( acts[ 3 ] ) or 75 )
				subSpacing  = ( tonumber( acts[ 4 ] ) or  5 )
				subTextSize = ( tonumber( acts[ 5 ] ) or  5 )
				
			elseif
			   actor == 'abort' then
				if firstAct then
					scene.aborts[ #scene.aborts + 1 ] = {}
					firstAct = false
				else
					local this = scene.aborts[ #scene.aborts ]
					if secondAct then
						this.actor = lower( v )
						this.acts  = {}
						secondAct  = false
					else
						this.acts[ #this.acts + 1 ] = v
					end
				end
				
			elseif actor == 'start_anim' then
				local name, anim, speed, wpn = 
				        lower(acts[ 2 ]), acts[ 3 ], tonumber( acts[4] ) or 1, acts[5]
				for k, v in pairs( actors ) do
					if v.name == name then
						SetAnimationName( k, anim )
						SetAnimationSpeed( k, speed )
						LoopAnimation( k )
						v.idleAnim = { Name = anim, speed = speed }
						if wpn then
							if lower(wpn) == 'showwpn' then
								ShowEntityAttachment( k )
							elseif 
							   lower(wpn) == 'hidewpn' then
								HideEntityAttachment( k )
							end
                        end
                        break
                    end
                end

			else
				if firstAct	then					
					scene.actions[ #scene.actions + 1 ] = { actor = actor, acts = {} }
					firstAct = false
				else
					local this = scene.actions[ #scene.actions ]
					this.acts[ #this.acts + 1 ] = v
				end
			end
		end
    end
end

local function changeAnimation( e, anim, loop, speed )
	local animSpeed = speed or anim.speed or 1
	--CharacterControlLimbo( e )
	--PromptDuration( "AS=" .. animSpeed or 'nil', 3000 )
	StopAnimation( e )
	SetAnimationName( e, anim.Name )
	SetAnimationSpeed( e, animSpeed )
	if loop then
		LoopAnimation( e )
	else
		PlayAnimation( e )
	end
end

local animDone = GetObjectAnimationFinished
local function animFinished( e )
	return animDone( e ) == 1
end

local currSubs  = {}
local checkSubs = nil

local actStrings = { 'idle', 'sub', 'anim', 'movestart', 'moveloop', 'movestop', 'move', 'teleport', 'delay', 'mplay', 
                     'mstop', 'mvol', 'vanish', 'speak', 'sub', 'sound', 'switch', 'look', 'activate', 'trigger',
					 'hidewpn', 'showwpn' 
				   }
				   
local function getSeparator( act )
	local separator = '_'
	local length = #act

	for _, actStr in pairs( actStrings ) do
		local pos = find( act, actStr )
		if pos ~= nil then
			pos = pos + #actStr
			local ch = ' '
			while ch == ' ' and pos < length do
				ch = sub( act, pos, pos )
				if ch == ' ' then pos = pos + 1 end
			end
			if ch ~= ' ' then
				separator = ch
				break
			end
		end
	end
	return separator	
end

local animExists = GetEntityAnimationNameExist
local function animExist( e, name )
	return animExists( e, name ) > 0
end

local RDX, RDY, RDZ = RDGetPathPointX, RDGetPathPointY, RDGetPathPointZ

local function pathGood( ax, ay, az, x, y, z )
	local pc = RDGetPathPointCount()
	if pc > 0 then
		-- first check the starting point matches entity position, RDFindPath can't find 'nearest' start which is no good
		if not U.CloserThan( ax, ay, az, RDX(0), RDY(0), RDZ(0), 25 ) then
			return false
		end
		-- check last point is close to the mark position
		if not U.CloserThan( x, y, z, RDX(pc-1), RDY(pc-1), RDZ(pc-1), 25 ) then
			return false
		end
		return true
	end
end

local function Act( e, actor, scene, act )
	if scene.actSeparator == nil then
		scene.actSeparator = getSeparator( act )
	end
	actor.action = C.GetArgs( act, scene.actSeparator )
	local action = actor.action[ 1 ]
	if action == 'idle' then
		actor.idleAnim = { Name = actor.action[ 2 ] }
		if actor.action[ 3 ] ~= nil then 
			actor.idleAnim.speed = tonumber( actor.action[ 3 ] ) 
		end
		actor.currAct = actor.currAct + 1

	elseif 
	   action == 'movestart' then
		actor.moveAnim1 = { Name = actor.action[ 2 ] }
		if actor.action[ 3 ] ~= nil then 
			actor.moveAnim1.speed = tonumber( actor.action[ 3 ] ) 
		end
		actor.currAct = actor.currAct + 1
	
	elseif 
	   action == 'moveloop' then
		actor.moveAnim2 = { Name = actor.action[ 2 ] }
		if actor.action[ 3 ] ~= nil then 
			actor.moveAnim2.speed = tonumber( actor.action[ 3 ] ) 
		end
		actor.currAct = actor.currAct + 1
	
	elseif 
	   action == 'movestop' then
		actor.moveAnim3 = { Name = actor.action[ 2 ] }
		if actor.action[ 3 ] ~= nil then 
			actor.moveAnim3.speed = tonumber( actor.action[ 3 ] ) 
		end
		actor.currAct = actor.currAct + 1
	
	elseif 
	   action == 'look' then 
	    actor.lookAt = nil
		local target = actor.action[ 2 ]
		if target == 'player' then
			actor.lookAt = 'player'
		elseif
		   target == 'angle' then
			actor.lookAt = tonumber( actor.action[ 3 ] )
		elseif
		   target == 'actor' then
			for k, v in pairs( actors ) do
				if v.name == lower( actor.action[ 3 ] ) then
					actor.lookAt = 1000 + k
					break
				end
			end
		elseif
		   target == 'mark' then
			local k, obj, x, y, z = CG_GetMarkWithOffset( lower( actor.action[ 3 ] ) )
			if k then
				PositionObject( obj, x, y, z )
				actor.lookAt = 1000 + k 
			end
		elseif
		   target == 'forward' then
			actor.lookAt = 0
		end
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'speak' then
		if actor.action[ 2 ] ~= nil then 
			local sndSlot = tonumber( actor.action[ 2 ] ) 
			PlaySpeech( e, sndSlot )

			if actor.action[ 3 ] ~= nil then
				SetSound( e, sndSlot )
				SetSoundVolume( tonumber( actor.action[ 3 ] )  )
			end
		end					
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'sub' then
		local num = tonumber( actor.action[ 2 ] )
		local ti   = C.getTime() + tonumber( actor.action[ 3 ] )
		local line = ( tonumber( actor.action[ 4 ] ) or 1 )
		local size = #scene.subtitles[ num ]
		if actor.action[ 5 ] ~= nil then 
			size = ( tonumber( actor.action[ 5 ] ) or size )						
		end
		currSubs[ line ] = { text = scene.subtitles[ num ], 
		                     ti = ti, line = line, size = size } 
		checkSubs = e
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'mplay' then
		if actor.action[ 2 ] ~= nil then
			music_play( 32, tonumber( actor.action[ 2 ] ) )
		else
			music_play( 32, 0 )
		end	
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'mstop' then
		if actor.action[ 2 ] ~= nil then
			music_stop( tonumber( actor.action[ 2 ] ) )
		else
			music_stop( 0 )
		end
		actor.currAct = actor.currAct + 1

	elseif 
	   action == 'mvol' then
		if actor.action[ 2 ] ~= nil then
			if actor.action[ 3 ] ~= nil then
				music_set_volume( tonumber( actor.action[ 2 ] ), 
								  tonumber( actor.action[ 3 ] ) )
			else
				music_set_volume( tonumber( actor.action[ 2 ] ), 0 )
			end
		end
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'anim' then
	    local anim = {}
		anim.Name = actor.action[ 2 ]
		if actor.action[ 3 ] ~= nil then 
			anim.speed = tonumber( actor.action[ 3 ] ) 
		end

		changeAnimation( e, anim )
		actor.state = 'acting'
		
	elseif
	   action == 'hidewpn' then
		-- Hide Weapon
		HideEntityAttachment(e)
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'showwpn' then
		-- Show Weapon 
		ShowEntityAttachment(e)
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'move' then
		local x, y, z = CG_GetMark( lower( actor.action[ 2 ] ) )
		actor.moveSpeed = GetEntityMoveSpeed(e) / 100
		if actor.action[ 3 ] ~= nil then
			actor.moveSpeed = tonumber( actor.action[ 3 ] ) / 100
		end
		actor.turnSpeed = GetEntityTurnSpeed(e) / 4
		if actor.action[ 4 ] ~= nil then
			actor.turnSpeed = tonumber( actor.action[ 4 ] ) / 4
		end
		if x ~= nil then
			StopAnimation( e )	
			--CharacterControlManual( e )
			--CharacterControlUnarmed( e )
			--AISetEntityControl( actor.obj, AI_MANUAL )
			--PromptLocal( e, actor.moveSpeed .. ", " .. actor.turnSpeed )
			local y = RDGetYFromMeshPosition( x, y, z )
			local ax, ay, az = GetObjectPosAng( actor.obj )

			RDFindPath( ax, ay, az, x, y, z )

			if pathGood( ax, ay, az, x, y, z ) then
			
				if actor.moveAnim1 ~= nil then
					if animExist( e, actor.moveAnim1.Name ) then
						changeAnimation( e, actor.moveAnim1, false, actor.moveSpeed )
						actor.state = 'start_walk'
					else
						actor.errStr = "No " .. actor.moveAnim1.Name .. " animation"
						actor.state  = 'done'
					end
					
				elseif
				   actor.moveAnim2 ~= nil then
					if animExist( e, actor.moveAnim2.Name ) then
						changeAnimation( e, actor.moveAnim2, true, actor.moveSpeed )
						actor.state = 'acting'
					else
						actor.errStr = "No " .. actor.moveAnim2.Name .. " animation"
						actor.state  = 'done'
					end
					
				else
					if animExist( e, "Walk_Start" ) then
						SetAnimationName( e, "Walk_Start" )
						SetAnimationSpeed( e, actor.moveSpeed )
						PlayAnimation( e )
						actor.state = 'start_walk'
					else
						actor.errStr = "No Walk_Start animation"
						actor.state  = 'done'
					end
				end
				StartMoveAndRotateToXYZ( e, actor.moveSpeed, actor.turnSpeed )
			else
				--actor.errStr = "Can't reach mark " .. ( actor.action[ 2 ] or 'nil' )
				--actor.state  = 'done'
			end
			
		else
			actor.errStr = "Can't find mark " .. ( actor.action[ 2 ] or 'nil' )
			actor.state  = 'done'
		end

	elseif
	   action == 'teleport' then
		local x, y, z, ax, ay, az = CG_GetMark( lower( actor.action[ 2 ] ) )
		if x ~= nil then
			_, ay = V.GetPYAngles( V.FromEuler( rad( ax ), rad( ay ), rad( az ) ) )
			ay = deg( ay )
			StopAnimation( e )
			--CharacterControlLimbo( e )
			CollisionOff( e )
			SetPosition( e, x, y, z )
			CollisionOn( e )
			AISetEntityPosition( actor.obj, x, y, z ) 
			SetRotationYSlowly( e, ay, 100 )
			actor.currAct = actor.currAct + 1
			actor.state = 'ready'
			actor.idling = false
		else
			actor.errStr = "Can't find mark " .. ( actor.action[ 2 ] or 'nil' )
			actor.state  = 'done'
		end

	elseif
	   action == 'vanish' then
		actor = nil
		SetAttachmentVisible( e, 0 )
		Destroy( e )
		return

	elseif
	   action == 'delay' then
		actor.timer = C.getTime() + tonumber( actor.action[ 2 ] )
		actor.state = 'delay'

	elseif
	   action == 'sound' then
		SetEntityString ( e, tonumber( actor.action[ 2 ] ), actor.action[ 3 ], 1 )
		actor.currAct = actor.currAct + 1
		
	elseif 
	   action == 'switch' then
		local newScript = lower( actor.action[ 2 ] )
		for i = 3, #actor.action do
			newScript = newScript .. "_" .. lower( actor.action[ i ] )
		end
		if scene.action < #scene.actions then
			scene.action = scene.action + 1
		end
		SetEntityHealthSilent( e, actor.health )
		SwitchScript( e, newScript )
		return

	elseif
	   action == 'activate' then
		ActivateIfUsed(e)
		actor.currAct = actor.currAct + 1

	elseif
	   action == 'trigger' then
		if CG_ActivateCamera ~= nil then
			CG_ActivateCamera( lower( actor.action[ 2 ] ) )
		end
		actor.currAct = actor.currAct + 1

	end
	return true
end
	
function cg_actor_main( e )

	local actor = actors[ e ]
	if actor == nil then return end
	
--	PromptLocal( e, actor.script or 'nil' )
	
	if C.checkForAbort( e ) and
	   CG_GetActiveCamera ~= nil and
	   CG_GetActiveCamera() ~= nil then
		for k, v in pairs( actors ) do
			if scenes[ v.script ].action and 
               scenes[ v.script ].action > 0 then
				v.state = 'abort'
			end
		end
	end
	
	if checkSubs == e then
		-- this actor has displayed a subtitle 
		-- display any that are still valid
		for k, v in pairs( currSubs ) do
			if C.getTime() <= v.ti then
				SetSpriteSize( backSpr[ v.line ], v.size, subSpacing )
				SetSpriteOffset( backSpr[ v.line ], v.size / 2, 0 )
				if debugOn then Prompt( v.size ) end
				local Ypos = subScrStart + ( v.line - 1 ) * subSpacing
				PasteSpritePosition( backSpr[ v.line ], 50, Ypos )
				TextCenterOnXColor( 50,  Ypos,             -- position
						            subTextSize,           -- size
				                    v.text,                -- text 
						            255, 255, 255 )        -- colour
			else
				SetSpritePosition( backSpr[ v.line ], 200, 200 )
			end
		end
	else
		SetSpritePosition( backSpr[ 1 ], 200, 200 )
		SetSpritePosition( backSpr[ 2 ], 200, 200 )
	end

	local scene = scenes[ actor.script ]
	if scene == nil then 
		scenes[ actor.script ] = {}
		return
	end
	
	if debugOn then
		if actor.action ~= nil then
			PromptLocal( e, actor.state .. ", " .. 
			                actor.action[ 1 ] .. ", " .. 
							( actor.lookAt or 'nil' ) )
		else
			PromptLocal( e, actor.state )
		end
	end
	
    if actor.state == 'idle' then
		
		if scene.actions == nil then
			-- read actions script for actor
			readActions( actor, scene )
			if actor.state == 'no file' then return end
		end	
		if #scene.actions > 0 then
			scene.action = 0
			actor.state = 'ready'
		else
			actor.state = 'error'
		end

	elseif
	   actor.state == 'ready' then
		if scene.action > 0 then
		
		  if scene.actions[ scene.action ].actor == actor.name then
		   
			-- do whatever the scene requires
			if actor.currAct == nil then
				actor.currAct = 1
			end

			local act = scene.actions[ scene.action ].acts[ actor.currAct ]
			if act ~= nil then
				if not Act( e, actor, scene, act ) then return end
			else
				-- no more acts for this actor
				if scene.action < #scene.actions then
					scene.action = scene.action + 1
					actor.state = 'ready'
					actor.currAct = nil
				end
			end
		  end
		end
		
		if actor.state ~= 'acting' and
		   actor.state ~= 'start_walk' then
			if not actor.idling then
				if actor.idleAnim ~= nil then
					changeAnimation( e, actor.idleAnim, true )
					actor.idling = true
				end
			end
		end
		
	elseif 
	   actor.state == 'abort' then
		for i = 1, 5 do StopSound( e, i - 1 ) end
		for _, v in pairs( scene.aborts ) do
			if v.actor == actor.name then
				
				for _, w in ipairs( v.acts ) do
					if not Act( e, actor, scene, w ) then return end
				end
				break
			end
		end
		actor.state = 'done'
		checkSubs   = nil
		
	elseif
	   actor.state == 'acting' then
		actor.idling = false
		if actor.action[ 1 ] == 'anim' and 
		   animFinished( e ) then
			-- animation finished, trigger next act
			actor.currAct = actor.currAct + 1
			actor.state = 'ready'
			
		elseif
		   actor.action[ 1 ] == 'move' then
			local x, y, z, xa, ya, za = CG_GetMark( lower( actor.action[ 2 ] ) ) 
			local ax, ay, az = GetObjectPosAng( actor.obj )
			RDFindPath( ax, ay, az, x, y, z )
			
			if not U.CloserThan( ax, ay, az, x, y, z, 25 ) then
				--PromptLocal( e, actor.moveSpeed .. ", " .. actor.turnSpeed )
				local pointindex = MoveAndRotateToXYZ( e, actor.moveSpeed, actor.turnSpeed )
			else
				actor.stop = false
				if actor.moveAnim3 ~= nil then
					if animExist( e, actor.moveAnim3.Name ) then
						changeAnimation( e, actor.moveAnim3, false, actor.moveSpeed )
						actor.state = 'end_walk'
					else
						actor.errStr = "No " .. actor.moveAnim3.Name .. " animation"
						actor.state  = 'done'
					end
					
				elseif 
				   actor.moveAnim2 == nil and
				   animExist( e, "Walk_Stop" ) then
					SetAnimationName( e, "Walk_Stop" )
					SetAnimationSpeed( e, actor.moveSpeed )
					PlayAnimation( e )
					actor.state = 'end_walk'

				else
					actor.stop  = true
					actor.state = 'end_walk'
				end	
			end
		end
	
	elseif 
	   actor.state == 'start_walk' then
		actor.idling = false
		if animFinished( e ) then
			if actor.moveAnim2 ~= nil then
				if animExist( e, actor.moveAnim2.Name ) then
					changeAnimation( e, actor.moveAnim2, true, actor.moveSpeed )
					actor.state = 'acting'
				else
					actor.errStr = "No " .. actor.moveAnim2.Name .. " animation"
					actor.state  = 'done'
				end
			else
				if animExist( e, "Walk_Loop" ) then
					SetAnimationName( e, "Walk_Loop" )
					SetAnimationSpeed( e, actor.moveSpeed )
					LoopAnimation( e )
					actor.state = 'acting'
				else
					actor.errStr = "No Walk_Loop animation"
					actor.state  = 'done'	
				end
			end
		end
		
	elseif
	   actor.state == 'end_walk' then
		actor.idling = false
		if actor.stop or animFinished( e ) then
			local _, _, _, xa, ya, za = CG_GetMark( lower( actor.action[ 2 ] ) ) 
			--CharacterControlLimbo( e )
			_, ya = V.GetPYAngles( V.FromEuler( rad( xa ), rad( ya ), rad( za ) ) )
			ya = deg( ya )
			SetRotationYSlowly( e, ya, 100 )
			actor.currAct = actor.currAct + 1
			actor.state = 'ready'
		end
		
	elseif
	   actor.state == 'delay' then
		if C.getTime() > actor.timer then
			actor.currAct = actor.currAct + 1
			actor.state = 'ready'
		end
		
	elseif
	   actor.state == 'done' then
		SetEntityHealthSilent( e, actor.health )
		if actor.errStr ~= nil then
			PromptLocal( e, actor.errStr )
		end
		
	elseif
       actor.state == 'error' then
		PromptLocal( e, "Cine Guru: Actor script error" )
		return
	elseif
	   actor.state == 'no file' then
		PromptLocal( e, "Cine Guru: No file - " .. ( actor.script or 'nil' ) )
		return
	end
	
	if actor.lookAt ~= nil then
		if actor.lookAt == 'player' then 
			SendMessageF_lookattargete( e, 0 )
            SendMessageF_lookatplayer( e, 10)

		elseif
		   type( actor.lookAt ) == "number" then
			if actor.lookAt == 0 then
				LookForward( e, 10 )
			elseif
			   abs( actor.lookAt ) < 360 then
				LookAtAngle( e, actor.lookAt )
			else
				SendMessageF_lookattargete( e, actor.lookAt - 1000 )
				SendMessageF_lookattarget( e, 10 )
			end
		end
	end	
end
 

	
	


