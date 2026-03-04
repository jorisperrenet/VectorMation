"""TimelineBar with labeled markers."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

timeline = TimelineBar(
    markers={0: 'Start', 2: 'Design', 5: 'Build', 8: 'Test', 10: 'Launch'},
    total_duration=10,
    x=200, y=540, width=1520,
)

v.add(timeline)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_timeline.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
