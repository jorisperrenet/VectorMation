"""Icosahedron on ThreeDAxes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
faces = Icosahedron(size=1.5, fill_color='#58C4DD')
for face in faces:
    axes.add_surface(face)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_icosahedron.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
