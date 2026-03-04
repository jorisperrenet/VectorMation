"""TextBox with dark background."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

tb = TextBox('System Online', x=830, y=510, font_size=28, padding=16,
             box_fill='#1e1e2e', text_color='#58C4DD')

v.add(tb)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_textbox.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
