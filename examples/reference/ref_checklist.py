"""Checklist with checked and unchecked items."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

cl = Checklist(
    ('Buy groceries', True),
    ('Walk the dog', True),
    'Write docs',
    'Deploy app',
    x=780, y=400,
)

v.add(cl)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_checklist.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
