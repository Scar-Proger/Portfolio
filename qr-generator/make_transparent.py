#!/usr/bin/env python3
"""
remove_bg.py — удаляет фон с PNG, делая его прозрачным.

Использование:
    python remove_bg.py вход.png выход.png
    python remove_bg.py email-qr.png qr_no_bg.png

Или отредактируй INPUT_PATH / OUTPUT_PATH ниже и просто запусти.
"""

from PIL import Image

# ============ НАСТРОЙКИ ============
INPUT_PATH  = "bash.webp"
OUTPUT_PATH = "qr_no_bg.png"

# Цвет фона, который надо удалить (RGB). 
# Примеры:
#   белый          → (255, 255, 255)
#   тёмно-бордовый → (58, 15, 20)
#   чёрный         → (0, 0, 0)
BG_TO_REMOVE = (0, 0, 0)

# Насколько "похожим" должен быть пиксель на фон, чтобы удалиться.
# 0   — только точное совпадение цвета
# 30  — небольшие отклонения (сглаживание, артефакты)
# 60  — сильные отклонения (риск задеть нужное)
TOLERANCE = 30
# ===================================


def remove_background(input_path, output_path, bg_color, tolerance):
    img = Image.open(input_path).convert("RGBA")
    px = img.load()
    w, h = img.size

    br, bg, bb = bg_color

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]

            # Насколько пиксель близок к цвету фона
            dr = abs(r - br)
            dg = abs(g - bg)
            db = abs(b - bb)

            if dr <= tolerance and dg <= tolerance and db <= tolerance:
                # Совпадает с фоном → делаем прозрачным
                px[x, y] = (r, g, b, 0)
            else:
                # Оставляем как есть
                px[x, y] = (r, g, b, a)

    img.save(output_path, "PNG")
    print(f"Готово: {output_path}")
    print(f"Удалён цвет: RGB{bg_color}, допуск: {tolerance}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        in_path = sys.argv[1]
        out_path = sys.argv[2]
    else:
        in_path = INPUT_PATH
        out_path = OUTPUT_PATH

    remove_background(in_path, out_path, BG_TO_REMOVE, TOLERANCE)