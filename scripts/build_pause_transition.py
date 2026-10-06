#!/usr/bin/env python3
"""Build the pause transition: side hop to front, crouch, sit, then meditate."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import build_jump_turn_staff_spin_v3 as action
import build_meditate_joshua_preview as meditation


ROOT = Path(__file__).resolve().parents[1]
ACTION_DIR = ROOT / "Assets" / "Actions" / "暂停过渡_跳跃转正面到坐下"
RESUME_DIR = ROOT / "Assets" / "Actions" / "继续过渡_打坐跳起回到走路"
SOURCES = ACTION_DIR / "Sources"
FRAMES = ACTION_DIR / "Frames"
PREVIEW = ACTION_DIR / "Preview"
MEDITATE_MASTER = ROOT / "Assets" / "Actions" / "坐下打坐" / "Sources" / "meditate-joshua-thought-master.png"
MEDITATE_FRAMES = ROOT / "Assets" / "Actions" / "坐下打坐" / "Frames"
RUNTIME_SIZE = (900, 900)

HALF_CROUCH = SOURCES / "01-half-crouch-lowering-staff.png"
DEEP_CROUCH = SOURCES / "02-deep-crouch-horizontal-staff.png"
SEATED_NO_BUBBLE = SOURCES / "03-seated-no-thought-bubble.png"

FRAME_DURATIONS_MS = [250, 70, 70, 85, 85, 180, 180, 180, 220, 120]
RESUME_DURATIONS_MS = [100, 100, 120, 100, 100, 80, 80, 140]


def runtime_frame(image: Image.Image) -> Image.Image:
    return image.convert("RGBA").resize(RUNTIME_SIZE, Image.Resampling.LANCZOS)


def fitted_runtime_keyframe(image: Image.Image, visible_width: int, ground_y: int) -> Image.Image:
    """Fit generated crouch art to the standing frame without altering its source."""
    rgba = image.convert("RGBA")
    box = rgba.getchannel("A").getbbox()
    if box is None:
        raise ValueError("Transition keyframe contains no visible pixels")
    crop = rgba.crop(box)
    scale = visible_width / crop.width
    resized = crop.resize(
        (visible_width, round(crop.height * scale)),
        Image.Resampling.LANCZOS,
    )
    frame = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    x = (RUNTIME_SIZE[0] - resized.width) // 2
    y = ground_y - resized.height
    frame.alpha_composite(resized, (x, y))
    return frame


def remove_thought_bubble(image: Image.Image) -> Image.Image:
    """Remove only the disconnected bubble and dots; keep Estelle untouched."""
    rgba = np.asarray(image.convert("RGBA")).copy()
    alpha = rgba[:, :, 3]
    count, labels, stats, centroids = cv2.connectedComponentsWithStats((alpha > 8).astype(np.uint8), 8)
    removal_mask = np.zeros(alpha.shape, dtype=np.uint8)
    for label in range(1, count):
        x, y, width, height, area = stats[label]
        center_x, center_y = centroids[label]
        is_bubble_or_dot = center_x > image.width * 0.52 and center_y < image.height * 0.42
        if is_bubble_or_dot:
            removal_mask[labels == label] = 255
    # Include the low-alpha antialiased halo surrounding each disconnected shape.
    removal_mask = cv2.dilate(removal_mask, np.ones((11, 11), np.uint8), iterations=1)
    rgba[removal_mask > 0] = 0
    # Keep the single connected Estelle-and-staff silhouette. This also removes
    # isolated sub-pixel remnants left by the bubble's antialiased edge.
    remaining = (rgba[:, :, 3] > 0).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(remaining, 8)
    if count > 1:
        subject = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        rgba[(labels != 0) & (labels != subject)] = 0
    return Image.fromarray(rgba)


def build_frames() -> list[Image.Image]:
    full_action = action_frames()
    standing_to_front = full_action[:6]

    # Both generated crouch sources are good drawings, but their transparent
    # canvases made them render 17% and 30% larger than the standing pose. Fit
    # only their runtime copies to the standing frame's 686 px visible width.
    half_crouch = fitted_runtime_keyframe(Image.open(HALF_CROUCH), visible_width=686, ground_y=848)
    deep_crouch = fitted_runtime_keyframe(Image.open(DEEP_CROUCH), visible_width=686, ground_y=875)

    raw_seated = remove_thought_bubble(Image.open(MEDITATE_MASTER).convert("RGBA"))
    seated = meditation.fit_to_standing_character_scale(raw_seated)
    seated.save(SEATED_NO_BUBBLE, optimize=True)

    full_meditation = Image.open(MEDITATE_FRAMES / "meditate-joshua-00.png").convert("RGBA")
    return standing_to_front + [half_crouch, deep_crouch, runtime_frame(seated), runtime_frame(full_meditation)]


def action_frames() -> list[Image.Image]:
    side = Image.open(action.SIDE_PATH).convert("RGBA")
    base, hand = action.load_spin_layers()
    staff, staff_pivot = action.make_staff()
    front_ready = action.held_staff_frame(base, hand, staff, staff_pivot, 90)
    return [
        runtime_frame(action.place_sprite(side, 0)),
        runtime_frame(action.place_sprite(side, 42)),
        runtime_frame(action.place_sprite(side, 82)),
        runtime_frame(action.lift_frame(front_ready, 82)),
        runtime_frame(action.lift_frame(front_ready, 38)),
        runtime_frame(action.lift_frame(front_ready, 0)),
    ]


def on_dark(image: Image.Image, size: tuple[int, int] = (720, 720)) -> Image.Image:
    background = Image.new("RGBA", image.size, (28, 29, 34, 255))
    background.alpha_composite(image)
    background.thumbnail(size, Image.Resampling.LANCZOS)
    return background.convert("RGB")


def write_preview(frames: list[Image.Image]) -> None:
    meditation_loop = [
        runtime_frame(Image.open(path))
        for path in sorted(MEDITATE_FRAMES.glob("meditate-joshua-*.png"))[:12]
    ]
    preview_frames = frames + meditation_loop
    durations = FRAME_DURATIONS_MS + [100] * len(meditation_loop)

    webp = PREVIEW / "暂停过渡_跳跃转正面到坐下.webp"
    gif = PREVIEW / "暂停过渡_跳跃转正面到坐下.gif"
    mp4 = PREVIEW / "暂停过渡_跳跃转正面到坐下.mp4"
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
                "3",
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


def write_resume_preview(frames: list[Image.Image]) -> None:
    preview_dir = RESUME_DIR / "Preview"
    preview_dir.mkdir(parents=True, exist_ok=True)
    webp = preview_dir / "继续过渡_打坐跳起回到走路.webp"
    gif = preview_dir / "继续过渡_打坐跳起回到走路.gif"
    mp4 = preview_dir / "继续过渡_打坐跳起回到走路.mp4"

    frames[0].save(
        webp,
        save_all=True,
        append_images=frames[1:],
        duration=RESUME_DURATIONS_MS,
        loop=0,
        lossless=True,
        method=6,
    )
    dark = [on_dark(frame) for frame in frames]
    dark[0].save(
        gif,
        save_all=True,
        append_images=dark[1:],
        duration=RESUME_DURATIONS_MS,
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
    SOURCES.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)

    frames = build_frames()
    if len(frames) != len(FRAME_DURATIONS_MS):
        raise ValueError(f"Expected {len(FRAME_DURATIONS_MS)} pause frames, found {len(frames)}")

    for stale in FRAMES.glob("pause-transition-*.png"):
        stale.unlink()
    for index, frame in enumerate(frames, start=1):
        frame.save(FRAMES / f"pause-transition-{index:02d}.png", optimize=True)
    write_preview(frames)

    # Continuing is intentionally not a plain reverse. She compresses into the
    # crouch, springs upward, turns back to the side at the apex, and lands on the
    # exact walk-cycle frame used by the staff action.
    resume_frames = [frames[index] for index in (9, 8, 7, 6, 3, 2, 1, 0)]
    resume_frames_dir = RESUME_DIR / "Frames"
    resume_frames_dir.mkdir(parents=True, exist_ok=True)
    for stale in resume_frames_dir.glob("resume-transition-*.png"):
        stale.unlink()
    for index, frame in enumerate(resume_frames, start=1):
        frame.save(resume_frames_dir / f"resume-transition-{index:02d}.png", optimize=True)
    write_resume_preview(resume_frames)

    print(f"Wrote {len(frames)} pause-transition frames")
    print(SEATED_NO_BUBBLE)
    print(PREVIEW / "暂停过渡_跳跃转正面到坐下.gif")
    print(RESUME_DIR / "Preview" / "继续过渡_打坐跳起回到走路.gif")


if __name__ == "__main__":
    main()
