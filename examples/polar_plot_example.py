import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/polar_plot')
canvas.set_background()

# Create polar axes and plot a rose curve
polar = PolarAxes(r_range=(0, 3), n_rings=3, n_sectors=12)

# Plot a 4-petal rose: r = 3*cos(2*theta)
curve = polar.plot_polar(
    lambda theta: 3 * abs(math.cos(math.radians(theta) * 2)),
    theta_range=(0, 360),
    stroke='#FF6666', stroke_width=3,
)

title = TexObject(r'Rose Curve: $r = 3|\cos(2\theta)|$',
                  font_size=44, fill='#fff')
title.center_to_pos(960, 80)

canvas.add_objects(polar, title)

if args.for_docs:
    canvas.write_frame(filename='docs/source/_static/videos/polar_plot_example.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
