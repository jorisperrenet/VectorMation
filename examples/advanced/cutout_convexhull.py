"""Cutout & ConvexHull Demo — spotlight overlay and convex hull wrapping."""
import random
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *

random.seed(42)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/cutout_convexhull')
canvas.set_background()

title = TexObject(r'Cutout \& ConvexHull', x=960, y=70, font_size=52,
                  fill='#FFFFFF', stroke_width=0, anchor='center')
title.fadein(0.0, 0.5)
canvas.add(title)

# --- Cutout (spotlight effect, left half of screen) ---
cutout_sub_title = TexObject(r'Cutout (spotlight)', x=440, y=170, font_size=28,
                             fill='#FFFFFF', stroke_width=0, anchor='center')
cutout_sub_title.fadein(0.2, 0.6)
canvas.add(cutout_sub_title)

# Background content behind the cutout
bg_star = Star(n=5, outer_radius=100, inner_radius=45, cx=350, cy=430,
               fill='#E84D60', stroke='#E84D60', stroke_width=2)
bg_star.fadein(0.0, 0.5)
canvas.add(bg_star)

bg_hex = RegularPolygon(n=6, radius=70, cx=530, cy=500,
                        fill='#58C4DD', stroke='#58C4DD', stroke_width=2)
bg_hex.fadein(0.0, 0.5)
canvas.add(bg_hex)

bg_circle = Circle(r=50, cx=400, cy=600, fill='#83C167',
                   stroke='#83C167', stroke_width=2)
bg_circle.fadein(0.0, 0.5)
canvas.add(bg_circle)

# The cutout overlay — starts covering everything, then reveals shapes
cutout = Cutout(
    hole_x=300, hole_y=350, hole_w=200, hole_h=200,
    color='#111122', opacity=0.85, rx=15, ry=15,
    creation=0, z=50,
)
cutout.fadein(0.3, 0.8)
# Animate the hole to grow and sweep across the shapes
cutout.set_hole(x=230, y=320, w=350, h=330, start=1.0, end=2.0)
cutout.set_hole(x=180, y=280, w=500, h=420, start=2.0, end=3.0)
canvas.add(cutout)

# --- ConvexHull (right half of screen) ---
hull_sub_title = TexObject(r'ConvexHull', x=1350, y=170, font_size=28,
                           fill='#FFFFFF', stroke_width=0, anchor='center')
hull_sub_title.fadein(0.2, 0.6)
canvas.add(hull_sub_title)

# Scattered dots
dot_positions = []
dots_colors = ['#E84D60', '#58C4DD', '#83C167', '#F5A623', '#9B59B6', '#4ECDC4']
for i in range(14):
    dx = random.uniform(1050, 1650)
    dy = random.uniform(250, 700)
    dot_positions.append((dx, dy))
    d = Dot(cx=dx, cy=dy, r=8, fill=dots_colors[i % len(dots_colors)],
            stroke_width=0)
    d.fadein(0.3 + i * 0.08, 0.6 + i * 0.08)
    canvas.add(d)

# ConvexHull polygon wrapping all dots
hull = ConvexHull(
    *dot_positions,
    fill='#58C4DD', fill_opacity=0.12, stroke='#58C4DD', stroke_width=2.5,
)
hull.fadein(1.5, 2.0)
canvas.add(hull)

hull_label = TexObject(r'Hull wraps all points', x=1350, y=760, font_size=22,
                       fill='#58C4DD', stroke_width=0, anchor='center')
hull_label.fadein(2.0, 2.4)
canvas.add(hull_label)

T = 5.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/cutout_convexhull.mp4', fps=30, end=T)
if not args.for_docs:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
