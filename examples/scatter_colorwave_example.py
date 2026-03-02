import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/scatter_colorwave')
canvas.set_background()

title = Text(text='Shaded Inequality', x=960, y=50,
             font_size=42, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 1)

# Shaded inequality
ax = Axes(x_range=(-1, 7), y_range=(-2, 4),
          plot_width=500, plot_height=300,
          x=100, y=300)
ax.add_coordinates()
ax.fadein(0.5, 1.5)

func = lambda x: math.sin(x) * 1.5 + 1
curve = ax.plot(func, stroke='#83C167', stroke_width=3)
curve.create(1.5, 2.5)

shade = ax.add_shaded_inequality(func, direction='below', creation=2,
                                  fill='#83C167', fill_opacity=0.15)
shade.fadein(2, 2.5)

ineq_label = Text(text='y < f(x)', x=550, y=290,
                  font_size=20, fill='#aaa', stroke_width=0, text_anchor='middle')
ineq_label.fadein(2, 2.5)

canvas.add_objects(ax, title, shade, ineq_label)

if args.verbose:
    canvas.export_video('docs/source/_static/videos/scatter_colorwave_example.mp4', fps=30, end=4)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
