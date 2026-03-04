"""Damped sine wave using FunctionGraph."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

curve = FunctionGraph(lambda x: math.sin(x) * math.exp(-x / 5),
                      x_range=(0, 20), stroke='#2ECC71', stroke_width=3)

v.add(curve)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_damped_sine.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
