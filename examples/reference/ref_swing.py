"""Pendulum-like swing oscillation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Rectangle(width=40, height=180, fill='#1ABC9C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.swing(start=0.3, end=2, amplitude=25)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_swing.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
