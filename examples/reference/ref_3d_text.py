"""Text3D label in 3D space."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.add_3d(Dot3D((1, 1, 1), radius=6, fill='#FC6255'))
axes.add_3d(Text3D('P(1,1,1)', point=(1.3, 1.3, 1.2), font_size=18, fill='#FC6255'))
axes.add_3d(Text3D('Origin', point=(0.2, 0.2, 0.2), font_size=16, fill='#aaaaaa'))

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_text.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
