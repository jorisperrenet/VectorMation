"""MatrixHeatmap with labeled rows and columns."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = MatrixHeatmap(
    data=[
        [1.0, 0.8, 0.2, 0.1],
        [0.8, 1.0, 0.5, 0.3],
        [0.2, 0.5, 1.0, 0.7],
        [0.1, 0.3, 0.7, 1.0],
    ],
    row_labels=['A', 'B', 'C', 'D'],
    col_labels=['A', 'B', 'C', 'D'],
    x=600, y=250, cell_size=80, font_size=18,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_matrix_heatmap.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
