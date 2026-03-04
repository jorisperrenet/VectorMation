"""3D surface with camera rotation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-1, 2))
axes.plot_surface(lambda x, y: math.exp(-(x**2 + y**2) / 2),
                  resolution=(20, 20),
                  checkerboard_colors=('#FF862F', '#4488ff'))
axes.begin_ambient_camera_rotation(start=0, rate=0.3)

v.add(axes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/3d_surface.mp4', fps=30, end=6)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=6)
