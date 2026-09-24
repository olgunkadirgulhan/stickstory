"""15 düz renkli vektör sahne. Her sahne W×H için zemin çizgisine (ground) göre yerleşir.

Sahneler rastgele renk tonu kaydırmasıyla çizilir (her video aynı görünmesin), sonra hafif
bulanıklaştırılıp kontrastı düşürülür; karakterler hep arka plandan net kalır.
"""
import colorsys
import math
import random

import cairo
import numpy as np
from PIL import Image, ImageFilter

from .rig import rrect

NAMES = ['kitchen', 'living_room', 'bedroom', 'classroom', 'hallway', 'office', 'street', 'park', 'supermarket',
         'restaurant', 'doctor', 'wedding', 'gym', 'bus_stop', 'backyard']


class Painter:
    def __init__(self, ctx, W, H, ground, rnd):
        self.c, self.W, self.H, self.g, self.r = ctx, W, H, ground, rnd
        self.hue = rnd.uniform(-0.04, 0.04)
        self.u = min(W, H) / 100.0  # ölçek birimi

    def col(self, rgb):
        h, l, s = colorsys.rgb_to_hls(*rgb)
        return colorsys.hls_to_rgb((h + self.hue) % 1, l, s)

    def rect(self, x, y, w, h, rgb, r=0, outline=True):
        c = self.c
        if r:
            rrect(c, x, y, w, h, r)
        else:
            c.rectangle(x, y, w, h)
        c.set_source_rgb(*self.col(rgb))
        if outline:
            c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(self.u * 0.35); c.stroke()
        else:
            c.fill()

    def circle(self, x, y, r, rgb, outline=True):
        c = self.c
        c.arc(x, y, r, 0, 2 * math.pi)
        c.set_source_rgb(*self.col(rgb))
        if outline:
            c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.35); c.set_line_width(self.u * 0.35); c.stroke()
        else:
            c.fill()

    def wall_floor(self, wall, floor, stripe=None):
        W, H, g = self.W, self.H, self.g
        self.rect(0, 0, W, g, wall, outline=False)
        if stripe:
            for x in np.arange(0, W, self.u * 9):
                self.rect(x, 0, self.u * 4.5, g, stripe, outline=False)
        self.rect(0, g - self.u * 20, W, self.u * 1.2, tuple(v * 0.9 for v in wall), outline=False)
        self.rect(0, g - self.u * 6, W, H - g + self.u * 6, floor, outline=False)
        self.rect(0, g - self.u * 6, W, self.u * 1.2, tuple(v * 0.8 for v in floor), outline=False)

    def sky(self, top, bottom):
        g = cairo.LinearGradient(0, 0, 0, self.g)
        g.add_color_stop_rgb(0, *self.col(top)); g.add_color_stop_rgb(1, *self.col(bottom))
        self.c.rectangle(0, 0, self.W, self.g); self.c.set_source(g); self.c.fill()

    def window(self, x, y, w, h, sky=(0.62, 0.85, 1.0)):
        u = self.u
        self.rect(x - u, y - u, w + 2 * u, h + 2 * u, (0.97, 0.97, 0.95), r=u)
        self.rect(x, y, w, h, sky, outline=False)
        self.circle(x + w * 0.3, y + h * 0.35, h * 0.12, (1, 1, 1), outline=False)
        self.circle(x + w * 0.42, y + h * 0.32, h * 0.15, (1, 1, 1), outline=False)
        self.rect(x + w / 2 - u * 0.6, y, u * 1.2, h, (0.97, 0.97, 0.95), outline=False)
        self.rect(x, y + h / 2 - u * 0.6, w, u * 1.2, (0.97, 0.97, 0.95), outline=False)

    def plant(self, x, base, s):
        u = self.u * s
        for a in (-0.6, -0.2, 0.2, 0.6):
            self.c.save(); self.c.translate(x, base - 7 * u); self.c.rotate(a)
            self.c.scale(1, 2.2); self.c.arc(0, -4 * u, 3 * u, 0, 2 * math.pi); self.c.restore()
            self.c.set_source_rgb(*self.col((0.3, 0.7, 0.35))); self.c.fill()
        self.rect(x - 4 * u, base - 8 * u, 8 * u, 8 * u, (0.85, 0.45, 0.3), r=u)


