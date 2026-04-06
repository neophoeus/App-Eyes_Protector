from __future__ import annotations

import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
ICON_PATH = ASSETS_DIR / "eyes_protector.ico"
VERSION_INFO_PATH = ASSETS_DIR / "windows_version_info.txt"

VERSION = "v2.0"
FILE_VERSION_TUPLE = (2, 0, 0, 0)

OUTPUT_SIZE = 256
SCALE = 4
CANVAS_SIZE = OUTPUT_SIZE * SCALE

TRANSPARENT = (0, 0, 0, 0)
WIDGET_BG = (232, 245, 233, 255)
WIDGET_BORDER = (165, 214, 167, 255)
EYE_COLOR = (44, 62, 80, 255)
HIGHLIGHT = (255, 255, 255, 255)


def blend_pixel(buffer: bytearray, width: int, x: int, y: int, color: tuple[int, int, int, int]):
    if x < 0 or y < 0 or x >= width:
        return
    height = len(buffer) // (width * 4)
    if y >= height:
        return
    index = ((y * width) + x) * 4
    src_r, src_g, src_b, src_a = color
    if src_a <= 0:
        return
    dst_r = buffer[index]
    dst_g = buffer[index + 1]
    dst_b = buffer[index + 2]
    dst_a = buffer[index + 3]
    inv_a = 255 - src_a
    out_a = src_a + ((dst_a * inv_a + 127) // 255)
    if out_a <= 0:
        return
    src_r_p = src_r * src_a
    src_g_p = src_g * src_a
    src_b_p = src_b * src_a
    dst_r_p = dst_r * dst_a
    dst_g_p = dst_g * dst_a
    dst_b_p = dst_b * dst_a
    out_r_p = src_r_p + ((dst_r_p * inv_a + 127) // 255)
    out_g_p = src_g_p + ((dst_g_p * inv_a + 127) // 255)
    out_b_p = src_b_p + ((dst_b_p * inv_a + 127) // 255)
    buffer[index] = out_r_p // out_a
    buffer[index + 1] = out_g_p // out_a
    buffer[index + 2] = out_b_p // out_a
    buffer[index + 3] = out_a


def fill_circle(buffer: bytearray, width: int, center_x: float, center_y: float, radius: float, color: tuple[int, int, int, int]):
    min_x = max(0, int(center_x - radius - 1))
    max_x = min(width - 1, int(center_x + radius + 1))
    height = len(buffer) // (width * 4)
    min_y = max(0, int(center_y - radius - 1))
    max_y = min(height - 1, int(center_y + radius + 1))
    radius_sq = radius * radius
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            dx = (x + 0.5) - center_x
            dy = (y + 0.5) - center_y
            if (dx * dx) + (dy * dy) <= radius_sq:
                blend_pixel(buffer, width, x, y, color)


def fill_ellipse(buffer: bytearray, width: int, x1: float, y1: float, x2: float, y2: float, color: tuple[int, int, int, int]):
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    radius_x = max(1.0, (x2 - x1) / 2)
    radius_y = max(1.0, (y2 - y1) / 2)
    min_x = max(0, int(x1) - 1)
    max_x = min(width - 1, int(x2) + 1)
    height = len(buffer) // (width * 4)
    min_y = max(0, int(y1) - 1)
    max_y = min(height - 1, int(y2) + 1)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            norm_x = ((x + 0.5) - center_x) / radius_x
            norm_y = ((y + 0.5) - center_y) / radius_y
            if (norm_x * norm_x) + (norm_y * norm_y) <= 1.0:
                blend_pixel(buffer, width, x, y, color)


def point_inside_rounded_rect(x: float, y: float, x1: float, y1: float, x2: float, y2: float, radius: float) -> bool:
    if x1 + radius <= x <= x2 - radius or y1 + radius <= y <= y2 - radius:
        return x1 <= x <= x2 and y1 <= y <= y2
    corner_centers = (
        (x1 + radius, y1 + radius),
        (x2 - radius, y1 + radius),
        (x1 + radius, y2 - radius),
        (x2 - radius, y2 - radius),
    )
    for center_x, center_y in corner_centers:
        dx = x - center_x
        dy = y - center_y
        if (dx * dx) + (dy * dy) <= radius * radius:
            return True
    return False


def fill_rounded_rect(buffer: bytearray, width: int, x1: float, y1: float, x2: float, y2: float, radius: float, color: tuple[int, int, int, int]):
    min_x = max(0, int(x1))
    max_x = min(width - 1, int(x2))
    height = len(buffer) // (width * 4)
    min_y = max(0, int(y1))
    max_y = min(height - 1, int(y2))
    for y in range(min_y, max_y + 1):
        sample_y = y + 0.5
        for x in range(min_x, max_x + 1):
            sample_x = x + 0.5
            if point_inside_rounded_rect(sample_x, sample_y, x1, y1, x2, y2, radius):
                blend_pixel(buffer, width, x, y, color)


def sample_quadratic_bezier(points: list[tuple[float, float]], steps: int) -> list[tuple[float, float]]:
    (x0, y0), (x1, y1), (x2, y2) = points
    sampled = []
    for index in range(steps + 1):
        t = index / steps
        inv_t = 1 - t
        x = (inv_t * inv_t * x0) + (2 * inv_t * t * x1) + (t * t * x2)
        y = (inv_t * inv_t * y0) + (2 * inv_t * t * y1) + (t * t * y2)
        sampled.append((x, y))
    return sampled


def draw_polyline(buffer: bytearray, width: int, points: list[tuple[float, float]], stroke_width: float, color: tuple[int, int, int, int]):
    if len(points) < 2:
        return
    radius = max(1.0, stroke_width / 2)
    for start, end in zip(points, points[1:]):
        x1, y1 = start
        x2, y2 = end
        distance = max(abs(x2 - x1), abs(y2 - y1), 1.0)
        steps = max(1, int(distance / max(1.0, radius / 2)))
        for index in range(steps + 1):
            t = index / steps
            x = x1 + ((x2 - x1) * t)
            y = y1 + ((y2 - y1) * t)
            fill_circle(buffer, width, x, y, radius, color)


def relative_point(box: tuple[float, float, float, float], x_ratio: float, y_ratio: float) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return (x1 + ((x2 - x1) * x_ratio), y1 + ((y2 - y1) * y_ratio))


def downsample_rgba(buffer: bytearray, source_size: int, factor: int) -> bytes:
    target_size = source_size // factor
    output = bytearray(target_size * target_size * 4)
    block_area = factor * factor
    for out_y in range(target_size):
        for out_x in range(target_size):
            sum_alpha = 0
            sum_r_p = 0
            sum_g_p = 0
            sum_b_p = 0
            for src_y in range(out_y * factor, (out_y + 1) * factor):
                for src_x in range(out_x * factor, (out_x + 1) * factor):
                    index = ((src_y * source_size) + src_x) * 4
                    r = buffer[index]
                    g = buffer[index + 1]
                    b = buffer[index + 2]
                    a = buffer[index + 3]
                    sum_alpha += a
                    sum_r_p += r * a
                    sum_g_p += g * a
                    sum_b_p += b * a
            out_index = ((out_y * target_size) + out_x) * 4
            avg_alpha = sum_alpha // block_area
            if avg_alpha > 0 and sum_alpha > 0:
                output[out_index] = min(255, sum_r_p // sum_alpha)
                output[out_index + 1] = min(255, sum_g_p // sum_alpha)
                output[out_index + 2] = min(255, sum_b_p // sum_alpha)
                output[out_index + 3] = avg_alpha
            else:
                output[out_index:out_index + 4] = bytes(TRANSPARENT)
    return bytes(output)


def png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", crc)


def make_png(width: int, height: int, rgba: bytes) -> bytes:
    rows = []
    stride = width * 4
    for y in range(height):
        start = y * stride
        rows.append(b"\x00" + rgba[start:start + stride])
    compressed = zlib.compress(b"".join(rows), level=9)
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return signature + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", compressed) + png_chunk(b"IEND", b"")


def make_ico(png_data: bytes) -> bytes:
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack(
        "<BBBBHHII",
        0,
        0,
        0,
        0,
        1,
        32,
        len(png_data),
        6 + 16,
    )
    return header + entry + png_data


def build_eye_icon_rgba() -> bytes:
    buffer = bytearray(CANVAS_SIZE * CANVAS_SIZE * 4)

    outer_margin = CANVAS_SIZE * 0.08
    outer_radius = CANVAS_SIZE * 0.24
    border_width = CANVAS_SIZE * 0.038

    fill_rounded_rect(
        buffer,
        CANVAS_SIZE,
        outer_margin,
        outer_margin,
        CANVAS_SIZE - outer_margin,
        CANVAS_SIZE - outer_margin,
        outer_radius,
        WIDGET_BORDER,
    )
    fill_rounded_rect(
        buffer,
        CANVAS_SIZE,
        outer_margin + border_width,
        outer_margin + border_width,
        CANVAS_SIZE - outer_margin - border_width,
        CANVAS_SIZE - outer_margin - border_width,
        outer_radius - border_width,
        WIDGET_BG,
    )

    icon_box = (
        CANVAS_SIZE * 0.19,
        CANVAS_SIZE * 0.22,
        CANVAS_SIZE * 0.81,
        CANVAS_SIZE * 0.72,
    )
    stroke_width = CANVAS_SIZE * 0.034

    upper_curve = sample_quadratic_bezier(
        [
            relative_point(icon_box, 0.15, 0.55),
            relative_point(icon_box, 0.50, 0.25),
            relative_point(icon_box, 0.85, 0.55),
        ],
        steps=64,
    )
    lower_curve = sample_quadratic_bezier(
        [
            relative_point(icon_box, 0.15, 0.55),
            relative_point(icon_box, 0.50, 0.85),
            relative_point(icon_box, 0.85, 0.55),
        ],
        steps=64,
    )
    draw_polyline(buffer, CANVAS_SIZE, upper_curve, stroke_width, EYE_COLOR)
    draw_polyline(buffer, CANVAS_SIZE, lower_curve, stroke_width, EYE_COLOR)

    pupil_top_left = relative_point(icon_box, 0.38, 0.40)
    pupil_bottom_right = relative_point(icon_box, 0.62, 0.66)
    fill_ellipse(
        buffer,
        CANVAS_SIZE,
        pupil_top_left[0],
        pupil_top_left[1],
        pupil_bottom_right[0],
        pupil_bottom_right[1],
        EYE_COLOR,
    )

    highlight_top_left = relative_point(icon_box, 0.47, 0.45)
    highlight_bottom_right = relative_point(icon_box, 0.56, 0.54)
    fill_ellipse(
        buffer,
        CANVAS_SIZE,
        highlight_top_left[0],
        highlight_top_left[1],
        highlight_bottom_right[0],
        highlight_bottom_right[1],
        HIGHLIGHT,
    )

    eyelash_pairs = [
        (relative_point(icon_box, 0.25, 0.46), relative_point(icon_box, 0.17, 0.36)),
        (relative_point(icon_box, 0.35, 0.40), relative_point(icon_box, 0.29, 0.28)),
        (relative_point(icon_box, 0.50, 0.37), relative_point(icon_box, 0.50, 0.23)),
        (relative_point(icon_box, 0.65, 0.40), relative_point(icon_box, 0.71, 0.28)),
        (relative_point(icon_box, 0.75, 0.46), relative_point(icon_box, 0.83, 0.36)),
    ]
    eyelash_width = CANVAS_SIZE * 0.026
    for start, end in eyelash_pairs:
        draw_polyline(buffer, CANVAS_SIZE, [start, end], eyelash_width, EYE_COLOR)

    return downsample_rgba(buffer, CANVAS_SIZE, SCALE)


def write_icon() -> None:
    rgba = build_eye_icon_rgba()
    png_data = make_png(OUTPUT_SIZE, OUTPUT_SIZE, rgba)
    ICON_PATH.write_bytes(make_ico(png_data))


def write_version_info() -> None:
    version_info = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={FILE_VERSION_TUPLE},
    prodvers={FILE_VERSION_TUPLE},
    mask=0x3F,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'App-Eyes Protector'),
          StringStruct('FileDescription', 'App-Eyes Protector'),
          StringStruct('FileVersion', '{VERSION}'),
          StringStruct('InternalName', 'EyesProtector'),
          StringStruct('OriginalFilename', 'EyesProtector.exe'),
          StringStruct('ProductName', 'App-Eyes Protector'),
          StringStruct('ProductVersion', '{VERSION}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    VERSION_INFO_PATH.write_text(version_info, encoding="utf-8")


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    write_icon()
    write_version_info()
    print(f"Generated {ICON_PATH}")
    print(f"Generated {VERSION_INFO_PATH}")


if __name__ == "__main__":
    main()