"""Cinematic material finish for the FIRST LIGHT Broadwing Kestrel.

The procedural mesh author deliberately keeps geometry simple and robust.  This pass
finishes the generated APBR maps for the night insertion: brighter readable hull
values, deterministic service markings, restrained cyan identification light, and
less mirror-dark metal response.  It only touches original Aegis Reach assets.
"""
from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
from native_format import ROOT

AS=ROOT/'Aegis Reach/Files/entitybank/Aegis Reach/First Light'
ATLAS=AS/'kestrel_broadwing_atlas.png'
EMISSIVE=AS/'kestrel_broadwing_emissive.png'
FPE_NAMES=(
 'Vanguard Kestrel Dropship - Flight.fpe',
 'Vanguard Kestrel Dropship - Conversion.fpe',
 'Vanguard Kestrel Dropship - VTOL Flare.fpe',
 'Vanguard Kestrel Dropship - Landed Ramp.fpe',
)


def _font(size):
    try:return ImageFont.truetype('DejaVuSans-Bold.ttf',size)
    except Exception:return ImageFont.load_default()


def finish_atlas():
    if not ATLAS.is_file() or not EMISSIVE.is_file():
        raise SystemExit('KESTREL FINISH: generated atlas/emissive maps are missing')
    img=Image.open(ATLAS).convert('RGB')
    # The authored night grade was crushing the original ~20-90 RGB hull almost to
    # black.  Lift values without bleaching the TPS/interior identity.
    img=ImageEnhance.Brightness(img).enhance(1.34)
    img=ImageEnhance.Contrast(img).enhance(1.08)
    draw=ImageDraw.Draw(img)
    tile=img.width//8
    # Shell/secondary identification bands.  These are deliberately broad enough to
    # survive mipmapping at the camera distances used by the insertion sequence.
    cyan=(82,181,188); pale=(200,207,198); dark=(28,36,39); amber=(210,126,69)
    for idx in (0,1):
        x=idx*tile
        draw.rectangle((x+14,18,x+tile-14,27),fill=cyan)
        draw.rectangle((x+14,tile-30,x+tile-14,tile-22),fill=dark)
        for px in (34,82,130):draw.rectangle((x+px,42,x+px+3,150),fill=(77,88,90))
    # Markings tile: readable military/flight-line identity instead of anonymous gray.
    x=4*tile
    draw.rectangle((x+12,40,x+tile-12,78),fill=pale)
    draw.rectangle((x+12,92,x+tile-12,128),fill=(74,91,91))
    draw.text((x+20,47),'VANGUARD',font=_font(20),fill=(31,40,42))
    draw.text((x+23,99),'KSTL-07',font=_font(18),fill=(210,221,214))
    draw.rectangle((x+14,140,x+tile-14,150),fill=amber)
    # Structure/TPS get edge-readable maintenance stripes without becoming glossy.
    for idx in (2,7):
        x=idx*tile
        for y in (24,88,152):draw.rectangle((x+18,y,x+tile-18,y+3),fill=(63,72,73))
    img.save(ATLAS,optimize=True)

    em=Image.open(EMISSIVE).convert('RGB');ed=ImageDraw.Draw(em)
    # Cool IFF/service strips on shell and markings; hot propulsion tiles remain owned
    # by the procedural generator.  The strips provide form even in near-black shots.
    for idx in (0,1,4):
        x=idx*tile
        ed.rectangle((x+18,18,x+tile-18,23),fill=(28,154,166))
        ed.rectangle((x+22,tile-26,x+tile-22,tile-22),fill=(10,88,96))
    em.save(EMISSIVE,optimize=True)


def set_field(text,key,value):
    pat=rf'(?mi)^\s*{re.escape(key)}\s*=.*$'
    line=f'{key} = {value}'
    if re.search(pat,text):return re.sub(pat,line,text)
    if not text.endswith('\n'):text+='\n'
    return text+line+'\n'


def finish_fpes():
    for name in FPE_NAMES:
        path=AS/name
        if not path.is_file():raise SystemExit('KESTREL FINISH: missing '+name)
        text=path.read_text(errors='replace')
        # Full-strength metalness plus dark albedo was producing a black void in the
        # night sequence.  Keep it metallic, but give environment light something to
        # read and let the restrained emissive service strips define silhouette.
        text=set_field(text,'roughnessStrength','0.90')
        text=set_field(text,'metalnessStrength','0.72')
        text=set_field(text,'emissiveStrength','1.30')
        text=set_field(text,'reflectance','0.30')
        path.write_text(text)


def main():
    finish_atlas();finish_fpes()
    print('FIRST LIGHT // KESTREL CINEMATIC MATERIAL PASS')
    print('Hull values lifted, VANGUARD/KSTL markings restored, cyan IFF strips active, APBR metal response restrained.')

if __name__=='__main__':main()
