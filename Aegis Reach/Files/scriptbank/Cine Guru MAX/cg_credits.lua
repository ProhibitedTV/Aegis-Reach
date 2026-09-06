---------------------------------------------------------------------
--   cg_credits.lua  Copyright C D Stapleton (AKA AmenMoses) 2020.   --
---------------------------------------------------------------------
-- Scrolling credits script, part of the Cine Guru pack.
--
-- For instructions on use see Cine Guru documentation.
---------------------------------------------------------------------
local lower = string.lower

local credits = {}

-- *** GG MAX part, does nothing in GG classic *** --
-- DESCRIPTION: Cine Guru Credits script. 
-- DESCRIPTION: Credits text file name [TextFile$=""]
-- DESCRIPTION: Width  [W=100]
-- DESCRIPTION: Height [H=70]
-- DESCRIPTION: Size   [SZ=4]
-- DESCRIPTION: Speed  [SPD=1]
function cg_credits_properties( e, crfile, w, h, sz, spd )
	local cr = credits[ e ]
	if cr == nil then return end
	if crfile ~= "" then cr.file = crfile end
	if w ~= 100 then cr.width  = w   end
	if h ~=  70 then cr.height = h   end
	if sz ~=  4 then cr.size   = sz  end
	
	if spd ~= 1 then cr.speed  = spd / 100 end
end				   
-----------------------------------------------------	

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local sub   = string.sub

local debugOn = false

local backSpr = CreateSprite( LoadImage("scriptbank\\Cine Guru MAX\\black.png") )

SetSpritePosition( backSpr, 200, 200 )
SetSpriteDepth   ( backSpr, 50 )

g_timeDiff = g_timeDiff or 1

function CG_IsCredits( e )
	return credits[ e ] ~= nil
end

C.Register( 'credits', CG_IsCredits )

function CG_RollCredits( e )
	local this = credits[ e ]
	if this.state == 'ready' then
		this.state = 'roll'
		C.clearAbort()
		return true
	end
end

function cg_credits_init( e )	
	credits[ e ] = { state  = 'init', 
					 width  = 100,
					 height =  70,
					 size   =   4,
					 speed  =   0.01
				   }
	Hide( e )
	CollisionOff( e )
end

local function readCredits( cred )
	cred.textStrings = {}
	for line in io.lines( cred.file ) do
		cred.textStrings[ #cred.textStrings + 1 ] = line
    end
	cred.currLine = 1
	cred.numLines = #cred.textStrings
end

function cg_credits_main( e )

	if C.checkForAbort( e ) then
		for k, v in pairs( credits ) do
			if v.state == 'roll'  then
				v.state = 'abort'
			end
		end
	end
	
	local cred = credits[ e ]
	if cred == nil then return end
		
	if cred.state == 'init' then
		SetSpriteSize( backSpr, cred.width, cred.height )
		SetSpriteOffset( backSpr, cred.width / 2, cred.height / 2 )
		readCredits( cred )
		
		if cred.numLines > 0 then
			cred.state = 'ready'
		else
			Show( e )
			PromptLocal( e, "CineGuru: No credits in file: " .. 
			                 cred.file )
		end
		
	elseif
	   cred.state == 'roll' then
		
		PasteSpritePosition( backSpr, 50, 50 )
		
		if cred.Ypos == nil then
			cred.Ypos  = 50 + cred.height / 2
			cred.Yend  = cred.Ypos - cred.size
			cred.Ybeg  = 50 - cred.height / 2
			cred.Ylast = cred.Ypos
			cred.Yspc  = cred.size
		else
			if cred.Ylast > cred.Ybeg then
				cred.Ypos = cred.Ypos - cred.speed * g_timeDiff
			else
				cred.state = 'abort'
			end
		end
		
		local Y = cred.Ypos
		for _, v in ipairs( cred.textStrings ) do
		
			if Y > cred.Ybeg and
			   Y < cred.Yend then
				TextCenterOnXColor( 50, Y,                 -- position
									cred.size,             -- size
									v,                     -- text 
									255, 255, 255 )        -- colour
			end					 
			if Y < cred.Yend then 
				cred.Ylast = Y
				Y = Y + cred.Yspc
			else
				break
			end
		end
		
	elseif 
	   cred.state == 'abort' then
	    SetSpritePosition( backSpr, 200, 200 )
		credits[ e ] = nil
	end

end
 

	
	


