"""Spring-like scale with overshoot."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = RegularPolygon(6, radius=70, fill='#F39C12', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.morph_scale(target_scale=1.8, start=0.3, end=2, overshoot=0.4, oscillations=3)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_morph_scale.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
