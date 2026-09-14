"""Regression: FIRST LIGHT opening has exactly one runtime camera owner."""
import json,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD

DESIGN=ROOT/'Aegis Reach/Design/First Light'
LAYOUT=DESIGN/'layout.json'
REPORT=DESIGN/'build-report.json'
MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
SCRIPT=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_director.lua'
COORD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_cinematic.lua'
MOUNT='aegis_reach\\firstlight_camera_mount.lua'
CINE='cine guru max\\cg_cinematic_camera.lua'


def _script(e):return str(e.get('101:eleprof.aimain_s','')).replace('/','\\').lower()
def _name(e):return str(e.get('101:eleprof.name_s',''))


def main():
    assert LAYOUT.is_file() and REPORT.is_file() and MAP.is_file(),'rebuild FIRST LIGHT first'
    layout=json.loads(LAYOUT.read_text());report=json.loads(REPORT.read_text())
    director=[p for p in layout if p.get('name')=='FIRST LIGHT // OPENING DIRECTOR']
    assert len(director)==1,len(director)
    meta=report.get('opening_director',{})
    assert meta.get('cut_count')==17,meta
    assert meta.get('opening_ms')==50800,meta
    assert meta.get('camera_owner')=='deterministic-director',meta
    assert meta.get('inert_opening_mounts')==17,meta
    source=SCRIPT.read_text()
    for token in ('SetCameraOverride(3)','SetCameraPosition(0,x,y,z)','SetCameraAngle(0,rx,ry,rz)',"aegis.cinematic_request='OPENING_DIRECTOR_LOCK'",'g_KeyPressSPACE==1'):
        assert token in source,token
    assert source.count("name='FL CG ARRIVAL ")>=17
    assert 'stop=50800' in source
    coord=COORD.read_text()
    assert 'if not aegis.insertion_complete and not cine.seen.ARRIVAL_PERIM' in coord
    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD);_,entities=read_ele(archive.read('map.ele'))
    opening=[e for e in entities if _name(e).startswith('FL CG ARRIVAL ')]
    assert len(opening)==17,len(opening)
    assert all(_script(e)==MOUNT for e in opening),[( _name(e),_script(e)) for e in opening if _script(e)!=MOUNT]
    assert not any(_script(e)==CINE for e in opening),'CineGuru still owns an opening camera entity'
    later=[e for e in entities if _name(e) in ('FL CG MIRA SIGNAL','FL CG AEGIS REVEAL','FL CG EXTRACTION')]
    assert len(later)==3 and all(_script(e)==CINE for e in later),'later story cameras must retain CineGuru'
    print('FIRST LIGHT // SINGLE CAMERA OWNER PASS')
    print('17 opening mounts are inert; deterministic director alone writes camera 0. CineGuru remains only on later story beats.')

if __name__=='__main__':main()
