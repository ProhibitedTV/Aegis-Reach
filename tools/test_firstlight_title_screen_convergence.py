"""Regression: playable FIRST LIGHT carries the title screen's landmark hierarchy."""
import json,zipfile
from native_format import ROOT,read_ele
from max_archive import PASSWORD
from firstlight_title_screen_convergence import LANDMARKS

DESIGN=ROOT/'Aegis Reach/Design/First Light'
MAP=ROOT/'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'


def suffix(entity,name,default=0):
    for key,value in entity.items():
        if key.split(':',1)[-1]==name:return value
    return default


def main():
    layout=json.loads((DESIGN/'layout.json').read_text())
    title=[p for p in layout if str(p.get('kind','')).startswith('title_')]
    assert len(title)==len(LANDMARKS),(len(title),len(LANDMARKS))
    assert sum(p.get('kind')=='title_landmark' for p in title)==2
    assert sum(p.get('kind')=='title_spire' for p in title)==5
    names={p['name'] for p in title}
    expected={row[0] for row in LANDMARKS};assert names==expected
    with zipfile.ZipFile(MAP) as archive:
        archive.setpassword(PASSWORD);_,entities=read_ele(archive.read('map.ele'))
    native={str(suffix(e,'eleprof.name_s','')):e for e in entities}
    for name in expected:
        e=native.get(name);assert e is not None,name
        assert int(suffix(e,'eleprof.physics',1) or 0)==0,name+' must stay visual-only'
    print('FIRST LIGHT // TITLE-SCREEN CONVERGENCE PASS')
    print(len(title),'visual-only skyline pieces // 2 broken crown arcs // 5 cyan-accent relay spires // fortified Northstar massing.')

if __name__=='__main__':main()
