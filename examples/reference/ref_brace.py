"""Brace annotation around a rectangle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

rect = Rectangle(400, 150, fill='#3498DB', fill_opacity=0.4, stroke='#3498DB')
brace = Brace(rect, direction='down', label='400 px', stroke='#F39C12')

v.add(rect, brace)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_brace.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
