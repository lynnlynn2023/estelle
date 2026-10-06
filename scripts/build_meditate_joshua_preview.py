#!/usr/bin/env python3
"""Build the meditation loop while keeping Estelle and the thought bubble still."""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
ACTION_DIR = ROOT / "Assets" / "Actions" / "坐下打坐"
SOURCE = ACTION_DIR / "Sources" / "meditate-joshua-thought-master.png"
SCALED_SOURCE = ACTION_DIR / "Sources" / "meditate-joshua-thought-master-standing-scale.png"
FRAMES_DIR = ACTION_DIR / "Frames"
PREVIEW_DIR = ACTION_DIR / "Preview"

FRAME_COUNT = 24
FRAME_MS = 100
PORTRAIT_CENTER = (987, 250)
STANDING_CHARACTER_SCALE = 0.72


def fit_to_standing_character_scale(image: Image.Image) -> Image.Image:
    """Match the seated character's head scale to the approved front standing pose."""
    alpha_box = image.getchannel("A").getbbox()
    if alpha_box is None:
        raise ValueError("Meditation image contains no visible pixels")

    width = round(image.width * STANDING_CHARACTER_SCALE)
    height = round(image.height * STANDING_CHARACTER_SCALE)
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    scaled_box = resized.getchannel("A").getbbox()
    if scaled_box is None:
        raise ValueError("Scaled meditation image contains no visible pixels")

    canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
    x = round((image.width - width) / 2)
    # Preserve the original ground line while adding the extra transparent room
    # required by the smaller, standing-matched character scale.
    y = image.height - scaled_box[3]
    canvas.alpha_composite(resized, (x, y))
    return canvas


def portrait_mask(image: Image.Image) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"))
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3]
    height, width = alpha.shape

    brightness = rgb.mean(axis=2)
    colour_range = rgb.max(axis=2) - rgb.min(axis=2)

    # Find the connected Joshua silhouette inside a conservative rectangle. This
    # avoids picking up the brown thought-bubble outline, which must never move.
    portrait_region = np.zeros((height, width), dtype=bool)
    portrait_region[45:458, 810:1192] = True
    content = portrait_region & (alpha > 0) & (
        (brightness < 244.0) | (colour_range > 13)
    )
    kernel = np.ones((3, 3), np.uint8)
    candidates = cv2.morphologyEx(content.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(candidates, connectivity=8)
    if count <= 1:
        raise RuntimeError("Could not find Joshua silhouette inside thought bubble")
    subject_label = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    component = (labels == subject_label).astype(np.uint8) * 255
    contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(component)
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)
    mask = cv2.dilate(mask, kernel, iterations=1)
    mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
    return Image.fromarray(mask, mode="L")


def prepare_layers(source: Image.Image) -> tuple[Image.Image, Image.Image, tuple[int, int, int, int]]:
    mask = portrait_mask(source)
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("Could not isolate Joshua's portrait")

    portrait = source.copy()
    portrait.putalpha(mask)

    # Remove the portrait beneath the moving layer. The interior of the bubble is
    # intentionally flat and nearly white, so a sampled median gives a clean fill.
    rgba = np.asarray(source.convert("RGBA"))
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    mask_np = np.asarray(mask)
    neutral = (
        (alpha > 0)
        & (rgb.mean(axis=2) > 245)
        & ((rgb.max(axis=2) - rgb.min(axis=2)) < 12)
        & (mask_np < 16)
    )
    fill_colour = tuple(int(v) for v in np.median(rgb[neutral], axis=0))
    fill = Image.new("RGBA", source.size, fill_colour + (255,))
    erase = mask.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(3.0))
    base = Image.composite(fill, source, erase)
    return base, portrait.crop(bbox), bbox


def animate_frame(
    base: Image.Image,
    portrait_crop: Image.Image,
    bbox: tuple[int, int, int, int],
    index: int,
) -> Image.Image:
    phase = 2.0 * math.pi * index / FRAME_COUNT
    dx = round(1.0 * math.sin(phase))
    dy = round(3.0 * math.sin(phase))
    scale = 1.0 + 0.007 * math.sin(phase)

    width = max(1, round(portrait_crop.width * scale))
    height = max(1, round(portrait_crop.height * scale))
    moving = portrait_crop.resize((width, height), Image.Resampling.LANCZOS)
    center_x = (bbox[0] + bbox[2]) / 2.0 + dx
    center_y = (bbox[1] + bbox[3]) / 2.0 + dy
    position = (round(center_x - width / 2.0), round(center_y - height / 2.0))

    frame = base.copy()
    frame.alpha_composite(moving, position)
    return frame


