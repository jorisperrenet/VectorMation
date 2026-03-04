"""BulletedList example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

bl = BulletedList(
    'Install dependencies',
    'Configure settings',
    'Run the application',
    font_size=40, fill='#fff', stroke_width=0,
)
v.add(bl)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_bulleted_list.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
