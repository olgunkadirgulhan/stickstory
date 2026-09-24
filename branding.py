"""Kanal görselleri: banner (2560x1440), profil (800x800), filigran (150x150) -> branding/

    python branding.py
"""
import math
import sys
from pathlib import Path

import cairo
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from stickstory import rig  # noqa: E402
from stickstory.render import pil_to_surface, text_block  # noqa: E402

OUT = HERE / 'branding'


def rays(ctx, W, H, cx, cy, c1, c2, n=18):
    ctx.set_source_rgb(*c1); ctx.paint()
    ctx.save(); ctx.translate(cx, cy)
    for i in range(n):
        a = i * 2 * math.pi / n
        ctx.move_to(0, 0); ctx.arc(0, 0, max(W, H) * 1.5, a, a + math.pi / n); ctx.close_path()
    ctx.set_source_rgb(*c2); ctx.fill(); ctx.restore()


def character(ctx, cid, x, ground, s, facing, emotion, pose, mouth='closed'):
    st = dict(rig.pose_targets(pose))
    st.update(emotion=emotion, mouth=mouth, t=0.2, breath=1.0, bend=st.get('bend', 'out'))
    if cid == 'mama_rose' and pose == 'fist':
        st['prop'] = 'slipper'
    rig.draw(ctx, cid, x, ground, s, facing, st)


def paste_text(ctx, words, size, cx, cy, maxw, color=(255, 255, 255)):
    surf = pil_to_surface(text_block(words, size, maxw, color=color, stroke_w=max(4, size // 9)))
    ctx.set_source_surface(surf, cx - surf.get_width() / 2, cy - surf.get_height() / 2)
    ctx.paint()


def banner():
    W, H = 2560, 1440
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    rays(ctx, W, H, W / 2, H / 2, (0.16, 0.5, 0.98), (0.26, 0.6, 1.0), 22)
    # alt zemin şeridi (güvenli alanın altı)
    ground = 925
    ctx.rectangle(0, ground - 8, W, H - ground + 8); ctx.set_source_rgb(0.99, 0.8, 0.2); ctx.fill()
    ctx.rectangle(0, ground - 8, W, 10); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
    s = 3.9
    cast = [('pip', 190, 1, 'excited', 'hips', 'wide'), ('big_tony', 420, 1, 'smug', 'arms_crossed', 'closed'),
            ('dex', 640, 1, 'excited', 'pointing', 'ai'),
            ('nia', 1800, -1, 'smug', 'hips', 'closed'), ('mama_rose', 2140, -1, 'angry', 'fist', 'closed'),
            ('coach_barry', 2390, -1, 'excited', 'fist', 'wide')]
    for cid, x, f, emo, pose, mouth in cast:
        character(ctx, cid, x, ground, s, f, emo, pose, mouth)
    paste_text(ctx, ['DEX', '&', 'FRIENDS'], 190, W / 2, 640, 1100, color=(255, 222, 40))
    paste_text(ctx, 'NEW ANIMATED COMEDY EVERY DAY'.split(), 58, W / 2, 815, 1300)
    surf.write_to_png(str(OUT / 'banner.png'))


def head_shot(cid, size, bg1, bg2, emotion='happy', ring=True):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    rays(ctx, size, size, size / 2, size / 2, bg1, bg2, 16)
    s = size / 64
    # baş merkezi (0,-77) -> kare ortası biraz aşağı
    character(ctx, cid, size / 2 - 3 * s, size / 2 + 79 * s, s, 1, emotion, 'standing', 'ai')
    if ring:
        ctx.arc(size / 2, size / 2, size / 2 - size * 0.02, 0, 2 * math.pi)
        ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.set_line_width(size * 0.035); ctx.stroke()
    return surf


def main():
    OUT.mkdir(exist_ok=True)
    banner()
    head_shot('dex', 800, (1.0, 0.62, 0.15), (1.0, 0.72, 0.3), emotion='excited').write_to_png(str(OUT / 'profile.png'))
    wm = head_shot('dex', 300, (0.9, 0.12, 0.15), (0.97, 0.25, 0.25), emotion='excited')
    wm.write_to_png(str(OUT / 'watermark.png'))
    Image.open(OUT / 'watermark.png').resize((150, 150), Image.LANCZOS).save(OUT / 'watermark.png')
    for p in sorted(OUT.glob('*.png')):
        print(p.name, Image.open(p).size, f'{p.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
