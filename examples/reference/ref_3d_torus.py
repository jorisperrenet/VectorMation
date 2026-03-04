"""Torus3D on ThreeDAxes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-4, 4), y_range=(-4, 4), z_range=(-2, 2))
torus = Torus3D(major_radius=2, minor_radius=0.5,
                checkerboard_colors=('#9B59B6', '#7D3C98'))
axes.add_surface(torus)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_torus.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
