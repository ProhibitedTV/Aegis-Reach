$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$aegisSpeech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$aegisSpeech.Rate = 0
$aegisSpeech.Volume = 90
$aegisAudio = Join-Path $PSScriptRoot '..\Aegis Reach\Files\audiobank\aegis_reach'
$aegisSpeech.SetOutputToWaveFile((Join-Path $aegisAudio 'briefing.wav'))
$aegisSpeech.Speak('Vanguard Seven, this is Kestrel. The Iron Wardens have seized our orbital defense network. Restore Northstar, then Lantern, then override the Aegis core. You have one chance to cancel the strike. Stay in cover and let your shield recharge. We will bring you home.')
$aegisSpeech.SetOutputToNull()
$aegisSpeech.Dispose()
Get-Item -LiteralPath (Join-Path $aegisAudio 'briefing.wav') | Select-Object Name,Length
