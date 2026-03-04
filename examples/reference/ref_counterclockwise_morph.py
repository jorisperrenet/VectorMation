"""counterclockwise_morph: circle to square morph."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

circle = Circle(r=120, cx=960, cy=540, fill='#58C4DD', stroke='#58C4DD')
square = Rectangle(240, 240, x=960, y=540, fill='#E74C3C', stroke='#E74C3C')

morph = counterclockwise_morph(circle, square, start=0, end=2)

v.add(morph)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_counterclockwise_morph.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
