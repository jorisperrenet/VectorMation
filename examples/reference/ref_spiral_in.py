"""Star with spiral_in effect."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Star(5, outer_radius=100, inner_radius=45, fill='#1ABC9C', fill_opacity=0.8)
c.spiral_in(start=0, end=2, n_turns=2)

v.add(c)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_spiral_in.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
