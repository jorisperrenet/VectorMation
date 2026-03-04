"""Periodic color pulsing."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=90, fill='#2ECC71', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulse_color(color='#E74C3C', start=0.3, end=2.5, n_pulses=4)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_pulse_color.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
