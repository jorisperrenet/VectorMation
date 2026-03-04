"""Circle with grow_from_center."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c1 = Circle(r=80, cx=480, cy=540, fill='#58C4DD', fill_opacity=0.8, stroke_width=3)
c2 = Circle(r=60, cx=960, cy=540, fill='#E74C3C', fill_opacity=0.8, stroke_width=3)
c3 = Circle(r=100, cx=1440, cy=540, fill='#83C167', fill_opacity=0.6, stroke_width=3)

v.add(c1, c2, c3)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/circle.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
