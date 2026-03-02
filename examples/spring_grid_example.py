import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/spring_grid')
canvas.set_background()

title = Text(text='Axes with Grid', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Axes with grid enabled
import math
ax = Axes(x_range=(-3, 3), y_range=(-2, 2),
          plot_width=700, plot_height=350,
          x=200, y=200)
ax.add_grid()
ax.add_coordinates()
ax.fadein(0.5, 1.5)

# Plot a sine wave
curve = ax.plot(math.sin, stroke='#58C4DD', stroke_width=3)
curve.create(1.5, 2.5)

canvas.add_objects(ax, title)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/spring_grid_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
