"""Text shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

t = Text('Hello, World!', x=960, y=540, font_size=72,
         fill='#fff', stroke_width=0, text_anchor='middle')
v.add(t)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_text.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
