"""StatusIndicator with different states."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

s1 = StatusIndicator('API Server', status='online', x=830, y=470)
s2 = StatusIndicator('Database', status='warning', x=830, y=510)
s3 = StatusIndicator('Cache', status='offline', x=830, y=550)

v.add(s1, s2, s3)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_status_indicator.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
