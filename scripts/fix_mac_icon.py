#!/usr/bin/env python3
"""Remove the opaque black square from the original macOS app icon.

Requires Pillow and Apple's iconutil, on a macOS GitHub Actions runner.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import subprocess
import sys
import tempfile

ICON_VARIANTS = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}


def prepare_icon(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    rgb = img.convert("RGB")
    bg = rgb.getpixel((0, 0))
    diff = ImageChops.difference(rgb, Image.new("RGB", img.size, bg))
    channel = ImageChops.lighter(
        ImageChops.lighter(diff.getchannel("R"), diff.getchannel("G")),
        diff.getchannel("B"),
    )
    visible = channel.point(lambda value: 255 if value > 24 else 0)
    bbox = visible.getbbox()
    if bbox is None:
        raise RuntimeError("Icon detection failed: no artwork found")
    left, top, right, bottom = bbox
    w, h = img.size
    # The artwork is a rounded square inset in a solid black square.
    # Only auto-crop when the detected matte is plausibly narrow.
    if 0 < left < w * 0.15 and 0 < top < h * 0.15 and right > w * 0.85 and bottom > h * 0.85:
        side = max(right - left, bottom - top)
        cx, cy = (left + right) / 2, (top + bottom) / 2
        crop = (
            int(round(cx - side / 2)), int(round(cy - side / 2)),
            int(round(cx + side / 2)), int(round(cy + side / 2)),
        )
        img = img.crop(crop)
        print(f"Removed opaque icon frame: {crop}, background RGB={bg}")
    else:
        print(f"No safe matte crop detected ({bbox}); applying alpha mask only")

    size = 1024
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size * 2, size * 2), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        (0, 0, size * 2 - 1, size * 2 - 1),
        radius=int(size * 2 * 0.225),
        fill=255,
    )
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)
    img.putalpha(ImageChops.multiply(mask, img.getchannel("A")))
    return img


def main(root: Path) -> None:
    source = root / "assets/app-icon/linkit-app-icon-source.png"
    destination = root / "macos/Resources/Linkit.icns"
    if not source.is_file() or not destination.is_file():
        raise FileNotFoundError(f"Upstream icon files missing: {source} or {destination}")
    icon = prepare_icon(Image.open(source))
    with tempfile.TemporaryDirectory(prefix="linkit-icon-") as tmp:
        folder = Path(tmp) / "Linkit.iconset"
        folder.mkdir()
        for name, side in ICON_VARIANTS.items():
            icon.resize((side, side), Image.Resampling.LANCZOS).save(folder / name)
        subprocess.run(
            ["iconutil", "-c", "icns", str(folder), "-o", str(destination)],
            check=True,
        )
    print(f"Rebuilt transparent rounded macOS icon: {destination}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: fix_mac_icon.py UPSTREAM_ROOT")
    main(Path(sys.argv[1]).resolve())
