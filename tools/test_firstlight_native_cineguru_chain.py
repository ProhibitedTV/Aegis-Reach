"""Regression: FIRST LIGHT has no native CineGuru insertion graph anymore."""
import zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD

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
        archive.setpassword(PASSWORD);_,entities=read_ele(archive.read('map.ele'))
    opening=[e for e in entities if str(suffix(e,'eleprof.name_s','')).startswith('FL CG ARRIVAL ')]
    assert not opening,[str(suffix(e,'eleprof.name_s','')) for e in opening]
    # The old graph controller may remain as an inert compatibility marker for build
    # tooling, but with zero ARRIVAL camera entities there is no native relationship
    # graph capable of driving the insertion.
    controller=[e for e in entities if str(suffix(e,'eleprof.name_s',''))==CHAIN_CONTROLLER]
    assert len(controller)==1,len(controller)
    script=str(suffix(controller[0],'eleprof.aimain_s','')).replace('/','\\').lower()
    assert script==CHAIN_SCRIPT.lower(),script
    print('FIRST LIGHT // CINEGURU INSERTION REMOVAL PASS')
    print('0 ARRIVAL camera entities exist in encrypted map.ele; the compatibility graph controller has nothing to activate.')

if __name__=='__main__':main()
