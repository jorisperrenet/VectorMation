"""Cross mark (X shape)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c1 = Cross(cx=600, cy=540, size=120, stroke='#FC6255', stroke_width=6)
c2 = Cross(cx=960, cy=540, size=80, stroke='#FFFF00', stroke_width=4)
c3 = Cross(cx=1320, cy=540, size=160, stroke='#83C167', stroke_width=8)
label1 = Text('size=120', x=600, y=660, font_size=22, fill='#aaa', text_anchor='middle')
label2 = Text('size=80', x=960, y=660, font_size=22, fill='#aaa', text_anchor='middle')
label3 = Text('size=160', x=1320, y=660, font_size=22, fill='#aaa', text_anchor='middle')
v.add(c1, c2, c3, label1, label2, label3)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_cross_mark.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
