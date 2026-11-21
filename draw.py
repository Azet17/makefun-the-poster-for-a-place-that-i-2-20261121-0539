#!/usr/bin/env python3
"""Procedurally draw a vintage travel poster for VELMARIS,
an invented place where the sea falls upward.
Renders 768x1024 PNG to entry.png next to this file."""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 768, 1024
random.seed(20261121)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def font(path, size):
    return ImageFont.truetype(path, size)


def sky_gradient(draw):
    # dusk: deep teal top -> coral peach horizon
    stops = [(8, 32, 58), (18, 74, 96), (64, 110, 122), (214, 138, 92), (246, 190, 120)]
    for y in range(H):
        t = y / H
        seg = min(int(t * (len(stops) - 1)), len(stops) - 2)
        ft = t * (len(stops) - 1) - seg
        draw.line([(0, y), (W, y)], fill=lerp(stops[seg], stops[seg + 1], ft))


def draw_sun(img, draw):
    # low, large sun just above the horizon, with glow
    cx, cy, r = W // 2 + 60, 600, 80
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(4, 0, -1):
        gd.ellipse([cx - r * i * 0.45, cy - r * i * 0.45,
                    cx + r * i * 0.45, cy + r * i * 0.45],
                   fill=(255, 190, 110, 14))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow), (0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 130))
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
                 fill=(255, 228, 160))
    # sun rays
    for k in range(24):
        a = math.radians(k * 15)
        x1 = cx + math.cos(a) * (r + 8)
        y1 = cy + math.sin(a) * (r + 8)
        x2 = cx + math.cos(a) * (r + 34)
        y2 = cy + math.sin(a) * (r + 34)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 214, 130), width=3)


def draw_sea(draw):
    # sea band with sun glitter path
    horizon = 700
    for y in range(horizon, H):
        t = (y - horizon) / (H - horizon)
        draw.line([(0, y), (W, y)], fill=lerp((214, 138, 92), (10, 38, 62), t))
    # glitter: horizontal strokes narrowing toward the sun, kept clear
    # of the bottom invitation line
    for i in range(90):
        yy = horizon + 8 + random.random() * (900 - horizon - 8)
        spread = 40 + (yy - horizon) * 0.55
        xx = W // 2 + 60 + (random.random() - 0.5) * 2 * spread
        ln = 8 + random.random() * 26
        alpha = random.random()
        col = (255, 220, 150) if alpha > 0.6 else (255, 180, 120)
        draw.line([(xx, yy), (xx + ln, yy)], fill=col, width=2)


def draw_islands(draw):
    # two floating islets with waterfalls that fall UPWARD into the sky
    def islet(cx, cy, rx, ry, color):
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)
        # rocky underside: tapering wedge below
        draw.polygon([(cx - rx + 12, cy + ry * 0.4), (cx + rx - 12, cy + ry * 0.4),
                      (cx + rx * 0.25, cy + ry + 95), (cx - rx * 0.15, cy + ry + 110)],
                     fill=(38, 52, 58))
        # pine silhouettes on top
        for k in range(5):
            px = cx - rx + 18 + k * (2 * rx - 36) / 4
            ph = 22 + (k % 3) * 8
            draw.polygon([(px, cy - ry - ph), (px - 9, cy - ry + 4),
                          (px + 9, cy - ry + 4)], fill=(16, 46, 40))

    islet(180, 470, 120, 42, (24, 62, 52))
    islet(560, 380, 95, 34, (28, 70, 58))
    islet(430, 300, 62, 24, (34, 80, 66))
    # upward waterfalls: pale ribbons curving from sea toward the islets
    for (x0, y0, x1, y1, wdt) in [(150, 700, 180, 500, 10),
                                  (210, 700, 185, 512, 7),
                                  (585, 700, 560, 410, 9),
                                  (450, 700, 430, 330, 6)]:
        pts = []
        for s in range(21):
            t = s / 20
            x = x0 + (x1 - x0) * t + math.sin(t * math.pi) * 26
            y = y0 + (y1 - y0) * t
            pts.append((x, y))
        draw.line(pts, fill=(214, 240, 244), width=wdt)
        draw.line(pts, fill=(255, 255, 255), width=3)


def draw_birds(draw):
    for (bx, by, s) in [(120, 180, 14), (170, 150, 11), (620, 210, 13), (660, 170, 10)]:
        draw.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340, fill=(20, 40, 48), width=3)
        draw.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340, fill=(20, 40, 48), width=3)


def draw_border(draw):
    draw.rectangle([18, 18, W - 18, H - 18], outline=(250, 232, 190), width=4)
    draw.rectangle([30, 30, W - 30, H - 30], outline=(250, 232, 190), width=2)


def draw_text(draw):
    cream = (250, 232, 190)
    # place name, big serif, top centre
    name = "VELMARIS"
    f_name = font(SERIF_BOLD, 96)
    bbox = draw.textbbox((0, 0), name, font=f_name)
    nw = bbox[2] - bbox[0]
    draw.text(((W - nw) / 2 - bbox[0], 62), name, font=f_name, fill=cream)
    # thin rule under the name
    draw.line([(W // 2 - 150, 178), (W // 2 + 150, 178)], fill=cream, width=2)
    # tagline
    tag = "WHERE THE SEA FALLS UPWARD"
    f_tag = font(SANS_BOLD, 25)
    bbox = draw.textbbox((0, 0), tag, font=f_tag)
    tw = bbox[2] - bbox[0]
    # letter-spaced tagline
    x = (W - tw) / 2 - bbox[0]
    draw.text((x, 196), tag, font=f_tag, fill=(255, 214, 130))
    # bottom line: invitation, small caps
    bottom = "COME AND SEE THE TIDE CLIMB THE SKY"
    f_bot = font(SANS, 22)
    bbox = draw.textbbox((0, 0), bottom, font=f_bot)
    bw = bbox[2] - bbox[0]
    draw.text(((W - bw) / 2 - bbox[0], 946), bottom, font=f_bot, fill=cream)


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    sky_gradient(draw)
    draw_sun(img, draw)
    draw = ImageDraw.Draw(img)
    draw_islands(draw)
    draw_sea(draw)
    draw_birds(draw)
    draw_border(draw)
    draw_text(draw)
    # gentle vignette via blur of a dark edge mask is skipped; keep crisp
    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
