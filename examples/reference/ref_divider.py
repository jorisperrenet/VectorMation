"""Divider with centered label."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

div = Divider(x=560, y=540, length=800, direction='horizontal',
              label='Section Break', stroke='#58C4DD')

v.add(div)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_divider.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
