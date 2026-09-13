"""Installation-independent regression tests for the owned asset-library auditor."""
from pathlib import Path
from tempfile import TemporaryDirectory

from max_asset_library_audit import scan,summarize


def write(path: Path,text: str):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text)


def main():
    with TemporaryDirectory() as td:
        root=Path(td)
        write(root/'Props/Crate.fpe','desc = Crate\nmodel = Crate.x\ncollisionmode = 0\nbaseColorMap = Crate_color.png\nnormalMap = Crate_normal.png\nsurfaceMap = Crate_surface.png\naimain = no_behavior_selected.lua\n')
        write(root/'Props/Crate.x','xof 0303txt 0032\n')
        for name in ('Crate_color.png','Crate_normal.png','Crate_surface.png'):write(root/'Props'/name,'fixture')
        write(root/'Characters/Guard.fpe','desc = Guard\nmodel = Guard.x\nischaracter = 1\naimain = people\\character_attack.lua\n')
        write(root/'Characters/Guard.x','xof 0303txt 0032\n')
        write(root/'Weapons/Rifle.fpe','desc = Rifle weapon\nmodel = Rifle.x\ncollisionmode = 11\n')
        write(root/'Weapons/Rifle.x','xof 0303txt 0032\n')
        write(root/'Broken/Missing.fpe','desc = Missing\nmodel = nope.x\ncollisionmode = 0\n')

        records=scan([('classic',root)])
        by={r.relative_fpe:r for r in records}
        assert by['Props/Crate.fpe'].category=='static_prop'
        assert by['Props/Crate.fpe'].risk=='low'
        assert by['Props/Crate.fpe'].pbr_ready
        assert by['Characters/Guard.fpe'].category=='character_or_creature'
        assert by['Characters/Guard.fpe'].risk=='high'
        assert by['Weapons/Rifle.fpe'].category=='weapon_or_ammo'
        assert by['Broken/Missing.fpe'].category=='missing_model'
        report=summarize(records)
        assert report['entity_count']==4
        assert report['top_static_candidates'][0]['relative_fpe']=='Props/Crate.fpe'
        assert report['policy']['copy_media_into_git'] is False
    print('MAX/CLASSIC ASSET AUDITOR PASS: portable, read-only, pack-audition policy enforced.')


if __name__=='__main__':main()
