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
    # Vesper's night grade crushed the original ~20-90 RGB hull almost to black.
    # Cinematic-v2 deliberately lifts the aircraft into a readable moonlit midrange;
    # the TPS/interior remain dark because their source tiles begin substantially lower.
    img=ImageEnhance.Brightness(img).enhance(1.55)
    img=ImageEnhance.Contrast(img).enhance(1.06)
    draw=ImageDraw.Draw(img)
    tile=img.width//8
    # Shell/secondary identification bands. These are broad enough to survive mipmaps
    # at insertion-camera distances and provide recognizable military airframe rhythm.
    cyan=(92,202,210); pale=(214,220,211); dark=(34,43,46); amber=(220,136,73)
    for idx in (0,1):
        x=idx*tile
        draw.rectangle((x+14,18,x+tile-14,29),fill=cyan)
        draw.rectangle((x+14,tile-32,x+tile-14,tile-22),fill=dark)
        for px in (34,82,130):draw.rectangle((x+px,42,x+px+4,150),fill=(91,104,106))
    # Markings tile: readable military/flight-line identity instead of anonymous gray.
    x=4*tile
    draw.rectangle((x+12,40,x+tile-12,78),fill=pale)
    draw.rectangle((x+12,92,x+tile-12,128),fill=(84,103,103))
    draw.text((x+20,47),'VANGUARD',font=_font(20),fill=(31,40,42))
    draw.text((x+23,99),'KSTL-07',font=_font(18),fill=(224,232,224))
    draw.rectangle((x+14,140,x+tile-14,151),fill=amber)
    # Structure/TPS get edge-readable maintenance stripes without becoming glossy.
    for idx in (2,7):
        x=idx*tile
        for y in (24,88,152):draw.rectangle((x+18,y,x+tile-18,y+3),fill=(72,82,83))
    img.save(ATLAS,optimize=True)

    em=Image.open(EMISSIVE).convert('RGB');ed=ImageDraw.Draw(em)
    # Cool IFF/service strips on shell and markings; hot propulsion tiles remain owned
    # by the procedural generator. These strips establish silhouette in near-black shots
    # without turning the entire hull into self-lit plastic.
    for idx in (0,1,4):
        x=idx*tile
        ed.rectangle((x+18,18,x+tile-18,25),fill=(36,190,204))
        ed.rectangle((x+22,tile-28,x+tile-22,tile-22),fill=(14,112,122))
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
        # Full metalness plus dark albedo was producing a black void. Keep a metallic
        # response, but bias toward diffuse readability and let cyan service emission
        # define form when the environment is nearly unlit.
        text=set_field(text,'roughnessStrength','0.92')
        text=set_field(text,'metalnessStrength','0.58')
        text=set_field(text,'emissiveStrength','1.55')
        text=set_field(text,'reflectance','0.36')
        path.write_text(text)


def main():
    finish_atlas();finish_fpes()
    print('FIRST LIGHT // KESTREL CINEMATIC MATERIAL PASS')
    print('Hull exposure raised for Vesper night, VANGUARD/KSTL markings restored, stronger cyan IFF silhouette active, APBR metal response restrained.')

if __name__=='__main__':main()
