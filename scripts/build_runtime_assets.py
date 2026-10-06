#!/usr/bin/env python3
"""Build square, transparent runtime frames for the macOS desktop pet."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

import build_jump_turn_staff_spin_v3 as action


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Sources/EstellePet/Resources"
RIGHT_WALK = ROOT / "Assets/Actions/从左向右走/Frames"
STRUGGLE = ROOT / "Assets/Actions/被鼠标提起_气呼呼挣扎/Frames"
MEDITATE = ROOT / "Assets/Actions/坐下打坐/Frames"
PAUSE_TRANSITION = ROOT / "Assets/Actions/暂停过渡_跳跃转正面到坐下/Frames"
RESUME_TRANSITION = ROOT / "Assets/Actions/继续过渡_打坐跳起回到走路/Frames"
STUMBLE = ROOT / "Assets/Actions/走路中差点摔倒又站稳/Frames"
RUNTIME_SIZE = (900, 900)

WALK_NAMES = [
    "01-right-foot-contact.png",
    "02-left-leg-passing.png",
    "03-left-foot-contact.png",
    "04-right-leg-passing.png",
]

STRUGGLE_NAMES = [
    "01-center.png",
    "02-left-leg-kick.png",
    "03-recoil.png",
    "04-right-leg-kick.png",
]


def runtime_frame(frame: Image.Image) -> Image.Image:
    return frame.resize(RUNTIME_SIZE, Image.Resampling.LANCZOS)


def save_walk_frames() -> None:
    for old_left_frame in RESOURCES.glob("walk-square-left-*.png"):
        old_left_frame.unlink()
    for index, filename in enumerate(WALK_NAMES, start=1):
        sprite = Image.open(RIGHT_WALK / filename).convert("RGBA")
        frame = runtime_frame(action.place_sprite(sprite, 0))
        frame.save(RESOURCES / f"walk-square-right-{index}.png", optimize=True)


def save_struggle_frames() -> None:
    """Normalize the four lifted poses without stretching their proportions."""
    sprites = [Image.open(STRUGGLE / filename).convert("RGBA") for filename in STRUGGLE_NAMES]
    boxes = [sprite.getchannel("A").getbbox() for sprite in sprites]
    if any(box is None for box in boxes):
        raise ValueError("A struggle frame contains no visible pixels")

    widths = [box[2] - box[0] for box in boxes if box is not None]
    heights = [box[3] - box[1] for box in boxes if box is not None]
    scale = min((RUNTIME_SIZE[0] - 36) / max(widths), (RUNTIME_SIZE[1] - 36) / max(heights))

    for old_frame in RESOURCES.glob("struggle-*.png"):
        old_frame.unlink()
    for index, (sprite, box) in enumerate(zip(sprites, boxes), start=1):
        assert box is not None
        crop = sprite.crop(box)
        crop = crop.resize(
            (round(crop.width * scale), round(crop.height * scale)),
            Image.Resampling.LANCZOS,
        )
        frame = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
        frame.alpha_composite(
            crop,
            ((RUNTIME_SIZE[0] - crop.width) // 2, (RUNTIME_SIZE[1] - crop.height) // 2),
        )
        frame.save(RESOURCES / f"struggle-{index:02d}.png", optimize=True)


def save_meditate_frames() -> None:
    """Copy the approved 24-frame pause loop into the app's square canvas."""
    source_frames = sorted(MEDITATE.glob("meditate-joshua-*.png"))
    if len(source_frames) != 24:
        raise ValueError(f"Expected 24 meditation frames, found {len(source_frames)}")

    for old_frame in RESOURCES.glob("meditate-*.png"):
        old_frame.unlink()
    for index, source_path in enumerate(source_frames, start=1):
        frame = Image.open(source_path).convert("RGBA")
        runtime_frame(frame).save(RESOURCES / f"meditate-{index:02d}.png", optimize=True)


