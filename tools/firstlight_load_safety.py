"""Apply surgical load-time safety fixes to the authored First Light .fpm.

The stock MAX weapon.lua can crash during level load for hand-authored weapon pickup
entities whose runtime weapon state has not been initialized. First Light does not
need the two optional ground weapons to validate Mission 01, so strip only entities
whose assigned AI script is exactly weapon.lua. Ammo pickups, the player's starting
weapon, enemies, objectives, terrain, and all other entities are left untouched.

This operates on the encrypted MAX .fpm in place, then re-applies MAX's legacy
ZipCrypto envelope using max_archive.convert(). It is idempotent.
"""
from pathlib import Path
import tempfile
import zipfile

from native_format import ROOT, read_ele, write_ele
from max_archive import PASSWORD, convert

MAP = ROOT / 'Aegis Reach/Files/mapbank/Aegis Reach - First Light.fpm'


def _script_name(entity):
    value = entity.get('101:eleprof.aimain_s', '')
    return str(value).replace('/', '\\').lower()


def patch_map(path=MAP):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as src:
        src.setpassword(PASSWORD)
        infos = src.infolist()
        payloads = {info.filename: src.read(info.filename) for info in infos}

    version, entities = read_ele(payloads['map.ele'])
    removed = [e for e in entities if _script_name(e) in ('weapon.lua', 'scriptbank\\weapon.lua')]
    if not removed:
        print('FIRST LIGHT // LOAD SAFETY: no stock weapon.lua pickup entities present')
        return 0

    kept = [e for e in entities if _script_name(e) not in ('weapon.lua', 'scriptbank\\weapon.lua')]
    payloads['map.ele'] = write_ele(version, kept)

    with tempfile.NamedTemporaryFile(suffix='.fpm', delete=False, dir=path.parent) as handle:
        temp = Path(handle.name)

    try:
        with zipfile.ZipFile(temp, 'w') as out:
            for info in infos:
                clone = zipfile.ZipInfo(info.filename, date_time=info.date_time)
                clone.compress_type = info.compress_type
                clone.external_attr = info.external_attr
                clone.internal_attr = info.internal_attr
                clone.create_system = info.create_system
                clone.comment = info.comment
                clone.extra = info.extra
                out.writestr(clone, payloads[info.filename])
        temp.replace(path)
        convert(path)
    finally:
        if temp.exists():
            temp.unlink()

    with zipfile.ZipFile(path) as check:
        check.setpassword(PASSWORD)
        _, verify = read_ele(check.read('map.ele'))
        assert not any(_script_name(e) in ('weapon.lua', 'scriptbank\\weapon.lua') for e in verify)
        assert all(info.flag_bits & 1 for info in check.infolist())

    names = [str(e.get('101:eleprof.name_s', '<unnamed>')) for e in removed]
    print('FIRST LIGHT // LOAD SAFETY: removed', len(removed), 'stock weapon.lua pickup entities')
    for name in names:
        print('  -', name)
    return len(removed)


if __name__ == '__main__':
    patch_map()
