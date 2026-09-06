"""Write the legacy ZipCrypto envelope required by MAX's cZip reader.

MAX calls unzOpenCurrentFilePassword unconditionally, including for entries
without the encrypted flag. A normal unencrypted ZIP therefore silently fails.
This is the public engine's file-format key, not user data encryption.
"""
from pathlib import Path
import os, struct, zipfile

PASSWORD = b'mypassword'
TABLE = [zipfile._gen_crc(n) for n in range(256)]

def encrypt(data):
    a, b, c = 0x12345678, 0x23456789, 0x34567890
    def update(ch):
        nonlocal a,b,c
        a = (a >> 8) ^ TABLE[(a ^ ch) & 255]
        b = ((b + (a & 255)) * 134775813 + 1) & 0xffffffff
        c = (c >> 8) ^ TABLE[(c ^ (b >> 24)) & 255]
    for ch in PASSWORD: update(ch)
    out = bytearray(len(data))
    for i,ch in enumerate(data):
        k = c | 2
        out[i] = ch ^ (((k * (k ^ 1)) >> 8) & 255)
        update(ch)
    return out

def convert(path):
    path = Path(path)
    source = path.read_bytes()
    central = bytearray()
    target = bytearray()
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if all(i.flag_bits & 1 for i in entries): return
        for i in entries:
            assert not i.flag_bits & 1, 'Mixed encryption is not supported'
            offset = len(target)
            h = struct.unpack_from('<IHHHHHIIIHH', source, i.header_offset)
            p = i.header_offset + 30 + h[-2] + h[-1]
            compressed = source[p:p+i.compress_size]
            name = i.filename.encode('ascii')
            time,date=h[4:6]
            payload=encrypt(os.urandom(11)+bytes([i.CRC>>24])+compressed)
            target.extend(struct.pack('<IHHHHHIIIHH',0x04034b50,20,1,i.compress_type,time,date,i.CRC,len(payload),i.file_size,len(name),0))
            target.extend(name);target.extend(payload)
            central.extend(struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,1,i.compress_type,time,date,i.CRC,len(payload),i.file_size,len(name),0,0,0,0,0,offset))
            central.extend(name)
    start=len(target)
    target.extend(central)
    target.extend(struct.pack('<IHHHHIIH',0x06054b50,0,0,len(entries),len(entries),len(central),start,0))
    tmp=path.with_suffix('.encrypting')
    tmp.write_bytes(target)
    with zipfile.ZipFile(tmp) as check:
        check.setpassword(PASSWORD)
        assert check.read('header.dat')
        assert check.read('map.ele')
        assert all(i.flag_bits & 1 for i in check.infolist())
    tmp.replace(path)
    print('MAX encrypted archive:',path.name,len(entries),'entries')

if __name__=='__main__':
    import sys
    convert(sys.argv[1])
