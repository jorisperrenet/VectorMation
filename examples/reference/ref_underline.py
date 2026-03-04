"""Underline beneath a text object."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

txt = Text(text='Important Text', x=960, y=520, font_size=48, fill='#fff', stroke_width=0)
ul = Underline(txt, buff=4, stroke='#58C4DD', stroke_width=3)

v.add(txt, ul)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_underline.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
