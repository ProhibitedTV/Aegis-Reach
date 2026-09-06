"""Generate original Aegis Reach field-art assets for Vesper environmental storytelling.

These are not lore cards. They are practical things people on Vesper would have made:
survey placards, tide gauges, maintenance marks, and Mira Sen's recurring waveform stamp.
The images are generated into imagebank for CineGuru, HUD, signage, or future decal use.
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "Aegis Reach"
FILES = GAME / "Files"
OUT = FILES / "imagebank" / "aegis_reach" / "story"


def font(size, bold=False):
    candidates = [
        FILES / "editors" / "templates" / "fonts" / "orbitron bold.ttf",
        FILES / "editors" / "uiv3" / "roboto-medium.ttf",
        Path(r"C:\Windows\Fonts\bahnschrift.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf") if bold else Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()


def weather(image: Image.Image, strength=1.0):
    """Add restrained directional Vesper wear without destroying legibility."""
    image = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = image.size
    for i in range(int(18 * strength)):
        y = 12 + (i * 37) % max(20, h - 24)
        d.line((0, y, w, y - 8), fill=(226, 229, 215, 12), width=2)
    for i in range(int(12 * strength)):
        x = 20 + (i * 53) % max(20, w - 40)
        d.line((x, 0, x - 20, h), fill=(6, 11, 14, 18), width=1)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.7))
    return Image.alpha_composite(image, overlay)


def waveform_points(x0, y0, width, height):
    pts = []
    for i in range(width):
        t = i / max(1, width - 1)
        # Two almost-commensurate harmonics create the recurring "Choir" field mark.
        value = 0.58 * math.sin(t * math.tau * 3.0) + 0.30 * math.sin(t * math.tau * 7.0 + 0.8)
        pts.append((x0 + i, y0 + height * 0.5 - value * height * 0.34))
    return pts


def mira_waveform(path: Path):
    img = Image.new("RGBA", (1024, 512), (8, 15, 18, 245))
    d = ImageDraw.Draw(img)
    cyan = (71, 205, 214, 255)
    pale = (192, 209, 207, 255)
    d.rectangle((38, 38, 986, 474), outline=(64, 82, 88, 255), width=3)
    d.text((72, 62), "VESPER MERIDIAN SURVEY // FIELD TRACE", font=font(31, True), fill=pale)
    d.text((72, 112), "M. SEN / ARRAY 04 / BRINE-SHELF RESONANCE", font=font(22), fill=(132, 153, 157, 255))
    d.line(waveform_points(78, 180, 860, 210), fill=cyan, width=5)
    d.line((78, 391, 938, 391), fill=(67, 78, 78, 255), width=2)
    for i, label in enumerate(("0", "8", "16", "24", "32", "40")):
        x = 78 + i * 172
        d.line((x, 383, x, 400), fill=(110, 132, 133, 255), width=2)
        d.text((x - 8, 409), label, font=font(18), fill=(110, 132, 133, 255))
    d.text((770, 445), "NOT AEGIS CALIBRATION", font=font(18, True), fill=(185, 126, 58, 255))
    weather(img, 1.2).save(path, optimize=True)


def tide_marker(path: Path, gauge="17", datum="+41.7 M"):
    img = Image.new("RGBA", (512, 1024), (18, 24, 26, 245))
    d = ImageDraw.Draw(img)
    pale = (210, 215, 202, 255)
    cyan = (67, 179, 188, 255)
    d.rectangle((32, 32, 480, 992), outline=(81, 92, 91, 255), width=4)
    d.text((60, 66), "VESPER HYDROGRAPHIC", font=font(27, True), fill=pale)
    d.text((60, 112), f"TIDE GAUGE {gauge}", font=font(49, True), fill=(234, 235, 221, 255))
    d.text((60, 178), "MERIDIAN SHELF", font=font(24), fill=(128, 145, 145, 255))
    # Historical water record drawn as physical scale, not exposition prose.
    top, bottom = 260, 900
    d.line((142, top, 142, bottom), fill=pale, width=7)
    for i in range(11):
        y = top + i * (bottom - top) / 10
        length = 84 if i % 5 == 0 else 48
        d.line((142, y, 142 + length, y), fill=pale, width=4)
        if i % 2 == 0:
            d.text((238, y - 16), f"{50-i*5:02} m", font=font(24), fill=(158, 170, 164, 255))
    old_y = 366
    d.rectangle((64, old_y - 8, 446, old_y + 8), fill=(222, 225, 209, 235))
    d.text((228, old_y - 54), "HISTORIC BRINE LINE", font=font(20, True), fill=cyan)
    d.text((62, 930), f"DATUM {datum}", font=font(22, True), fill=(179, 126, 57, 255))
    weather(img, 1.6).save(path, optimize=True)


def field_patch(path: Path):
    img = Image.new("RGBA", (768, 768), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dark = (13, 23, 27, 252); cyan = (69, 198, 207, 255); pale = (210, 219, 213, 255)
    d.polygon([(384, 28), (692, 206), (692, 562), (384, 740), (76, 562), (76, 206)], fill=dark, outline=cyan)
    d.ellipse((240, 206, 528, 494), outline=(100, 125, 126, 255), width=4)
    d.line(waveform_points(198, 280, 372, 140), fill=cyan, width=7)
    d.text((222, 520), "MERIDIAN", font=font(38, True), fill=pale)
    d.text((284, 570), "SURVEY", font=font(34), fill=(150, 169, 168, 255))
    d.text((301, 625), "VESPER", font=font(28, True), fill=cyan)
    weather(img, 0.8).save(path, optimize=True)


def occupancy_notice(path: Path):
    img = Image.new("RGBA", (1024, 512), (26, 26, 24, 248))
    d = ImageDraw.Draw(img)
    amber = (224, 151, 63, 255); pale = (221, 222, 210, 255)
    d.rectangle((28, 28, 996, 484), outline=amber, width=5)
    d.text((56, 58), "AEGIS REACH // RELAYFALL", font=font(34, True), fill=pale)
    d.text((56, 120), "SHELF ACCESS // TIDAL FRACTURE CONTROL", font=font(27, True), fill=amber)
    d.text((56, 196), "CIVILIAN ROUTE CLOSED", font=font(54, True), fill=(234, 226, 207, 255))
    d.text((58, 280), "AUTHORIZED FIELD TEAMS USE MERIDIAN MARKERS", font=font(23), fill=(145, 157, 153, 255))
    d.text((58, 324), "DO NOT CROSS ACTIVE VENT FLAGS DURING AURELIA PERIGEE", font=font(23), fill=(145, 157, 153, 255))
    d.text((58, 414), "NOTICE 04-771 / REV 6", font=font(20), fill=(107, 120, 118, 255))
    weather(img, 1.3).save(path, optimize=True)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "mira_waveform.png": mira_waveform,
        "tide_gauge_17.png": lambda p: tide_marker(p, "17", "+41.7 M"),
        "tide_gauge_22.png": lambda p: tide_marker(p, "22", "+39.2 M"),
        "meridian_survey_patch.png": field_patch,
        "shelf_access_notice.png": occupancy_notice,
    }
    for name, fn in assets.items():
        fn(OUT / name)
    return [str((OUT / name).relative_to(FILES)) for name in assets]


def main():
    generated = build()
    print("AEGIS REACH // STORY ART")
    for item in generated:
        print(" -", item)


if __name__ == "__main__":
    main()
