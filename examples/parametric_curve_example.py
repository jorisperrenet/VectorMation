import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/parametric_curve')
canvas.set_background()

# Plot a Lissajous figure as a parametric curve
axes = Axes(x_range=(-4, 4), y_range=(-4, 4), show_grid=True,
            plot_height=900)

# Lissajous: x = 3*sin(3t), y = 3*sin(2t)
curve = axes.plot_parametric(
    lambda t: (3 * math.sin(3 * t), 3 * math.sin(2 * t)),
    t_range=(0, 2 * math.pi),
    num_points=300,
    stroke='#83C167', stroke_width=4,
)

title = Text(text='Lissajous Figure (3:2)', x=960, y=60,
             font_size=48, fill='#fff', stroke_width=0, text_anchor='middle')

canvas.add_objects(axes, title)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/parametric_curve_example.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
