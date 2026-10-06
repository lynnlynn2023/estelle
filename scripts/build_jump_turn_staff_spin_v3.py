#!/usr/bin/env python3
"""Build a higher-frame-count hop-turn and true multi-angle staff spin."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SIDE_PATH = ROOT / "Assets/Actions/从左向右走/Sources/WalkV3/Right/04-right-leg-passing-staff-back.png"
FRONT_PATH = ROOT / "Assets/Actions/原地转棍/Sources/StaffTwirlV1/01-ready-vertical.png"
SOURCE_OUT = ROOT / "Assets/Actions/原地转棍/Generated/StaffTwirlV3"
PREVIEW_OUT = ROOT / "Assets/Actions/原地转棍/Preview"
SOURCE_OUT.mkdir(parents=True, exist_ok=True)
PREVIEW_OUT.mkdir(parents=True, exist_ok=True)

CANVAS = (1500, 1500)
SPRITE_OFFSET = (147, 100)
GROUND_Y = 1406
PIVOT_LOCAL = (404, 580)
PIVOT = (SPRITE_OFFSET[0] + PIVOT_LOCAL[0], SPRITE_OFFSET[1] + PIVOT_LOCAL[1])
SPIN_ANGLES = [90, 135, 180, 225, 270, 315, 360, 405]


def line_geometry(size: tuple[int, int], start: tuple[float, float], end: tuple[float, float]):
    width, height = size
    yy, xx = np.mgrid[0:height, 0:width]
    points = np.stack([xx, yy], axis=-1)
    p0 = np.asarray(start, dtype=float)
    p1 = np.asarray(end, dtype=float)
    vector = p1 - p0
    t = np.clip(((points - p0) * vector).sum(axis=-1) / (vector @ vector), 0, 1)
    projection = p0 + t[..., None] * vector
    distance = np.linalg.norm(points - projection, axis=-1)
    return t, distance


def remove_reference_staff(image: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Remove the diagonal reference staff while retaining a hand overlay."""
    rgba = np.asarray(image.convert("RGBA")).copy()
    height, width = rgba.shape[:2]
    t, distance = line_geometry((width, height), (316, 35), (463, 1184))
    red, green, blue = [rgba[:, :, index].astype(float) for index in range(3)]
    alpha = rgba[:, :, 3]
    yy, xx = np.mgrid[0:height, 0:width]

    # A full geometric corridor is more reliable than color selection here: it
    # removes the shaft, both silver caps, antialiasing, and their dark outlines.
    mask = ((distance < 73) & (t >= 0) & (t <= 1)).astype(np.uint8) * 255
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)
    mask_bool = mask > 0

    inpainted = cv2.inpaint(rgba[:, :, :3], mask, 7, cv2.INPAINT_TELEA)
    base = rgba.copy()
    base[:, :, :3] = inpainted
    base_alpha = base[:, :, 3]
    base_alpha[mask_bool] = 0

    # The vertical staff overlaps the left twin-tail. Reconstruct that narrow
    # strip from the matching right twin-tail rather than painting a flat patch.
    mirror_x = np.clip(1300 - xx, 0, width - 1)
    mirrored = rgba[yy, mirror_x]
    mr, mg, mb = [mirrored[:, :, index].astype(float) for index in range(3)]
    mirrored_hair = (
        (mirrored[:, :, 3] > 0)
        & (mr > 125)
        & (mg > 70)
        & (mg < 185)
        & (mb < 120)
        & (mr > mg * 1.25)
        & (mr < mg * 2.45)
    )
    hair_fill = mask_bool & mirrored_hair & (yy > 210) & (yy < 980)
    base[hair_fill, :3] = mirrored[hair_fill, :3]
    base_alpha[hair_fill] = mirrored[hair_fill, 3]
    base[:, :, 3] = base_alpha
    base[base[:, :, 3] == 0, :3] = 0

    # Preserve the gloved gripping hand as a top layer above every rotated staff angle.
    hand = np.zeros_like(rgba)
    hand_region = (((xx - 404) / 104) ** 2 + ((yy - 580) / 105) ** 2) <= 1
    skin = (red > 185) & (green > 120) & (blue > 85)
    glove = (red > 105) & (green > 55) & (green < 175) & (blue < 115) & (red < green * 2.5)
    hand_core = ((skin | glove) & hand_region & (alpha > 0)).astype(np.uint8) * 255
    hand_mask = cv2.dilate(hand_core, np.ones((7, 7), np.uint8), iterations=1) > 0
    staff_red = (red > 65) & (green < 125) & (blue < 120) & (red > green * 1.35)
    hand_keep = hand_mask & hand_region & (alpha > 0) & ~staff_red
    hand[hand_keep] = rgba[hand_keep]
    hand_image = Image.fromarray(hand)
    glove_base = Image.new("RGBA", hand_image.size, (0, 0, 0, 0))
    glove_draw = ImageDraw.Draw(glove_base)
    glove_draw.rounded_rectangle(
        (362, 540, 450, 621),
        radius=26,
        fill=(166, 108, 58, 255),
        outline=(79, 47, 34, 255),
        width=5,
    )
    hand_image = Image.alpha_composite(glove_base, hand_image)
    return Image.fromarray(base), hand_image


