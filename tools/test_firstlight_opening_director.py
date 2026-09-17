"""Regression: FIRST LIGHT insertion is a hard native replacement, not layered CineGuru."""
import json,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD

DESIGN=ROOT/'Aegis Reach/Design/First Light'
LAYOUT=DESIGN/'layout.json'
REPORT=DESIGN/'build-report.json'
MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
NATIVE=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_native.lua'
HUD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_hud.lua'
COORD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_cinematic.lua'
CINE='cine guru max\\cg_cinematic_camera.lua'


def _script(e):return str(e.get('101:eleprof.aimain_s','')).replace('/','\\').lower()
def _name(e):return str(e.get('101:eleprof.name_s',''))


def main():
    assert LAYOUT.is_file() and REPORT.is_file() and MAP.is_file(),'rebuild FIRST LIGHT first'
    layout=json.loads(LAYOUT.read_text());report=json.loads(REPORT.read_text())
    assert not [p for p in layout if str(p.get('name','')).startswith('FL CG ARRIVAL ')],'legacy opening camera placement survived'
    assert len([p for p in layout if p.get('name')=='FIRST LIGHT // CAMERA RIG'])==1
    assert len([p for p in layout if p.get('name')=='FIRST LIGHT // OPENING DIRECTOR'])==1
    meta=report.get('opening_director',{})
    assert meta.get('cut_count')==17,meta
    assert meta.get('opening_ms')==50800,meta
    assert meta.get('camera_owner')=='mission-hud-native-hard-replacement',meta
    assert meta.get('removed_opening_cameras')==17,meta
    assert meta.get('runtime_entry')=='firstlight_hud.lua -> fl_opening_native_tick()',meta

    native=NATIVE.read_text();hud=HUD.read_text();coord=COORD.read_text()
    for token in (
        'FreezePlayer()','UnFreezePlayer()','SetCameraOverride(3)',
        'SetCameraPosition(0,x,y,z)','SetCameraAngle(0,rx,ry,rz)',
        "aegis.cinematic_request='OPENING_NATIVE_LOCK'",'g_KeyPressSPACE==1',
        "FL KESTREL INSERTION FLIGHT","KSTL-01 FORWARD CHASE // LIVE",
        "KSTL-08 GEAR CLOSE // LIVE","KSTL-10 PORT REAR OBS // DEPLOY",
        'for id=1,4096 do','trackship=true','local floor=ground(cx,cz)+(s.clear or 60)',
        'off2=','opening_shot_progress','SetCameraPanelFOV(focal)',
    ):
        assert token in native,token
    assert 'SetCameraPanelFOV(focal/2)' not in native,'authored FOV degrees are being halved again'
    assert native.count("beat='ARRIVAL_")>=17
    assert "stop=50800" in native
    first_shot=native.index("beat='ARRIVAL_NOSE'")
    assert first_shot<native.index("beat='ARRIVAL_GATE'"),'opening no longer begins with the Kestrel as subject'
    assert "require 'scriptbank\\\\aegis_reach\\\\firstlight_opening_native'" in hud
    assert 'if fl_opening_native_tick then fl_opening_native_tick() end' in hud
    assert 'if false and not cine.seen.ARRIVAL_PERIM' in coord,'legacy coordinator opener still enabled'

    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD);_,entities=read_ele(archive.read('map.ele'))
    opening=[e for e in entities if _name(e).startswith('FL CG ARRIVAL ')]
    assert not opening,[(_name(e),_script(e)) for e in opening]
    later=[e for e in entities if _name(e) in ('FL CG MIRA SIGNAL','FL CG AEGIS REVEAL','FL CG EXTRACTION')]
    assert len(later)==3 and all(_script(e)==CINE for e in later),'later story cameras must retain CineGuru'
    print('FIRST LIGHT // HARD-REPLACEMENT OPENING PASS')
    print('0 insertion CineGuru cameras in map.ele; 17 native Kestrel-subject cuts use smooth moving-camera language and real FOV degrees; CineGuru remains for later story beats.')

if __name__=='__main__':main()
