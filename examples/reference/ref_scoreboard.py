"""Scoreboard metric panel."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = Scoreboard(
    entries=[
        ('Users', '12.4K'),
        ('Revenue', '$84K'),
        ('Growth', '+18%'),
        ('Uptime', '99.9%'),
    ],
    x=360, y=420, col_width=300, row_height=200,
    font_size=56,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_scoreboard.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
