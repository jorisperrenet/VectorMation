"""Cutout & ConvexHull Demo — spotlight overlay and convex hull wrapping."""
import random
from vectormation.objects import *

random.seed(42)

canvas = VectorMathAnim()
canvas.set_background()

title = TexObject(r'Cutout \& ConvexHull', x=960, y=70, font_size=52,
                  fill='#FFFFFF', stroke_width=0, anchor='center')
title.fadein(0.0, 0.5)
canvas.add(title)

# The cutout overlay — starts covering everything, then reveals shapes
cutout = Cutout(
    hole_x=800, hole_y=350, hole_w=200, hole_h=200,
    color='#111122', opacity=0.85, rx=15, ry=15,
    creation=0, z=50,
)
cutout.fadein(0.5, 1.0)
# Animate the hole to grow and sweep across the shapes
cutout.set_hole(x=730, y=320, w=350, h=330, start=1.0, end=2.0)
cutout.set_hole(x=680, y=280, w=500, h=420, start=2.0, end=3.0)
cutout.fadeout(3, 4)
canvas.add(cutout)

# --- ConvexHull (right half of screen) ---
hull_sub_title = TexObject(r'ConvexHull', x=960, y=170, font_size=28,
                           fill='#FFFFFF', stroke_width=0, anchor='center')
hull_sub_title.fadein(0.2, 0.6)
canvas.add(hull_sub_title)

# Scattered dots
dot_positions = []
dots_colors = ['#E84D60', '#58C4DD', '#83C167', '#F5A623', '#9B59B6', '#4ECDC4']
for i in range(14):
    dx = random.uniform(960-200, 960+200)
    dy = random.uniform(200, 500)*2 - 100
    dot_positions.append((dx, dy))
    d = Dot(cx=dx, cy=dy, r=8, fill=dots_colors[i % len(dots_colors)],
            stroke_width=0)
    d.fadein(0.3 + i * 0.08, 0.6 + i * 0.08)
    canvas.add(d)

# ConvexHull polygon wrapping all dots
hull = ConvexHull(
    *dot_positions,
    fill='#58C4DD', fill_opacity=0.2, stroke='#58C4DD', stroke_width=3,
)
hull.create(1.5, 2.5)
canvas.add(hull)

T = 5.0

canvas.show(end=T)
