"""Ambient camera rotation around a 3D scene."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
sphere = Sphere3D(radius=1.5, checkerboard_colors=('#FC6255', '#c44030'))
axes.add_surface(sphere)
axes.begin_ambient_camera_rotation(start=0, rate=0.3)

v.add(axes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_3d_ambient_rotation.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
