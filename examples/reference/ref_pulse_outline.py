"""Pulsating outline glow."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = RegularPolygon(5, radius=100, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulse_outline(start=0.3, end=2, color='#F1C40F', max_width=10, cycles=3)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_pulse_outline.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
