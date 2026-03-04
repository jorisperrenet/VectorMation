"""Animated pie chart with value transitions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

pie = PieChart([30, 20, 50], labels=['A', 'B', 'C'])
pie.fadein(start=0, end=1)
pie.animate_values([40, 40, 20], start=2, end=3)

v.add(pie)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_animated_pie.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
