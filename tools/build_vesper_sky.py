"""Project an original lat-long sky into MAX's native DDS cubemap format.

This is texture-format conversion, not a native game render. The source panorama
is retained unchanged. D3D face order: +X, -X, +Y, -Y, +Z, -Z. Longitude zero is
world +Z (north), increasing toward +X. No licensed sky textures are used.
"""
from pathlib import Path
import math
import struct
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT/'Aegis Reach/Design/First Light/Sky/vesper-orbital-panorama.png'
DEST = ROOT/'Aegis Reach/Files/skybank/vesper_orbital'
SIZE = 1024


def sample(source, x, y, z):
    """Bilinear periodic-longitude sampling with pixel-center coordinates."""
    h, w = source.shape[:2]
    norm = np.sqrt(x*x+y*y+z*z)
    u = (np.arctan2(x,z)/(2*np.pi)) % 1
    v = np.arccos(np.clip(y/norm,-1,1))/np.pi
    sx = u*w-.5
    sy = np.clip(v*h-.5,0,h-1)
    ix = np.floor(sx).astype(int); iy = np.floor(sy).astype(int)
    fx = (sx-ix)[...,None]; fy = (sy-iy)[...,None]
    a = source[iy,ix%w]*(1-fx)+source[iy,(ix+1)%w]*fx
    b = source[np.minimum(iy+1,h-1),ix%w]*(1-fx)+source[np.minimum(iy+1,h-1),(ix+1)%w]*fx
    return np.clip(a*(1-fy)+b*fy,0,255).astype('uint8')


def directions(face, size):
    q = (np.arange(size,dtype=np.float32)+.5)*2/size-1
    u,v = np.meshgrid(q,q); one = np.ones_like(u)
    return ((one,-v,-u),(-one,-v,u),(u,one,v),
            (u,-one,-v),(u,-v,one),(-u,-v,-one))[face]


def write_cube(path, faces):
    n = faces[0].width
    levels = int(math.log2(n))+1
    # Legacy RGBA8 DDS; all six faces, complete face-major mip chain.
    header = [124,0x2100F,n,n,n*4,0,levels]+[0]*11
    header += [32,0x41,0,32,0xff,0xff00,0xff0000,0xff000000]
    header += [0x401008,0xfe00,0,0,0]
    with path.open('wb') as f:
        f.write(b'DDS '+struct.pack('<31I',*header))
        for face in faces:
            for level in range(levels):
                edge = max(1,n>>level)
                mip = face if level==0 else face.resize((edge,edge),Image.Resampling.BOX)
                f.write(mip.convert('RGBA').tobytes())


def build():
    source = np.asarray(Image.open(SOURCE).convert('RGB'),dtype=np.float32)
    assert source.shape[1] == source.shape[0]*2, 'sky must cover the full sphere'
    faces = [Image.fromarray(sample(source,*directions(i,SIZE))) for i in range(6)]
    DEST.mkdir(parents=True,exist_ok=True)
    write_cube(DEST/'vesper_orbital_cube.dds',faces)
    (DEST/'skyspec.txt').write_text('; Original Vesper orbital sky\nSunRotationX = 82\nSunRotationY = 280\nSunRotationZ = 0\n')
    # An asset picker thumbnail, not game evidence.
    source_im = Image.open(SOURCE).convert('RGB')
    source_im.resize((256,128),Image.Resampling.LANCZOS).save(DEST/'preview.bmp')
    # Perspective projection to check celestial shape and cube orientation offline.
    width,height = 1280,720
    u,v=np.meshgrid((np.arange(width)+.5-width/2)/(width/2),
                    (height/2-np.arange(height)-.5)/(width/2))
    x=u*np.tan(np.deg2rad(90/2));y=v*np.tan(np.deg2rad(90/2));z=np.ones_like(x)
    pitch=np.deg2rad(20);yy=y*np.cos(pitch)+z*np.sin(pitch);zz=z*np.cos(pitch)-y*np.sin(pitch)
    yaw=np.deg2rad(290);xx=x*np.cos(yaw)+zz*np.sin(yaw);zz2=zz*np.cos(yaw)-x*np.sin(yaw)
    preview=Image.fromarray(sample(source,xx,yy,zz2))
    d=ImageDraw.Draw(preview);d.rectangle((0,0,530,26),fill=(0,0,0))
    d.text((8,8),'SKY TEXTURE PROJECTION / NOT A NATIVE MAX SCREENSHOT',fill=(220,230,240))
    preview.save(SOURCE.parent/'projection-preview.png')
    print('VESPER SKY: six 1024px RGBA faces, 11 mip levels, original source retained')


if __name__=='__main__':
    build()
