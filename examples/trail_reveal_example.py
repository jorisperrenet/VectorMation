import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/trail_reveal')
canvas.set_background()

title = Text(text='Min/Max Labels', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with min/max labels
ax = Axes(x_range=(-1, 7), y_range=(-2, 3),
          plot_width=500, plot_height=300,
          x=100, y=350)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x * 1.5) * 2
curve = ax.plot(func, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

labels = ax.add_min_max_labels(func, creation=2.5)
labels.fadein(2.5, 3)

canvas.add_objects(ax, title, labels)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/trail_reveal_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
