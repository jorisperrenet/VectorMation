"""Axes.add_vector: draw a vector on axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

axes = Axes(x_range=(-4, 4), y_range=(-3, 3))
axes.add_coordinates()
axes.add_vector(2, 1, stroke='#FFFF00', fill='#FFFF00')
axes.add_vector(-1, 2, stroke='#58C4DD', fill='#58C4DD')

v.add(axes)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_vector_on_axes.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
