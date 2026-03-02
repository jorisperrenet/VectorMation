"""Showcase get_subcurve: extract a portion of a polyline."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/curve_effects')

poly = Lines((700, 250), (850, 250), (900, 350), (850, 450), (700, 450), (650, 350),
             stroke='#555', stroke_width=2, fill_opacity=0)
poly.fadein(start=0, end=1)
sub = poly.get_subcurve(0.2, 0.6, stroke='#E74C3C', stroke_width=4, fill_opacity=0)
sub.create(start=1, end=2.5)
label = Text("get_subcurve(0.2, 0.6)", x=775, y=510, font_size=20, fill='#888')
label.fadein(start=0, end=1)

v.add(poly, sub, label)
if args.for_docs:
    v.export_video('docs/source/_static/videos/curve_effects_example.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
