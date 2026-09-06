-----------------------------------------------------------------------------
--   cg_image_trigger.lua  Copyright C D Stapleton (AKA AmenMoses) 2022.   --
-----------------------------------------------------------------------------
-- Image trigger script, part of the Cine Guru GameGuru MAX pack.
--
-- For instructions on use see Cine Guru MAX documentation.
---------------------------------------------------------------------
local lower = string.lower

local images = {}

-- This line is to force the image to be copied over to the standalone.
LoadImage( "scriptbank\\Cine Guru MAX\\letterbox.png" )

-- DESCRIPTION: Cine Guru Image trigger. 
-- DESCRIPTION: Trigger [@ImageType=1(1=Image,2=Sequence,3=Letterbox)]
-- DESCRIPTION: Image to use [ImageFile$=""]
-- DESCRIPTION: When to display image [TriggerTime#=0] (seconds)
-- DESCRIPTION: How long to display image [ImageDuration#=0] (seconds)
-- DESCRIPTION: For sequence; time to display each frame [FrameTime=100] (milliseconds)
local imgTypes = { 'image','sequence','letterbox' }
function cg_image_trigger_properties( e, typ, name, ti, dur, spd )
	local image = images[ e ]
	if image == nil then return end
	image.typ = imgTypes[ typ ]
	if name ~= "" then image.name = name end
	image.filmtime = ti  * 1000
	image.duration = dur * 1000
	if image.typ == 'sequence' then
		if spd > 0 then image.speed = spd end
	end
end				   
-----------------------------------------------------	

local C = require "scriptbank\\Cine Guru MAX\\cg_lib"

local open  = io.open
local close = io.close
local find  = string.find
local sub   = string.sub

function cg_image_trigger_init( e )
	images[ e ] = { state = "init" }
	Hide( e )
	CollisionOff( e )
end

function CG_IsImage( e )
	return images[ e ] ~= nil
end

C.Register( 'image', CG_IsImage )

local letterboxLastFrame = false

local function showSprite( img )
	if img.typ == 'sequence' then
		local timeNow = C.getTime()
		if img.ftimer == nil then
			img.ftimer = timeNow + img.speed
		elseif
		   timeNow > img.ftimer then
			img.ftimer = timeNow + img.speed - ( timeNow - img.ftimer )
			if img.curFrame < #img.frames then 
				img.curFrame = img.curFrame + 1
			else
				img.curFrame = 1
			end
		end
		C.AddSprite( 'overlay', img.frames[ img.curFrame ] )
	else
		C.AddSprite( 'overlay', img.spr )
	end
end

function cg_image_trigger_main( e )
	if CG_GetActiveCamera == nil then return end
	
	local img = images[ e ]
	if img == nil or img.state == 'done' then return end
	
	if img.state == 'init' then
		local links = C.GetEntityLinks( e, { 'camera', 'node' } )
		-- can only be connected to one camera or 
		-- one node at present
		for _, v in pairs( links ) do
			if C.isCamera( v ) then
				img.camera = v
				img.node   = 0
				break
			elseif 
			   C.isNode( v ) then
				local node = CG_GetNode( v )
				img.camera = node.camera
				img.node   = node.node
				break
			end
		end
		-- if we are not linked to a camera then
		-- it is an error
		if img.typ ~= 'letterbox' and 
		   img.camera == nil then
			Show( e )
			img.state = 'no camera'
			return
		end
		
		if img.typ == 'sequence' then
			--local imgPath = GetEntityString( e, 1 )
			local imgPath = img.name
			local pos = find( imgPath, "1.png" ) or #imgPath
			-- first strip off the <num.png part
			if pos < #imgPath then
				imgPath = sub( imgPath, 1, pos - 1 )
			end
			-- now find the path only
			while pos > 1 do
				pos = pos - 1
				if sub( imgPath, pos, pos ) == '\\' then break end
			end
			local fileName = sub( imgPath, pos + 1, #imgPath )
			imgPath = sub( imgPath, 1, pos )
			
			img.frames = {}
			local moreFiles = true
			local num = 1
			local fname
			while moreFiles do
				fname = imgPath .. fileName .. num .. ".png"
				local file = open( fname, 'r' )
				if not file then 
					fname = imgPath .. "_e_" .. fileName .. num .. ".png"
					file = open( fname, 'r' )
				end
				if file then
					close( file )
					img.frames[ num ] = CreateSprite( LoadImage( fname ) )
					SetSpritePosition( img.frames[ num ], 200, 200 )
					SetSpriteSize(     img.frames[ num ], 100, 100 )
					SetSpriteDepth(    img.frames[ num ], 40 )
					num = num + 1
				else
					moreFiles = false
				end
			end
			if #img.frames > 0 then
				img.curFrame = 1
				img.state = 'ready'
			else
				Show( e )
				img.state = 'no file'
			end
			
		else
			local imgFile = ''
			if img.typ == 'letterbox' then
				imgFile = 'scriptbank\\Cine Guru MAX\\letterbox.png'
			else
				imgFile = img.name
			end
			if #imgFile > 0 then
				img.spr = CreateSprite( LoadImage( imgFile ) )
				SetSpriteSize( img.spr, 100, 100 )
				if img.typ == 'letterbox' then
					SetSpriteDepth( img.spr, 30 )
				else
					SetSpriteDepth( img.spr, 40 )
				end
				SetSpritePosition( img.spr, 200, 200 )
				img.state = 'ready'
			else
				Show( e )
				img.state = 'no file'
			end
		end
		
	elseif
	   img.state == 'ready' then
		local camera, cnode, ti = CG_GetActiveCamera()	

		if camera == nil then
			if letterboxLastFrame and
			   img.typ == 'letterbox' then
				C.AddSprite( 'letterbox', img.spr )
				letterboxLastFrame = false
			end

		elseif
		   img.typ == 'letterbox' then
			C.AddSprite( 'letterbox', img.spr )
			letterboxLastFrame = true

		elseif camera == img.camera then
			if ( img.node == 0 or
				 img.node == cnode ) and
			   ( ti >= img.filmtime ) then
				if img.timer == nil and
				   img.duration ~= 0 then
					img.timer = C.getTime() + img.duration
					img.state = 'triggered'
				end

				showSprite( img )
			end
		end
		
	elseif
	   img.state == 'triggered' then
		if not C.checkForAbort( e ) and
		   C.getTime() < img.timer then
		   
		    showSprite( img )
			
		else
			img.state = 'done'
			if img.typ == 'sequence' then
				for _, v in pairs( img.frames ) do 
					C.RemoveSprite( 'overlay', v )
					DeleteSprite( v )
				end
			elseif 
			   img.typ ~= 'letterbox' then
			    C.RemoveSprite( 'overlay', img.spr )
				DeleteSprite( img.spr )
			end
		end
		
	elseif
	   img.state == 'no camera' then
		PromptLocal( e, "CineGuru: Not correctly connected" )
		
	elseif
	   img.state == 'no file' then
		PromptLocal( e, "CineGuru: No Image File(s)" )
	end
end