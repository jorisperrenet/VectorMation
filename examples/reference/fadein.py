"""Compare fadein, write, and create side by side."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=50, cx=380, cy=540, fill='#58C4DD')
c.fadein(start=0, end=1.5)
label_c = Text('fadein', x=380, y=650, font_size=28, fill='#aaa', text_anchor='middle')
label_c.fadein(start=0, end=0.5)

s = Square(side=100, x=910, y=490, fill='#E74C3C')
s.write(start=0, end=1.5)
label_s = Text('write', x=960, y=650, font_size=28, fill='#aaa', text_anchor='middle')
label_s.fadein(start=0, end=0.5)

t = RegularPolygon(5, radius=55, cx=1540, cy=540, fill='#83C167')
t.create(start=0, end=1.5)
label_t = Text('create', x=1540, y=650, font_size=28, fill='#aaa', text_anchor='middle')
label_t.fadein(start=0, end=0.5)

v.add(c, s, t, label_c, label_s, label_t)
if args.for_docs:
    v.export_video('docs/source/_static/videos/fadein.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
