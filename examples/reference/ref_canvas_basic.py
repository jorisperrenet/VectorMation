"""Basic canvas scene with shapes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background(fill='#1a1a2e')

c = Circle(r=100, cx=600, cy=540, fill='#58C4DD', fill_opacity=0.8)
r = Rectangle(200, 140, x=1220, y=470, fill='#E74C3C', fill_opacity=0.8)
t = Text('Hello!', x=960, y=300, font_size=60, fill='#fff',
         stroke_width=0, text_anchor='middle')

v.add(c, r, t)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_canvas_basic.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
