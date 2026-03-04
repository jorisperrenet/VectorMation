"""Brace between two points."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

d1 = Dot(cx=500, cy=540, r=8, fill='#FF6B6B')
d2 = Dot(cx=1420, cy=540, r=8, fill='#FF6B6B')
line = DashedLine(x1=500, y1=540, x2=1420, y2=540, stroke='#aaa', stroke_width=2)
brace = brace_between_points((500, 540), (1420, 540),
                              direction='down', label='width')
v.add(line, d1, d2, brace)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_brace_between.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
