"""Array highlight and swap."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

arr = Array([5, 3, 8, 1, 9, 2])
arr.center_to_pos()
arr.fadein(start=0, end=0.5)
arr.highlight_cell(2, start=1, end=2, color='#58C4DD')
arr.swap_cells(0, 4, start=2.5, end=3.5)

v.add(arr)
if args.for_docs:
    v.export_video('docs/source/_static/videos/array.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
