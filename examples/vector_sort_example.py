import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/vector_sort')
canvas.set_background()

title = Text(text='Vectors, Intervals & Sort Children', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with vectors
ax = Axes(x_range=(-3, 4), y_range=(-2, 4),
          plot_width=550, plot_height=400,
          x=100, y=180)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Add some vectors
v1 = ax.add_vector(2, 3, stroke='#FF6B6B', fill='#FF6B6B')
v1.fadein(1.5, 2)
v2 = ax.add_vector(-1, 2, stroke='#83C167', fill='#83C167')
v2.fadein(1.8, 2.3)
v3 = ax.add_vector(3, 1, stroke='#58C4DD', fill='#58C4DD')
v3.fadein(2.1, 2.6)

# Vertical lines at several points
import math
curve = ax.plot(lambda x: 0.3 * x ** 2, stroke='#aaa', stroke_width=2)
curve.create(2.5, 3)
vlines = ax.get_vertical_lines(lambda x: 0.3 * x ** 2, [0, 1, 2, 3],
                                stroke='#FFFF00', creation=3)
vlines.fadein(3, 3.5)

# Interval bracket
intv = ax.add_interval(1, 3, creation=3.5, stroke='#FF6B6B', stroke_width=3)
intv.fadein(3.5, 4)

# Sort children demo
values = [5, 2, 8, 1, 3]
dots = VCollection(
    *[Dot(cx=1100 + i * 80, cy=700, r=18,
          fill=['#FF6B6B', '#83C167', '#58C4DD', '#FFFF00', '#FF79C6'][i])
      for i in range(5)]
)
labels = VCollection(
    *[Text(text=str(v), x=1100 + i * 80, y=660,
           font_size=20, fill='#fff', stroke_width=0, text_anchor='middle')
      for i, v in enumerate(values)]
)
dots.fadein(4, 4.5)
labels.fadein(4, 4.5)

sort_label = Text(text='Sort by label value', x=1300, y=610,
                  font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
sort_label.fadein(4.5, 5)

# Sort by the associated value
label_vals = values[:]
dots.sort_children(key=lambda obj, t: label_vals[dots.objects.index(obj)],
                   start=5, end=6)
labels.sort_children(key=lambda obj, t: int(obj.text.at_time(t)),
                     start=5, end=6)

canvas.add_objects(ax, title, dots, labels, sort_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/vector_sort_example.mp4', fps=30, end=6)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
