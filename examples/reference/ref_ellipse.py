"""Ellipse shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

e = Ellipse(rx=200, ry=100, fill='#58C4DD', fill_opacity=0.6, stroke='#58C4DD')
v.add(e)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_ellipse.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
