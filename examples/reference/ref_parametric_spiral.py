"""Parametric spiral using ParametricFunction."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

spiral = ParametricFunction(
    lambda t: (960 + 200 * t * math.cos(6 * t), 540 + 200 * t * math.sin(6 * t)),
    t_range=(0, math.pi), num_points=300,
    stroke='#FC6255', stroke_width=3)

v.add(spiral)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_parametric_spiral.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
