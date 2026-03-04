"""BoxPlot with multiple data groups."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = BoxPlot(
    data_groups=[
        [2, 5, 7, 8, 9, 10, 12, 14, 15],
        [1, 3, 4, 6, 7, 8, 10, 11, 18],
        [5, 6, 7, 8, 9, 10, 11, 12, 13],
    ],
    x=500, y=200, plot_width=600, plot_height=500,
    box_color='#58C4DD', median_color='#E74C3C',
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_box_plot.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
