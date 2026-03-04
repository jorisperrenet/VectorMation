"""Lines: open polyline through vertices."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

zigzag = Lines(
    (400, 700), (600, 380), (800, 700), (1000, 380), (1200, 700), (1400, 380), (1600, 700),
    stroke='#58C4DD', stroke_width=4, fill_opacity=0,
)

v.add(zigzag)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_lines.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