def on_dark(image: Image.Image, size: tuple[int, int] | None = None) -> Image.Image:
    canvas = Image.new("RGBA", image.size, (28, 29, 34, 255))
    canvas.alpha_composite(image)
    if size:
        canvas.thumbnail(size, Image.Resampling.LANCZOS)
    return canvas.convert("RGB")


def write_contact_sheet(frames: list[Image.Image], path: Path) -> None:
    selected = [frames[i] for i in (0, 6, 12, 18)]
    tile_size = 420
    sheet = Image.new("RGB", (tile_size * 4, tile_size + 42), (20, 21, 25))
    draw = ImageDraw.Draw(sheet)
    for column, frame in enumerate(selected):
        tile = on_dark(frame, (tile_size, tile_size))
        x = column * tile_size + (tile_size - tile.width) // 2
        y = (tile_size - tile.height) // 2
        sheet.paste(tile, (x, y))
        draw.text((column * tile_size + 14, tile_size + 12), f"phase {column + 1}", fill=(225, 225, 230))
    sheet.save(path)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    source = Image.open(SOURCE).convert("RGBA")
    base, portrait_crop, bbox = prepare_layers(source)
    unscaled_frames = [animate_frame(base, portrait_crop, bbox, index) for index in range(FRAME_COUNT)]

    # The original seated illustration was drawn with a noticeably larger head
    # than the standing and crouching poses. Scale the complete composition only
    # after animating Joshua so every loop frame keeps the exact same registration.
    frames = [fit_to_standing_character_scale(frame) for frame in unscaled_frames]
    fit_to_standing_character_scale(source).save(SCALED_SOURCE, optimize=True)

    for stale in FRAMES_DIR.glob("meditate-joshua-*.png"):
        stale.unlink()
    for index, frame in enumerate(frames):
        frame.save(FRAMES_DIR / f"meditate-joshua-{index:02d}.png", optimize=True)

    webp_path = PREVIEW_DIR / "坐下打坐_想念约修亚-v1.webp"
    gif_path = PREVIEW_DIR / "坐下打坐_想念约修亚-v1.gif"
    mp4_path = PREVIEW_DIR / "坐下打坐_想念约修亚-v1.mp4"
    contact_path = PREVIEW_DIR / "坐下打坐_想念约修亚-v1-contact-sheet.png"

    frames[0].save(
        webp_path,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        lossless=True,
        method=6,
    )
    dark_frames = [on_dark(frame, (720, 720)) for frame in frames]
    dark_frames[0].save(
        gif_path,
        save_all=True,
        append_images=dark_frames[1:],
        duration=FRAME_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )
    write_contact_sheet(frames, contact_path)

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-stream_loop",
                "3",
                "-i",
                str(gif_path),
                "-vf",
                "format=yuv420p",
                "-movflags",
                "+faststart",
                str(mp4_path),
            ],
            check=True,
        )

    # Everything outside the portrait's working area must remain identical.
    guard = np.zeros((source.height, source.width), dtype=bool)
    x0, y0, x1, y1 = bbox
    margin = 12
    guard[max(0, y0 - margin):min(source.height, y1 + margin), max(0, x0 - margin):min(source.width, x1 + margin)] = True
    reference = np.asarray(unscaled_frames[0])
    max_outside_delta = max(
        int(np.abs(np.asarray(frame).astype(np.int16) - reference.astype(np.int16))[~guard].max(initial=0))
        for frame in unscaled_frames[1:]
    )
    print(f"portrait_bbox={bbox}")
    print(f"fill_colour={tuple(base.getpixel(PORTRAIT_CENTER)[:3])}")
    print(f"max_outside_portrait_delta={max_outside_delta}")
    print(f"standing_character_scale={STANDING_CHARACTER_SCALE}")
    print(SCALED_SOURCE)
    print(webp_path)
    print(gif_path)
    print(contact_path)


if __name__ == "__main__":
    main()
