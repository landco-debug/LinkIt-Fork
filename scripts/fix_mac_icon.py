#!/usr/bin/env python3
"""Restore Linkit's ORIGINAL dark phone-to-laptop macOS icon without its black square.

The original icon is macos/Resources/Linkit.icns. DO NOT use
assets/app-icon/linkit-app-icon-source.png: it is a different blue circular logo.
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter
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

def restore_original_icon(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    if w < 256 or h < 256:
        raise RuntimeError(f"Unexpected original icon resolution: {img.size}")

    # Regression guard: the previous release mistakenly used the blue round logo.
    top_rgb = img.getpixel((w // 2, h // 5))
    print(f"ORIGINAL icon {img.size} interior/top={top_rgb} corner={img.getpixel((0,0))}")
    if top_rgb[2] > 130 and top_rgb[2] > 1.9 * (top_rgb[0] + 1):
        raise RuntimeError("Wrong blue icon source instead of original dark design")

    if img.getpixel((0, 0))[3] < 32:
        alpha = img.getchannel("A")
        bounds = alpha.point(lambda a: 255 if a > 24 else 0).getbbox()
        print("Original corners already transparent")
    else:
        # Remove only the external solid black rectangle. Preserve all interior
        # dark artwork, reflections and cyan/green device-transfer illustration.
        matte_color = img.getpixel((0, 0))[:3]
        rgb = img.convert("RGB")
        diff = ImageChops.difference(rgb, Image.new("RGB", img.size, matte_color))
        important = ImageChops.lighter(
            ImageChops.lighter(diff.getchannel("R"), diff.getchannel("G")),
            diff.getchannel("B")
        )
        foreground = important.point(lambda d: 255 if d > 16 else 0)
        bounds = foreground.getbbox()
        if bounds is None:
            raise RuntimeError("Cannot separate original artwork from black matte")
        fp = foreground.load()
        matte_mask = Image.new("L", img.size, 0)
        mp = matte_mask.load()
        for y in range(h):
            lo, hi = None, None
            for x in range(w):
                if fp[x, y]:
                    if lo is None:
                        lo = x
                    hi = x
            if lo is not None:
                for x in range(lo, hi + 1):
                    mp[x, y] = 255
        img.putalpha(matte_mask.filter(ImageFilter.GaussianBlur(0.6)))
        print(f"Removed black square matte; foreground={bounds}")
    if bounds is None:
        raise RuntimeError("Empty original icon")
    left, top, right, bottom = bounds
    if right - left < 0.48 * w or bottom - top < 0.48 * h:
        raise RuntimeError(f"Suspicious artwork bounding box: {bounds}")

    side = max(right - left, bottom - top) * 1.01
    cx, cy = (left + right) / 2, (top + bottom) / 2
    trimmed = img.crop((
        round(cx - side / 2), round(cy - side / 2),
        round(cx + side / 2), round(cy + side / 2)
    ))
    # MacOS 15 app icon optical scale: 822/1024 prevents oversized Launchpad icon.
    size = 822
    canvas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    canvas.alpha_composite(
        trimmed.resize((size, size), Image.Resampling.LANCZOS),
        ((1024 - size) // 2, (1024 - size) // 2)
    )
    return canvas

def main(root: Path) -> None:
    destination = root / "macos/Resources/Linkit.icns"
    if not destination.is_file():
        raise FileNotFoundError(f"Missing original icon: {destination}")
    # Extract source before replacing it with rebuilt transparent ICNS.
    with Image.open(destination) as original:
        icon = restore_original_icon(original.copy())
    preview = root / "linkit-icon-preview.png"
    icon.save(preview)
    with tempfile.TemporaryDirectory(prefix="linkit-icon-") as tmp:
        folder = Path(tmp) / "Linkit.iconset"
        folder.mkdir()
        for name, side in ICON_VARIANTS.items():
            icon.resize((side, side), Image.Resampling.LANCZOS).save(folder / name)
        subprocess.run(["iconutil", "-c", "icns", str(folder), "-o", str(destination)], check=True)
    print(f"Original dark artwork restored to: {destination}; preview: {preview}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: fix_mac_icon.py UPSTREAM_ROOT")
    main(Path(sys.argv[1]).resolve())
