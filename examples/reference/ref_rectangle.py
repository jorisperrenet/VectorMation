"""Rectangle shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

r = Rectangle(300, 180, fill='#E74C3C', fill_opacity=0.6, stroke='#E74C3C')
v.add(r)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_rectangle.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
