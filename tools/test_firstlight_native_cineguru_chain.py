"""Regression: FIRST LIGHT opener is a native CineGuru relationship graph in map.ele."""
from pathlib import Path
import zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD
from firstlight_cineguru_native_chain import OPENING_CAMERA_NAMES

MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'
CHAIN_CONTROLLER='FIRST LIGHT // CINEGURU NATIVE CHAIN'
CHAIN_SCRIPT=r'aegis_reach\firstlight_cineguru_chain.lua'


def suffix(entity,name,default=0):
    for key,value in entity.items():
        if key.split(':',1)[-1]==name:return value
    return default


def main():
    assert MAP.is_file(),MAP
    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD)
        _,entities=read_ele(archive.read('map.ele'))
    by_name={str(suffix(e,'eleprof.name_s','')):e for e in entities}
    cams=[by_name[name] for name in OPENING_CAMERA_NAMES]
    link_ids=[int(suffix(e,'eleprof.iObjectLinkID',0) or 0) for e in cams]
    assert len(set(link_ids))==len(cams) and min(link_ids)>0,'opening cameras need unique native object-link IDs'
    for i,e in enumerate(cams):
        actual={int(suffix(e,f'eleprof.iObjectRelationships[{slot}]',0) or 0) for slot in range(10)}-{0}
        expected=set()
        if i>0:expected.add(link_ids[i-1])
        if i+1<len(cams):expected.add(link_ids[i+1])
        assert actual==expected,(OPENING_CAMERA_NAMES[i],actual,expected)
    controller=by_name.get(CHAIN_CONTROLLER);assert controller is not None,'native CineGuru chain controller missing'
    script=str(suffix(controller,'eleprof.aimain_s','')).replace('/','\\').lower()
    assert script==CHAIN_SCRIPT.lower(),script
    print('FIRST LIGHT // NATIVE CINEGURU OPENING CHAIN PASS')
    print(len(cams),'camera entities are physically linked PERIM -> ... -> DEPART in encrypted map.ele.')

if __name__=='__main__':main()
