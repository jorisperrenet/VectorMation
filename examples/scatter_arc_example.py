import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/scatter_arc')
canvas.set_background()

title = Text(text='Scatter Plot, Arc Paths & Align', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with scatter data
ax = Axes(x_range=(0, 10), y_range=(0, 20),
          plot_width=700, plot_height=400,
          x=150, y=200)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Scatter plot
import random
random.seed(42)
xs = [i * 0.5 for i in range(1, 19)]
ys = [0.2 * x ** 2 + random.uniform(-2, 2) for x in xs]
scatter = ax.plot_scatter(xs, ys, r=4, fill='#FF6B6B')
scatter.fadein(1.5, 2.5)

# Highlight y-range showing a band
band = ax.highlight_y_range(5, 15, fill='#58C4DD', fill_opacity=0.1)
band.fadein(2.5, 3)

# Three dots that move in arcs
colors = ['#FF6B6B', '#83C167', '#FFFF00']
dots = []
for i, color in enumerate(colors):
    d = Dot(cx=1200 + i * 100, cy=800, r=15, fill=color)
    dots.append(d)

group = VCollection(*dots)
group.fadein(1, 1.5)

# Move dots along arc paths to new positions
import math
dots[0].path_arc(1200, 650, start=3, end=4, angle=math.pi / 2)
dots[1].path_arc(1300, 650, start=3.2, end=4.2, angle=-math.pi / 2)
dots[2].path_arc(1400, 650, start=3.4, end=4.4, angle=math.pi)

# Now align them to left edge
# Create some rectangles to demonstrate align_submobjects
rects = VCollection(
    Rectangle(80, 40, x=1150, y=650, fill='#FF6B6B', fill_opacity=0.5, stroke_width=1, stroke='#fff'),
    Rectangle(120, 40, x=1200, y=700, fill='#83C167', fill_opacity=0.5, stroke_width=1, stroke='#fff'),
    Rectangle(60, 40, x=1250, y=750, fill='#FFFF00', fill_opacity=0.5, stroke_width=1, stroke='#fff'),
)
rects.fadein(4.5, 5)

# Align all rectangles to left edge
rects.align_submobjects('left', start_time=5.5)

canvas.add_objects(ax, title, group, rects)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
