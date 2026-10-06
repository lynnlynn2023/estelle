#!/usr/bin/env python3
"""Build the standalone preview named `从左向右走`."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Assets/Actions/从左向右走/Frames"
OUT = ROOT / "Assets/Actions/从左向右走/Preview"
PATHS = [
    SOURCE / "01-right-foot-contact.png",
    SOURCE / "02-left-leg-passing.png",
    SOURCE / "03-left-foot-contact.png",
    SOURCE / "04-right-leg-passing.png",
]
FRAME_DURATION_MS = 220
FPS = 25
FRAME_SIZE = (700, 600)
SCALE = 0.45


def anchors(image: Image.Image) -> tuple[float, float]:
    rgba = np.asarray(image.convert("RGBA"))
    rgb = rgba[:, :, :3].astype(np.int16)
    alpha = rgba[:, :, 3]
    yy, xx = np.indices(alpha.shape)
    hair = (
        (alpha > 64)
        & (rgb[:, :, 0] > 135)
        & (rgb[:, :, 0] > rgb[:, :, 1] * 1.35)
        & (rgb[:, :, 1] > rgb[:, :, 2] * 1.10)
        & (yy < 800)
    )
    _, hair_xs = np.where(hair)
    hair_x = float(np.median(hair_xs)) if len(hair_xs) else image.width / 2
    boots = (
        (alpha > 64)
        & (rgb[:, :, 0] > 150)
        & (rgb[:, :, 1] > 145)
        & (rgb[:, :, 2] > 135)
        & (yy > 700)
        & (np.abs(xx - hair_x) < 310)
    )
    boot_ys, _ = np.where(boots)
    ground_y = float(np.percentile(boot_ys, 99.5)) if len(boot_ys) else image.height * 0.93
    return hair_x, ground_y


def normalize(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    hair_x, ground_y = anchors(image)
    resized = image.resize(
        (round(image.width * SCALE), round(image.height * SCALE)),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    x = round(FRAME_SIZE[0] / 2 - hair_x * SCALE)
    y = round(FRAME_SIZE[1] - 14 - ground_y * SCALE)
    canvas.alpha_composite(resized, (x, y))
    return canvas


def background(frame: Image.Image, size: tuple[int, int], position: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, "#242731")
    canvas.alpha_composite(frame, position)
    return canvas.convert("RGB")


def save_in_place(frames: list[Image.Image]) -> None:
    stem = OUT / "从左向右走-原地循环"
    frames[0].save(
        stem.with_suffix(".webp"),
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        lossless=True,
        method=4,
    )
    palette_frames = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
        for frame in frames
    ]
    palette_frames[0].save(
        stem.with_suffix(".gif"),
        save_all=True,
        append_images=palette_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        disposal=2,
        optimize=False,
    )


def save_moving(frames: list[Image.Image]) -> None:
    width, height = 1100, 600
    sprite_scale = 0.72
    sprite_size = (
        round(FRAME_SIZE[0] * sprite_scale),
        round(FRAME_SIZE[1] * sprite_scale),
    )
    total_seconds = 8
    total_frames = total_seconds * FPS
    frames_per_drawing = max(1, round(FRAME_DURATION_MS * FPS / 1000))
    mp4_path = OUT / "从左向右走.mp4"
    gif_frames = []
    writer = cv2.VideoWriter(
        str(mp4_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        FPS,
        (width, height),
    )

    for number in range(total_frames):
        progress = number / max(total_frames - 1, 1)
        x = round(-sprite_size[0] + progress * (width + sprite_size[0]))
        key = (number // frames_per_drawing) % len(frames)
        sprite = frames[key].resize(sprite_size, Image.Resampling.LANCZOS)
        frame = background(sprite, (width, height), (x, height - sprite_size[1] - 8))
        writer.write(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR))
        if number % 2 == 0:
            gif_frames.append(frame.resize((880, 480), Image.Resampling.LANCZOS))
    writer.release()

    palette_frames = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
        for frame in gif_frames
    ]
    palette_frames[0].save(
        OUT / "从左向右走.gif",
        save_all=True,
        append_images=palette_frames[1:],
        duration=round(2000 / FPS),
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [normalize(path) for path in PATHS]
    save_in_place(frames)
    save_moving(frames)
    for path in sorted(OUT.glob("从左向右走*")):
        print(path)


if __name__ == "__main__":
    main()