def make_staff() -> tuple[Image.Image, tuple[int, int]]:
    """Render one reusable low-poly-style staff on a transparent layer."""
    scale = 3
    width, height = 1080, 150
    image = Image.new("RGBA", (width * scale, height * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def box(values):
        return tuple(round(value * scale) for value in values)

    def polygon(points, fill, outline=None, line_width=1):
        scaled = [(round(x * scale), round(y * scale)) for x, y in points]
        draw.polygon(scaled, fill=fill)
        if outline:
            draw.line(scaled + [scaled[0]], fill=outline, width=line_width * scale, joint="curve")

    # Dark outline and shaded red shaft.
    draw.rounded_rectangle(box((91, 55, 989, 95)), radius=13 * scale, fill=(71, 31, 33, 255))
    draw.rounded_rectangle(box((97, 59, 983, 91)), radius=10 * scale, fill=(147, 55, 62, 255))
    draw.rounded_rectangle(box((100, 62, 980, 74)), radius=6 * scale, fill=(183, 79, 78, 255))
    draw.line((110 * scale, 67 * scale, 970 * scale, 67 * scale), fill=(221, 132, 119, 170), width=2 * scale)

    # Silver collars and faceted tips.
    for left in (72, 82, 92):
        draw.rectangle(box((left, 49, left + 12, 101)), fill=(132, 139, 153, 255))
        draw.line((left * scale, 53 * scale, left * scale, 96 * scale), fill=(232, 237, 244, 230), width=2 * scale)
    for left in (976, 988, 1000):
        draw.rectangle(box((left, 49, left + 12, 101)), fill=(132, 139, 153, 255))
        draw.line((left * scale, 53 * scale, left * scale, 96 * scale), fill=(232, 237, 244, 230), width=2 * scale)

    polygon([(8, 75), (36, 40), (75, 50), (75, 100), (36, 110)], (184, 190, 202, 255), (82, 87, 99, 255), 3)
    polygon([(8, 75), (36, 40), (47, 75), (36, 110)], (226, 230, 237, 230))
    polygon([(1072, 75), (1044, 40), (1005, 50), (1005, 100), (1044, 110)], (184, 190, 202, 255), (82, 87, 99, 255), 3)
    polygon([(1072, 75), (1044, 40), (1033, 75), (1044, 110)], (226, 230, 237, 230))

    image = image.resize((width, height), Image.Resampling.LANCZOS)
    return image, (width // 2, height // 2)


def place_sprite(sprite: Image.Image, lift: int = 0) -> Image.Image:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    x = (CANVAS[0] - sprite.width) // 2
    y = GROUND_Y - sprite.height - lift
    canvas.alpha_composite(sprite, (x, y))
    return canvas


def staff_layer(staff: Image.Image, staff_pivot: tuple[int, int], angle: float) -> Image.Image:
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    x = round(PIVOT[0] - staff_pivot[0])
    y = round(PIVOT[1] - staff_pivot[1])
    canvas.alpha_composite(staff, (x, y))
    return canvas.rotate(angle, resample=Image.Resampling.BICUBIC, center=PIVOT, expand=False)


def tip_trails(angle: float, strength: float = 1.0) -> Image.Image:
    """Draw short arcs behind the two ends; never draw another staff."""
    glow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    crisp = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cd = ImageDraw.Draw(crisp)
    current = (-angle) % 360

    for tip_angle in (current, (current + 180) % 360):
        start = tip_angle
        end = tip_angle + 36
        for index, radial_offset in enumerate((-10, 0, 10)):
            radius = 513 + radial_offset
            box = (PIVOT[0] - radius, PIVOT[1] - radius, PIVOT[0] + radius, PIVOT[1] + radius)
            fade = strength * (1.0 - index * 0.16)
            gd.arc(box, start, end, fill=(186, 60, 49, round(100 * fade)), width=22)
            cd.arc(box, start + 3, end - 4, fill=(228, 117, 89, round(150 * fade)), width=8)
            cd.arc(box, start + 8, end - 10, fill=(255, 226, 183, round(165 * fade)), width=3)

    return Image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)), crisp)


