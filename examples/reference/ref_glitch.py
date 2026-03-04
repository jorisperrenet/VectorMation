"""Random offset glitch flickers."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Rectangle(width=200, height=120, fill='#2ECC71', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.glitch(start=0.3, end=1.5, intensity=15, n_flashes=6)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_glitch.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
