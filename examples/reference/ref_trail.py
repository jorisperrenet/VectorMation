"""Ghost trail following a moving object."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Dot(cx=300, cy=540, r=16, fill='#E67E22')
c.fadein(start=0, end=0.3)
c.shift(dx=1300, start=0.3, end=2.5)
ghosts = c.trail(start=0.3, end=2.5, n_copies=6, fade=True)
v.add(c)
v.add(*ghosts)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_trail.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
