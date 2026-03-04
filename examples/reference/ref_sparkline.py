"""SparkLine inline chart."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

spark = SparkLine(
    data=[10, 14, 12, 18, 15, 22, 20, 26, 24, 30, 28, 35],
    x=560, y=440, width=800, height=200,
    stroke='#58C4DD', stroke_width=3, show_endpoint=True,
)

v.add(spark)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_sparkline.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
