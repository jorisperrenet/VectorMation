"""3D primitives: dot, line, arrow."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.add_3d(Dot3D((1, 0, 0), radius=8, fill='#FC6255'))
axes.add_3d(Dot3D((0, 2, 0), radius=8, fill='#83C167'))
axes.add_3d(Dot3D((0, 0, 1.5), radius=8, fill='#58C4DD'))
axes.add_3d(Line3D((0, 0, 0), (1, 0, 0), stroke='#FC6255', stroke_width=3))
axes.add_3d(Line3D((0, 0, 0), (0, 2, 0), stroke='#83C167', stroke_width=3))
axes.add_3d(Arrow3D((0, 0, 0), (0, 0, 1.5), stroke='#58C4DD', stroke_width=3))

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/3d_primitives.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
