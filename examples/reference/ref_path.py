"""Path shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

d = 'M 560,640 C 660,300 1260,300 1360,640'
p = Path(d, stroke='#E74C3C', stroke_width=5, fill_opacity=0)
v.add(p)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_path.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
