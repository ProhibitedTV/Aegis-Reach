"""Regression: FIRST LIGHT opening has one known-running native camera owner."""
import json,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD

DESIGN=ROOT/'Aegis Reach/Design/First Light'
LAYOUT=DESIGN/'layout.json'
REPORT=DESIGN/'build-report.json'
MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
STUB=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_director.lua'
NATIVE=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_native.lua'
HUD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_hud.lua'
COORD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_cinematic.lua'
MOUNT='aegis_reach\\firstlight_camera_mount.lua'
CINE='cine guru max\\cg_cinematic_camera.lua'


def _script(e):return str(e.get('101:eleprof.aimain_s','')).replace('/','\\').lower()
def _name(e):return str(e.get('101:eleprof.name_s',''))


def main():
    assert LAYOUT.is_file() and REPORT.is_file() and MAP.is_file(),'rebuild FIRST LIGHT first'
    layout=json.loads(LAYOUT.read_text());report=json.loads(REPORT.read_text())
    compat=[p for p in layout if p.get('name')=='FIRST LIGHT // OPENING DIRECTOR']
    assert len(compat)==1,len(compat)
    meta=report.get('opening_director',{})
    assert meta.get('cut_count')==17,meta
    assert meta.get('opening_ms')==50800,meta
    assert meta.get('camera_owner')=='mission-hud-native',meta
    assert meta.get('inert_opening_mounts')==17,meta
    assert meta.get('runtime_entry')=='firstlight_hud.lua -> fl_opening_native_tick()',meta

    native=NATIVE.read_text();hud=HUD.read_text();stub=STUB.read_text();coord=COORD.read_text()
    for token in (
        'FreezePlayer()','UnFreezePlayer()','SetCameraOverride(3)',
        'SetCameraPosition(0,x,y,z)','SetCameraAngle(0,rx,ry,rz)',
        "aegis.cinematic_request='OPENING_NATIVE_LOCK'",'g_KeyPressSPACE==1',
        "FL KESTREL INSERTION FLIGHT","KSTL-01 NOSE EO // LIVE","KSTL-02 STBD SHOULDER // LIVE",
    ):
        assert token in native,token
    assert native.count("beat='ARRIVAL_")>=17
    assert "stop=50800" in native
    assert "require 'scriptbank\\\\aegis_reach\\\\firstlight_opening_native'" in hud
    assert 'if fl_opening_native_tick then fl_opening_native_tick() end' in hud
    assert 'fl_opening_native_reset' in hud
    # The old map entity is a compatibility marker only: it must not be able to
    # override, position, or rotate the game camera anymore.
    for forbidden in ('SetCameraOverride','SetCameraPosition','SetCameraAngle','fl_dialogue('):
        assert forbidden not in stub,forbidden
    assert 'if not aegis.insertion_complete and not cine.seen.ARRIVAL_PERIM' in coord

    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD);_,entities=read_ele(archive.read('map.ele'))
    opening=[e for e in entities if _name(e).startswith('FL CG ARRIVAL ')]
    assert len(opening)==17,len(opening)
    assert all(_script(e)==MOUNT for e in opening),[(_name(e),_script(e)) for e in opening if _script(e)!=MOUNT]
    assert not any(_script(e)==CINE for e in opening),'CineGuru still owns an opening camera entity'
    later=[e for e in entities if _name(e) in ('FL CG MIRA SIGNAL','FL CG AEGIS REVEAL','FL CG EXTRACTION')]
    assert len(later)==3 and all(_script(e)==CINE for e in later),'later story cameras must retain CineGuru'
    print('FIRST LIGHT // HUD-NATIVE CAMERA OWNER PASS')
    print('Mission HUD ticks one 50.8s direct camera timeline; 17 opening entities are inert; CineGuru remains only on later story beats.')

if __name__=='__main__':main()
