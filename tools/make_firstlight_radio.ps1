Add-Type -AssemblyName System.Speech
$destination=Join-Path $PSScriptRoot '..\Aegis Reach\Files\audiobank\aegis_reach\firstlight'
New-Item -ItemType Directory -Path $destination -Force | Out-Null
$voice=New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
$voice.Rate=-1
$lines=@{
 intro='Seven. The colony has gone silent. Northstar can tell us why. Follow the old survey road. I will keep a channel open.'
 power='Northstar is online. That distress call is coming from Operations. Go east. We need the evacuation manifest.'
 records='Mira is still alive. Her team is under Shelter twelve. Aegis is aimed at the shelter. Get to the core. Now.'
 core='Firing order cancelled. Shelter twelve is clear. Take the west service yard back to Gate seven. I am coming in.'
}
foreach($name in $lines.Keys){
 $voice.SetOutputToWaveFile((Join-Path $destination ($name+'.wav')))
 $voice.Speak($lines[$name])
 $voice.SetOutputToNull()
}
$voice.Dispose()
Write-Output 'Four temporary radio performance clips generated.'
