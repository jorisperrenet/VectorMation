"""Variable display with numeric value."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

var = Variable(label='x', value=3.14, font_size=48)

v.add(var)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_variable.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
