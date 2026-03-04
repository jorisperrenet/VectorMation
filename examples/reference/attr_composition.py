"""Chaining multiple attribute calls over time."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dot = Dot(cx=360, cy=540, r=20, fill='#E74C3C')
dot.fadein(start=0, end=0.5)

# Chain: move right, then set a constant position, then move again
dot.c.move_to(0.5, 2, (960, 540))       # slide to centre
dot.c.set_onward(2, (960, 300))          # jump up instantly
dot.c.move_to(2.5, 4, (1560, 540))      # slide to right

v.add(dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/attr_composition.mp4', fps=30, end=4.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4.5)
