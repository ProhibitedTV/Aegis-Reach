"""Regression: FIRST LIGHT opening is owned by the deterministic 17-cut director."""
import json
from native_format import ROOT

DESIGN=ROOT/'Aegis Reach/Design/First Light'
LAYOUT=DESIGN/'layout.json'
REPORT=DESIGN/'build-report.json'
SCRIPT=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_opening_director.lua'
COORD=ROOT/'Aegis Reach/Files/scriptbank/aegis_reach/firstlight_cinematic.lua'


def main():
    assert LAYOUT.is_file() and REPORT.is_file(),'rebuild FIRST LIGHT first'
    layout=json.loads(LAYOUT.read_text());report=json.loads(REPORT.read_text())
    director=[p for p in layout if p.get('name')=='FIRST LIGHT // OPENING DIRECTOR']
    assert len(director)==1,len(director)
    meta=report.get('opening_director',{})
    assert meta.get('cut_count')==17,meta
    assert meta.get('opening_ms')==50800,meta
    assert meta.get('camera_owner')=='deterministic-director',meta
    source=SCRIPT.read_text()
    for token in ('SetCameraOverride(3)','SetCameraPosition(0,x,y,z)','SetCameraAngle(0,rx,ry,rz)',"aegis.cinematic_request='OPENING_DIRECTOR_LOCK'",'g_KeyPressSPACE==1'):
        assert token in source,token
    assert source.count("name='FL CG ARRIVAL ")>=17
    assert 'stop=50800' in source
    coord=COORD.read_text()
    assert 'if not aegis.insertion_complete and not cine.seen.ARRIVAL_PERIM' in coord
    print('FIRST LIGHT // DETERMINISTIC OPENING DIRECTOR PASS')
    print('17 authored camera mounts are hard-cut by one 50.8s game-camera timeline; legacy opener is gated after handoff.')

if __name__=='__main__':main()
