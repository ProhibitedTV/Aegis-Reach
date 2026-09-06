-------------------------------------------------------------------
--   cg_lib.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
-------------------------------------------------------------------
-- cinematic library module, part of the Cine Guru GameGuru pack.
--
--(strongly suggest you don't make changes to this library!)
 
local U = require "scriptbank\\utillib"
local Q = require "scriptbank\\quatlib"
local V = require "scriptbank\\vectlib"

-- replace global ResumeGame() function so we can detect standalone game 
-- resumption for timing purposes

local resume = resume or _G.ResumeGame

local gamePaused = false
 
function ResumeGame()
	gamePaused = true
	resume()
end

local CG = {_G = _G}

-- import section: modules
local sqrt = math.sqrt
local deg  = math.deg
local abs  = math.abs
local atan = math.atan2
local log  = math.log
local min  = math.min
local find = string.find
local sub  = string.sub

local pairs  = pairs
local ipairs = ipairs
local fopen  = io.open
local fclose = io.close
local fout   = io.output
local fwrite = io.write
local dtrace = debug.traceback
local ddate  = os.date

-- import section: GG functions
local getObPos    = GetObjectPosAng
local pasteSprP   = PasteSpritePosition
local getEntLinks = GetEntityRelationshipID
local getCombMus  = GetCombatMusicTrackPlaying

-- include these for debugging
local Prompt  = Prompt
local PromptD = PromptDuration
local PromptE = PromptLocal

local gEnt = g_Entity

_ENV = CG 

local function plrHealth() return _G.g_PlayerHealth end

local function abortKeyPressed() return _G.g_KeyPressSPACE == 1 end
local abortDelay = 200

local lastTime = 0
local tDiff    = 0 

function CG.getTime()
	local tn = _G.g_Time
	local tD = tn - lastTime
	if ( timePaused or tD > 1000 ) and lastTime ~= 0 then
		tDiff = tDiff + tD
		timePaused = false
	end
	lastTime = tn
	return tn - tDiff
end

local lastHealth     = plrHealth()
local nextHealthTime = 0

function CG.inCombat( e )
	local health = plrHealth()
	local retVal = false
	if health ~= lastHealth then
		if health < lastHealth then
			nextHealthTime = getTime() + 5000
			retVal = true
		end
		lastHealth = health
	elseif 
	   getTime() < nextHealthTime then
		retVal = true
	else
		retVal = getCombMus() == 1
	end
	return retVal
end
		
local CG_EntList = 
	{ credits   = {}, actor    = {}, camera = {}, node   = {}, trigger     = {}, 
	  trigEnt   = {}, image    = {}, zone   = {}, tgtEnt = {}, focal       = {},
	  endpoint  = {}, shake    = {}, sound  = {}, post   = {}, lightmarker = {},
      lightnode = {}, lightend = {}
	}

function CG.Register( name, func )
	if CG_EntList[ name ].func ~= nil then return end
	CG_EntList[ name ].func = func
end

function CG.isCredits( e )
	local func = CG_EntList[ 'credits' ].func
	if func ~= nil then return func( e ) end
end

function CG.isActor( e )
	local func = CG_EntList[ 'actor' ].func
	if func ~= nil then return func( e ) end
end

function CG.isCamera( e )
	local func = CG_EntList[ 'camera' ].func
	if func ~= nil then return func( e ) end
end

function CG.isNode( e )
	local func = CG_EntList[ 'node' ].func
	if func ~= nil then return func( e ) end
end

function CG.isTrigger( e )
	local func = CG_EntList[ 'trigger' ].func
	if func ~= nil then return func( e ) end
end

function CG.isTriggerEnt( e )
	local func = CG_EntList[ 'trigEnt' ].func
	if func ~= nil then return func( e ) end
end

function CG.isImage( e )
	local func = CG_EntList[ 'image' ].func
	if func ~= nil then return func( e ) end
end

function CG.isZone( e )
	local func = CG_EntList[ 'zone' ].func
	if func ~= nil then return func( e ) end
end

function CG.isTargetEnt( e )
	local func = CG_EntList[ 'tgtEnt' ].func
	if func ~= nil then return func( e ) end
end

function CG.isFocalPoint( e )
	local func = CG_EntList[ 'focal' ].func
	if func ~= nil then return func( e ) end
end

function CG.isEndpoint( e )
	local func = CG_EntList[ 'endpoint' ].func
	if func ~= nil then return func( e ) end
end

function CG.isShake( e )
	local func = CG_EntList[ 'shake' ].func
	if func ~= nil then return func( e ) end
end

function CG.isPost( e )
	local func = CG_EntList[ 'post' ].func
	if func ~= nil then return func( e ) end
end

function CG.isSound( e )
	local func = CG_EntList[ 'sound' ].func
	if func ~= nil then return func( e ) end
end

function CG.isLightNode( e )
	local func = CG_EntList[ 'lightnode' ].func
	if func ~= nil then return func( e ) end
end

function CG.isLightMarker( e )
	local func = CG_EntList[ 'lightmarker' ].func
	if func ~= nil then return func( e ) end
end

function CG.isLightEnd( e )
	local func = CG_EntList[ 'lightend' ].func
	if func ~= nil then return func( e ) end
end

local function isValid( e, validList )
	for _, v in pairs( validList ) do
		if v == 'other' then
			if not( isCamera( e )    or isNode( e )        or 
		            isTrigger( e )   or isEndpoint( e )    or
				    isCredits( e )   or isFocalPoint( e )  or
				    isImage( e )     or isSound( e )       or
				    isShake( e )     or isTriggerEnt( e )  or
				    isActor( e )     or isTargetEnt( e )   or
				    isZone( e )      or isPost( e )        or
					isLightNode( e ) or isLightMarker( e ) or
					isLightEnd( e )
			       ) then
				return true
			end
		elseif
		   CG_EntList[ v ].func ~= nil and
		   CG_EntList[ v ].func( e ) then 
			return true
		end
	end
end

function CG.GetEntityLinks( e, validList )
	local list = {}
	for i = 0, 9 do
		local elink = getEntLinks( e, i )
		if elink > 0 then
			if validList == nil or 
			   isValid( elink, validList ) then
				list[ #list + 1 ] = elink
			end
		end
	end
	return list
end

local log2 = log( 2 )

-- good for IEEE754, double precision
local function islarge (x) return x > 2 ^ 28 end
local function issmall (x) return x < 2 ^ (-28) end

local function isinfornan (x)
  return x ~= x or x == INF or x == -INF
end

local function log1p ( x ) -- not very precise, but works well
	local u = 1 + x
	if u == 1 then return x end -- x < eps?
	return log( u ) * x / ( u - 1 )
end

local function asinh( x )
	local y = abs( x )
	if issmall( y ) then return x end
	local a
	if islarge( y ) then -- very large?
		if isinfornan( x ) then return x + x end
		a = log2 + log( y )
	elseif y > 2 then
		a = log( 2 * y + 1 / ( y + sqrt( 1 + y * y ) ) )
	else
		local y2 = y * y
		a = log1p( y + y2 / ( 1 + sqrt( 1 + y2 ) ) )
	end
	return x < 0 and -a or a -- transfer sign
end

function CG.myFunkyMath( t )
	t = t * 2
	local res = 0.5 + asinh( ( t - 1 ) * 8 ) / 5.6
	if res < 0 then return 0 end
	return min( res, 1 )
end

function CG.myFunkyMath2( t )
	local res = ( log( t ) + 2 ) / 2
	if res < t then return t end
	return min( res, 1 )
end

-- this function takes a Euler angle representation of orientation and 
-- returns the Roll component
function CG.getRollAngle( xa, ya, za )  -- Euler radians 
	-- first get a normalised 'facing forward' for given Euler angles
	local v = V.FromEuler( xa, ya, za )
	
	local _,_, Quadrant =  V.GetPYAngles( v )
	
	-- now get a normalised 'up facing' vector for given Euler angles
	v = V.FromEuler( xa, ya, za, true )

	-- now work out the roll angle from the components of the result
	if Quadrant == 'E' then return atan( -v.z, abs( v.y ) ) end
	if Quadrant == 'N' then return atan(  v.x, abs( v.y ) ) end
	if Quadrant == 'S' then return atan( -v.x, abs( v.y ) ) end
	return atan( v.z, abs( v.y ) )
end	

-- simple function to strip off leading and trailing spaces in a string
local function trimStr( str )
	local firstChar = 1
	for i = 1, #str do
		if sub( str, i, i ) ~= ' ' then
			firstChar = i
			break
		end
	end
	local lastChar = #str
	for i = lastChar, firstChar, -1 do
		if sub( str, i, i ) ~= ' ' then
			lastChar = i
			break
		end
	end
	return sub( str, firstChar, lastChar )
end

-- function takes a string containing multiple arguments separated by
-- a specified character and returns them in a list
-- so for example GetArgs( 'a_b_c', '_' ) would return:
-- { 'a', 'b', 'c' }
function CG.GetArgs( str, sep )
    local sep = sep or ','
    local pos = 1
    local list = {}
    local length = #str
      
    while pos < length + 1 do
        local nextPos = find( str, sep, pos + 1 ) or length
        if nextPos < length then
            list[ #list + 1 ] = trimStr( sub( str, pos, nextPos - 1 ) )
        else
			if sub( str, nextPos, nextPos ) == sep then
				nextPos = nextPos - 1
			end
            list[ #list + 1 ] = trimStr( sub( str, pos, nextPos ) )
            break
        end
        pos = nextPos + 1
    end
    return list
end

local spriteList = {}

-- Adds sprites to be pasted in a particular order once per frame
-- typ is one of (in rendering order) 'overlay', 'letterbox, 'subtitle', 'fade'
function CG.AddSprite( typ, spr, x, y )
	x = x or 0
	y = y or 0
	
	if typ == nil or spr == nil then
		local file = fopen( "scriptbank\\gg_debug.out", "a+" )
		if file ~= nil then
			fout( file )
			if typ == nil then 
				fwrite( ddate() .. " !!Error!! Nil image type " )
			else
				fwrite( ddate() .. " !!Error!! Nil sprite " )
			end
			fwrite( dtrace() .. '\n\n' )
			fclose( file )
		end
	end
	
	local sl = spriteList[ typ ]
	if sl == nil then 
		spriteList[ typ ] = {}
		sl = spriteList[ typ ]
	end

	if sl[ spr ] == nil then
		sl[ spr ] = { x = x, y = y }
	end
end

function CG.RemoveSprite( typ, spr )
	if spriteList[ typ ] ~= nil then
		spriteList[ typ ][ spr ] = nil
	end
end

function CG.DisplaySprites()
	for k, v in pairs( spriteList[ 'overlay' ] or {} ) do
		pasteSprP( k, v.x, v.y )
	end
	for k, v in pairs( spriteList[ 'letterbox' ] or {} ) do
		pasteSprP( k, v.x, v.y )
	end
	for k, v in pairs( spriteList[ 'subtitle' ] or {} ) do
		pasteSprP( k, v.x, v.y )
	end
	for k, v in pairs( spriteList[ 'fade' ] or {} ) do
		pasteSprP( k, v.x, v.y )
	end
	spriteList = {}
end

-- Catmull-Rom needs at least four points so this function adds a dummy point at start
-- and end 
local function AddExtraPoints( CM )
	local vec = V.Sub( CM[ 2 ].pos, CM[ 3 ].pos )
	
	-- invented first point
	CM[ 1 ] = { pos = V.Add( CM[ 2 ].pos, vec ), ti = CM[ 2 ].ti }
	
	-- invented last point
	local endPos = #CM
	vec = V.Sub( CM[ endPos ].pos, CM[ endPos -1 ].pos )
	
	CM[ endPos + 1 ] = { pos = V.Add( CM[ endPos ].pos, vec ) }
end

function CG.copyObject( from, to )
	if from == nil then return end
	if to == nil then to = {} end
	for k, v in pairs( from ) do
		to[k] = v
	end
	return to
end

local function createPoint( x, y, z, obj, ft, data )
	return { pos  = V.Create( x, y, z ), 
	         obj  = obj,
             data = copyObject( data ),			 
		     ti   = ft }
end

-- builds a list of Catmull-Rom points and ads them to the provided list.
-- vectlib function CR_Point can then use this list to provide smooth
-- path points. 
function CG.BuildCMPoints( list )
	if list.endPos == nil and #list.nodes == 0 then return end
	
	local CMList = {}
	local cx, cy, cz = getObPos( list.obj )
	
	CMList[ 2 ] = createPoint( cx, cy, cz, list.obj, list.filmtime, 
	                           list.data )
	
	if #list.nodes == 0 then
		-- simple case, just camera and endpoint
		local ep = list.endPos
		local ex, ey, ez = getObPos( ep.obj )
		CMList[ 3 ] = createPoint( ex, ey, ez, ep.obj, list.filmtime )
		
	else
		for i = 1, #list.nodes do
			local node = list.nodes[ i ]
			if node == nil then
				PromptD( "cg_lib.BuildCMPoints Error - missing node: " .. i, 4000 )
				return
			else
				local nx, ny, nz = getObPos( node.obj )
				CMList[ 2 + i ] = createPoint( nx, ny, nz, node.obj, node.filmtime, 
											   node.data )
			end
		end
		
		if list.endPos ~= nil then
			local ep = list.endPos
			local ex, ey, ez = getObPos( ep.obj )
			local lastnode = list.nodes[ #list.nodes ]
			CMList[ 2 + #list.nodes + 1 ] = createPoint( ex, ey, ez, ep.obj, 
											             lastnode.filmtime )
		end
	end
	
	AddExtraPoints( CMList )
	
	list.CMList = CMList
	list.curCM  = 2
	list.endCM  = #CMList - 2
end

-- function to detect when Euler anges are at the gimbal lock position
-- if so it simply returns the last position (prior to lock) when the 
-- function was called.  
-- p is the list it will use to store the angles in.
function CG.avoidGimbalLock( p, xA, yA, zA ) -- angles in radians
	if p.lastyA ~= nil then
		if abs( deg( yA ) ) > 89.99995 then
			return p.lastxA, p.lastyA, p.lastzA
		end
	end
	p.lastxA, p.lastyA, p.lastzA = xA, yA, zA
	return xA, yA, zA
end

local controlEnt    = nil
local abortEnabled  = true
local abortPressed  = false
local abortTimer    = nil
local abortTrigger  = false

function CG.checkForAbort( e )
	if controlEnt == nil then 
		controlEnt = e 
	elseif
	   controlEnt == e and
	   abortEnabled then
	   
		if abortKeyPressed() then
			if abortPressed then 
				abortTrigger = getTime() > abortTimer
			else
				abortPressed = true
				abortTimer = getTime() + abortDelay
			end
		else
			abortPressed = false
			abortTimer   = nil
		end
	end 
	return abortTrigger
end

function CG.enableAbort()  abortEnabled = true end
function CG.disableAbort() abortEnabled = false end
	
function CG.clearAbort()
	abortTrigger = false
	controlEnt   = nil
end

return CG
