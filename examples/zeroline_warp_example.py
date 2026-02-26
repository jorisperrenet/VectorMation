import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/zeroline_warp')
canvas.set_background()

title = Text(text='Zero Line, Dot Labels & Warp', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with negative range to show zero line
ax = Axes(x_range=(-2, 6), y_range=(-3, 5),
          plot_width=650, plot_height=400,
          x=150, y=180)
ax.add_coordinates()
ax.add_zero_line(axis='x')
ax.add_zero_line(axis='y')
ax.fadein(0.5, 1.5)

# Plot a curve that crosses zero
import math
curve = ax.plot(lambda x: math.sin(x) * 2, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

# Dot labels at key points
ax.add_dot_label(0, 0, label='origin', creation=2.5)
ax.add_dot_label(math.pi / 2, 2, label='peak', creation=2.5)
ax.add_dot_label(math.pi, 0, label='zero', creation=2.5)

# Warp demo on right side
shapes = VCollection(
    Circle(cx=1350, cy=400, r=50, fill='#FF6B6B', fill_opacity=0.6,
           stroke='#FF6B6B', stroke_width=2),
    Rectangle(100, 100, x=1450, y=350, fill='#83C167', fill_opacity=0.6,
              stroke='#83C167', stroke_width=2),
    Star(outer_radius=50, inner_radius=25, cx=1600, cy=400,
         fill='#FFFF00', fill_opacity=0.6, stroke='#FFFF00', stroke_width=2),
)
shapes.fadein(3, 3.5)

warp_label = Text(text='Warp Effect', x=1450, y=300,
                  font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle')
warp_label.fadein(3, 3.5)

shapes[0].warp(start=3.5, end=5.5, amplitude=0.2, frequency=4)
shapes[1].warp(start=4, end=6, amplitude=0.15, frequency=3)
shapes[2].warp(start=4.5, end=6.5, amplitude=0.25, frequency=5)

canvas.add_objects(ax, title, shapes, warp_label)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
