"""LabeledLine with midpoint text."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ll = LabeledLine(x1=660, y1=540, x2=1260, y2=540, label='600 px', stroke='#58C4DD')

v.add(ll)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_labeled_line.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
