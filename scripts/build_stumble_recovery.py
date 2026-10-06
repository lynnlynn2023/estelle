#!/usr/bin/env python3
"""Build the right-walking stumble, staff brace, and recovery animation."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image

import build_jump_turn_staff_spin_v3 as action


ROOT = Path(__file__).resolve().parents[1]
ACTION_DIR = ROOT / "Assets" / "Actions" / "走路中差点摔倒又站稳"
SOURCES = ACTION_DIR / "Sources"
FRAMES = ACTION_DIR / "Frames"
PREVIEW = ACTION_DIR / "Preview"
WALK_ENTRY = ROOT / "Assets" / "Actions" / "从左向右走" / "Frames" / "01-right-foot-contact.png"

TOE_CATCH = SOURCES / "01-toe-catch-start.png"
STAFF_BRACE = SOURCES / "02-staff-brace-save.png"
RUNTIME_SIZE = (900, 900)
VISIBLE_HEIGHT = 722
GROUND_Y = 800
SUBJECT_CENTER_X = 414
FRAME_DURATIONS_MS = [100, 120, 220, 140, 180]


def runtime_frame(image: Image.Image) -> Image.Image:
    return image.convert("RGBA").resize(RUNTIME_SIZE, Image.Resampling.LANCZOS)


def fitted_generated_frame(image: Image.Image) -> Image.Image:
    """Match generated keyframes to the approved walk frame's visible scale."""
    rgba = image.convert("RGBA")
    box = rgba.getchannel("A").getbbox()
    if box is None:
        raise ValueError("Stumble keyframe contains no visible pixels")
    crop = rgba.crop(box)
    scale = VISIBLE_HEIGHT / crop.height
    resized = crop.resize(
        (round(crop.width * scale), VISIBLE_HEIGHT),
        Image.Resampling.LANCZOS,
    )
    frame = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    x = round(SUBJECT_CENTER_X - resized.width / 2)
    y = GROUND_Y - resized.height
    frame.alpha_composite(resized, (x, y))
    return frame


def build_frames() -> list[Image.Image]:
    entry = runtime_frame(action.place_sprite(Image.open(WALK_ENTRY).convert("RGBA"), 0))
    toe_catch = fitted_generated_frame(Image.open(TOE_CATCH))
    staff_brace = fitted_generated_frame(Image.open(STAFF_BRACE))

    # Reuse the same correct toe-catch drawing on recovery. This deliberately
    # follows economical classic-JRPG keyframe animation and prevents the model
    # from changing her limb or hair proportions in a separate recovery drawing.
    return [entry, toe_catch, staff_brace, toe_catch.copy(), entry.copy()]


def on_dark(image: Image.Image, size: tuple[int, int] = (720, 720)) -> Image.Image:
    background = Image.new("RGBA", image.size, (28, 29, 34, 255))
    background.alpha_composite(image)
    background.thumbnail(size, Image.Resampling.LANCZOS)
    return background.convert("RGB")


def write_preview(frames: list[Image.Image]) -> None:
    webp = PREVIEW / "走路中差点摔倒又站稳.webp"
    gif = PREVIEW / "走路中差点摔倒又站稳.gif"
    mp4 = PREVIEW / "走路中差点摔倒又站稳.mp4"

    preview_frames = [frames[0], frames[0]] + frames[1:] + [frames[-1], frames[-1]]
    durations = [220, 120] + FRAME_DURATIONS_MS[1:] + [180, 220]
    preview_frames[0].save(
        webp,
        save_all=True,
        append_images=preview_frames[1:],
        duration=durations,
        loop=0,
        lossless=True,
        method=6,
    )
    dark = [on_dark(frame) for frame in preview_frames]
    dark[0].save(
        gif,
        save_all=True,
        append_images=dark[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loglevel",
                "error",
                "-stream_loop",
                "5",
                "-i",
                str(gif),
                "-vf",
                "format=yuv420p",
                "-movflags",
                "+faststart",
                str(mp4),
            ],
            check=True,
        )


def main() -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    frames = build_frames()
    if len(frames) != len(FRAME_DURATIONS_MS):
        raise ValueError("Unexpected stumble frame count")

    for stale in FRAMES.glob("stumble-*.png"):
        stale.unlink()
    for index, frame in enumerate(frames, start=1):
        frame.save(FRAMES / f"stumble-{index:02d}.png", optimize=True)
    write_preview(frames)

    print(f"Wrote {len(frames)} stumble frames")
    print(PREVIEW / "走路中差点摔倒又站稳.gif")


if __name__ == "__main__":
    main()
