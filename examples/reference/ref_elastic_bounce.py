"""Bouncing with squash and stretch."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=50, fill='#2ECC71', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.elastic_bounce(start=0.3, end=2.5, height=150, n_bounces=4, squash_factor=1.5)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_elastic_bounce.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
