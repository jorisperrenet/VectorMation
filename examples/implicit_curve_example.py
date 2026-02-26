import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/implicit_curve')
canvas.set_background()

# Plot implicit curves: circle and lemniscate
axes = Axes(x_range=(-4, 4), y_range=(-3, 3), show_grid=True,
            x_label='x', y_label='y')
axes.fadein(0, 1)

# Unit circle: x^2 + y^2 - 1 = 0
circle_curve = axes.plot_implicit(
    lambda x, y: x**2 + y**2 - 1,
    num_points=80, stroke='#FF6666', stroke_width=3,
)
circle_curve.create(1, 2)

# Lemniscate of Bernoulli: (x^2 + y^2)^2 = 4(x^2 - y^2)
lemniscate = axes.plot_implicit(
    lambda x, y: (x**2 + y**2)**2 - 4 * (x**2 - y**2),
    num_points=120, stroke='#58C4DD', stroke_width=3,
)
lemniscate.create(2, 3.5)

title = Text(text='Implicit Curves', x=960, y=60,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(axes, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