def _xs(p, n):
    """Yatay yerleşim: n nesneyi genişliğe yay."""
    return [p.W * (i + 0.5) / n for i in range(n)]


def kitchen(p):
    u, g = p.u, p.g
    p.wall_floor((0.99, 0.93, 0.7), (0.8, 0.62, 0.45))
    for x in np.arange(0, p.W, u * 6):  # fayans
        for y in np.arange(g - u * 44, g - u * 26, u * 6):
            p.rect(x, y, u * 6, u * 6, (0.9, 0.96, 0.98), outline=True)
    p.window(p.W * 0.38, g - u * 70, u * 26, u * 20)
    p.rect(0, g - u * 26, p.W, u * 20, (0.55, 0.78, 0.8), outline=True)
    p.rect(0, g - u * 27.5, p.W, u * 3, (0.95, 0.95, 0.95))
    for x in np.arange(u * 2, p.W, u * 16):
        p.rect(x, g - u * 23, u * 13, u * 14, (0.6, 0.83, 0.85), r=u)
        p.circle(x + u * 6.5, g - u * 19, u * 0.9, (0.9, 0.9, 0.9))
    fx = p.W - u * 24
    p.rect(fx, g - u * 62, u * 20, u * 56, (0.94, 0.95, 0.97), r=u * 2)
    p.rect(fx, g - u * 42, u * 20, u * 0.8, (0.7, 0.7, 0.75), outline=False)
    p.rect(fx + u * 16, g - u * 56, u * 1.2, u * 9, (0.6, 0.6, 0.65), outline=False)
    for x in np.arange(u * 4, p.W * 0.33, u * 20):
        p.rect(x, g - u * 75, u * 17, u * 14, (0.55, 0.78, 0.8), r=u)


def living_room(p):
    u, g = p.u, p.g
    p.wall_floor((0.78, 0.9, 0.85), (0.72, 0.52, 0.38), stripe=(0.75, 0.88, 0.83))
    p.window(u * 6, g - u * 66, u * 24, u * 24)
    p.rect(p.W * 0.5 - u * 16, g - u * 72, u * 32, u * 20, (0.95, 0.85, 0.6), r=u)
    p.rect(p.W * 0.5 - u * 13, g - u * 69, u * 26, u * 14, (0.55, 0.75, 0.95), outline=False)
    p.circle(p.W * 0.5 - u * 3, g - u * 62, u * 4, (1, 0.9, 0.4), outline=False)
    # kanepe
    x0 = p.W * 0.18
    p.rect(x0, g - u * 30, p.W * 0.64, u * 16, (0.9, 0.45, 0.4), r=u * 3)
    p.rect(x0 - u * 3, g - u * 22, p.W * 0.64 + u * 6, u * 14, (0.85, 0.38, 0.35), r=u * 3)
    p.plant(p.W - u * 10, g - u * 4, 1.2)
    p.rect(p.W - u * 26, g - u * 50, u * 1.2, u * 44, (0.3, 0.3, 0.3), outline=False)
    p.circle(p.W - u * 25.4, g - u * 52, u * 6, (1, 0.9, 0.6))


def bedroom(p):
    u, g = p.u, p.g
    p.wall_floor((0.8, 0.82, 0.98), (0.65, 0.5, 0.42))
    p.window(p.W - u * 32, g - u * 70, u * 24, u * 22, sky=(0.2, 0.25, 0.5))
    p.circle(p.W - u * 14, g - u * 64, u * 3, (1, 1, 0.8), outline=False)
    p.rect(u * 8, g - u * 72, u * 16, u * 22, (1, 0.6, 0.3), r=u)
    p.circle(u * 16, g - u * 61, u * 5, (1, 0.95, 0.5), outline=False)
    p.rect(-u * 5, g - u * 32, p.W * 0.55, u * 22, (0.55, 0.38, 0.28), r=u * 2)
    p.rect(-u * 5, g - u * 26, p.W * 0.55, u * 12, (0.45, 0.65, 0.95), r=u * 2)
    p.rect(u * 2, g - u * 34, u * 16, u * 7, (1, 1, 1), r=u * 3)
    p.rect(p.W * 0.62, g - u * 22, u * 12, u * 16, (0.6, 0.42, 0.3), r=u)


