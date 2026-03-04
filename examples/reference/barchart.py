"""Bar chart grow and sort."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bc = BarChart([40, 70, 25, 55, 90], labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
              colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6'])
bc.grow_from_zero(start=0, end=1.5)
bc.animate_sort(start=2, end=3.5)

v.add(bc)
if args.for_docs:
    v.export_video('docs/source/_static/videos/barchart.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
