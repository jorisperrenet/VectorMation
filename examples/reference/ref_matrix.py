"""Matrix with bracket delimiters."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

matrix = Matrix(
    data=[
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ],
    font_size=40,
)

v.add(matrix)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_matrix.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
