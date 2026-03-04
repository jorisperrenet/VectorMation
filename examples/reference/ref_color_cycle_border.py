"""Animated color-cycling border (AnimatedBoundary)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

rect = Rectangle(300, 200, fill='#1a1a2e', fill_opacity=0.9)
rect.center_to_pos(posx=960, posy=540)
border = AnimatedBoundary(rect, cycle_rate=0.5, buff=10, stroke_width=4)
v.add(rect, border)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_color_cycle_border.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
