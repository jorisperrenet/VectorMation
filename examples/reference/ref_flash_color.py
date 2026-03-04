"""Quick color flash effect."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = RegularPolygon(6, radius=100, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.flash_color(color='#FF6B6B', start=0.5, end=1.2)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_flash_color.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
