"""RoundedRectangle shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

r = RoundedRectangle(300, 180, corner_radius=20, fill='#9B59B6', fill_opacity=0.6, stroke='#9B59B6')
v.add(r)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_rounded_rect.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
