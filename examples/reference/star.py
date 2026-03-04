"""Star creation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

s5 = Star(5, outer_radius=90, inner_radius=40, cx=480, cy=540,
          fill='#F1C40F', fill_opacity=0.8, stroke_width=2)
s6 = Star(6, outer_radius=90, inner_radius=50, cx=960, cy=540,
          fill='#E74C3C', fill_opacity=0.8, stroke_width=2)
s8 = Star(8, outer_radius=90, inner_radius=55, cx=1440, cy=540,
          fill='#9B59B6', fill_opacity=0.8, stroke_width=2)

v.add(s5, s6, s8)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/star.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
