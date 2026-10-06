#!/usr/bin/env python3
"""Draw the mouthless twin-tail silhouette used by the macOS status item."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "Assets" / "UI"
RESOURCE_DIR = ROOT / "Sources" / "EstellePet" / "Resources"
MASTER_SIZE = 1024


def cubic(p0, p1, p2, p3, steps=20):
    points = []
    for index in range(1, steps + 1):
        t = index / steps
        u = 1.0 - t
        points.append((
            u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
            u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
        ))
    return points


def scale(points):
    factor = MASTER_SIZE / 100.0
    return [(round(x * factor), round(y * factor)) for x, y in points]


def mirror(points):
    return [(100 - x, y) for x, y in points]


def left_tail():
    points = [(31, 29)]
    segments = [
        ((24, 24), (14, 27), (11, 36)),
        ((7, 47), (15, 54), (9, 64)),
        ((4, 72), (7, 83), (16, 91)),
        ((17, 78), (29, 72), (31, 59)),
        ((33, 48), (26, 39), (31, 29)),
    ]
    current = points[0]
    for control1, control2, end in segments:
        points.extend(cubic(current, control1, control2, end))
        current = end
    return points


def head_shape():
    # A chibi-proportioned round head: full cheeks and a soft chin, with only a
    # tiny top bump suggesting Estelle's hair rather than a crown of spikes.
    points = [(28, 39)]
    segments = [
        ((28, 25), (36, 15), (47, 13)),
        ((49, 9), (54, 8), (56, 13)),
        ((66, 16), (72, 26), (72, 39)),
        ((72, 57), (61, 76), (50, 76)),
        ((39, 76), (28, 57), (28, 39)),
    ]
    current = points[0]
    for control1, control2, end in segments:
        points.extend(cubic(current, control1, control2, end))
        current = end
    return points


def draw_silhouette() -> Image.Image:
    image = Image.new("RGBA", (MASTER_SIZE, MASTER_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    tail = left_tail()
    draw.polygon(scale(tail), fill=(0, 0, 0, 255))
    draw.polygon(scale(mirror(tail)), fill=(0, 0, 0, 255))

    # Round ties support the softer chibi silhouette.
    factor = MASTER_SIZE / 100.0
    draw.ellipse(tuple(round(value * factor) for value in (24, 29, 35, 40)), fill=(0, 0, 0, 255))
    draw.ellipse(tuple(round(value * factor) for value in (65, 29, 76, 40)), fill=(0, 0, 0, 255))
    draw.polygon(scale(head_shape()), fill=(0, 0, 0, 255))
    return image


def make_preview(master: Image.Image) -> Image.Image:
    preview = Image.new("RGB", (900, 450), (246, 246, 247))
    dark = Image.new("RGB", (450, 450), (35, 35, 38))
    preview.paste(dark, (450, 0))
    icon = master.resize((300, 300), Image.Resampling.LANCZOS)
    preview.paste(icon, (75, 75), icon)
    white = Image.new("RGBA", icon.size, (255, 255, 255, 0))
    white.putalpha(icon.getchannel("A"))
    preview.paste(white, (525, 75), white)
    return preview


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    RESOURCE_DIR.mkdir(parents=True, exist_ok=True)
    master = draw_silhouette()
    master.resize((512, 512), Image.Resampling.LANCZOS).save(ASSET_DIR / "status-icon-twintail-master.png")
    master.save(
        ASSET_DIR / "status-icon-twintail.ico",
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    make_preview(master).save(ASSET_DIR / "status-icon-twintail-preview.png")
    master.resize((72, 72), Image.Resampling.LANCZOS).save(RESOURCE_DIR / "status-icon.png", optimize=True)
    print(ASSET_DIR / "status-icon-twintail-preview.png")
    print(RESOURCE_DIR / "status-icon.png")


if __name__ == "__main__":
    main()
