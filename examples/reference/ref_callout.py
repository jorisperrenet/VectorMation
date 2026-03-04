"""Callout pointing to a target position."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dot = Dot(cx=960, cy=540, fill='#58C4DD')
callout = Callout('Look here!', target=(960, 540), direction='up', distance=80)

v.add(dot, callout)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_callout.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
