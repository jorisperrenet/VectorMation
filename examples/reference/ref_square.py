"""Square shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

squares = VCollection(
    Square(side=120, fill='#58C4DD', fill_opacity=0.7, stroke='#58C4DD'),
    Square(side=160, fill='#FF6B6B', fill_opacity=0.7, stroke='#FF6B6B'),
    Square(side=200, fill='#83C167', fill_opacity=0.7, stroke='#83C167'),
)
squares.arrange(direction='right', buff=60)
squares.center_to_pos()

v.add(squares)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_square.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
