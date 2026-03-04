"""Flash the object border."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=90, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.highlight_border(start=0.5, end=1.2, color='#FFFF00', width=6)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_highlight_border.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
