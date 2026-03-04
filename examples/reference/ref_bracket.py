"""Bracket decoration with label."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

rect = Rectangle(300, 60, x=810, y=500, fill='#333', stroke='#58C4DD')
bracket = Bracket(x=810, y=570, width=300, height=20, direction='down',
                  stroke='#F39C12', text='width = 300')

v.add(rect, bracket)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_bracket.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
