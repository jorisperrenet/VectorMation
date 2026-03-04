"""Breadcrumb navigation trail."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bc = Breadcrumb('Home', 'Products', 'Electronics', 'Laptops',
                x=750, y=530, active_color='#58C4DD')

v.add(bc)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_breadcrumb.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
