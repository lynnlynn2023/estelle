#!/usr/bin/env python3
"""Export every approved desktop-pet action as a transparent animated WebP."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Sources" / "EstellePet" / "Resources"
ACTIONS = ROOT / "Assets" / "Actions"

WALK_CANVAS = (1280, 720)
WALK_SPRITE_SIZE = (300, 300)
WALK_FPS = 12
WALK_SECONDS = 12
WALK_DRAWING_MS = 220

ACTION_DURATIONS = [
    250, 70, 70, 85, 85, 230,
    *([72] * 16),
    260,
    160, 85, 85, 85, 75, 120,
]
PAUSE_DURATIONS = [250, 70, 70, 85, 85, 180, 180, 180, 220, 120]
RESUME_DURATIONS = [100, 100, 120, 100, 100, 80, 80, 140]
STRUGGLE_SEQUENCE = [0, 1, 2, 3, 2, 1]
STRUGGLE_DURATIONS = [190, 180, 160, 180, 160, 180]
STUMBLE_DURATIONS = [160, 180, 170, 220, 280, 180, 150, 150, 180]


@dataclass(frozen=True)
class ExportSpec:
    action_dir: str
    output_name: str
    resource_stem: str
    frame_count: int
    durations: list[int]


EXPORTS = [
    ExportSpec("原地转棍", "原地转棍_透明.webp", "action", 29, ACTION_DURATIONS),
    ExportSpec("坐下打坐", "坐下打坐_透明.webp", "meditate", 24, [100] * 24),
    ExportSpec(
        "暂停过渡_跳跃转正面到坐下",
        "暂停过渡_跳跃转正面到坐下_透明.webp",
        "pause-transition",
        10,
        PAUSE_DURATIONS,
    ),
    ExportSpec(
        "继续过渡_打坐跳起回到走路",
        "继续过渡_打坐跳起回到走路_透明.webp",
        "resume-transition",
        8,
        RESUME_DURATIONS,
    ),
    ExportSpec(
        "走路中差点摔倒又站稳",
        "走路中差点摔倒又站稳_透明.webp",
        "stumble",
        9,
        STUMBLE_DURATIONS,
    ),
]


def load_frames(stem: str, count: int) -> list[Image.Image]:
    paths = [RESOURCES / f"{stem}-{index:02d}.png" for index in range(1, count + 1)]
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing frames for {stem}: {missing}")
    return [Image.open(path).convert("RGBA") for path in paths]


def save_webp(path: Path, frames: list[Image.Image], durations: list[int]) -> None:
    if len(frames) != len(durations):
        raise ValueError(f"Frame/duration mismatch for {path}: {len(frames)} != {len(durations)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        lossless=True,
        method=6,
        background=(0, 0, 0, 0),
    )


def build_walking_crossing() -> tuple[list[Image.Image], list[int]]:
    source = [
        Image.open(RESOURCES / f"walk-square-right-{index}.png").convert("RGBA")
        for index in range(1, 5)
    ]
    sprites = [frame.resize(WALK_SPRITE_SIZE, Image.Resampling.LANCZOS) for frame in source]

    reference_box = sprites[0].getchannel("A").getbbox()
    if reference_box is None:
        raise ValueError("Walking reference frame has no visible pixels")
    start_x = -reference_box[0]
    end_x = WALK_CANVAS[0] - reference_box[2]
    y = WALK_CANVAS[1] - WALK_SPRITE_SIZE[1] - 18

    frame_count = WALK_FPS * WALK_SECONDS
    frames: list[Image.Image] = []
    for index in range(frame_count):
        elapsed_ms = index * 1000 / WALK_FPS
        drawing = int(elapsed_ms // WALK_DRAWING_MS) % len(sprites)
        progress = index / (frame_count - 1)
        x = round(start_x + (end_x - start_x) * progress)
        canvas = Image.new("RGBA", WALK_CANVAS, (0, 0, 0, 0))
        canvas.alpha_composite(sprites[drawing], (x, y))
        frames.append(canvas)
    return frames, [round(1000 / WALK_FPS)] * frame_count


def export_walk() -> Path:
    frames, durations = build_walking_crossing()
    output = (
        ACTIONS
        / "从左向右走"
        / "Preview"
        / "透明背景"
        / "从左向右走_横跨画布_透明.webp"
    )
    save_webp(output, frames, durations)
    return output


def export_struggle() -> Path:
    unique = load_frames("struggle", 4)
    frames = [unique[index] for index in STRUGGLE_SEQUENCE]
    output = (
        ACTIONS
        / "被鼠标提起_气呼呼挣扎"
        / "Preview"
        / "透明背景"
        / "被鼠标提起_气呼呼挣扎_透明.webp"
    )
    save_webp(output, frames, STRUGGLE_DURATIONS)
    return output


def validate(path: Path) -> tuple[int, tuple[int, int]]:
    image = Image.open(path)
    frame_count = getattr(image, "n_frames", 1)
    image.seek(0)
    rgba = image.convert("RGBA")
    if rgba.getpixel((0, 0))[3] != 0:
        raise ValueError(f"Background is not transparent: {path}")
    return frame_count, image.size


def main() -> None:
    outputs = [export_walk(), export_struggle()]
    for spec in EXPORTS:
        frames = load_frames(spec.resource_stem, spec.frame_count)
        output = ACTIONS / spec.action_dir / "Preview" / "透明背景" / spec.output_name
        save_webp(output, frames, spec.durations)
        outputs.append(output)

    for output in outputs:
        frame_count, size = validate(output)
        print(f"{output.relative_to(ROOT)} | {frame_count} frames | {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
