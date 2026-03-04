"""Fibonacci Spiral — golden ratio visualization.

Draws successive Fibonacci squares and the inscribed quarter-circle arcs
that form the classic golden spiral. Numbers and proportions animate in.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/fibonacci_spiral')
canvas.set_background()

fibs = [1, 1, 2, 3, 5, 8]
scale = 100
colors = color_gradient(['#58C4DD', '#83C167', '#FFFF00', '#FF6B6B', '#BD93F9'], n=len(fibs))

# Build square positions spiralling outward: down, left, up, right
pos = [(0, 0, scale), (scale, 0, scale)]
for i in range(2, len(fibs)):
    s = fibs[i] * scale
    x0 = min(p[0] for p in pos)
    y0 = min(p[1] for p in pos)
    x1 = max(p[0] + p[2] for p in pos)
    y1 = max(p[1] + p[2] for p in pos)
    pos.append([(x1 - s, y1, s), (x0 - s, y1 - s, s),
                (x0, y0 - s, s), (x1, y0, s)][(i - 2) % 4])

# Center on canvas
ax = [p[0] for p in pos] + [p[0] + p[2] for p in pos]
ay = [p[1] for p in pos] + [p[1] + p[2] for p in pos]
ox, oy = 960 - (min(ax) + max(ax)) / 2, 540 - (min(ay) + max(ay)) / 2
pos = [(x + ox, y + oy, s) for x, y, s in pos]

# Arc spec per direction: (corner_dx, corner_dy, start_angle, end_angle)
ARC = [((1, 1), 180, 90), ((0, 1), 90, 0), ((0, 0), 360, 270), ((1, 0), 270, 180)]

title = TexObject(r'Fibonacci Spiral', x=960, y=55, font_size=44, fill='#fff',
                  stroke_width=0, anchor='center')
title.fadein(0, 0.5)
canvas.add(title)

t = 0.3
for i, (sx, sy, s) in enumerate(pos):
    sq = Rectangle(s, s, x=sx, y=sy, creation=t,
                   fill=colors[i], fill_opacity=0.25, stroke=colors[i], stroke_width=2)
    sq.grow_from_center(t, t + 0.5)

    lbl = TexObject(str(fibs[i]), x=sx + s / 2, y=sy + s / 2,
                    font_size=min(s * 0.4, 36), fill='#fff', stroke_width=0,
                    anchor='center', creation=t + 0.2)
    lbl.center_to_pos(sx + s / 2, sy + s / 2)
    lbl.fadein(t + 0.2, t + 0.5)

    (cdx, cdy), sa, ea = ARC[i % 4]
    arc = Arc(cx=sx + cdx * s, cy=sy + cdy * s, r=s, start_angle=sa, end_angle=ea,
              stroke='#FFB86C', stroke_width=3, fill_opacity=0, creation=t + 0.3)
    arc.create(t + 0.3, t + 0.45)

    canvas.add(sq, lbl, arc)
    t += 0.4

phi_str = f'{(1 + math.sqrt(5)) / 2:.6f}'
phi_lbl = TexObject(rf'$\varphi = {phi_str}\ldots$', x=960, y=1030,
                    font_size=28, fill='#fff', stroke_width=0, anchor='center',
                    creation=t)
phi_lbl.fadein(t, t + 0.5)
canvas.add(phi_lbl)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/fibonacci_spiral.mp4', fps=30, end=6)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or 6, fps=args.fps, port=args.port)
