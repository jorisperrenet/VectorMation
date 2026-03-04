"""Star shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

s = Star(5, outer_radius=140, inner_radius=60, cx=960, cy=540,
         fill='#F1C40F', fill_opacity=0.7, stroke='#F1C40F')
v.add(s)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_star_shape.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
