"""Meter bar (vertical fill level)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

meter = Meter(value=0.65, x=940, y=340, width=40, height=200,
              direction='vertical', fill_color='#2ECC71')

v.add(meter)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_meter.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
