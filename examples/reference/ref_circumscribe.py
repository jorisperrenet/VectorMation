"""Rectangle with circumscribe effect."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

r = Rectangle(200, 140, fill='#3498DB', fill_opacity=0.8)
r.fadein(start=0, end=0.3)
outline = r.circumscribe(start=0.5, end=2, buff=14, color='#FFFF00')

v.add(r, outline)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_circumscribe.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
