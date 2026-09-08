from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from models.project import ProjectState


def generate_thumbnail(
    state: ProjectState,
    width: int = 1080,
    height: int = 1920,
) -> Path:
    if not state.script:
        raise ValueError("Script required for thumbnail")

    thumbnail_path = state.output_dir / "thumbnail.jpg"
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (width, height), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    title = state.script.title.upper()
    hook = state.script.hook

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        hook_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        hook_font = ImageFont.load_default()

    title_y = height // 3
    draw.text(
        (width // 2, title_y),
        title,
        fill=(255, 255, 255),
        font=title_font,
        anchor="mm",
    )

    hook_y = title_y + 120
    draw.text(
        (width // 2, hook_y),
        hook,
        fill=(200, 200, 200),
        font=hook_font,
        anchor="mm",
    )

    img.save(thumbnail_path, "JPEG", quality=90)
    state.thumbnail_path = thumbnail_path
    state.save()
    return thumbnail_path