def save_pause_transition_frames() -> None:
    """Copy the approved 10-frame pause-entry animation into app resources."""
    source_frames = sorted(PAUSE_TRANSITION.glob("pause-transition-*.png"))
    if len(source_frames) != 10:
        raise ValueError(f"Expected 10 pause transition frames, found {len(source_frames)}")

    for old_frame in RESOURCES.glob("pause-transition-*.png"):
        old_frame.unlink()
    for index, source_path in enumerate(source_frames, start=1):
        frame = Image.open(source_path).convert("RGBA")
        runtime_frame(frame).save(RESOURCES / f"pause-transition-{index:02d}.png", optimize=True)


def save_resume_transition_frames() -> None:
    """Copy the approved 8-frame spring-up animation into app resources."""
    source_frames = sorted(RESUME_TRANSITION.glob("resume-transition-*.png"))
    if len(source_frames) != 8:
        raise ValueError(f"Expected 8 resume transition frames, found {len(source_frames)}")

    for old_frame in RESOURCES.glob("resume-transition-*.png"):
        old_frame.unlink()
    for index, source_path in enumerate(source_frames, start=1):
        frame = Image.open(source_path).convert("RGBA")
        runtime_frame(frame).save(RESOURCES / f"resume-transition-{index:02d}.png", optimize=True)


def save_stumble_frames() -> None:
    """Copy the five-frame walking stumble into app resources."""
    source_frames = sorted(STUMBLE.glob("stumble-*.png"))
    if len(source_frames) != 9:
        raise ValueError(f"Expected 9 stumble frames, found {len(source_frames)}")

    for old_frame in RESOURCES.glob("stumble-*.png"):
        old_frame.unlink()
    for index, source_path in enumerate(source_frames, start=1):
        frame = Image.open(source_path).convert("RGBA")
        runtime_frame(frame).save(RESOURCES / f"stumble-{index:02d}.png", optimize=True)


def build_action_frames() -> list[Image.Image]:
    side = Image.open(RIGHT_WALK / WALK_NAMES[3]).convert("RGBA")
    base, hand = action.load_spin_layers()
    staff, staff_pivot = action.make_staff()
    front_ready = action.held_staff_frame(base, hand, staff, staff_pivot, 90)

    enter = [
        action.place_sprite(side, 0),
        action.place_sprite(side, 42),
        action.place_sprite(side, 82),
        action.lift_frame(front_ready, 82),
        action.lift_frame(front_ready, 38),
        action.lift_frame(front_ready, 0),
    ]
    spin_once = [
        action.spin_frame(
            base,
            hand,
            staff,
            staff_pivot,
            angle,
            0.45 if index == 0 else 1.0,
        )
        for index, angle in enumerate(action.SPIN_ANGLES)
    ]
    spin = spin_once + spin_once
    # Hold the recognizable vertical angle briefly, then reverse the hop so the
    # last frame exactly matches the right-walk cycle's fourth frame.
    exit_frames = [
        action.lift_frame(front_ready, 0),
        action.lift_frame(front_ready, 38),
        action.lift_frame(front_ready, 82),
        action.place_sprite(side, 82),
        action.place_sprite(side, 42),
        action.place_sprite(side, 0),
    ]
    return enter + spin + [spin_once[0]] + exit_frames


def save_action_frames() -> None:
    frames = build_action_frames()
    for old_frame in RESOURCES.glob("action-*.png"):
        old_frame.unlink()
    for index, frame in enumerate(frames, start=1):
        runtime_frame(frame).save(RESOURCES / f"action-{index:02d}.png", optimize=True)
    print(f"Wrote {len(frames)} two-turn action frames and 4 walk frames to {RESOURCES}")


def main() -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)
    save_walk_frames()
    save_struggle_frames()
    save_meditate_frames()
    save_pause_transition_frames()
    save_resume_transition_frames()
    save_stumble_frames()
    save_action_frames()


if __name__ == "__main__":
    main()
