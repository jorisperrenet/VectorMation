"""2D vector field on axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(-4, 4), y_range=(-4, 4))
ax.add_coordinates()
ax.plot_vector_field(lambda x, y: (-y, x), x_step=1, y_step=1, stroke='#58C4DD')

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/graph_vector_field.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=1)
