"""MorphObject morphing a circle into a square."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

circle = Circle(r=120, fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
square = Rectangle(240, 240, fill='#E74C3C', fill_opacity=0.8, stroke='#E74C3C')

morph = MorphObject(circle, square, start=0.5, end=2.5)

v.add(morph)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_morph.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
