"""Final material invariants applied after the authored First Light art pass.

The texture-polish stage is allowed to derive rich high-frequency detail from source
art.  This module owns engine/material semantics that must not drift with that art:
brineglass is a dielectric crystal, never metal, and its packed APBR roughness must
stay inside the range already validated by the Meridian material regression.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

from PIL import Image

BRINEGLASS_SURFACES=(
    'vesper_brineglass_mineral_surface.png',
    'vesper_brineglass_resonant_mineral_surface.png',
)
ROUGHNESS_MIN=45
ROUGHNESS_MAX=110


def correct_brineglass_surface(surface: Image.Image) -> Image.Image:
    """Return an APBR surface map with the project brineglass contract enforced."""
    rgba=surface.convert('RGBA')
    occlusion,roughness,_metalness,reflectance=rgba.split()
    roughness=roughness.point(lambda v:max(ROUGHNESS_MIN,min(ROUGHNESS_MAX,v)))
    metalness=Image.new('L',rgba.size,0)
    return Image.merge('RGBA',(occlusion,roughness,metalness,reflectance))


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def enforce_material_contracts(root: Path | None=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    target=root/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
    design=root/'Aegis Reach/Design/First Light'
    changed=[]
    for name in BRINEGLASS_SURFACES:
        path=target/name
        if not path.is_file():
            raise FileNotFoundError(f'brineglass surface missing: {path}')
        with Image.open(path) as src:
            before=src.convert('RGBA')
            fixed=correct_brineglass_surface(before)
            before_b=before.getchannel('B').getextrema()
            before_g=before.getchannel('G').getextrema()
        if before_b!=(0,0) or before_g[0]<ROUGHNESS_MIN or before_g[1]>ROUGHNESS_MAX:
            fixed.save(path,optimize=True,compress_level=9)
            changed.append(name)
        with Image.open(path) as check:
            if check.getchannel('B').getextrema()!=(0,0):
                raise ValueError(f'brineglass metalness contract failed: {name}')
            lo,hi=check.getchannel('G').getextrema()
            if not (ROUGHNESS_MIN<=lo<=hi<=ROUGHNESS_MAX):
                raise ValueError(f'brineglass roughness contract failed: {name} {lo}..{hi}')

    # Keep the material-polish manifest honest after the final semantic pass.
    marker=design/'material-polish.json'
    if marker.is_file():
        payload=json.loads(marker.read_text())
        outputs=payload.setdefault('outputs',{})
        for name in BRINEGLASS_SURFACES:
            outputs[name]=_sha256(target/name)
        marker.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')

    if changed:
        print('FIRST LIGHT // MATERIAL CONTRACTS PASS:',', '.join(changed))
    else:
        print('FIRST LIGHT // MATERIAL CONTRACTS CURRENT')
    return changed
