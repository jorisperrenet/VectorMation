"""Fibonacci Spiral — golden ratio visualization.

Draws successive Fibonacci squares and the inscribed quarter-circle arcs
that form the classic golden spiral. Numbers and proportions animate in.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/fibonacci_spiral')
canvas.set_background()

# ── Fibonacci sequence ─────────────────────────────────────────────────
fibs = [1, 1, 2, 3, 5, 8, 13]
n = len(fibs)
scale = 50  # pixels per unit

# Colors for each square
colors = color_gradient(['#58C4DD', '#83C167', '#FFFF00', '#FF6B6B', '#BD93F9'], n=n)

# ── Layout: build squares spiralling outward ───────────────────────────
# Each square is placed adjacent to the previous rectangle.
# Direction cycles: right, up, left, down
dx = [1, 0, -1, 0]
dy = [0, -1, 0, 1]

# Track bounding rect as we grow
cx, cy = 960, 540  # start centered
x, y = cx, cy      # current placement anchor (bottom-left of first square)

squares = []
positions = []  # (x, y, size) for each square

for i, f in enumerate(fibs):
    size = f * scale
    d = i % 4  # direction index

    if i == 0:
        # First square: place at origin
        sx, sy = x, y
    elif d == 0:  # right
        prev_x, prev_y, prev_s = positions[-1]
        sx = prev_x + prev_s
        sy = prev_y + prev_s - size
    elif d == 1:  # up
        prev_x, prev_y, prev_s = positions[-1]
        sx = prev_x + prev_s - size
        sy = prev_y - size
    elif d == 2:  # left
        prev_x, prev_y, prev_s = positions[-1]
        sx = prev_x - size
        sy = prev_y
    else:  # down
        prev_x, prev_y, prev_s = positions[-1]
        sx = prev_x
        sy = prev_y + prev_s

    # Adjust second square placement
    if i == 1:
        sx = x + fibs[0] * scale
        sy = y

    positions.append((sx, sy, size))

# Center the whole arrangement
all_xs = [p[0] for p in positions] + [p[0] + p[2] for p in positions]
all_ys = [p[1] for p in positions] + [p[1] + p[2] for p in positions]
offset_x = 960 - (min(all_xs) + max(all_xs)) / 2
offset_y = 540 - (min(all_ys) + max(all_ys)) / 2
positions = [(px + offset_x, py + offset_y, s) for px, py, s in positions]

# ── Draw squares and labels ────────────────────────────────────────────
t = 0.3
for i, (sx, sy, size) in enumerate(positions):
    sq = Rectangle(size, size, x=sx, y=sy, creation=t,
                   fill=colors[i], fill_opacity=0.25, stroke=colors[i],
                   stroke_width=2)
    sq.grow_from_center(t, t + 0.5)
    canvas.add(sq)

    # Fibonacci number label
    lbl = Text(text=str(fibs[i]), x=sx + size / 2, y=sy + size / 2 + 8,
               font_size=min(size * 0.4, 36), fill='#fff', stroke_width=0,
               text_anchor='middle', creation=t + 0.2)
    lbl.fadein(t + 0.2, t + 0.5)
    canvas.add(lbl)
    t += 0.4

# ── Draw the golden spiral (quarter-circle arcs) ───────────────────────
spiral_start = t
arc_paths = []
for i, (sx, sy, size) in enumerate(positions):
    d = i % 4
    # Determine arc center (corner of square) and start/end angles
    if d == 0:    # arc from bottom-left to top-right, center at bottom-right
        acx, acy = sx + size, sy + size
        start_a, end_a = 180, 270
    elif d == 1:  # center at bottom-left
        acx, acy = sx, sy + size
        start_a, end_a = 270, 360
    elif d == 2:  # center at top-left
        acx, acy = sx, sy
        start_a, end_a = 0, 90
    else:         # center at top-right
        acx, acy = sx + size, sy
        start_a, end_a = 90, 180

    arc = Arc(cx=acx, cy=acy, r=size, start_angle=start_a, end_angle=end_a,
              stroke='#FFB86C', stroke_width=3, fill_opacity=0, creation=spiral_start)
    arc.create(spiral_start, spiral_start + 0.3)
    canvas.add(arc)
    spiral_start += 0.15

# ── Title ──────────────────────────────────────────────────────────────
title = Text(text='Fibonacci Spiral', x=960, y=55,
             font_size=44, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 0.5)
canvas.add(title)

# ── Golden ratio label ─────────────────────────────────────────────────
phi = (1 + math.sqrt(5)) / 2
ratio_text = Text(text=f'\u03c6 = {phi:.6f}...', x=960, y=1030,
                  font_size=28, fill='#888', stroke_width=0, text_anchor='middle',
                  creation=t)
ratio_text.fadein(t, t + 0.5)
canvas.add(ratio_text)

canvas.browser_display(start=args.start or 0, end=args.end or 6,
                           fps=args.fps, port=args.port)
