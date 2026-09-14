"""Fast regression checks for the First Light material-polish pipeline."""
from pathlib import Path
import numpy as np
from PIL import Image
from firstlight_material_polish import _compose_tiles,_normal_from_albedo,_surface_from_albedo,_replace_field,_source_image

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/texture_sources/first_light'

def main():
    path=SOURCE/'first_light_material_sources.jpg'
    assert path.is_file(), path
    for kind in ('kestrel_hull','kestrel_interior','meridian','m17','flora','brineglass'):
        im=_source_image(SOURCE,kind)
        assert min(im.size)>=256,(kind,im.size)
        assert np.asarray(im.resize((64,64))).std()>12,(kind,'source lacks detail')
    tile=Image.new('RGB',(32,32),(72,96,124))
    atlas=_compose_tiles([tile]*8)
    assert atlas.size==(256,32)
    normal=_normal_from_albedo(atlas,12.0)
    assert normal.size==atlas.size
    surface=_surface_from_albedo(atlas,32,(100,)*8,(200,)*8)
    assert surface.mode=='RGBA' and surface.getpixel((2,2))[0]==255
    assert 80<=surface.getpixel((2,2))[1]<=120
    assert surface.getpixel((2,2))[2]==200 and surface.getpixel((2,2))[3]==255
    text='effect = effectbank\\reloaded\\apbr_basic.fx\nbaseColorMap = old.png\n'
    text=_replace_field(text,'normalMap','new_normal.png')
    text=_replace_field(text,'baseColorMap','new_base.png')
    assert 'normalMap = new_normal.png' in text and 'baseColorMap = new_base.png' in text
    print('FIRST LIGHT // MATERIAL POLISH REGRESSION PASS')
    print('Source atlases: 6 // APBR packing + normal generation + binding helpers verified.')

if __name__=='__main__':main()
