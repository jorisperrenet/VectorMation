"""Bar chart with sorting animation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bc = BarChart([3, 7, 2, 5], labels=['Q1', 'Q2', 'Q3', 'Q4'],
              colors=['#E74C3C', '#3498DB', '#2ECC71', '#F39C12'])
bc.fadein(start=0, end=1)
bc.animate_sort(start=2, end=3)

v.add(bc)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_bar_sort.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
