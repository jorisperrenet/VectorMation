"""Passing flash along stroke."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=100, fill_opacity=0, stroke='#58C4DD', stroke_width=4)
c.fadein(start=0, end=0.3)
flash = c.show_passing_flash(start=0.3, end=1.5, flash_width=0.2, color='#FFFF00', stroke_width=6)
v.add(c)
v.add(flash)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_show_passing_flash.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
