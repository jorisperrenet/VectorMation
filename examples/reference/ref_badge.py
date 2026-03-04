"""Badge pill-shaped label."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

b1 = Badge(text='v2.0', x=860, y=520, bg_color='#58C4DD', text_color='#000')
b2 = Badge(text='stable', x=960, y=520, bg_color='#2ECC71', text_color='#000')
b3 = Badge(text='beta', x=1050, y=520, bg_color='#F39C12', text_color='#000')

v.add(b1, b2, b3)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_badge.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
