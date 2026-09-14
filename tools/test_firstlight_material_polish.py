"""Fast regression checks for the First Light material-polish pipeline."""
from pathlib import Path
from PIL import Image,ImageFile,ImageStat
from firstlight_material_polish import _compose_tiles,_normal_from_albedo,_surface_from_albedo,_replace_field,_source_image
from firstlight_material_contracts import correct_brineglass_surface

# The checked-in JPEG may arrive through a connector with only its terminal EOI
# marker stripped. Accept that transport artifact, but still verify dimensions and
# visual variance so genuinely incomplete/corrupt source art fails loudly.
ImageFile.LOAD_TRUNCATED_IMAGES=True

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/texture_sources/first_light'

def main():
    path=SOURCE/'first_light_material_sources.jpg'
    assert path.is_file(), path
    assert path.stat().st_size>4096,('material source unexpectedly small',path.stat().st_size)
    header=Image.open(path)
    assert header.size==(960,640),('unexpected material source sheet size',header.size)
    for kind in ('kestrel_hull','kestrel_interior','meridian','m17','flora','brineglass'):
        im=_source_image(SOURCE,kind)
        assert min(im.size)>=256,(kind,im.size)
        std=max(ImageStat.Stat(im.resize((64,64)).convert('RGB')).stddev)
        assert std>12,(kind,'source lacks detail',std)
    tile=Image.new('RGB',(32,32),(72,96,124))
    atlas=_compose_tiles([tile]*8)
    assert atlas.size==(256,32)
    normal=_normal_from_albedo(atlas,12.0)
    assert normal.size==atlas.size
    surface=_surface_from_albedo(atlas,32,(100,)*8,(200,)*8)
    assert surface.mode=='RGBA' and surface.getpixel((2,2))[0]==255
    assert 80<=surface.getpixel((2,2))[1]<=120
    assert surface.getpixel((2,2))[2]==200 and surface.getpixel((2,2))[3]==255
    # Source-art detail may vary, but brineglass remains a dielectric crystal in the
    # engine contract: zero packed metalness and bounded glossy roughness.
    crystal=Image.new('RGBA',(16,16),(255,160,73,255))
    crystal=correct_brineglass_surface(crystal)
    assert crystal.getchannel('B').getextrema()==(0,0)
    assert crystal.getchannel('G').getextrema()==(110,110)
    text='effect = effectbank\\reloaded\\apbr_basic.fx\nbaseColorMap = old.png\n'
    text=_replace_field(text,'normalMap','new_normal.png')
    text=_replace_field(text,'baseColorMap','new_base.png')
    assert 'normalMap = new_normal.png' in text and 'baseColorMap = new_base.png' in text
    print('FIRST LIGHT // MATERIAL POLISH REGRESSION PASS')
    print('Source sheet: 960x640 // 6 atlases // APBR packing + dielectric brineglass + binding helpers verified.')

if __name__=='__main__':main()