def classroom(p):
    u, g = p.u, p.g
    p.wall_floor((0.98, 0.9, 0.75), (0.75, 0.6, 0.45))
    p.rect(p.W * 0.12, g - u * 74, p.W * 0.76, u * 30, (0.6, 0.45, 0.3), r=u)
    p.rect(p.W * 0.12 + u * 2, g - u * 72, p.W * 0.76 - u * 4, u * 26, (0.2, 0.42, 0.32), outline=False)
    c = p.c
    c.set_source_rgba(1, 1, 1, 0.8); c.set_line_width(u * 0.6)
    c.move_to(p.W * 0.2, g - u * 64); c.line_to(p.W * 0.45, g - u * 64)
    c.move_to(p.W * 0.2, g - u * 58); c.line_to(p.W * 0.38, g - u * 58); c.stroke()
    c.arc(p.W * 0.7, g - u * 60, u * 5, 0, 2 * math.pi); c.stroke()
    p.circle(p.W - u * 8, g - u * 82, u * 5, (1, 1, 1))
    for x in _xs(p, 3):
        p.rect(x - u * 10, g - u * 20, u * 20, u * 3, (0.85, 0.65, 0.4))
        p.rect(x - u * 8, g - u * 17, u * 1.5, u * 11, (0.4, 0.4, 0.45), outline=False)
        p.rect(x + u * 6.5, g - u * 17, u * 1.5, u * 11, (0.4, 0.4, 0.45), outline=False)


def hallway(p):
    u, g = p.u, p.g
    p.wall_floor((0.93, 0.93, 0.85), (0.7, 0.75, 0.8))
    x = u * 2
    cols = [(0.35, 0.6, 0.95), (0.95, 0.45, 0.45), (0.35, 0.6, 0.95), (0.95, 0.75, 0.3)]
    i = 0
    while x < p.W:
        p.rect(x, g - u * 62, u * 11, u * 56, cols[i % 4], r=u * 0.6)
        for k in range(3):
            p.rect(x + u * 2.5, g - u * 58 + k * u * 1.8, u * 6, u * 0.7, (0.2, 0.2, 0.25), outline=False)
        p.rect(x + u * 8.5, g - u * 38, u * 1, u * 5, (0.8, 0.8, 0.8), outline=False)
        x += u * 12.5; i += 1
    p.rect(0, g - u * 80, p.W, u * 14, (0.85, 0.85, 0.78), outline=False)


def office(p):
    u, g = p.u, p.g
    p.wall_floor((0.85, 0.9, 0.95), (0.55, 0.6, 0.68))
    p.rect(p.W * 0.15, g - u * 80, p.W * 0.7, u * 40, (0.7, 0.85, 1.0))
    for y in np.arange(g - u * 80, g - u * 40, u * 3):
        p.rect(p.W * 0.15, y, p.W * 0.7, u * 1.3, (0.95, 0.95, 0.95), outline=False)
    p.rect(u * 4, g - u * 24, p.W - u * 8, u * 3, (0.85, 0.7, 0.5))
    for x in _xs(p, 2):
        p.rect(x - u * 8, g - u * 38, u * 16, u * 11, (0.2, 0.22, 0.28), r=u)
        p.rect(x - u * 7, g - u * 37, u * 14, u * 9, (0.4, 0.75, 0.95), outline=False)
        p.rect(x - u * 1, g - u * 27, u * 2, u * 3, (0.3, 0.3, 0.3), outline=False)
    p.plant(u * 8, g - u * 4, 1.3)


