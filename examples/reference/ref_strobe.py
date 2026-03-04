"""Rapid on/off strobe blink."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=80, fill='#E74C3C', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.strobe(start=0.3, end=2, n_flashes=8, duty=0.4)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_strobe.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
