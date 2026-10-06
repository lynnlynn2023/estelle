#!/usr/bin/env python3
"""Build a preview for Estelle's mouthless picked-up struggle loop."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Assets" / "Actions" / "被鼠标提起_气呼呼挣扎" / "Frames"
OUT = ROOT / "Assets" / "Actions" / "被鼠标提起_气呼呼挣扎" / "Preview"
OUT.mkdir(parents=True, exist_ok=True)

FRAME_PATHS = [
    SOURCE / "01-center.png",
    SOURCE / "02-left-leg-kick.png",
    SOURCE / "03-recoil.png",
    SOURCE / "04-right-leg-kick.png",
]
FRAME_NAMES = ["基准", "左腿踢", "收腿", "右腿踢"]


def normalize(frame: Image.Image, size: tuple[int, int] = (1280, 1420)) -> Image.Image:
    """Keep a stable character scale while centering each transparent sprite."""
    frame = frame.convert("RGBA")
    alpha = frame.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("Frame contains no visible pixels")
    crop = frame.crop(bbox)
    scale = min((size[0] - 50) / crop.width, (size[1] - 50) / crop.height)
    # Use one capped scale so pose extension remains visible without changing identity.
    scale = min(scale, 1.0)
    crop = crop.resize(
        (round(crop.width * scale), round(crop.height * scale)),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - crop.width) // 2
    y = (size[1] - crop.height) // 2
    canvas.alpha_composite(crop, (x, y))
    return canvas


def on_background(frame: Image.Image, size: tuple[int, int] = (720, 800)) -> Image.Image:
    canvas = Image.new("RGBA", size, "#242731")
    scale = min((size[0] - 24) / frame.width, (size[1] - 24) / frame.height)
    sprite = frame.resize(
        (round(frame.width * scale), round(frame.height * scale)),
        Image.Resampling.LANCZOS,
    )
    canvas.alpha_composite(sprite, ((size[0] - sprite.width) // 2, (size[1] - sprite.height) // 2))
    return canvas.convert("RGB")


def contact_sheet(frames: list[Image.Image]) -> Image.Image:
    thumb_size = (360, 400)
    sheet = Image.new("RGB", (thumb_size[0] * 2, thumb_size[1] * 2), "#242731")
    draw = ImageDraw.Draw(sheet)
    for index, (frame, name) in enumerate(zip(frames, FRAME_NAMES)):
        thumb = on_background(frame, thumb_size)
        x = (index % 2) * thumb_size[0]
        y = (index // 2) * thumb_size[1]
        sheet.paste(thumb, (x, y))
        draw.rectangle((x + 8, y + 8, x + 104, y + 34), fill=(16, 18, 24))
        draw.text((x + 15, y + 14), f"{index + 1}", fill=(255, 228, 164))
    return sheet


def main() -> None:
    unique = [normalize(Image.open(path)) for path in FRAME_PATHS]

    # Center -> left kick -> recoil -> right kick -> recoil -> left kick.
    # Returning to center then closes the loop without a hard leg swap.
    order = [0, 1, 2, 3, 2, 1]
    # Deliberate, readable flailing rather than a rapid vibration.
    durations = [190, 180, 160, 180, 160, 180]
    transparent = [unique[index] for index in order]
    preview = [on_background(frame) for frame in transparent]

    stem = OUT / "被鼠标提起_气呼呼挣扎-v1"
    transparent[0].save(
        stem.with_suffix(".webp"),
        save_all=True,
        append_images=transparent[1:],
        duration=durations,
        loop=0,
        lossless=True,
        method=4,
    )

    gif_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=255) for frame in preview]
    gif_frames[0].save(
        stem.with_suffix(".gif"),
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )

    fps = 30
    video_frames: list[Image.Image] = []
    for frame, duration in zip(preview, durations):
        video_frames.extend([frame] * max(1, round(duration * fps / 1000)))
    writer = cv2.VideoWriter(
        str(stem.with_suffix(".mp4")),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        video_frames[0].size,
    )
    for _ in range(5):
        for frame in video_frames:
            writer.write(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR))
    writer.release()

    sheet_path = stem.with_name(stem.name + "-contact-sheet").with_suffix(".png")
    contact_sheet(unique).save(sheet_path)

    for path in (stem.with_suffix(".webp"), stem.with_suffix(".gif"), stem.with_suffix(".mp4"), sheet_path):
        print(path)


if __name__ == "__main__":
    main()