def street(p):
    u, g = p.u, p.g
    p.sky((0.45, 0.75, 1.0), (0.8, 0.93, 1.0))
    x, i = -u * 5, 0
    cols = [(0.95, 0.6, 0.5), (0.6, 0.75, 0.95), (0.98, 0.85, 0.55), (0.7, 0.9, 0.7)]
    while x < p.W:
        w = u * p.r.uniform(22, 32); h = u * p.r.uniform(50, 85)
        p.rect(x, g - h, w, h, cols[i % 4])
        for wy in np.arange(g - h + u * 5, g - u * 20, u * 11):
            for wx in np.arange(x + u * 4, x + w - u * 6, u * 9):
                p.rect(wx, wy, u * 5, u * 6, (0.85, 0.95, 1.0))
        x += w + u * 2; i += 1
    p.rect(0, g - u * 8, p.W, u * 5, (0.8, 0.8, 0.8))
    p.rect(0, g - u * 3, p.W, p.H - g + u * 3, (0.45, 0.47, 0.52), outline=False)
    for x in np.arange(0, p.W, u * 18):
        p.rect(x, g + u * 12, u * 9, u * 1.5, (1, 1, 1), outline=False)


def park(p):
    u, g = p.u, p.g
    p.sky((0.5, 0.8, 1.0), (0.85, 0.95, 1.0))
    p.circle(p.W - u * 15, u * 15, u * 8, (1, 0.9, 0.4), outline=False)
    p.circle(p.W * 0.3, g - u * 20, p.W * 0.6, (0.55, 0.82, 0.45), outline=False)
    for x in (u * 10, p.W - u * 14, p.W * 0.55):
        p.rect(x - u * 2.5, g - u * 40, u * 5, u * 36, (0.55, 0.35, 0.22))
        p.circle(x, g - u * 46, u * 13, (0.3, 0.68, 0.35))
        p.circle(x - u * 8, g - u * 40, u * 9, (0.33, 0.72, 0.38))
    p.rect(0, g - u * 6, p.W, p.H - g + u * 6, (0.45, 0.78, 0.38), outline=False)
    p.rect(p.W * 0.3, g - u * 16, u * 30, u * 3, (0.75, 0.5, 0.3))
    p.rect(p.W * 0.3, g - u * 22, u * 30, u * 3, (0.75, 0.5, 0.3))


def supermarket(p):
    u, g = p.u, p.g
    p.wall_floor((0.95, 0.97, 0.95), (0.85, 0.87, 0.85))
    p.rect(0, u * 4, p.W, u * 8, (0.9, 0.25, 0.3), outline=False)
    for sx in (u * 3, p.W * 0.53):
        w = p.W * 0.44
        p.rect(sx, g - u * 70, w, u * 64, (0.75, 0.78, 0.82))
        for k in range(4):
            y = g - u * 66 + k * u * 15
            p.rect(sx, y + u * 11, w, u * 2, (0.6, 0.62, 0.66), outline=False)
            x = sx + u
            while x < sx + w - u * 5:
                bw = u * p.r.uniform(3, 6)
                col = p.r.choice([(0.95, 0.4, 0.35), (0.35, 0.65, 0.95), (1, 0.8, 0.3), (0.4, 0.8, 0.5), (0.9, 0.5, 0.8)])
                bh = u * p.r.uniform(6, 10)
                p.rect(x, y + u * 11 - bh, bw, bh, col)
                x += bw + u * 0.5


def restaurant(p):
    u, g = p.u, p.g
    p.wall_floor((0.62, 0.3, 0.3), (0.45, 0.3, 0.22), stripe=(0.58, 0.27, 0.27))
    for x in _xs(p, 3):
        p.rect(x - u * 0.3, 0, u * 0.6, u * 20, (0.2, 0.2, 0.2), outline=False)
        p.c.new_path(); p.c.arc(x, u * 24, u * 6, math.pi, 2 * math.pi); p.c.close_path()
        p.c.set_source_rgb(*p.col((0.95, 0.8, 0.4))); p.c.fill()
        p.circle(x, u * 25, u * 2, (1, 1, 0.8), outline=False)
        p.rect(x - u * 12, g - u * 22, u * 24, u * 3, (1, 1, 1))
        p.rect(x - u * 1, g - u * 19, u * 2, u * 13, (0.3, 0.2, 0.15), outline=False)
        p.circle(x - u * 4, g - u * 24, u * 2.5, (0.95, 0.95, 0.95))
    p.rect(p.W * 0.35, g - u * 72, p.W * 0.3, u * 20, (0.95, 0.85, 0.6), r=u)


