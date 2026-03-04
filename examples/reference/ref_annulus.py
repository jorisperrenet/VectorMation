"""Annulus shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

a = Annulus(inner_radius=80, outer_radius=160, cx=960, cy=540,
            fill='#E74C3C', fill_opacity=0.6, stroke='#E74C3C')
v.add(a)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_annulus.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
