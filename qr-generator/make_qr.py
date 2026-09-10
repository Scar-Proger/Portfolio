#!/usr/bin/env python3
"""
styled_qr.py — генерирует QR-код в стиле референса:
тёмный фон, скруглённые "капли"-модули, скруглённые квадраты-маркеры
в углах, кружок с PNG-логотипом по центру.

Зависимости: reportlab + Pillow.
    pip install reportlab pillow

Запуск:
    python styled_qr.py
"""

import math

from PIL import Image, ImageDraw

from reportlab.graphics.barcode.qr import QrCodeWidget

# ============================== НАСТРОЙКИ ==============================

LINK = "mailto:anton.code@gmail.com"

LOGO_PNG_PATH = "email.png"      # прозрачный контур конверта без круга
OUTPUT_PATH = "../img/email-qr.png"

BG_COLOR = (26, 8, 8)          # тёмно-бордовый фон
MODULE_COLOR = (224, 164, 92)  # оранжево-песочный цвет модулей
LOGO_CIRCLE_COLOR = MODULE_COLOR
LOGO_ICON_COLOR = BG_COLOR

BOX = 40            # размер одного модуля в пикселях
BORDER = 3          # "тихие" модули по краям
LOGO_SCALE = 0.26   # доля ширины QR под кружок с логотипом
HOLE_MARGIN = 1.22  # во сколько раз пустая зона под логотип шире кружка

# =======================================================================


def get_matrix(link: str):
    w = QrCodeWidget(link, barLevel="H")
    w.qr.make()
    n = w.qr.getModuleCount()
    matrix = [[bool(v) for v in row] for row in w.qr.modules]
    return matrix, n


def is_finder_area(r, c, n):
    """True, если модуль (r,c) относится к одному из 3-х угловых маркеров 7x7."""
    def in_corner(r0, c0):
        return r0 <= r < r0 + 7 and c0 <= c < c0 + 7
    return in_corner(0, 0) or in_corner(0, n - 7) or in_corner(n - 7, 0)


def draw_finder_eye(draw, x0, y0, size):
    """Скруглённый 'глаз' маркера: внешний квадрат + внутренняя точка."""
    outer_r = size * 0.28
    inner_pad = size * 0.16
    dot_pad = size * 0.32

    draw.rounded_rectangle(
        [x0, y0, x0 + size, y0 + size], radius=outer_r, fill=MODULE_COLOR
    )
    draw.rounded_rectangle(
        [x0 + inner_pad, y0 + inner_pad, x0 + size - inner_pad, y0 + size - inner_pad],
        radius=outer_r * 0.6,
        fill=BG_COLOR,
    )
    draw.rounded_rectangle(
        [x0 + dot_pad, y0 + dot_pad, x0 + size - dot_pad, y0 + size - dot_pad],
        radius=outer_r * 0.5,
        fill=MODULE_COLOR,
    )


def draw_blob_module(draw, x0, y0, box, neighbors):
    """Модуль как скруглённый прямоугольник, сливающийся с соседями."""
    up, down, left, right = neighbors
    r = box * 0.5

    tl = r if not (up or left) else 0
    tr = r if not (up or right) else 0
    br = r if not (down or right) else 0
    bl = r if not (down or left) else 0

    x1, y1 = x0 + box, y0 + box
    _draw_variable_round_rect(draw, x0, y0, x1, y1, r, tl, tr, br, bl)


def _draw_variable_round_rect(draw, x0, y0, x1, y1, r, tl, tr, br, bl):
    draw.rectangle([x0, y0, x1, y1], fill=MODULE_COLOR)
    if tl > 0:
        draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=BG_COLOR)
        draw.rectangle([x0, y0, x0 + r, y0 + r], fill=BG_COLOR)
        draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=MODULE_COLOR)
    if tr > 0:
        draw.rectangle([x1 - r, y0, x1, y0 + r], fill=BG_COLOR)
        draw.pieslice([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=MODULE_COLOR)
    if br > 0:
        draw.rectangle([x1 - r, y1 - r, x1, y1], fill=BG_COLOR)
        draw.pieslice([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=MODULE_COLOR)
    if bl > 0:
        draw.rectangle([x0, y1 - r, x0 + r, y1], fill=BG_COLOR)
        draw.pieslice([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=MODULE_COLOR)


def load_logo(px_size: int) -> Image.Image:
    """Просто загружает PNG и ресайзит. Без перекраски."""
    logo = Image.open(LOGO_PNG_PATH).convert("RGBA")
    logo = logo.resize((px_size, px_size), Image.LANCZOS)
    return logo

def main():
    matrix, n = get_matrix(LINK)
    total = n + BORDER * 2
    img_size = total * BOX
    img = Image.new("RGB", (img_size, img_size), BG_COLOR)
    draw = ImageDraw.Draw(img)

    logo_px = int(img_size * LOGO_SCALE)
    hole_radius_px = (logo_px / 2) * HOLE_MARGIN
    center_px = img_size / 2

    def module_center_px(r, c):
        x0 = (c + BORDER) * BOX
        y0 = (r + BORDER) * BOX
        return x0 + BOX / 2, y0 + BOX / 2

    def in_hole(r, c):
        mx, my = module_center_px(r, c)
        return math.hypot(mx - center_px, my - center_px) <= hole_radius_px

    def dark(r, c):
        if r < 0 or c < 0 or r >= n or c >= n:
            return False
        if in_hole(r, c):
            return False
        return matrix[r][c]

    for r in range(n):
        for c in range(n):
            if not matrix[r][c]:
                continue
            if is_finder_area(r, c, n):
                continue
            if in_hole(r, c):
                continue
            x0 = (c + BORDER) * BOX
            y0 = (r + BORDER) * BOX
            neighbors = (dark(r - 1, c), dark(r + 1, c), dark(r, c - 1), dark(r, c + 1))
            draw_blob_module(draw, x0, y0, BOX, neighbors)

    # маркеры — 3 угла
    finder_size = 7 * BOX
    draw_finder_eye(draw, BORDER * BOX, BORDER * BOX, finder_size)
    draw_finder_eye(draw, (BORDER + n - 7) * BOX, BORDER * BOX, finder_size)
    draw_finder_eye(draw, BORDER * BOX, (BORDER + n - 7) * BOX, finder_size)

    # логотип — просто PNG по центру, без круга
    logo = load_logo(logo_px)
    pos = (int(center_px - logo_px / 2), int(center_px - logo_px / 2))
    img.paste(logo, pos, logo)

    img.save(OUTPUT_PATH, "PNG")
    print(f"Готово: {OUTPUT_PATH}")
    print(f"Ссылка: {LINK}")


if __name__ == "__main__":
    main()