def doctor(p):
    u, g = p.u, p.g
    p.wall_floor((0.85, 0.95, 0.97), (0.8, 0.85, 0.88))
    p.rect(u * 6, g - u * 70, u * 18, u * 24, (1, 1, 1))
    for k in range(5):
        p.rect(u * 9, g - u * 65 + k * u * 4, u * (12 - k * 2), u * 2, (0.2, 0.2, 0.2), outline=False)
    cx = p.W - u * 20
    p.rect(cx - u * 8, g - u * 76, u * 16, u * 16, (1, 1, 1), r=u * 2)
    p.rect(cx - u * 2, g - u * 73, u * 4, u * 10, (0.9, 0.2, 0.25), outline=False)
    p.rect(cx - u * 5, g - u * 70, u * 10, u * 4, (0.9, 0.2, 0.25), outline=False)
    p.rect(p.W * 0.3, g - u * 22, p.W * 0.4, u * 6, (0.4, 0.75, 0.8), r=u * 2)
    p.rect(p.W * 0.3, g - u * 23, p.W * 0.4, u * 2, (1, 1, 1))
    for x in (p.W * 0.32, p.W * 0.68 - u * 2):
        p.rect(x, g - u * 16, u * 2, u * 10, (0.7, 0.7, 0.75), outline=False)


def wedding(p):
    u, g = p.u, p.g
    p.wall_floor((1.0, 0.92, 0.94), (0.9, 0.85, 0.8))
    c = p.c
    for x in _xs(p, 3):
        c.new_path(); c.arc(x, g - u * 55, u * 13, math.pi, 2 * math.pi)
        c.set_source_rgb(*p.col((1, 1, 1))); c.set_line_width(u * 2.5); c.stroke()
        for a in np.linspace(math.pi, 2 * math.pi, 7):
            p.circle(x + u * 13 * math.cos(a), g - u * 55 + u * 13 * math.sin(a), u * 2.2,
                     p.r.choice([(1, 0.6, 0.7), (1, 1, 1), (0.95, 0.4, 0.55)]), outline=False)
    # pasta
    x = p.W / 2
    for k, (w, h) in enumerate(((22, 7), (16, 6), (10, 5))):
        y = g - u * 22 - sum(hh for _, hh in ((22, 7), (16, 6), (10, 5))[:k + 1]) * u
        p.rect(x - w * u / 2, y, w * u, h * u, (1, 0.97, 0.9), r=u)
    p.rect(x - u * 15, g - u * 22, u * 30, u * 2, (0.95, 0.95, 0.95))
    p.rect(x - u * 1, g - u * 20, u * 2, u * 14, (0.8, 0.8, 0.8), outline=False)


def gym(p):
    u, g = p.u, p.g
    p.wall_floor((0.35, 0.4, 0.5), (0.25, 0.25, 0.3))
    p.rect(p.W * 0.1, g - u * 72, p.W * 0.8, u * 40, (0.7, 0.8, 0.9))
    p.rect(p.W * 0.1 + u, g - u * 71, p.W * 0.8 - 2 * u, u * 38, (0.8, 0.88, 0.95), outline=False)
    p.rect(0, g - u * 82, p.W, u * 5, (0.95, 0.8, 0.2), outline=False)
    y = g - u * 16
    p.rect(u * 5, y, p.W - u * 10, u * 2.5, (0.6, 0.6, 0.65))
    for x in np.arange(u * 8, p.W - u * 8, u * 12):
        p.circle(x, y - u * 3, u * 3.5, (0.15, 0.15, 0.18))
        p.circle(x, y - u * 3, u * 1.2, (0.6, 0.6, 0.65), outline=False)


