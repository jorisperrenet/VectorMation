"""Animated camera rotation with set_camera_orientation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.plot_surface(lambda x, y: math.sin(x) * math.cos(y),
                  resolution=(20, 20), fill_color='#58C4DD')
axes.set_camera_orientation(0, 3, phi=math.radians(30), theta=math.radians(-120))

v.add(axes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_3d_camera_rotation.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
