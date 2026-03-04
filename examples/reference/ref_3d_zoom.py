"""Zooming in on a 3D scene with set_camera_zoom."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
faces = Cube(side_length=2, fill_color='#58C4DD')
for face in faces:
    axes.add_surface(face)
axes.set_camera_zoom(2.0, start=0, end=2)

v.add(axes)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_3d_zoom.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
