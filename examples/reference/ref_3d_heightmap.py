"""Height-map surface (z = f(x, y))."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def paraboloid(x, y):
    return (x**2 + y**2) / 4

surface = Surface(paraboloid, u_range=(-2, 2), v_range=(-2, 2),
                  resolution=(20, 20), fill_color='#4488ff')
axes.add_surface(surface)

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_3d_heightmap.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
