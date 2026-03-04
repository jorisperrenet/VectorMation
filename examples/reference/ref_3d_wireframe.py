"""Surface with wireframe mesh overlay using SurfaceMesh."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def saddle(x, y):
    return (x**2 - y**2) / 4

surface = Surface(saddle, resolution=(20, 20),
                  fill_color='#58C4DD', fill_opacity=0.8)
mesh = SurfaceMesh(surface, stroke_color='#ffffff', stroke_opacity=0.3)
axes.add_surface(surface)
axes.add_surface(mesh)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_wireframe.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