def spin_frame(base: Image.Image, hand: Image.Image, staff: Image.Image, staff_pivot, angle: float, trail_strength: float) -> Image.Image:
    character = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    character.alpha_composite(base, SPRITE_OFFSET)
    hand_canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    hand_canvas.alpha_composite(hand, SPRITE_OFFSET)

    frame = Image.alpha_composite(character, tip_trails(angle, trail_strength))
    frame = Image.alpha_composite(frame, staff_layer(staff, staff_pivot, angle))
    return Image.alpha_composite(frame, hand_canvas)


def preview_background(frame: Image.Image, size=(960, 960)) -> Image.Image:
    canvas = Image.new("RGBA", size, "#242731")
    scale = min((size[0] - 12) / frame.width, (size[1] - 12) / frame.height)
    sprite = frame.resize((round(frame.width * scale), round(frame.height * scale)), Image.Resampling.LANCZOS)
    canvas.alpha_composite(sprite, ((size[0] - sprite.width) // 2, size[1] - sprite.height - 3))
    return canvas.convert("RGB")


def main() -> None:
    side = Image.open(SIDE_PATH).convert("RGBA")
    front = Image.open(FRONT_PATH).convert("RGBA")
    base, hand = remove_reference_staff(front)
    staff, staff_pivot = make_staff()

    base.save(SOURCE_OUT / "front-standing-without-staff.png")
    hand.save(SOURCE_OUT / "right-hand-overlay.png")
    staff.save(SOURCE_OUT / "staff-layer.png")

    transition_frames = [
        place_sprite(side, 0),
        place_sprite(side, 42),
        place_sprite(side, 82),
        place_sprite(front, 82),
        place_sprite(front, 38),
        place_sprite(front, 0),
    ]
    transition_durations = [250, 70, 70, 85, 85, 230]

    spin_frames = []
    for index, angle in enumerate(SPIN_ANGLES, start=1):
        strength = 0.45 if index == 1 else 1.0
        frame = spin_frame(base, hand, staff, staff_pivot, angle, strength)
        frame.save(SOURCE_OUT / f"spin-{index:02d}-{angle:+04d}deg.png")
        spin_frames.append(frame)

    frames = transition_frames + spin_frames + [spin_frames[0]]
    durations = transition_durations + [72] * len(spin_frames) + [260]
    stem = PREVIEW_OUT / "estelle-jump-turn-staff-spin-v3"

    frames[0].save(
        stem.with_suffix(".webp"),
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        lossless=True,
        method=4,
    )
    gif_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=255) for frame in frames]
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
    video_frames = []
    for frame, duration in zip(frames, durations):
        video_frames.extend([preview_background(frame)] * max(1, round(duration * fps / 1000)))
    writer = cv2.VideoWriter(
        str(stem.with_suffix(".mp4")),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        video_frames[0].size,
    )
    for _ in range(4):
        for frame in video_frames:
            writer.write(cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR))
    writer.release()

    for path in sorted(SOURCE_OUT.glob("spin-*.png")):
        print(path)
    for path in (stem.with_suffix(".gif"), stem.with_suffix(".webp"), stem.with_suffix(".mp4")):
        print(path)


if __name__ == "__main__":
    main()
