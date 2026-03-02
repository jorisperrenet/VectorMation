import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import math
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/tangent_line')
canvas.set_background()

title = Text(text='Tangent Line on Graph', x=960, y=60,
             font_size=48, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

ax = Axes(x_range=(-3, 3), y_range=(-2, 10),
          plot_width=1200, plot_height=700,
          x=360, y=140)
ax.fadein(0.5, 1)

func = lambda x: x ** 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)

# Tangent at x=1
tan1 = ax.get_tangent_line(func, x_val=1, length=300, stroke='#FF6B6B', stroke_width=2)
tan1.fadein(1.5, 2)

# Tangent at x=-1.5
tan2 = ax.get_tangent_line(func, x_val=-1.5, length=300, stroke='#FFFF00', stroke_width=2)
tan2.fadein(2.5, 3)

# Tangent at x=0 (horizontal)
tan3 = ax.get_tangent_line(func, x_val=0, length=300, stroke='#83C167', stroke_width=2)
tan3.fadein(3.5, 4)

# Dots at tangent points
for xv, color in [(1, '#FF6B6B'), (-1.5, '#FFFF00'), (0, '#83C167')]:
    sx, sy = ax.coords_to_point(xv, func(xv))
    dot = Dot(cx=sx, cy=sy, fill=color)
    dot.fadein(1.5, 2)
    canvas.add_objects(dot)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/tangent_line_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
