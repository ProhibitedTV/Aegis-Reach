-- LUA Script - precede every function and global member with lowercase name of script + '_main'
-- Weather Event v7 by Necrym59 with special thanks to Bolt Action Gaming
-- DESCRIPTION: Apply to an object and can be activated by switch or zone.
-- DESCRIPTION: [#EVENT_PACE=0.01(0.01,60.0)] Higher = Slower
-- DESCRIPTION: [CLOUD_DENSITY=1(1,400)]
-- DESCRIPTION: [CLOUD_COVERAGE=1(1,200)]
-- DESCRIPTION: [CLOUD_HEIGHT=1(-100,3500)] Meters
-- DESCRIPTION: [CLOUD_THICKNESS=1(1,400)] Meters
-- DESCRIPTION: [CLOUD_SPEED=1(1,50)]
-- DESCRIPTION: [#WIND_SPEED=0.1(0.0,0.3)]
-- DESCRIPTION: [SUN_EXPOSURE=0(0,400)] 0=Not used
-- DESCRIPTION: [TRIGGER_STAGE=2(1,7)] Will activate an external entity at this event stage
-- DESCRIPTION: [WEATHER_WARNING$=""] Weather warning text sent to a User Global at stage before trigger stage
-- DESCRIPTION: [@@WARNING_USER_GLOBAL$=""(0=globallist)] eg: MyWeatherWarning
-- DESCRIPTION: [REPEATDELAY=60(1,300)] Seconds
-- DESCRIPTION: [DIAGNOSTIC!=0]

local weather_event			= {}
local event_pace 			= {}
local cloud_density 		= {}
local cloud_coverage 		= {}
local cloud_height 			= {}
local cloud_thickness 		= {}
local cloud_speed 			= {}
local wind_speed			= {}
local sun_exposure 			= {}
local trigger_stage			= {}
local weather_warning		= {}
local warning_user_global	= {}
local repeatdelay			= {}
local diagnostic			= {}

local current_value	= {}
local doonce		= {}
local endval1 		= {}
local endval2 		= {}
local endval3 		= {}
local endval4 		= {}
local endval5 		= {}
local endval6		= {}
local endval7		= {}
local endvalue 		= {}
local endevent		= {}
local pace			= {}
local status		= {}
local trigonce		= {}
local warnonce		= {}
local timedelay		= 0 
local original_density	= {}
local original_coverage	= {}
local original_height 	= {}
local original_thickness= {}
local original_speed 	= {}
local original_wind 	= {}

function weather_event_properties(e, event_pace, cloud_density, cloud_coverage, cloud_height, cloud_thickness, cloud_speed, wind_speed, sun_exposure, trigger_stage, weather_warning, warning_user_global, repeatdelay, diagnostic)
	weather_event[e].event_pace = event_pace
	weather_event[e].cloud_density = cloud_density
	weather_event[e].cloud_coverage = cloud_coverage
	weather_event[e].cloud_height = cloud_height
	weather_event[e].cloud_thickness = cloud_thickness
	weather_event[e].cloud_speed = cloud_speed
	weather_event[e].wind_speed = wind_speed	
	weather_event[e].sun_exposure = sun_exposure
	weather_event[e].trigger_stage = trigger_stage
	weather_event[e].weather_warning = weather_warning
	weather_event[e].warning_user_global = warning_user_global	
	weather_event[e].repeatdelay = (repeatdelay * 1000)
	weather_event[e].diagnostic	= diagnostic or 0	
end

function weather_event_init(e)
	weather_event[e] = {}
	weather_event[e].event_pace = 1	
	weather_event[e].cloud_density = 0
	weather_event[e].cloud_coverage = 0
	weather_event[e].cloud_height = 0
	weather_event[e].cloud_thickness = 0
	weather_event[e].cloud_speed = 0
	weather_event[e].wind_speed = 0	
	weather_event[e].sun_exposure = 0
	weather_event[e].trigger_stage = 0
	weather_event[e].weather_warning = ""
	weather_event[e].warning_user_global = ""
	weather_event[e].repeatdelay = 60
	weather_event[e].diagnostic	= 0		
	
	original_density[e] = 0
	original_coverage[e] = 0
	original_height[e] = 0
	original_thickness[e] = 0
	original_speed[e] = 0
	original_wind[e] = 0
	
	current_value[e] = 0
	doonce[e] = 0
	endval1[e] = 0
	endval2[e] = 0
	endval3[e] = 0
	endval4[e] = 0
	endval5[e] = 0
	endval6[e] = 0
	endval7[e] = 0		
	endvalue[e] = 0	
	endevent[e] = 0
	pace[e] = 0
	trigonce[e] = 0
	warnonce[e] = 0	
	status[e] = "init"
end

function weather_event_main(e)

	if status[e] == "init" then		
		SetActivated(e,0)
		status[e] = "do_event"
		timedelay = 0 
	end
	
	if g_Entity[e]['activated'] == 1 then
		if doonce[e] == 0 then
			-- Capture original values
			original_density[e] = GetCloudDensity()
			original_coverage[e] = GetCloudCoverage()
			original_height[e] = GetCloudHeight()
			original_thickness[e] = GetCloudThickness()
			original_speed[e] = GetCloudSpeed()
			original_wind[e] = GetTreeWind()
			
			_G["g_UserGlobal['"..weather_event[e].warning_user_global.."']"] = ""
			pace[e] = g_Time + (weather_event[e].event_pace * 1000)
			doonce[e] = 1		
		end	

		if status[e] == "do_event" and g_Time > pace[e] then
			--CloudDensity--
			if GetCloudDensity()*100 < weather_event[e].cloud_density and endval1[e] == 0 then
				SetCloudDensity(GetCloudDensity()+current_value[e])
				if GetCloudDensity()*100 >= weather_event[e].cloud_density then	endval1[e] = 1 end
			end
			if GetCloudDensity()*100 > weather_event[e].cloud_density and endval1[e] == 0 then
				SetCloudDensity(GetCloudDensity()-current_value[e])
				if GetCloudDensity()*100 <= weather_event[e].cloud_density then	endval1[e] = 1 end
			end
			--CloudCoverage--
			if GetCloudCoverage()*100 < weather_event[e].cloud_coverage and endval2[e] == 0 then
				SetCloudCoverage(GetCloudCoverage()+current_value[e])
				if GetCloudCoverage()*100 >= weather_event[e].cloud_coverage then endval2[e] = 1 end
			end
			if GetCloudCoverage()*100 > weather_event[e].cloud_coverage and endval2[e] == 0 then
				SetCloudCoverage(GetCloudCoverage()-current_value[e])
				if GetCloudCoverage()*100 <= weather_event[e].cloud_coverage then endval2[e] = 1 end
			end
			--CloudHeight--
			if GetCloudHeight()/39.36 < weather_event[e].cloud_height and endval3[e] == 0 then
				SetCloudHeight(GetCloudHeight()+current_value[e]*393.6)
				if GetCloudHeight()/39.36 >= weather_event[e].cloud_height then endval3[e] = 1 end
			end
			if GetCloudHeight()/39.36 > weather_event[e].cloud_height and endval3[e] == 0 then
				SetCloudHeight(GetCloudHeight()-current_value[e]*393.6)
				if GetCloudHeight()/39.36 <= weather_event[e].cloud_height then endval3[e] = 1 end
			end
			--CloudThickness--			
			if GetCloudThickness()/393.6 < weather_event[e].cloud_thickness and endval4[e] == 0 then
				SetCloudThickness(GetCloudThickness()+current_value[e]*393.6)
				if GetCloudThickness()/393.6 >= weather_event[e].cloud_thickness then endval4[e] = 1 end
			end
			if GetCloudThickness()/393.6 > weather_event[e].cloud_thickness and endval4[e] == 0 then
				SetCloudThickness(GetCloudThickness()-current_value[e]*393.6)
				if GetCloudThickness()/393.6 <= weather_event[e].cloud_thickness then endval4[e] = 1 end
			end			
			--CloudSpeed--			
			if GetCloudSpeed() < weather_event[e].cloud_speed and endval5[e] == 0 then
				SetCloudSpeed(GetCloudSpeed()+current_value[e])
				if GetCloudSpeed() >= weather_event[e].cloud_speed then endval5[e] = 1 end
			end
			if GetCloudSpeed() > weather_event[e].cloud_speed and endval5[e] == 0 then
				SetCloudSpeed(GetCloudSpeed()-current_value[e])
				if GetCloudSpeed() <= weather_event[e].cloud_speed then endval5[e] = 1 end
			end			
			--SunExposure--	
			if weather_event[e].sun_exposure ~= 0 then
				if GetExposure()*100 < weather_event[e].sun_exposure and endval6[e] == 0 then
					SetExposure(GetExposure()+current_value[e]/10)
					if GetExposure()*100 >= weather_event[e].sun_exposure then endval6[e] = 1 end
				end	
				if GetExposure()*100 > weather_event[e].sun_exposure and endval6[e] == 0 then
					SetExposure(GetExposure()-current_value[e]/10)
					if GetExposure()*100 <= weather_event[e].sun_exposure then endval6[e] = 1 end
				end
			else 
				endval6[e] = 1
			end
			--TreeWind--
			if GetTreeWind() < weather_event[e].wind_speed and endval7[e] == 0 then
				SetTreeWind(GetTreeWind()+current_value[e])
				if GetTreeWind() >= weather_event[e].wind_speed then endval7[e] = 1 end
			end
			if GetTreeWind() > weather_event[e].wind_speed and endval7[e] == 0 then
				SetTreeWind(GetTreeWind()-current_value[e])
				if GetTreeWind() <= weather_event[e].wind_speed then endval7[e] = 1 end
			end	
			
			-- Completion value
			endvalue[e] = endval1[e]+endval2[e]+endval3[e]+endval4[e]+endval5[e]+endval6[e]+endval7[e]
			
			-- Pacing updating
			if endvalue[e] < 6 then
				-- Pace of change for the next step
				current_value[e] = round_up_5dp(current_value[e] + 0.00001)
				-- Pace for the next loop
				pace[e] = g_Time + (weather_event[e].event_pace * 1000)
			end
			
			-- Trigger logic
			if endvalue[e] == (weather_event[e].trigger_stage - 1) and warnonce[e] == 0 then
				if weather_event[e].warning_user_global ~= "" then				
					_G["g_UserGlobal['"..weather_event[e].warning_user_global.."']"] = weather_event[e].weather_warning
					warnonce[e] = 1
				end
			end			
			if endvalue[e] == weather_event[e].trigger_stage and trigonce[e] == 0 then
				ActivateIfUsed(e)
				PerformLogicConnections(e)
				trigonce[e] = 1
			end			
			
			if endvalue[e] == 6 then 
				status[e] = "start_fade"
				PerformLogicConnections(e)
			end
		end
		if status[e] == "start_fade" then
			current_value[e] = 0.00001 -- Base speed for the fade
			status[e] = "fade_back"
			pace[e] = g_Time + (weather_event[e].event_pace * 1000)
		end
		if status[e] == "fade_back" and g_Time > pace[e] then
			--CloudDensity--
			if GetCloudDensity() < original_density[e] and endval1[e] == 1 then
				SetCloudDensity(GetCloudDensity()+current_value[e])
				if GetCloudDensity() >= original_density[e] then 
					SetCloudDensity(original_density[e])
					endval1[e] = 2 
				end
			end
			if GetCloudDensity() > original_density[e] and endval1[e] == 1 then
				SetCloudDensity(GetCloudDensity()-current_value[e])
				if GetCloudDensity() <= original_density[e] then 
					SetCloudDensity(original_density[e])
					endval1[e] = 2 
				end
			end
			--CloudCoverage--
			if GetCloudCoverage() < original_coverage[e] and endval2[e] == 1 then
				SetCloudCoverage(GetCloudCoverage()+current_value[e])
				if GetCloudCoverage() >= original_coverage[e] then 
					SetCloudCoverage(original_coverage[e])
					endval2[e] = 2 
				end
			end
			if GetCloudCoverage() > original_coverage[e] and endval2[e] == 1 then
				SetCloudCoverage(GetCloudCoverage()-current_value[e])
				if GetCloudCoverage() <= original_coverage[e] then 
					SetCloudCoverage(original_coverage[e])
					endval2[e] = 2 
				end
			end
			--CloudHeight-- (Note: Using *39.36 to convert original meter-based value to engine units)
			if GetCloudHeight()/39.36 < original_height[e]/39.36 and endval3[e] == 1 then
				SetCloudHeight(GetCloudHeight()+current_value[e]*393.6)
				if GetCloudHeight()/39.36 >= original_height[e] then 
					SetCloudHeight(original_height[e])
					endval3[e] = 2 
				end
			end
			if GetCloudHeight()/39.36 > original_height[e]/39.36 and endval3[e] == 1 then
				SetCloudHeight(GetCloudHeight()-current_value[e]*393.6)
				if GetCloudHeight()/39.36 <= original_height[e] then 
					endval3[e] = 2 
					SetCloudHeight(original_height[e])
				end
			end
			--CloudThickness--
			if GetCloudThickness()/393.6 < original_thickness[e]/393.6 and endval4[e] == 1 then
				SetCloudThickness(GetCloudThickness()+current_value[e]*393.6)
				if GetCloudThickness()/393.6 >= original_thickness[e] then 
					SetCloudThickness(original_thickness[e])
					endval4[e] = 2 
				end
			end
			if GetCloudThickness()/393.6 > original_thickness[e]/393.6 and endval4[e] == 1 then
				SetCloudThickness(GetCloudThickness()-current_value[e]*393.6)
				if GetCloudThickness()/393.6 <= original_thickness[e] then 
					SetCloudThickness(original_thickness[e])
					endval4[e] = 2 
				end
			end
			--CloudSpeed--
			if GetCloudSpeed() < original_speed[e] and endval5[e] == 1 then
				SetCloudSpeed(GetCloudSpeed()+current_value[e])
				if GetCloudSpeed() >= original_speed[e] then 
					SetCloudSpeed(original_speed[e])
					endval5[e] = 2 
				end
			end
			if GetCloudSpeed() > original_speed[e] and endval5[e] == 1 then
				SetCloudSpeed(GetCloudSpeed()-current_value[e])
				if GetCloudSpeed() <= original_speed[e] then 
					SetCloudSpeed(original_speed[e])
					endval5[e] = 2 
				end
			end
			--SunExposure--	
			if weather_event[e].sun_exposure ~= 0 then
				if GetExposure()*100 < weather_event[e].sun_exposure and endval6[e] == 1 then
					SetExposure(GetExposure()+current_value[e]/10)
					if GetExposure()*100 >= weather_event[e].sun_exposure then endval6[e] = 2 end
				end	
				if GetExposure()*100 > weather_event[e].sun_exposure and endval6[e] == 1 then
					SetExposure(GetExposure()-current_value[e]/10)
					if GetExposure()*100 <= weather_event[e].sun_exposure then endval6[e] = 2 end
				end
			else 
				endval6[e] = 2
			end			
			--TreeWind--
			if GetTreeWind() < original_wind[e] and endval7[e] == 1 then -- TreeWind used endval7 in your code
				SetTreeWind(GetTreeWind()+current_value[e])
				if GetTreeWind() >= original_wind[e] then 
					SetTreeWind(original_wind[e])
					endval7[e] = 2 
				end
			end
			if GetTreeWind() > original_wind[e] and endval7[e] == 1 then
				SetTreeWind(GetTreeWind()-current_value[e])
				if GetTreeWind() <= original_wind[e] then 
					SetTreeWind(original_wind[e])
					endval7[e] = 2 
				end
			end	

			-- Calculate how many properties have completed the reverse fade (stage 2)
			local fade_complete = 0
			if endval1[e] == 2 then fade_complete = fade_complete + 1 end
			if endval2[e] == 2 then fade_complete = fade_complete + 1 end
			if endval3[e] == 2 then fade_complete = fade_complete + 1 end
			if endval4[e] == 2 then fade_complete = fade_complete + 1 end
			if endval5[e] == 2 then fade_complete = fade_complete + 1 end
			if endval6[e] == 2 then fade_complete = fade_complete + 1 end			
			if endval7[e] == 2 then fade_complete = fade_complete + 1 end -- endval7 used for TreeWind

			if fade_complete < 6 then
				-- Keep speeding up the fade and resetting the pace
				current_value[e] = round_up_5dp(current_value[e] + 0.00001)
				pace[e] = g_Time + (weather_event[e].event_pace * 1000)
			else
				-- Fade is complete, now start the delay
				status[e] = "end_delay"
				StartTimer(e)
			end
		end
	end
	timedelay = GetTimer(e)
	if status[e] == "end_delay" and timedelay > weather_event[e].repeatdelay then
		-- Event State Resets --
		current_value[e] = 0
		endvalue[e] = 0
		trigonce[e] = 0
		warnonce[e] = 0		
		-- Individual Property Completion Resets (CRITICAL for re-run) --
		endval1[e] = 0  -- CloudDensity
		endval2[e] = 0  -- CloudCoverage
		endval3[e] = 0  -- CloudHeight
		endval4[e] = 0  -- CloudThickness
		endval5[e] = 0  -- CloudSpeed
		endval6[e] = 0  -- Sun Exposure (if Used)
		endval7[e] = 0  -- TreeWind
		
		-- Pacing Reset --
		pace[e] = 0
		
		-- Global Variable Cleanup --
		if weather_event[e].warning_user_global ~= "" then	
			_G["g_UserGlobal['"..weather_event[e].warning_user_global.."']"] = ""
		end	
		
		-- Reset Object Activation Status --
		SetActivated(e,0)
		status[e]="init"		
	end
	
	if weather_event[e].diagnostic == 1 then
		Text(5,44,3,"Status: " ..status[e])
		Text(5,46,3,"Time: " ..g_Time)
		Text(5,48,3,"Event Pace: " ..pace[e])
		Text(5,50,3,"Cloud Density: " .. GetCloudDensity()*100 .. " Original : " .. original_density[e])
		Text(5,52,3,"Cloud Cover: " ..GetCloudCoverage()*100 .. " Original : " .. original_coverage[e])
		Text(5,54,3,"Cloud Height: " ..GetCloudHeight()/39.36 .. " Original : " .. original_height[e]/39.36)
		Text(5,56,3,"Cloud Thickness: " ..GetCloudThickness()/393.6 .. " Original : " .. original_thickness[e]/393.6)
		Text(5,58,3,"Cloud Speed: " ..GetCloudSpeed() .. " Original : " .. original_speed[e])
		Text(5,60,3,"Sun Exposure: " ..GetExposure()*100)
		Text(5,62,3,"Wind Speed: " ..GetTreeWind() .. " Original : " .. original_wind[e])
		Text(5,64,3,"Current Stage: " ..endvalue[e].. " of 7")
		Text(5,66,3,"Trigger Stage: " ..weather_event[e].trigger_stage)
		Text(5,68,3,"Time Delay: " ..timedelay)
	end	
end

function round_up_5dp(num)
  local mult = 10^5
  return math.ceil(num * mult) / mult
end

function weather_event_exit(e)
end