"""Geometric optics — convex lens focusing parallel rays."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *

canvas = VectorMathAnim(save_dir='svgs/optics')
canvas.set_background()

# Create a convex lens
lens = Lens(cx=960, cy=540, height=400, focal_length=250,
            color='#58C4DD', show_focal_points=True, show_axis=True)

# Create several parallel rays at different heights
ray_colors = ['#FFFF00', '#FFD700', '#FFA500', '#FF8C00', '#FF6347']
rays = []
offsets = [-150, -75, 0, 75, 150]
for i, offset in enumerate(offsets):
    ray = Ray(x1=150, y1=540 + offset, angle=0, length=1600,
              lenses=[lens], color=ray_colors[i], stroke_width=2,
              show_arrow=True)
    rays.append(ray)

title = Text('Convex Lens — Parallel Rays', x=960, y=60, font_size=36,
             text_anchor='middle', fill='#fff', stroke_width=0)

focal_label = Text('Focal Point', x=1210 + 30, y=540 + 25, font_size=18,
                    fill='#FFFF00', stroke_width=0)

# Animations
lens.fadein(start=0, end=1)
title.fadein(start=0, end=1)
focal_label.fadein(start=0.5, end=1.5)
for i, ray in enumerate(rays):
    ray.fadein(start=0.5 + i * 0.15, end=1.5 + i * 0.15)

canvas.add_objects(lens, *rays, title, focal_label)
args = parse_args()
if args.verbose:
    canvas.export_video('docs/source/_static/videos/optics_example.mp4', fps=30, end=3)
if not args.no_display:
    canvas.browser_display(start=0, end=3, fps=args.fps, port=args.port)
