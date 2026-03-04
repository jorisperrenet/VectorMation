"""GanttChart for project timelines."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = GanttChart(
    tasks=[
        ('Research', 0, 3, '#58C4DD'),
        ('Design', 2, 5, '#E74C3C'),
        ('Develop', 4, 9, '#2ECC71'),
        ('Testing', 7, 10, '#F39C12'),
        ('Deploy', 9, 11, '#9B59B6'),
    ],
    x=100, y=200, width=1600,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_gantt.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
