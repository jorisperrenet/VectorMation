"""Demo of extended animation effects: dissolve, shimmer, breathe, bounce,
typewriter, parallax, snap_to_grid, follow_spline, and more."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    Circle, Square, Rectangle, Dot, Text, VectorMathAnim, parse_args,
)

v = VectorMathAnim('/tmp')

# ── Section 1: dissolve_in / dissolve_out (0-2s) ──────────────
title1 = Text(text='dissolve_in / dissolve_out', x=960, y=80, font_size=28,
              text_anchor='middle', creation=0)
v.add(title1)
title1.fadeout(start=2, end=2.3)

c1 = Circle(r=80, cx=500, cy=500, fill='#4FC3F7')
c1.dissolve_in(start=0, end=1)
c1.dissolve_out(start=1.2, end=2)
v.add(c1)

s1 = Square(120, x=1200, y=440, fill='#FF8A65')
s1.dissolve_in(start=0.2, end=1)
s1.dissolve_out(start=1.4, end=2)
v.add(s1)

# ── Section 2: shimmer and breathe (2-4s) ─────────────────────
title2 = Text(text='shimmer / breathe', x=960, y=80, font_size=28,
              text_anchor='middle', creation=2)
v.add(title2)
title2.fadeout(start=4, end=4.3)

c2 = Circle(r=80, cx=500, cy=500, fill='#81C784', creation=2)
c2.shimmer(start=2, end=4, passes=2)
v.add(c2)

c3 = Circle(r=80, cx=1420, cy=500, fill='#CE93D8', creation=2)
c3.breathe(start=2, end=4, amplitude=0.15)
v.add(c3)

# ── Section 3: bounce_in / bounce_out (4-6s) ──────────────────
title3 = Text(text='bounce_in / bounce_out', x=960, y=80, font_size=28,
              text_anchor='middle', creation=4)
v.add(title3)
title3.fadeout(start=6, end=6.3)

r1 = Rectangle(width=140, height=100, x=390, y=420, fill='#F48FB1', creation=4)
r1.bounce_in(start=4, end=5)
r1.bounce_out(start=5.5, end=6)
v.add(r1)

r2 = Square(120, x=1260, y=420, fill='#FFE082', creation=4)
r2.bounce_in(start=4.3, end=5)
r2.bounce_out(start=5.3, end=6)
v.add(r2)

# ── Section 4: wipe / wipe reverse (6-8s) ───
title4 = Text(text='wipe / wipe reverse', x=960, y=80,
              font_size=28, text_anchor='middle', creation=6)
v.add(title4)
title4.fadeout(start=8, end=8.3)

txt = Text(text='Hello, Animation!', x=960, y=450, font_size=48,
           text_anchor='middle', creation=6)
txt.wipe(start=6, end=7.2)
txt.wipe(start=7.5, end=8, reverse=True)
v.add(txt)

# ── Section 5: follow_spline / animate_along_object (8-10s) ───
title5 = Text(text='follow_spline / animate_along_object', x=960, y=80,
              font_size=28, text_anchor='middle', creation=8)
v.add(title5)
title5.fadeout(start=10, end=10.3)

d1 = Dot(cx=200, cy=500, r=15, fill='#4FC3F7', creation=8)
d1.follow_spline([(200, 500), (500, 200), (960, 600), (1700, 400)], start=8, end=10)
v.add(d1)

orbit_path = Circle(r=200, cx=1400, cy=500, fill_opacity=0, stroke='#555',
                    stroke_width=2, creation=8)
v.add(orbit_path)
d2 = Dot(cx=1600, cy=500, r=12, fill='#FF8A65', creation=8)
d2.animate_along_object(orbit_path, start=8, end=10)
v.add(d2)

# ── Section 6: snap_to_grid / parallax (10-12s) ──────────────
title6 = Text(text='snap_to_grid / parallax', x=960, y=80, font_size=28,
              text_anchor='middle', creation=10)
v.add(title6)
title6.fadeout(start=12, end=12.3)

# Snap to grid: move objects then snap
dots_snap = []
for i in range(6):
    d = Dot(cx=200 + i * 100, cy=300 + (i % 3) * 80, r=12, fill='#81C784', creation=10)
    d.snap_to_grid(start=10.5, grid_size=100)
    v.add(d)
    dots_snap.append(d)

# Parallax: two layers at different depths
bg_sq = Square(100, x=1150, y=300, fill='#37474F', creation=10)
fg_sq = Square(80, x=1250, y=400, fill='#FFE082', creation=10)
bg_sq.parallax(dx=200, dy=0, start=10, end=12, depth_factor=0.3)
fg_sq.parallax(dx=200, dy=0, start=10, end=12, depth_factor=0.8)
v.add(bg_sq)
v.add(fg_sq)

# ── Section 7: rotate_in / squish / visibility_toggle (12-14s)
title7 = Text(text='rotate_in / squish / visibility_toggle', x=960, y=80,
              font_size=28, text_anchor='middle', creation=12)
v.add(title7)
title7.fadeout(start=14, end=14.3)

r3 = Rectangle(width=120, height=80, x=350, y=420, fill='#CE93D8', creation=12)
r3.rotate_in(start=12, end=13)
v.add(r3)

c4 = Circle(r=60, cx=960, cy=500, fill='#4FC3F7', creation=12)
c4.squish(start=12.5, end=13.5)
v.add(c4)

blinking = Dot(cx=1500, cy=500, r=20, fill='#FF8A65', creation=12)
blinking.visibility_toggle(12, 12.5, 13, 13.5, 14)
v.add(blinking)

# ── Section 8: appear_from / animate_to / move_towards (14-16s)
title8 = Text(text='appear_from / animate_to / move_towards', x=960, y=80,
              font_size=28, text_anchor='middle', creation=14)
v.add(title8)

source = Dot(cx=200, cy=500, r=8, fill='#aaa', creation=14)
v.add(source)
c5 = Circle(r=50, cx=700, cy=500, fill='#81C784', creation=14)
c5.appear_from(source, start=14, end=15)
v.add(c5)

c6 = Circle(r=40, cx=1100, cy=300, fill='#F48FB1', creation=14)
c7 = Circle(r=40, cx=1500, cy=700, fill='#FFE082', creation=14)
c6.fadein(start=14, end=14.5)
c6.animate_to(c7, start=14.5, end=15.5)
v.add(c6)
v.add(c7)

c7.fadein(start=14, end=14.5)

if __name__ == '__main__':
    args = parse_args()
    if not args.no_display:
        v.browser_display(start=args.start or 0, end=args.end or 16,
                          fps=args.fps, port=args.port)
