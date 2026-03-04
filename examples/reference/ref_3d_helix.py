"""ParametricCurve3D helix."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def helix(t):
    return (math.cos(t), math.sin(t), t / (2 * math.pi))

curve = ParametricCurve3D(helix, t_range=(0, 4 * math.pi),
                          num_points=200, stroke='#FFFF00', stroke_width=3)
axes.add_3d(curve)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_helix.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