def bus_stop(p):
    u, g = p.u, p.g
    p.sky((0.95, 0.7, 0.5), (1.0, 0.9, 0.7))
    for x in np.arange(0, p.W, u * 26):
        h = u * p.r.uniform(30, 60)
        p.rect(x, g - h - u * 8, u * 24, h, (0.75, 0.65, 0.75), outline=False)
    p.rect(0, g - u * 8, p.W, p.H - g + u * 8, (0.55, 0.55, 0.6), outline=False)
    p.rect(0, g - u * 8, p.W, u * 4, (0.8, 0.8, 0.8))
    x = p.W * 0.12
    p.rect(x, g - u * 60, u * 2, u * 52, (0.3, 0.35, 0.4), outline=False)
    p.rect(x + p.W * 0.7, g - u * 60, u * 2, u * 52, (0.3, 0.35, 0.4), outline=False)
    p.rect(x - u * 2, g - u * 62, p.W * 0.7 + u * 6, u * 4, (0.2, 0.55, 0.85))
    c = p.c
    c.rectangle(x + u * 2, g - u * 58, p.W * 0.7 - u * 2, u * 38)
    c.set_source_rgba(0.8, 0.95, 1, 0.35); c.fill()
    p.rect(p.W - u * 14, g - u * 70, u * 1.5, u * 62, (0.3, 0.35, 0.4), outline=False)
    p.circle(p.W - u * 13.2, g - u * 72, u * 5, (1, 1, 1))
    p.circle(p.W - u * 13.2, g - u * 72, u * 3.5, (0.2, 0.55, 0.85), outline=False)


def backyard(p):
    u, g = p.u, p.g
    p.sky((0.45, 0.78, 1.0), (0.85, 0.95, 1.0))
    p.rect(0, g - u * 70, p.W * 0.45, u * 64, (0.98, 0.85, 0.6))
    p.c.new_path(); p.c.move_to(-u * 4, g - u * 70); p.c.line_to(p.W * 0.225, g - u * 90)
    p.c.line_to(p.W * 0.45 + u * 4, g - u * 70); p.c.close_path()
    p.c.set_source_rgb(*p.col((0.8, 0.3, 0.3))); p.c.fill()
    p.window(u * 6, g - u * 60, u * 14, u * 14)
    p.rect(p.W * 0.28, g - u * 36, u * 12, u * 30, (0.55, 0.35, 0.25))
    for x in np.arange(p.W * 0.47, p.W, u * 5):
        p.rect(x, g - u * 26, u * 4, u * 22, (1, 1, 1))
    p.rect(p.W * 0.47, g - u * 20, p.W, u * 2, (1, 1, 1), outline=False)
    p.rect(0, g - u * 6, p.W, p.H - g + u * 6, (0.5, 0.8, 0.4), outline=False)


DRAW = {n: globals()[n] for n in NAMES}


def render(name, W, H, ground, seed=0, blur=True):
    """cairo.ImageSurface döndürür (hafif bulanık, düşük kontrast)."""
    rnd = random.Random(seed)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    p = Painter(ctx, W, H, ground, rnd)
    DRAW.get(name, living_room)(p)
    # zemin altı: hafif gölge gradyanı
    g = cairo.LinearGradient(0, ground, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0); g.add_color_stop_rgba(1, 0, 0, 0, 0.18)
    ctx.rectangle(0, ground, W, H - ground); ctx.set_source(g); ctx.fill()
    surf.flush()
    arr = np.ndarray((H, W, 4), np.uint8, surf.get_data()).copy()
    img = Image.fromarray(arr[:, :, [2, 1, 0, 3]], 'RGBA').convert('RGB')
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(min(W, H) / 540))
    a = np.asarray(img).astype(np.float32)
    a = a * 0.86 + 255 * 0.1  # kontrastı düşür, açık tut
    return from_rgb(np.clip(a, 0, 255).astype(np.uint8))


def from_rgb(a):
    H, W = a.shape[:2]
    out = np.empty((H, W, 4), np.uint8)
    out[:, :, 0], out[:, :, 1], out[:, :, 2], out[:, :, 3] = a[:, :, 2], a[:, :, 1], a[:, :, 0], 255
    surf = cairo.ImageSurface.create_for_data(memoryview(out), cairo.FORMAT_ARGB32, W, H, W * 4)
    return surf
