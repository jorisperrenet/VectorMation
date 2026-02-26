import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/polar_plot')
canvas.set_background()

# Create polar axes and plot a rose curve
polar = PolarAxes(r_range=(0, 3), n_rings=3, n_sectors=12)
polar.fadein(0, 1)

# Plot a 4-petal rose: r = 3*cos(2*theta)
curve = polar.plot_polar(
    lambda theta: 3 * abs(math.cos(math.radians(theta) * 2)),
    theta_range=(0, 360),
    stroke='#FF6666', stroke_width=3,
)
curve.create(1, 3)

title = Text(text='Rose Curve: r = 3|cos(2\u03b8)|', x=960, y=80,
             font_size=44, fill='#fff', stroke_width=0, text_anchor='middle')
title.write(0, 1)

canvas.add_objects(polar, title)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
