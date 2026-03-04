"""Checkerboard surface colours."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
surface = Surface(lambda x, y: math.sin(x) * math.cos(y),
                  u_range=(-3, 3), v_range=(-3, 3),
                  resolution=(20, 20))
surface.set_checkerboard('#FC6255', '#c44030')
axes.add_surface(surface)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_checkerboard.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
