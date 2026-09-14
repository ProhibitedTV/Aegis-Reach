"""High-detail First Light material finishing pass.

The mission builders intentionally own geometry, UVs and gameplay.  This pass owns
only the authored APBR texture outputs and three visible M-17 material bindings.
It consumes original OpenAI-generated source atlases checked into tools/texture_sources
and preserves the existing eight-tile UV contracts used by Kestrel, Meridian and
Vesper assets.

GameGuru MAX APBR surface packing used here:
  R = occlusion, G = roughness, B = metalness, A = reflectance.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import sys
from typing import Iterable

from PIL import Image, ImageEnhance, ImageFilter

MODULE_VERSION = "first-light-material-polish-v1"
REGIONS = (
    (0.00, 0.00, 0.50, 0.50),
    (0.50, 0.00, 1.00, 0.50),
    (0.00, 0.50, 0.50, 1.00),
    (0.50, 0.50, 1.00, 1.00),
    (0.08, 0.18, 0.58, 0.68),
    (0.42, 0.16, 0.92, 0.66),
    (0.06, 0.42, 0.56, 0.92),
    (0.44, 0.42, 0.94, 0.92),
)


def _paths(root: Path):
    source = root / "tools/texture_sources/first_light"
    target = root / "Aegis Reach/Files/entitybank/Aegis Reach/First Light"
    design = root / "Aegis Reach/Design/First Light"
    return source, target, design


def _source_image(source: Path, kind: str) -> Image.Image:
    path = source / "first_light_material_sources.jpg"
    if not path.is_file():
        raise FileNotFoundError(f"material source sheet missing: {path}")
    sheet = Image.open(path).convert("RGB")
    cells = {
        "kestrel_hull": (0,0), "kestrel_interior": (1,0), "meridian": (2,0),
        "m17": (0,1), "flora": (1,1), "brineglass": (2,1),
    }
    if kind not in cells:
        raise KeyError(kind)
    cw, ch = sheet.width//3, sheet.height//2
    if min(cw,ch) < 256:
        raise ValueError(f"material source cells too small: {path} {sheet.size}")
    cx,cy=cells[kind]
    return sheet.crop((cx*cw,cy*ch,(cx+1)*cw,(cy+1)*ch))


def _crop(im: Image.Image, region, size: int, *, base=None, remove_dark=False, contrast=1.05, saturation=0.94):
    w, h = im.size
    x0, y0, x1, y1 = region
    box = (round(x0*w), round(y0*h), round(x1*w), round(y1*h))
    tile = im.crop(box).resize((size, size), Image.Resampling.LANCZOS)
    tile = tile.filter(ImageFilter.UnsharpMask(radius=1.15, percent=105, threshold=2))
    tile = ImageEnhance.Contrast(tile).enhance(contrast)
    tile = ImageEnhance.Color(tile).enhance(saturation)
    if base is not None:
        under = Image.new("RGB", (size, size), base)
        if remove_dark:
            lum = tile.convert("L")
            mask = lum.point(lambda v: max(0, min(255, (v-24)*4))).filter(ImageFilter.GaussianBlur(2.0))
            tile = Image.composite(tile, under, mask)
        else:
            tile = Image.blend(under, tile, 0.80)
    return tile


def _compose_tiles(tiles: Iterable[Image.Image]) -> Image.Image:
    tiles = list(tiles)
    if len(tiles) != 8 or len({t.size for t in tiles}) != 1:
        raise ValueError("material atlases require exactly eight equal-size tiles")
    size = tiles[0].width
    out = Image.new("RGB", (size*8, size))
    for i, tile in enumerate(tiles):
        out.paste(tile, (i*size, 0))
    return out


def _normal_from_albedo(albedo: Image.Image, strength: float) -> Image.Image:
    gray = albedo.convert("L").filter(ImageFilter.GaussianBlur(0.35))
    scale=max(0.7, 9.5/max(1.0,strength))
    gx=gray.filter(ImageFilter.Kernel((3,3),(-1,0,1,-2,0,2,-1,0,1),scale=scale,offset=128))
    gy=gray.filter(ImageFilter.Kernel((3,3),(-1,-2,-1,0,0,0,1,2,1),scale=scale,offset=128))
    blue=Image.new("L",albedo.size,244)
    return Image.merge("RGB",(gx,gy,blue))


def _surface_from_albedo(albedo: Image.Image, tile_size: int, roughness, metalness, reflectance=255) -> Image.Image:
    if len(roughness) != 8 or len(metalness) != 8:
        raise ValueError("surface semantics must cover all eight UV tiles")
    out=Image.new("RGBA",albedo.size,(255,128,0,reflectance))
    for i,(rgh,met) in enumerate(zip(roughness,metalness)):
        box=(i*tile_size,0,(i+1)*tile_size,tile_size)
        lum=albedo.crop(box).convert("L")
        rough=lum.point(lambda v,r=rgh:max(35,min(240,round(r-(v-128)*.16))))
        ao=Image.new("L",lum.size,255); metallic=Image.new("L",lum.size,met); refl=Image.new("L",lum.size,reflectance)
        out.paste(Image.merge("RGBA",(ao,rough,metallic,refl)),box)
    return out


def _surface_tile(albedo: Image.Image, roughness: int, metalness: int, reflectance=255) -> Image.Image:
    lum=albedo.convert("L")
    rough=lum.point(lambda v:max(35,min(240,round(roughness-(v-128)*.16))))
    return Image.merge("RGBA",(Image.new("L",lum.size,255),rough,Image.new("L",lum.size,metalness),Image.new("L",lum.size,reflectance)))


def _emission_tile(tile: Image.Image, color: tuple[int,int,int], threshold=145) -> Image.Image:
    lum = tile.convert("L")
    mask = lum.point(lambda v: max(0, min(255, (v-threshold)*3))).filter(ImageFilter.GaussianBlur(1.2))
    return Image.composite(Image.new("RGB",tile.size,color), Image.new("RGB",tile.size,(0,0,0)), mask)


def _emission(atlas: Image.Image, tile_size: int, colors: dict[int, tuple[int,int,int]], threshold=145) -> Image.Image:
    out = Image.new("RGB", atlas.size, (0,0,0))
    for tile, color in colors.items():
        crop = atlas.crop((tile*tile_size, 0, (tile+1)*tile_size, tile_size))
        lum = crop.convert("L")
        mask = lum.point(lambda v: max(0, min(255, (v-threshold)*3))).filter(ImageFilter.GaussianBlur(1.2))
        glow = Image.new("RGB", crop.size, color)
        black = Image.new("RGB", crop.size, (0,0,0))
        out.paste(Image.composite(glow, black, mask), (tile*tile_size,0))
    return out


def _save(path: Path, image: Image.Image):
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=(image.width <= 4096), compress_level=6 if image.width > 4096 else 9)


def _build_kestrel(source: Path, target: Path):
    hull = _source_image(source, "kestrel_hull")
    interior = _source_image(source, "kestrel_interior")
    size = 512
    tiles = [_crop(hull, REGIONS[i], size, contrast=1.08, saturation=.82) for i in range(7)]
    tiles.append(_crop(interior, REGIONS[4], size, contrast=1.06, saturation=.80))
    atlas = _compose_tiles(tiles)
    normal = _normal_from_albedo(atlas, 16.0)
    surface = _surface_from_albedo(atlas,size,(150,138,132,160,112,118,175,156),(188,205,175,210,230,224,82,128))
    emissive = _emission(atlas,size,{4:(255,92,28),5:(75,180,220),7:(32,112,128)},threshold=160)
    outputs={"kestrel_broadwing_atlas.png":atlas,"kestrel_broadwing_normal.png":normal,"kestrel_broadwing_surface.png":surface,"kestrel_broadwing_emissive.png":emissive}
    for name,im in outputs.items(): _save(target/name,im)
    return list(outputs)


def _build_meridian(source: Path, target: Path):
    src=_source_image(source,"meridian");size=512
    tiles=[_crop(src,r,size,contrast=1.07,saturation=.75) for r in REGIONS]
    tiles[4]=Image.blend(tiles[4],Image.new("RGB",(size,size),(238,177,88)),.20)
    tiles[5]=Image.blend(tiles[5],Image.new("RGB",(size,size),(67,145,158)),.22)
    atlas=_compose_tiles(tiles);normal=_normal_from_albedo(atlas,14.0)
    surface=_surface_from_albedo(atlas,size,(188,204,136,174,108,118,190,178),(18,42,210,54,24,20,12,72))
    emission=_emission(atlas,size,{4:(255,193,104),5:(25,112,132)},threshold=168)
    outputs={"meridian_fieldkit.png":atlas,"meridian_fieldkit_normal.png":normal,"meridian_fieldkit_surface.png":surface,"meridian_fieldkit_emission.png":emission}
    for name,im in outputs.items(): _save(target/name,im)
    return list(outputs)


def _build_m17(source: Path, target: Path):
    src=_source_image(source,"m17");size=512;order=(0,1,4,2,3,5,6,7)
    tiles=[_crop(src,REGIONS[i],size,contrast=1.11,saturation=.78) for i in order]
    atlas=_compose_tiles(tiles);normal=_normal_from_albedo(atlas,20.0)
    surface=_surface_from_albedo(atlas,size,(184,170,142,198,122,134,208,188),(146,170,210,132,230,220,98,172))
    outputs={"m17_wreck_atlas.png":atlas,"m17_wreck_normal.png":normal,"m17_wreck_surface.png":surface}
    for name,im in outputs.items(): _save(target/name,im)
    return list(outputs)


def _build_biosphere(source: Path, target: Path):
    flora=_source_image(source,"flora");crystal=_source_image(source,"brineglass");size=1024
    bases=((80,93,86),(119,99,112),(102,132,127),(119,117,106),(87,108,109),(93,107,124),(86,124,118),(116,102,125));rough=(202,184,154,196,172,118,126,178);metal=(0,0,0,0,0,18,16,0);glow={2:(52,104,111),5:(78,126,174),6:(50,170,154)}
    tiles=[];normals=[];surfaces=[];emissions=[]
    for i in range(8):
        src=crystal if i in (5,6) else flora
        tile=_crop(src,REGIONS[i],size,base=bases[i],remove_dark=True,contrast=1.05,saturation=.86)
        tiles.append(tile);normals.append(_normal_from_albedo(tile,10.0));surfaces.append(_surface_tile(tile,rough[i],metal[i]));emissions.append(_emission_tile(tile,glow[i],174) if i in glow else Image.new("RGB",(size,size),(0,0,0)))
    atlas=_compose_tiles(tiles);normal=_compose_tiles(normals);surface=Image.new("RGBA",(size*8,size));emission=_compose_tiles(emissions)
    for i,tile in enumerate(surfaces): surface.paste(tile,(i*size,0))
    outputs={"vesper_biosphere.png":atlas,"vesper_biosphere_normal.png":normal,"vesper_biosphere_surface.png":surface,"vesper_biosphere_emission.png":emission}
    for name,im in outputs.items(): _save(target/name,im)
    return list(outputs)


def _square_mineral(src: Image.Image, region, size, tint, resonant=False):
    tile=_crop(src,region,size,contrast=1.10 if resonant else 1.06,saturation=1.02)
    return Image.blend(tile,Image.new("RGB",tile.size,tint),.12 if resonant else .08)


def _build_brineglass(source: Path, target: Path):
    src=_source_image(source,"brineglass");size=1024
    calm=_square_mineral(src,REGIONS[0],size,(88,142,137),False);resonant=_square_mineral(src,REGIONS[5],size,(84,88,164),True)
    outputs={"vesper_brineglass_mineral.png":calm,"vesper_brineglass_mineral_surface.png":_surface_tile(calm,104,22),"vesper_brineglass_mineral_normal.png":_normal_from_albedo(calm,14.0),"vesper_brineglass_energy.png":_emission_tile(calm,(38,190,178),148),"vesper_brineglass_resonant_mineral.png":resonant,"vesper_brineglass_resonant_mineral_surface.png":_surface_tile(resonant,88,28),"vesper_brineglass_resonant_mineral_normal.png":_normal_from_albedo(resonant,17.0),"vesper_brineglass_resonant.png":_emission_tile(resonant,(82,92,255),132)}
    for name,im in outputs.items(): _save(target/name,im)
    return list(outputs)


def _replace_field(text: str, key: str, value: str) -> str:
    pattern=rf"(?mi)^{re.escape(key)}\s*=.*$";line=f"{key} = {value}"
    if re.search(pattern,text): return re.sub(pattern,line,text)
    anchor=re.search(r"(?mi)^effect\s*=.*$",text)
    if anchor:
        pos=anchor.end();return text[:pos]+"\n"+line+text[pos:]
    return text.rstrip()+"\n"+line+"\n"


def _bind_m17(target: Path):
    names=("Meridian M17 Transport Wreck.fpe","Meridian M17 Detached Engine.fpe","Meridian M17 Torn Panel.fpe");changed=[]
    for name in names:
        path=target/name
        if not path.is_file(): raise FileNotFoundError(f"M-17 FPE missing: {path}")
        text=path.read_text()
        for key,value in (("textured","m17_wreck_atlas.png"),("baseColorMap","m17_wreck_atlas.png"),("normalMap","m17_wreck_normal.png"),("surfaceMap","m17_wreck_surface.png")): text=_replace_field(text,key,value)
        path.write_text(text);changed.append(name)
    return changed


def _bind_brineglass(target: Path):
    specs=(("Vesper Brineglass Bloom.fpe","vesper_brineglass_mineral_normal.png"),("Vesper Resonant Brineglass Bloom.fpe","vesper_brineglass_resonant_mineral_normal.png"));changed=[]
    for name,normal in specs:
        path=target/name
        if not path.is_file(): raise FileNotFoundError(f"brineglass FPE missing: {path}")
        text=path.read_text();text=_replace_field(text,"normalMap",normal);text=_replace_field(text,"normalStrength","0.62");path.write_text(text);changed.append(name)
    return changed


def _hash_sources(source: Path) -> str:
    h=hashlib.sha256(MODULE_VERSION.encode());path=source/"first_light_material_sources.jpg";h.update(path.name.encode());h.update(b"\0");h.update(path.read_bytes());h.update(b"\0");return h.hexdigest()


def apply_material_polish(root: Path | None = None, *, force=False):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1];source,target,design=_paths(root);marker=design/"material-polish.json";signature=_hash_sources(source);prior={}
    try: prior=json.loads(marker.read_text())
    except Exception: pass
    required=("kestrel_broadwing_atlas.png","kestrel_broadwing_normal.png","kestrel_broadwing_surface.png","kestrel_broadwing_emissive.png","meridian_fieldkit.png","meridian_fieldkit_normal.png","meridian_fieldkit_surface.png","meridian_fieldkit_emission.png","m17_wreck_atlas.png","m17_wreck_normal.png","m17_wreck_surface.png","vesper_biosphere.png","vesper_biosphere_normal.png","vesper_biosphere_surface.png","vesper_biosphere_emission.png","vesper_brineglass_mineral.png","vesper_brineglass_mineral_surface.png","vesper_brineglass_mineral_normal.png","vesper_brineglass_energy.png","vesper_brineglass_resonant_mineral.png","vesper_brineglass_resonant_mineral_surface.png","vesper_brineglass_resonant_mineral_normal.png","vesper_brineglass_resonant.png")
    current=(prior.get("source_sha256")==signature and prior.get("version")==MODULE_VERSION and all((target/n).is_file() for n in required))
    if current and not force: print("FIRST LIGHT // MATERIAL POLISH CURRENT",signature[:16]);return prior
    outputs=[];outputs+=_build_kestrel(source,target);outputs+=_build_meridian(source,target);outputs+=_build_m17(source,target);outputs+=_build_biosphere(source,target);outputs+=_build_brineglass(source,target);bindings=_bind_m17(target)+_bind_brineglass(target);out_hashes={name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in outputs};payload={"version":MODULE_VERSION,"source_sha256":signature,"outputs":out_hashes,"bindings":bindings};marker.parent.mkdir(parents=True,exist_ok=True);marker.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print("FIRST LIGHT // MATERIAL POLISH PASS");print(f"High-detail APBR outputs: {len(outputs)} // bindings: {len(bindings)}");return payload


def _self_test(root: Path):
    from PIL import ImageStat
    payload=apply_material_polish(root,force=True);_,target,_=_paths(root);expected={"kestrel_broadwing_atlas.png":(4096,512),"meridian_fieldkit.png":(4096,512),"m17_wreck_atlas.png":(4096,512),"vesper_biosphere.png":(8192,1024),"vesper_brineglass_mineral.png":(1024,1024)}
    for name,size in expected.items():
        im=Image.open(target/name);assert im.size==size,(name,im.size,size);std=max(ImageStat.Stat(im.resize((128,128)).convert("RGB")).stddev);assert std>10.0,(name,"insufficient material variance",std)
    for name in ("Meridian M17 Transport Wreck.fpe","Meridian M17 Detached Engine.fpe","Meridian M17 Torn Panel.fpe"):
        text=(target/name).read_text();assert "m17_wreck_atlas.png" in text and "m17_wreck_normal.png" in text and "m17_wreck_surface.png" in text
    print("FIRST LIGHT // MATERIAL POLISH SELF TEST PASS",payload["source_sha256"][:16])


if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--self-test": _self_test(Path(sys.argv[2]))
    else: apply_material_polish()
